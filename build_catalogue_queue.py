"""Create an editable, image-first catalogue campaign; no model API or paid tools.

Layouts reuse original product photos without changing the products. Captions are
hand-written from the current store descriptions. Music is an original synthesis.
"""
import array, html, json, math, shutil, subprocess, sys, wave
from pathlib import Path
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'.vendor'))
from PIL import Image, ImageDraw, ImageFont, ImageOps
GREEN='#28483e'; CREAM='#f6f0e6'; INK='#264238'; ACCENT='#b27860'
FONT=Path('C:/Windows/Fonts')
def font(size,serif=False): return ImageFont.truetype(str(FONT/('georgia.ttf' if serif else 'segoeui.ttf')),size)
PRODUCTS={p['content_key']:p for p in json.loads((ROOT/'catalogue.json').read_text(encoding='utf-8'))}
PICTURED_VARIANTS={'pageglow':'49933805027566','dawnrise':'49933785891054','emberglow':'49572433658094',
 'easeknead':'49572431495406','quietweight':'49572435296494','lumanest':'49572436312302',
 'nocturne':'49572439032046','hushwave':'49572440244462','stillnight':'49572456071406',
 'warmease':'49579082449134','lumarest':'49599480234222'}
DETAILS={
 'soothesight':('SootheSight S5','Make room for a warmer pause.','Warmth · Massage · Bluetooth audio','S5 also has a digital display and three colour choices. Select the exact model on the product page.','After-work comfort','A little technology. A quieter ritual.'),
 'pageglow':('PageGlow','One more chapter. Less overhead light.','Clip-on · Flexible neck · Rechargeable','PageGlow clips onto a book, desk or headboard. Choose warm, white or cool lighting and position the flexible neck for your reading corner.','Reading corner','A reading light that goes where the book goes.'),
 'dawnrise':('DawnRise','A softer start to darker mornings.','Wake-up light · Clock · Touch controls','DawnRise combines sunrise-style lighting, a digital clock display and colourful ambient light. This selected model is USB-powered.','Morning ritual','Meet your bedside morning companion.'),
 'emberglow':('EmberGlow','Turn down the day. Keep the glow.','Amber + red light · Adjustable brightness','EmberGlow brings amber and red light into a compact bedside lamp with dimming. Bases, clocks and remote controls vary by selected version.','Evening atmosphere','A warmer corner of the room.'),
 'easeknead':('EaseKnead','Let your break be a little more hands-on.','Kneading massage · 4 intensities · Rechargeable','EaseKnead is a rechargeable handheld scalp and body massager with four intensity levels. Start gently and follow its included instructions.','A considered pause','Small tool. A more intentional break.'),
 'quietweight':('QuietWeight','A little weight. A little stillness.','Weighted feel · Light-blocking · Soft fabric','QuietWeight combines a gently weighted design with light-blocking coverage. Keep it close for a quiet break; follow the care instructions.','Quiet moments','Choose a pause without another screen.'),
 'lumanest':('LumaNest','Give the room its own quiet soundtrack.','10 soundscapes · Ambient light · Sleep timer','LumaNest combines ten built-in sounds with colourful light and 15, 30 or 60-minute timers. The selected Q2 version has on-device controls, with no remote.','Bedside atmosphere','Rain, waves or white noise tonight?'),
 'nocturne':('Nocturne','Your evening audio. A darker space.','Bluetooth audio · 3D contour · Soft lining','Nocturne combines a contoured sleep mask with integrated stereo speakers and Bluetooth connection. It is a different product from the heated SootheSight massager.','Darkness + sound','A sleep mask with its own soundtrack.'),
 'hushwave':('HushWave','Bedtime audio, without wearing earbuds.','Under-pillow speaker · Bluetooth · Timer','HushWave is designed for under-pillow listening, with Bluetooth, TF-card playback and an auto-off timer. Sound varies with your pillow and listening setup.','Bedtime listening','Your pillow has a new listening companion.'),
 'stillnight':('StillNight','Pack a little darkness for your next pause.','Contoured shape · Light-blocking · Compact','StillNight is a separate contoured sleep mask for a darker rest space. Colours and patterns depend on the selected style.','Simple comforts','Sometimes the simplest ritual is the one you keep.'),
 'warmease':('WarmEase','Make a little room for warmth.','Adjustable warmth · Vibration · Cordless','WarmEase is a flexible heated wrap for shoulder or knee use, with adjustable warmth and vibration. Follow its fitting instructions and choose a comfortable setting.','Warming comfort','A wrap for the slower part of your day.'),
 'lumarest':('LumaRest','Give your skincare routine a considered pause.','Silicone LED panels · Separate controller','LumaRest offers a face mask or a separate face-and-neck set. The panels connect to a controller by cable. Check kit contents, instructions and destination availability before ordering.','Skincare ritual','Face mask or face-and-neck set?')
}
def wrap(draw,text,f,max_width):
    words=text.split(); lines=[]; line=''
    for word in words:
        test=(line+' '+word).strip()
        if draw.textlength(test,font=f)>max_width and line: lines.append(line); line=word
        else: line=test
    if line: lines.append(line)
    return lines
def text_block(d,text,xy,size=58,width=900,serif=False,color=INK,gap=15):
    f=font(size,serif); x,y=xy
    for line in wrap(d,text,f,width):
        d.text((x,y),line,font=f,fill=color); y+=size+gap
    return y
def card(key,kind,vertical=False,headline=None,slug=None):
    name,hook,features,body,category,second=DETAILS[key]
    w,h=1080,1920 if vertical else 1350
    bg=CREAM if kind!=1 else '#e7ede6'
    im=Image.new('RGB',(w,h),bg); d=ImageDraw.Draw(im)
    # Native editorial layout: no synthetic changes to product pixels.
    d.line((72,100,1008,100),fill='#c8c5b8',width=2)
    d.text((72,40),'Solacen',font=font(40,True),fill=GREEN)
    d.text((720,52),category.upper(),font=font(17),fill=GREEN)
    title=headline or [hook,features,second][kind]
    y=text_block(d,title,(72,140),size=58 if kind!=1 else 48,width=920,serif=(kind!=1))
    source=ROOT/PRODUCTS[key]['reference_file']
    if key=='soothesight': source=ROOT/'assets'/'s5-pink-reference.jpg'
    photo=Image.open(source).convert('RGB')
    top=max(y+36,340 if not vertical else 440)
    box=(936,(640 if not vertical else 940))
    fitted=ImageOps.contain(photo,box,Image.Resampling.LANCZOS)
    # A clean photographic panel, full product visible, no distortion or crop.
    im.paste(fitted,((w-fitted.width)//2,top+(box[1]-fitted.height)//2))
    bottom=top+box[1]+34
    d.text((72,bottom),name,font=font(40,True),fill=GREEN)
    tagline=features if kind!=1 else 'Explore the details. Find your own ritual.'
    text_block(d,tagline,(72,bottom+65),size=25,width=920,gap=8)
    d.line((72,h-90,1008,h-90),fill='#c8c5b8',width=2)
    d.text((72,h-65),'THOUGHTFUL TOOLS FOR YOUR WIND-DOWN',font=font(18),fill=GREEN)
    d.text((800,h-65),'solacen.store',font=font(20),fill=GREEN)
    path=ROOT/'assets'/(f'{slug}-cover.jpg' if slug else f'{key}-editorial-{kind+1}{"-vertical" if vertical else ""}.jpg')
    im.save(path,quality=92,subsampling=0)
    return path.name
def music(path):
    """Original slow ambient bell/pad composition; no borrowed song or voice."""
    rate=32000; duration=12; samples=array.array('h')
    chords=[(130.8128,164.8138,195.9977),(110,130.8128,164.8138),(87.3071,110,130.8128)]
    for n in range(rate*duration):
        t=n/rate; v=0
        for j,chord in enumerate(chords):
            local=t-j*4
            if local<0: continue
            envelope=min(1,local/1.2)*math.exp(-local/6)
            for freq in chord:
                v+=0.034*envelope*(math.sin(2*math.pi*freq*t)+.28*math.sin(2*math.pi*(freq*2+.2)*t))
        for j,freq in enumerate((523.251,659.255,783.991,659.255,587.33,523.251)):
            elapsed=t-j*1.75-.3
            if elapsed>=0:
                v+=.045*min(1,elapsed/.03)*math.exp(-elapsed/1.1)*(math.sin(2*math.pi*freq*elapsed)+.14*math.sin(2*math.pi*freq*3*elapsed))
        fade=min(1,t/1.2,(duration-t)/1.8)
        value=int(max(-.9,min(.9,v*fade))*32767)
        samples.extend((value,value))
    with wave.open(str(path),'wb') as f:
        f.setnchannels(2);f.setsampwidth(2);f.setframerate(rate);f.writeframes(samples.tobytes())
def reel(key):
    files=[card(key,i,True) for i in range(3)]
    tmp=ROOT/'state'/'local-music.wav'
    if not tmp.exists(): music(tmp)
    args=['ffmpeg','-hide_banner','-loglevel','error','-y']
    for file in files: args+=['-loop','1','-framerate','30','-t','4', '-i',str(ROOT/'assets'/file)]
    args+=['-i',str(tmp),'-filter_complex','[0:v]settb=AVTB[v0];[1:v]settb=AVTB[v1];[2:v]settb=AVTB[v2];[v0][v1]xfade=transition=fade:duration=0.35:offset=3.65[x];[x][v2]xfade=transition=fade:duration=0.35:offset=7.3,format=yuv420p[v]',
           '-map','[v]','-map','3:a','-c:v','libx264','-preset','fast','-crf','22','-r','30','-c:a','aac','-b:a','160k','-af','afade=t=out:st=9.5:d=1.8','-t','11.3','-movflags','+faststart',str(ROOT/'assets'/f'{key}-ambient-reel.mp4')]
    subprocess.run(args,check=True)
    return f'{key}-ambient-reel.mp4'
def build(render=True):
    for key in DETAILS:
        for kind in range(3): card(key,kind)
    old=json.loads((ROOT/'docs'/'initial-s5-queue.json').read_text(encoding='utf-8'))[:24]
    s5=[]
    for i,row in enumerate(old):
        row.update(product_key='soothesight',product_handle=PRODUCTS['soothesight']['handle'],variant_id='49549901398254',disclosure_required=False)
        # A headline on the first frame rather than only in the caption.
        row['assets']=[f'soothesight-editorial-{i%3+1}.jpg']+row['assets'][:2]
        row['format']='carousel';s5.append(row)
    names=['pageglow','emberglow','dawnrise','nocturne','lumanest','hushwave','quietweight','easeknead','stillnight','warmease','lumarest']
    others=[]
    for angle in range(3):
        for key in names:
            name,hook,features,body,category,second=DETAILS[key]
            headline=[hook,second,f'{name}: the details that matter.'][angle]
            ig_cta=['Save this for your next quiet evening.','Which detail fits your routine?','See the selected version through our profile.'][angle]
            fb_cta=['What would you add to your evening corner?','Explore the features and choose your setup.','See the product details before choosing your version.'][angle]
            assets=[f'{key}-editorial-{angle+1}.jpg',f'{key}-editorial-{(angle+1)%3+1}.jpg']
            if key=='pageglow' and (ROOT/'assets'/'pageglow-reading-lifestyle.jpg').exists(): assets.insert(1,'pageglow-reading-lifestyle.jpg')
            if key=='dawnrise' and (ROOT/'assets'/'dawnrise-morning-lifestyle.jpg').exists(): assets.insert(1,'dawnrise-morning-lifestyle.jpg')
            extra=''
            if key=='stillnight': extra=' Eligible SootheSight S5, S6 and S7 orders can include one complimentary StillNight when both products are added through the pairing selector. S3 excluded; cannot combine discounts.'
            row={'id':f'{key}{angle+1:02d}','family':['ritual','choice','features'][angle], 'hook':headline,
                 'format':'carousel','assets':assets,'alt':f'Solacen {name}: {features}. Exact store product photograph in a branded layout.',
                 'instagram_caption':f'{headline}\n\n{body}{extra}\n\n{ig_cta}\nExplore {name}: link in bio.\n\n#Solacen #EveningRoutine #{name}',
                 'facebook_caption':f'{headline}\n\n{body}{extra}\n\n{fb_cta}\nExplore {name}: {{url}}',
                 'product_key':key,'product_handle':PRODUCTS[key]['handle'],'variant_id':PICTURED_VARIANTS[key],'review_state':'ready','generation_cost_eur':0,
                 'ai_assisted':True,'disclosure_required':False,'claim_source':'catalogue.json: live Shopify description, 22 November 2026'}
            others.append(row)
    # Alternate a lead-product lesson with catalogue discovery. The first week
    # deliberately introduces reading, light, morning and audio products.
    rows=[];si=oi=0
    while si<len(s5) or oi<len(others):
        if si<len(s5): rows.append(s5[si]);si+=1
        if oi<len(others): rows.append(others[oi]);oi+=1
    for n,(keys,headline,body) in enumerate([
      (['pageglow','emberglow'],'Reading light or room light?','PageGlow directs light toward a book. EmberGlow adds ambient light to a corner of the room. Different roles, one considered evening.'),
      (['nocturne','hushwave'],'Two ways to bring audio to bedtime.','Nocturne combines a sleep mask with speakers. HushWave sits under a pillow. Compare the format you would actually enjoy using.'),
      (['quietweight','stillnight'],'Find your kind of quiet.','QuietWeight offers a gently weighted feel. StillNight is a separate contoured sleep mask. Compare the materials, shape and selected style on each product page.')]):
        rows.append({'id':f'compare{n+1:02d}','family':'comparison','hook':headline,'format':'carousel',
          'assets':[f'{k}-editorial-1.jpg' for k in keys], 'alt':headline,
          'instagram_caption':f'{headline}\n\n{body}\n\nSave the comparison. Explore the collection: link in bio.\n\n#Solacen #EveningRoutine',
          'facebook_caption':f'{headline}\n\n{body}\n\nCompare both products: {{url}}','collection_link':True,
          'product_key':'comparison','review_state':'ready','generation_cost_eur':0,'ai_assisted':True,'disclosure_required':False,'claim_source':'catalogue.json'})
    # Six product-only slideshow Reels, original instrumental embedded. No
    # invented human demonstration or photorealistic AI motion is presented.
    music_keys={'s5o02':'soothesight','emberglow01':'emberglow','lumanest01':'lumanest','hushwave02':'hushwave','pageglow03':'pageglow','nocturne03':'nocturne'}
    for index,row in enumerate(rows):
        row['day_index']=index
        if row.get('product_key') in DETAILS:
            cover=card(row['product_key'],index%3,headline=row['hook'],slug=row['id'])
            row['assets'][0]=cover
        row['experiment']={'hypothesis':f"{row['family']} / {row.get('product_key')} can drive qualified product interest",'primary_outcome':'Shopify sessions, carts, orders and contribution; views are diagnostic','platforms_evaluated_separately':True}
        if row['id'] in music_keys:
            key=music_keys[row['id']]; file=f'{key}-ambient-reel.mp4'
            if render and not (ROOT/'assets'/file).exists(): reel(key)
            row.update(format='reel',assets=[file],music='Original Solacen ambient composition; generated deterministically, no sampled or licensed third-party song',disclosure_required=False)
            row['music_is_product_sound_demo']=False
    (ROOT/'queue.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    snippets=[]
    for row in rows:
        media=''.join(f'<video controls preload="none" src="assets/{a}"></video>' if a.endswith('.mp4') else f'<img loading="lazy" src="assets/{a}">' for a in row['assets'])
        snippets.append(f'<article><small>Day {row["day_index"]+1} · {html.escape(row["family"])} · {row["format"]}</small><h2>{html.escape(row["hook"])}</h2><div class="media">{media}</div><details><summary>Instagram caption</summary><pre>{html.escape(row["instagram_caption"])}</pre></details><details><summary>Facebook caption</summary><pre>{html.escape(row["facebook_caption"])}</pre></details></article>')
    page='''<!doctype html><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Solacen · Organic library</title><style>body{background:#f6f0e6;color:#28483e;font:16px system-ui;max-width:1200px;margin:40px auto;padding:20px}h1{font:48px Georgia}main{display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:24px}article{padding:22px;background:#fff;border-radius:18px}h2{font:28px Georgia}.media{display:flex;overflow:auto;gap:10px}.media>*{width:100%;max-width:330px;object-fit:contain}pre{white-space:pre-wrap;font:15px/1.5 system-ui}summary{cursor:pointer;margin-top:16px}</style><h1>Solacen · A quieter feed</h1><p>60 daily concepts · all 12 products · six original-music Reels · separate Instagram and Facebook copy</p><main>'''+''.join(snippets)+'</main>'
    (ROOT/'library.html').write_text(page,encoding='utf-8')
    print('Prepared',len(rows),'concepts across',len(DETAILS),'products, including',len(music_keys),'music Reels.')
if __name__=='__main__': build()
