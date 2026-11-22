"""Zero-model-cost Buffer scheduler. Secrets never enter the queue or logs.

Remote state is reconciled before every write. An uncertain mutation is NOT
blindly retried: its caption/channel/due-time identity is checked on the next run.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent/'.vendor'))
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parent
POST_FIELDS = "id channelId text status dueAt sentAt externalLink schedulingType metricsUpdatedAt metrics { type value unit } error { message }"
READ_POSTS = "query Posts($input: PostsInput!, $after: String) { posts(input:$input, first:100, after:$after) { edges { node { " + POST_FIELDS + " } } pageInfo { hasNextPage endCursor } } }"
CREATE = "mutation Create($input: CreatePostInput!) { createPost(input:$input) { __typename ... on PostActionSuccess { post { " + POST_FIELDS + " } } ... on InvalidInputError { message } ... on LimitReachedError { message } ... on NotFoundError { message } ... on UnexpectedError { message } } }"
RETRY = "mutation Retry($input: PublishPostNowInput!) { publishPostNow(input:$input) { __typename ... on PostActionSuccess { post { " + POST_FIELDS + " } } ... on MutationError { message } } }"

def load(path, default=None):
    return json.loads(path.read_text(encoding='utf-8-sig')) if path.exists() else default

def save(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix+'.tmp')
    tmp.write_text(json.dumps(value,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    tmp.replace(path)

class APIError(RuntimeError):
    pass

class Buffer:
    def __init__(self, key):
        self.key = key

    def query(self, query, variables=None, *, mutation=False):
        payload=json.dumps({'query':query,'variables':variables or {}}).encode()
        req=urllib.request.Request('https://api.buffer.com',payload,headers={
            'Authorization':'Bearer '+self.key,'Content-Type':'application/json',
            'User-Agent':'SolacenOrganic/1.0'})
        # Reads can retry transient errors. Writes have uncertain outcomes and cannot.
        for attempt in range(1 if mutation else 3):
            try:
                with urllib.request.urlopen(req,timeout=45) as response:
                    obj=json.load(response)
                if obj.get('errors'):
                    raise APIError('; '.join(e.get('message','GraphQL error') for e in obj['errors']))
                return obj['data']
            except urllib.error.HTTPError as exc:
                if exc.code in (401,403):
                    raise APIError('Buffer authorization rejected; owner must refresh the key or channel connection.') from None
                if not mutation and exc.code in (429,500,502,503,504) and attempt<2:
                    time.sleep(2**attempt*2)
                    continue
                raise APIError(f'Buffer HTTP {exc.code}; '+('write outcome uncertain, reconcile next run.' if mutation else 'read failed.')) from None
            except (urllib.error.URLError,TimeoutError) as exc:
                if not mutation and attempt<2:
                    time.sleep(2**attempt*2)
                    continue
                raise APIError('Network failure; '+('write outcome uncertain, reconcile next run.' if mutation else 'read failed.')) from None

    def channels(self, org):
        return self.query('query Channels($input:ChannelsInput!) { channels(input:$input) { id name displayName service externalLink isDisconnected isLocked isQueuePaused } }',{'input':{'organizationId':org}})['channels']

    def posts(self, org, channel_ids, start):
        result=[]
        after=None
        for _ in range(30):
            # Live API check: startDate hid every known scheduled post. Reconcile
            # by exact channels and pagination; never risk duplicate writes on a
            # silently empty date-filter result.
            data=self.query(READ_POSTS,{'input':{'organizationId':org,'filter':{'channelIds':channel_ids}},'after':after})['posts']
            result.extend(e['node'] for e in data['edges'])
            if not data['pageInfo']['hasNextPage']:
                return result
            after=data['pageInfo']['endCursor']
        raise APIError('History exceeds the safe pagination window; no scheduling performed.')

def parse_time(value):
    return datetime.fromisoformat(value.replace('Z','+00:00')) if value else None

def post_identity(channel,text,due):
    normalized=parse_time(due).astimezone(timezone.utc).isoformat() if due else ''
    return hashlib.sha256((channel+'\n'+text+'\n'+normalized).encode()).hexdigest()

def tracked_url(config,platform,item_id,row=None):
    row=row or {}
    args={'utm_source':platform,'utm_medium':'organic_social',
          'utm_campaign':config['campaign'],'utm_content':item_id}
    variant=row.get('variant_id',config['variant_id'] if not row.get('product_handle') else None)
    if variant: args['variant']=variant
    path='/collections/all' if row.get('collection_link') else '/products/'+row.get('product_handle',config['product_handle'])
    return config['store_url']+path+'?'+urllib.parse.urlencode(args)

def make_input(config,row,platform,day,*,draft=False):
    hour,minute=map(int,config['posting_times'][platform].split(':'))
    due=datetime(day.year,day.month,day.day,hour,minute,tzinfo=ZoneInfo(config['target_timezone'])).astimezone(timezone.utc)
    text=row[platform+'_caption'].replace('{url}',tracked_url(config,platform,row['id'],row))
    assets=[]
    for name in row['assets']:
        url=config['asset_base_url'].rstrip('/')+'/'+urllib.parse.quote(name)
        if row.get('format')=='reel':
            assets.append({'video':{'url':url,'metadata':{'title':row['hook'],'thumbnailOffset':1000}}})
        else:
            assets.append({'image':{'url':url,'metadata':{'altText':row['alt']}}})
    data={'channelId':config['channels'][platform],'text':text,'assets':assets,
          'schedulingType':'automatic','mode':'customScheduled','dueAt':due.isoformat().replace('+00:00','Z'),
          'needsApproval':False,'saveToDraft':draft,'aiAssisted':True}
    if platform=='instagram':
        data['metadata']={'instagram':{'type':'reel' if row.get('format')=='reel' else 'post','shouldShareToFeed':True,'isAiGenerated':bool(row.get('disclosure_required',False))}}
    else:
        data['metadata']={'facebook':{'type':'reel' if row.get('format')=='reel' else 'post'}}
    return data

def validate(config,queue,*,live=False):
    if config.get('paid_spending_allowed'):
        raise ValueError('This system never enables paid spending.')
    if len({r['id'] for r in queue})!=len(queue):
        raise ValueError('Duplicate queue identifiers.')
    if not queue:
        raise ValueError('Empty content queue.')
    if live and (not config['organization_id'] or not all(config['channels'].values())):
        raise ValueError('Both exact Solacen channel IDs and organization ID are required.')
    if live and not config['asset_base_url'].startswith('https://'):
        raise ValueError('Public HTTPS asset hosting must be configured.')
    for row in queue:
        if row['review_state']!='ready':
            continue
        if len(row['instagram_caption'])>2200:
            raise ValueError('Instagram caption too long: '+row['id'])
        if not 1<=len(row['assets'])<=10:
            raise ValueError('Unsupported image count: '+row['id'])
        for asset in row['assets']:
            if Path(asset).name!=asset or not (ROOT/'assets'/asset).is_file():
                raise ValueError('Missing or unsafe asset: '+asset)

def check_assets(config,row):
    for asset in row['assets']:
        req=urllib.request.Request(config['asset_base_url'].rstrip('/')+'/'+urllib.parse.quote(asset),method='HEAD')
        with urllib.request.urlopen(req,timeout=20) as resp:
            expected='video/' if row.get('format')=='reel' else 'image/'
            if not resp.headers.get('Content-Type','').startswith(expected):
                raise ValueError('Asset URL does not serve the expected media type: '+asset)

def plan(config,queue,now):
    first=date.fromisoformat(config['first_day'])
    today=now.astimezone(ZoneInfo(config['target_timezone'])).date()
    end=today+timedelta(days=config['lookahead_days'])
    for day_offset in range(max(0,(today-first).days),(end-first).days+1):
        cycle,index=divmod(day_offset,len(queue))
        maximum_cycle=config.get('maximum_cycle',1)
        if (maximum_cycle>0 and cycle>=maximum_cycle) or (cycle and not config.get('evergreen_rotation')):
            break
        row=dict(queue[index])
        if cycle:
            # An explicit 30-day cooldown; no identical caption reposts. No new model cost.
            row['id']+=f'_c{cycle+1}'
            prefaces=['A little reminder for your evening.','Make room for a quieter moment.',
              'Comfort, at your own pace.','Give the slower part of your day some space.',
              'Thoughtful details for an everyday wind-down.','A small pause can be part of your routine.',
              'Keep a moment that feels like yours.','Your next quiet evening starts with a little space.',
              'A familiar ritual, a little more considered.','Take a closer look at your evening comforts.',
              'Leave a little room for rest.','Revisit a favourite way to wind down.']
            for platform in ('instagram','facebook'):
                row[platform+'_caption']=prefaces[(cycle-1)%len(prefaces)]+'\n\n'+row[platform+'_caption']
                if today.month not in (11,12,1,2):
                    row[platform+'_caption']=row[platform+'_caption'].replace('winter evening','evening')
        if row['review_state']!='ready':
            continue
        day=first+timedelta(days=day_offset)
        for platform in ('instagram','facebook'):
            data=make_input(config,row,platform,day)
            if parse_time(data['dueAt'])>now+timedelta(minutes=20):
                yield row,platform,data

def run(config,queue,api,now,*,write=False):
    validate(config,queue,live=write)
    state=load(ROOT/'state'/'publishing.json',{'posts':{},'alerts':[]})
    state['alerts']=[]
    if not write:
        data=[{'id':r['id'],'platform':p,'dueAt':v['dueAt'],'images':len(v['assets'])} for r,p,v in plan(config,queue,now)]
        print(json.dumps({'mode':'dry_run','proposed_posts':data},indent=2))
        return state
    if not config['enabled']:
        raise ValueError('Publishing disabled in config.json; nothing sent.')
    channels={c['id']:c for c in api.channels(config['organization_id'])}
    intended=list(config['channels'].values())
    remote=api.posts(config['organization_id'],intended,(now-timedelta(days=100)).isoformat())
    known={post_identity(p['channelId'],p['text'],p.get('dueAt')):p for p in remote if p['status']!='draft'}
    pending={c:sum(p['channelId']==c and p['status'] not in ('sent','error','failed','draft','notSent') for p in remote) for c in intended}
    for row,platform,data in plan(config,queue,now):
        channel=data['channelId']
        key=post_identity(channel,data['text'],data['dueAt'])
        ch=channels.get(channel)
        if not ch or ch['isDisconnected'] or ch['isLocked'] or ch['isQueuePaused']:
            state['alerts'].append(f'{platform}: channel missing/disconnected/locked/paused; owner reconnect may be needed.')
            continue
        if key in known:
            p=known[key]
            previous=state['posts'].get(key,{})
            state['posts'][key]={**previous,'queue_id':row['id'],'family':row['family'],'platform':platform,**p}
            if p['status'] in ('error','failed','notSent'):
                state['alerts'].append(f"{platform} {row['id']}: {p.get('error') or p['status']}; retained existing post, no duplicate retry.")
            continue
        # Persistent uncertain intents are reconciled but never repeated automatically.
        if key in state['posts']:
            state['alerts'].append(f"{platform} {row['id']}: prior write needs reconciliation; no duplicate sent.")
            continue
        if pending[channel]>=min(config['queue_limit_per_channel'],10):
            continue
        try:
            check_assets(config,row)
            state['posts'][key]={'queue_id':row['id'],'family':row['family'],'platform':platform,'status':'intent','dueAt':data['dueAt']}
            save(ROOT/'state'/'publishing.json',state)
            result=api.query(CREATE,{'input':data},mutation=True)['createPost']
            if result['__typename']!='PostActionSuccess':
                # Typed refusal is definitive; a later run may retry safely.
                del state['posts'][key]
                raise APIError(result.get('message',result['__typename']))
            p=result['post']
            state['posts'][key].update(p)
            known[key]=p
            pending[channel]+=1
            save(ROOT/'state'/'publishing.json',state)
        except (APIError,ValueError,urllib.error.URLError,TimeoutError) as exc:
            state['alerts'].append(f"{platform} {row['id']}: {exc}")
            # Stop this platform's additions after an error, preserve the other platform.
            pending[channel]=10
    # Refresh metrics for ALL historical posts, not only the current lookahead window.
    for p in remote:
        key=post_identity(p['channelId'],p['text'],p.get('dueAt'))
        if key in state['posts']:
            state['posts'][key].update(p)
    for post in state['posts'].values():
        due=parse_time(post.get('dueAt'))
        if post.get('status') in ('scheduled','sending') and due and now-due>timedelta(hours=3):
            state['alerts'].append(f"{post.get('platform')} {post.get('queue_id')}: overdue; inspect the existing post, do not create a duplicate.")
    # Retry only a definitively failed, transient post, using its EXISTING Buffer ID.
    # Authentication, permissions, invalid media and unknown outcomes need attention.
    for key,post in list(state['posts'].items()):
        if post.get('status') not in ('error','failed') or not post.get('id'):
            continue
        message=(post.get('error') or {}).get('message','').lower()
        transient=any(x in message for x in ('temporar','timeout','rate limit','unavailable','try again','network'))
        if not transient or post.get('retry_attempts',0)>=2:
            state['alerts'].append(f"{post.get('queue_id')}: publishing failure needs attention; no replacement post created.")
            continue
        due=parse_time(post.get('dueAt'))
        if not due or not timedelta(0)<=now-due<=timedelta(days=1):
            continue
        if post.get('retry_uncertain'):
            continue
        post['retry_attempts']=post.get('retry_attempts',0)+1
        post['retry_uncertain']=True
        save(ROOT/'state'/'publishing.json',state)
        try:
            result=api.query(RETRY,{'input':{'id':post['id']}},mutation=True)['publishPostNow']
            if result['__typename']=='PostActionSuccess':
                post.update(result['post'])
            else:
                state['alerts'].append(f"Retry refused for {post.get('queue_id')}: {result.get('message',result['__typename'])}")
            post['retry_uncertain']=False
        except APIError as exc:
            state['alerts'].append(f"Retry outcome uncertain for {post.get('queue_id')}; reconcile existing post: {exc}")
    state['last_run_utc']=now.isoformat()
    save(ROOT/'state'/'publishing.json',state)
    save(ROOT/'state'/'health.json',{'last_run_utc':now.isoformat(),'alerts':state['alerts'],
         'posts_known':len(state['posts']),'remaining_original_concepts':min(len(queue),max(0,len(queue)-(now.date()-date.fromisoformat(config['first_day'])).days))})
    # Some platform metrics default missing values to zero. Keep availability caveat.
    print(json.dumps({'posts_known':len(state['posts']),'alerts':state['alerts']},indent=2))
    return state

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--write',action='store_true')
    parser.add_argument('--discover',action='store_true')
    args=parser.parse_args()
    config=load(ROOT/'config.json')
    queue=load(ROOT/'queue.json',[])
    key=os.environ.get('BUFFER_API_KEY','').strip()
    if not key and (ROOT/'.buffer-key').exists():
        key=(ROOT/'.buffer-key').read_text(encoding='utf-8-sig').strip()
    api=Buffer(key)
    if args.discover:
        if not key: raise ValueError('Buffer API key is not configured.')
        organizations=api.query('query { account { organizations { id name } } }')['account']['organizations']
        print(json.dumps([{'organization':o,'channels':api.channels(o['id'])} for o in organizations],indent=2))
        return
    if args.write and not config['enabled']:
        print('Publishing disabled; nothing sent.')
        return
    if args.write and not key: raise ValueError('Buffer API key is not configured.')
    result=run(config,queue,api,datetime.now(timezone.utc),write=args.write)
    if args.write and result['alerts']:
        raise SystemExit(2)

if __name__=='__main__':
    try: main()
    except (APIError,ValueError) as exc:
        print(str(exc),file=sys.stderr)
        raise SystemExit(1)
