"""Expand 60 base concepts into 60 days with four varied posts per day.

Existing afternoon captions/IDs stay intact so scheduled posts reconcile without
replacement. New posts reuse approved product assets in distinct editorial covers.
"""
import copy,html,json
import build_catalogue_queue as b
ROOT=b.ROOT
POOLS={
 'morning':['dawnrise','pageglow','quietweight','stillnight','easeknead','soothesight'],
 'evening':['soothesight','emberglow','pageglow','warmease','easeknead','lumarest'],
 'night':['nocturne','hushwave','lumanest','stillnight','quietweight']}
HOOKS={
 'dawnrise':['Light for the start of your day.','Meet a softer bedside morning.','Your clock, with a little more glow.','A little colour beside your morning.','Make space for a gentler start.'],
 'pageglow':['Your next chapter deserves its own light.','A little light, right where you read.','Keep the reading corner simple.','One lamp. Your favourite reading spot.','A flexible light for a slower chapter.'],
 'quietweight':['Put a little stillness on your list.','A pause with a gently weighted feel.','Keep a little quiet within reach.','A darker space for a quiet break.','A soft detail for your wind-down.'],
 'stillnight':['Take your quiet moment with you.','A small mask for a darker pause.','Leave a little room for darkness.','A compact comfort for your bedside.','Make the light fade for a moment.'],
 'easeknead':['A hands-on pause in a busy day.','Four intensities. Your own pace.','Make your next break more considered.','Rechargeable comfort within reach.','A little kneading, a quieter moment.'],
 'soothesight':['Warmth, massage and your own soundtrack.','Take your next pause away from the screen.','A tech detail for your softer evening.','Your quiet moment has three colours.','Let S5 be part of your wind-down.'],
 'emberglow':['A softer glow for your reading corner.','The overhead light can take a break.','A little amber for the end of the day.','Set the room at your own brightness.','A bedside glow with a warmer feel.'],
 'warmease':['A warming wrap for a slower moment.','Comfort that fits your quiet routine.','Make warmth part of your evening.','A cordless detail for your wind-down.','Your shoulder or knee. Your comfortable setting.'],
 'lumarest':['A little more intention in your skincare ritual.','Choose the coverage for your routine.','A closer look at your LED setup.','A face mask. Or a face-and-neck set.','The details behind a considered skincare pause.'],
 'nocturne':['Give your bedtime audio a darker space.','One sleep mask. Your favourite audio.','Make room for sound and stillness.','A contoured mask with built-in speakers.','A softer place for your evening soundtrack.'],
 'hushwave':['Listen from beneath your pillow.','An alternative to wearing earbuds at bedtime.','Your next sleep story has a new spot.','A small speaker for your bedside routine.','Choose the soundtrack. Keep your ears free.'],
 'lumanest':['What does your quieter room sound like?','A little sound. A softer glow.','Rain, waves or a familiar soundscape?','Set a timer for your bedside sound.','Let the room feel a little more settled.']}
CONTEXT={
 'morning':['Small comforts can have a place in your morning, too.','Keep a little space before the day gets busy.','A considered corner can be part of an ordinary day.','Your next quiet moment does not have to wait until bedtime.','A useful detail for a routine that feels like yours.','Start with one small comfort you would actually use.'],
 'evening':['The slower part of the day can be simple.','Make room for a corner that feels like yours.','Soft light, familiar surroundings, a little time to yourself.','Let your evening have its own pace.','Keep the comforts you enjoy within reach.','An everyday ritual does not need to be elaborate.'],
 'night':['A small detail for the last part of your evening.','Choose the atmosphere that feels comfortable to you.','Keep your bedtime routine considered and simple.','Give the room a little less noise and a little more intention.','Find the kind of quiet you enjoy returning to.','A familiar comfort for your next wind-down.']}
def choose(slot,day,used):
    pool=POOLS[slot]
    for offset in range(len(pool)):
        key=pool[(day+offset)%len(pool)]
        if key not in used:return key
    raise ValueError('Unable to make a varied daily mix.')
def build():
    base=json.loads((ROOT/'docs'/'sixty-base-concepts.json').read_text(encoding='utf-8'))
    assert len(base)==60
    rows=[]
    for day,afternoon in enumerate(base):
        used={afternoon.get('product_key')}
        additions={}
        for slot in ['morning','evening','night']:
            key=choose(slot,day,used);used.add(key)
            name,_,features,body,_,_=b.DETAILS[key]
            if key=='soothesight':body='SootheSight S5 combines warmth, massage and Bluetooth audio with a digital display. Pink, white and black are separate colour choices.'
            hook=HOOKS[key][(day//len(POOLS[slot]))%len(HOOKS[key])]
            context=CONTEXT[slot][(day//5)%len(CONTEXT[slot])]
            identifier=f'd{day+1:02d}_{slot}_{key}'
            cover=b.card(key,day%3,headline=hook,slug=identifier)
            assets=[cover,f'{key}-editorial-{(day+1)%3+1}.jpg']
            if key=='pageglow': assets.insert(1,'pageglow-reading-lifestyle.jpg')
            if key=='dawnrise': assets.insert(1,'dawnrise-morning-lifestyle.jpg')
            ig_cta=['Save this idea for your own routine.','See the product details through our profile.','Which listed feature would you use most?','Explore the selected version through our profile.'][day%4]
            fb_cta=['See the features and selected version.','Find the details before choosing your setup.','Would this fit your own routine?','Explore the current product information.'][day%4]
            row={'id':identifier,'day_index':day,'time_slot':slot,'family':f'{slot}_'+['ritual','features','choice','lifestyle'][day%4],
              'hook':hook,'format':'carousel','assets':assets,'alt':f'Solacen {name}: {features}. Product photograph in a branded editorial layout.',
              'instagram_caption':f'{hook}\n\n{context}\n\n{body}\n\n{ig_cta}\nExplore {name}: link in bio.\n\n#Solacen #EveningRoutine #{name}',
              'facebook_caption':f'{hook}\n\n{context}\n\n{body}\n\n{fb_cta}\nExplore {name}: {{url}}',
              'product_key':key,'product_handle':b.PRODUCTS[key]['handle'],'variant_id':b.PICTURED_VARIANTS.get(key,'49549901398254'),
              'review_state':'ready','generation_cost_eur':0,'ai_assisted':True,'disclosure_required':False,
              'claim_source':'catalogue.json; exact current store description and original image',
              'experiment':{'hypothesis':f'{slot} {key} content can generate qualified product interest','primary_outcome':'Shopify visits, carts, real orders and contribution','cadence_experiment':'four posts/day/platform; not proof that frequency improves reach'}}
            additions[slot]=row
        afternoon=copy.deepcopy(afternoon);afternoon.update(day_index=day,time_slot='afternoon')
        rows.extend([additions['morning'],afternoon,additions['evening'],additions['night']])
    (ROOT/'queue.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    parts=[]
    for row in rows:
        media=''.join(f'<video controls preload="none" src="assets/{a}"></video>' if a.endswith('.mp4') else f'<img loading="lazy" src="assets/{a}">' for a in row['assets'])
        parts.append(f'<article><small>Day {row["day_index"]+1} · {row["time_slot"]} · {row["format"]}</small><h2>{html.escape(row["hook"])}</h2><div class="media">{media}</div><details><summary>Instagram caption</summary><pre>{html.escape(row["instagram_caption"])}</pre></details><details><summary>Facebook caption</summary><pre>{html.escape(row["facebook_caption"])}</pre></details></article>')
    page='''<!doctype html><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Solacen · Four daily</title><style>body{background:#f6f0e6;color:#28483e;font:16px system-ui;max-width:1200px;margin:40px auto;padding:20px}h1{font:48px Georgia}main{display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:24px}article{padding:22px;background:#fff;border-radius:18px}h2{font:28px Georgia}.media{display:flex;overflow:auto;gap:10px}.media>*{width:100%;max-width:330px;object-fit:contain}pre{white-space:pre-wrap;font:15px/1.5 system-ui}summary{cursor:pointer;margin-top:16px}</style><h1>Solacen · Four daily</h1><p>60 days · 240 post variations per platform · morning / afternoon / evening / night · US Eastern time</p><p>Existing store images and AI lifestyle assets are reused in distinct editorial layouts. This does not represent 240 newly generated photographs.</p><main>'''+''.join(parts)+'</main>'
    (ROOT/'library.html').write_text(page,encoding='utf-8')
    print('Prepared',len(rows),'post variations for 60 days at four/day/platform. Existing afternoon identities preserved.')
if __name__=='__main__':build()
