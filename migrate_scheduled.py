"""Update existing scheduled posts by date, preserving IDs and recovery state.

Run only during the explicit disabled-refill maintenance window. Never create or
delete posts. Re-running reconciles edits by existing post ID.
"""
import json
from datetime import datetime, timezone
import publisher as p
EDIT='mutation Edit($input:EditPostInput!) { editPost(input:$input) { __typename ... on PostActionSuccess { post { '+p.POST_FIELDS+' } } ... on MutationError { message } } }'
def run():
    c=p.load(p.ROOT/'config.json'); assert c['enabled'] is False,'Refill must be disabled during migration.'
    q=p.load(p.ROOT/'queue.json');p.validate(c,q,live=True)
    api=p.Buffer((p.ROOT/'.buffer-key').read_text(encoding='utf-8-sig').strip())
    remote=api.posts(c['organization_id'],list(c['channels'].values()),None)
    state=p.load(p.ROOT/'state'/'publishing.json')
    recovery=p.ROOT/'state'/'local-queue-migration.json'
    log=p.load(recovery,{'before_posts':remote,'edits':[]})
    p.save(recovery,log)
    count=0
    for day,row,platform,data in p.plan(c,q,datetime.now(timezone.utc)):
        matches=[x for x in remote if x['channelId']==data['channelId'] and x.get('dueAt') and p.parse_time(x['dueAt'])==p.parse_time(data['dueAt']) and x['status']=='scheduled']
        if not matches: continue
        assert len(matches)==1,'Unexpected duplicate scheduled slot; inspect manually.'
        post=matches[0]
        edit={k:v for k,v in data.items() if k in ('text','assets','metadata','aiAssisted','schedulingType')}
        edit['id']=post['id']
        intent={'id':post['id'],'queue_id':row['id'],'platform':platform,'status':'intent','input':edit}
        log['edits'].append(intent);p.save(recovery,log)
        result=api.query(EDIT,{'input':edit},mutation=True)['editPost']
        if result['__typename']!='PostActionSuccess': raise p.APIError(str(result))
        updated=result['post']
        assert updated['id']==post['id'] and updated['status']=='scheduled'
        assert updated['text']==data['text'] and p.parse_time(updated['dueAt'])==p.parse_time(post['dueAt'])
        previous=[key for key,value in state['posts'].items() if value.get('id')==post['id']]
        assert len(previous)==1,'Each existing post must have one local identity.'
        record=state['posts'].pop(previous[0]);record.update(updated,queue_id=row['id'],platform=platform,product_key=row.get('product_key'),format=row['format'])
        key=p.post_identity(updated['channelId'],updated['text'],updated['dueAt'])
        state['posts'][key]=record
        p.save(p.ROOT/'state'/'publishing.json',state)
        intent['status']='confirmed';p.save(recovery,log)
        count+=1
        print(platform,row['id'],'updated existing ID',post['id'])
    fresh=api.posts(c['organization_id'],list(c['channels'].values()),None)
    before={x['id'] for x in remote};after={x['id'] for x in fresh}
    assert before==after,'No posts may be created or deleted by this migration.'
    assert len(state['posts'])==len({x.get('id') for x in state['posts'].values()})
    log['completed_utc']=datetime.now(timezone.utc).isoformat();log['same_remote_ids']=True;p.save(recovery,log)
    print('Confirmed',count,'in-place updates; no post IDs added or deleted.')
if __name__=='__main__':run()
