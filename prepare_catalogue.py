"""Read public Shopify product source material and preserve original image files."""
import concurrent.futures, json, urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parent
def fetch(product):
    handle=product['handle']
    name=product['title'].replace('Solacen ','').split()[0].lower()
    product['content_key']=name
    url=product['featuredMedia']['preview']['image']['url']
    suffix=Path(url.split('?')[0]).suffix
    path=ROOT/'sources'/(name+suffix)
    path.parent.mkdir(exist_ok=True)
    with urllib.request.urlopen(url,timeout=40) as r: path.write_bytes(r.read())
    product['reference_file']=str(path.relative_to(ROOT))
    return product
if __name__=='__main__':
    products=json.loads((ROOT/'catalogue.json').read_text())
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool: products=list(pool.map(fetch,products))
    (ROOT/'catalogue.json').write_text(json.dumps(products,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print('Saved public descriptions and original references for',len(products),'products.')
