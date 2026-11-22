"""Summarize observed post metrics; never infer orders/profit from engagement."""
import json
from collections import defaultdict
from pathlib import Path

ROOT=Path(__file__).resolve().parent

def build():
    path=ROOT/'state'/'publishing.json'
    state=json.loads(path.read_text()) if path.exists() else {'posts':{}}
    groups=defaultdict(lambda:{'sent':0,'pending':0,'metrics_available':0,'metrics':defaultdict(float)})
    for post in state['posts'].values():
        key=(post.get('platform','unknown'),post.get('family','unknown'))
        group=groups[key]
        group['sent' if post.get('status')=='sent' else 'pending']+=1
        if post.get('status')=='sent' and post.get('metrics') is not None:
            group['metrics_available']+=1
            for metric in post['metrics']:
                # Do not sum percentages/rates with counts or combine unlike measures.
                if metric.get('unit')=='count':
                    group['metrics'][metric['type']]+=metric['value']
    lines=['# Organic publishing evidence','',
      'Automatically generated from Buffer readbacks. Shopify orders and contribution are NOT inferred from these metrics.',
      'Some unreported platform metrics may appear as zero; availability and source freshness matter.',
      '', '| Platform / family | Sent | Pending or other | Posts with metrics | Available count metrics |',
      '|---|---:|---:|---:|---|']
    for (platform,family),v in sorted(groups.items()):
        metrics=', '.join(f'{k}={n:g}' for k,n in sorted(v['metrics'].items())) or 'Not available'
        lines.append(f"| {platform} / {family} | {v['sent']} | {v['pending']} | {v['metrics_available']} | {metrics} |")
    lines+=['','## Next decision','',
      'Keep the initial concept rotation while observations are sparse. Compare Shopify source-tagged sessions, carts and real purchases before changing allocation.',
      'High reach with no visits: improve product/CTA relevance. Visits without carts: investigate offer/page fit. Carts without purchases: investigate checkout and trust.',
      'A strong engagement result alone does not authorize ad spending or prove profitability. A new image batch should adapt actual questions and buying objections.']
    (ROOT/'state').mkdir(exist_ok=True)
    (ROOT/'state'/'performance.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')

if __name__=='__main__': build()
