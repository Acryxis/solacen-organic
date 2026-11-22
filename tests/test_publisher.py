import copy
import contextlib
import io
import json
import tempfile
import unittest
from datetime import datetime,timezone
from pathlib import Path
from unittest.mock import patch
import publisher as p

class FakeBuffer:
    def __init__(self, fail=None, uncertain=None):
        self.created=[];self.fail=fail;self.uncertain=uncertain;self.retry_calls=0
    def channels(self,org):
        return [{'id':c,'isDisconnected':False,'isLocked':False,'isQueuePaused':False} for c in ('ig','fb')]
    def posts(self,*args): return self.created[:]
    def query(self,q,variables,mutation=False):
        data=variables['input']
        if 'publishPostNow' in q:
            self.retry_calls+=1
            post=next(x for x in self.created if x['id']==data['id'])
            post['status']='sending'
            return {'publishPostNow':{'__typename':'PostActionSuccess','post':post}}
        if data['channelId']==self.uncertain:
            raise p.APIError('write outcome uncertain')
        if data['channelId']==self.fail:
            return {'createPost':{'__typename':'InvalidInputError','message':'temporary refusal'}}
        post={'id':str(len(self.created)+1),'channelId':data['channelId'],'text':data['text'],
              'dueAt':data['dueAt'],'status':'buffer','schedulingType':'automatic'}
        self.created.append(post)
        return {'createPost':{'__typename':'PostActionSuccess','post':post}}

class SchedulerTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.root=Path(self.tmp.name)
        (self.root/'assets').mkdir()
        (self.root/'assets'/'one.jpg').write_bytes(b'image')
        self.config=json.loads((p.ROOT/'config.json').read_text())
        self.config.update(enabled=True,organization_id='org',asset_base_url='https://example.com/assets',lookahead_days=2,first_day='2026-11-24')
        self.config['channels']={'instagram':'ig','facebook':'fb'}
        self.rows=[{'id':'one','day_index':0,'family':'ritual','assets':['one.jpg'],'alt':'S5',
              'instagram_caption':'S5. Link in bio.','facebook_caption':'S5 {url}', 'review_state':'ready'}]
        self.now=datetime(2026,11,23,10,tzinfo=timezone.utc)
    def tearDown(self): self.tmp.cleanup()
    def execute(self,api):
        with patch.object(p,'ROOT',self.root),patch.object(p,'check_assets'),contextlib.redirect_stdout(io.StringIO()):
            return p.run(self.config,self.rows,api,self.now,write=True)
    def test_repeat_run_does_not_duplicate(self):
        api=FakeBuffer();self.execute(api);self.execute(api)
        self.assertEqual(len(api.created),4)
    def test_one_platform_failure_preserves_other(self):
        api=FakeBuffer(fail='fb');state=self.execute(api)
        self.assertEqual([x['channelId'] for x in api.created],['ig','ig'])
        self.assertTrue(state['alerts'])
    def test_uncertain_write_is_not_retried(self):
        api=FakeBuffer(uncertain='ig');self.execute(api);api.uncertain=None
        state=self.execute(api)
        self.assertEqual([x['channelId'] for x in api.created],['fb','fb','ig'])
        self.assertTrue(any(x['status']=='intent' for x in state['posts'].values()))
        self.assertTrue(any('reconciliation' in a for a in state['alerts']))
    def test_media_cap_is_enforced(self):
        self.config['queue_limit_per_channel']=1
        api=FakeBuffer();self.execute(api)
        self.assertEqual(len(api.created),2)
    def test_timezone_and_attribution(self):
        data=p.make_input(self.config,self.rows[0],'facebook',self.now.date())
        self.assertEqual(data['dueAt'],'2026-11-23T19:35:00Z')
        self.assertIn('utm_source=facebook',data['text'])
        self.assertEqual(data['schedulingType'],'automatic')
        self.assertEqual(data['metadata']['facebook']['type'],'post')
    def test_disabled_publishing_sends_nothing(self):
        self.config['enabled']=False
        api=FakeBuffer()
        with self.assertRaises(ValueError): self.execute(api)
        self.assertFalse(api.created)
    def test_catalogue_link_does_not_send_another_product_to_s5(self):
        row=dict(self.rows[0],product_handle='solacen-pageglow-rechargeable-reading-light')
        data=p.make_input(self.config,row,'facebook',self.now.date())
        self.assertIn('/products/solacen-pageglow-rechargeable-reading-light?',data['text'])
        self.assertNotIn('variant=',data['text'])
    def test_music_reel_is_automatic_video_on_both_channels(self):
        row=dict(self.rows[0],format='reel',assets=['calm.mp4'],hook='Quiet evening')
        for platform in ('instagram','facebook'):
            data=p.make_input(self.config,row,platform,self.now.date())
            self.assertEqual(data['metadata'][platform]['type'],'reel')
            self.assertIn('video',data['assets'][0])
            self.assertEqual(data['schedulingType'],'automatic')
    def test_optional_image_disclosure_and_required_disclosure_are_distinct(self):
        row=self.rows[0]
        self.assertFalse(p.make_input(self.config,row,'instagram',self.now.date())['metadata']['instagram']['isAiGenerated'])
        row=dict(row,disclosure_required=True)
        self.assertTrue(p.make_input(self.config,row,'instagram',self.now.date())['metadata']['instagram']['isAiGenerated'])
    def test_transient_retry_uses_same_post_not_new_creation(self):
        api=FakeBuffer();self.execute(api)
        api.created[0].update(status='error',error={'message':'Temporary network failure'})
        self.now=datetime(2026,11,24,20,tzinfo=timezone.utc)
        self.execute(api)
        self.assertEqual(api.retry_calls,1)
        self.assertEqual(len(api.created),6)
        self.assertEqual(sum(x['id']=='1' for x in api.created),1)
    def test_auth_error_is_not_retried(self):
        api=FakeBuffer();self.execute(api)
        api.created[0].update(status='error',error={'message':'Permission revoked; reconnect'})
        self.execute(api)
        self.assertEqual(api.retry_calls,0)
    def test_evergreen_can_continue_after_ninety_days(self):
        self.config['maximum_cycle']=0
        self.assertTrue(list(p.plan(self.config,self.rows,p.datetime(2027,3,1,10,tzinfo=p.timezone.utc))))
    def test_overdue_post_alert_does_not_duplicate_it(self):
        self.config['maximum_cycle']=1
        api=FakeBuffer();self.execute(api)
        for x in api.created:x['status']='scheduled'
        self.now=datetime(2026,11,27,20,tzinfo=timezone.utc)
        state=self.execute(api)
        self.assertTrue(any('overdue' in x for x in state['alerts']))
        self.assertEqual(len(api.created),2)

if __name__=='__main__': unittest.main()
