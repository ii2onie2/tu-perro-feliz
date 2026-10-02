#!/usr/bin/env python3
import argparse, json, pathlib, requests, urllib.parse

API="https://commons.wikimedia.org/w/api.php"
HEADERS={"User-Agent":"TuPerroFeliz/1.0 (https://github.com/ii2onie2/tu-perro-feliz)"}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--content",required=True)
    ap.add_argument("--out",default="media")
    args=ap.parse_args()

    content_path=pathlib.Path(args.content)
    data=json.loads(content_path.read_text(encoding="utf-8"))
    out=pathlib.Path(args.out)
    out.mkdir(parents=True,exist_ok=True)
    downloaded=[]

    with requests.Session() as session:
        session.headers.update(HEADERS)
        for i,item in enumerate(data.get("media") or [],1):
            if not isinstance(item,dict):
                continue
            title=item.get("commons_title")
            if not title:
                continue
            params={
                "action":"query","format":"json","formatversion":"2",
                "prop":"imageinfo","iiprop":"url|extmetadata",
                "titles":title,"origin":"*"
            }
            r=session.get(API,params=params,timeout=30)
            r.raise_for_status()
            payload=r.json()
            pages=payload.get("query",{}).get("pages",[])
            if not pages:
                raise RuntimeError(f"No Wikimedia Commons page found for {title!r}")
            info_list=pages[0].get("imageinfo") or []
            if not info_list:
                raise RuntimeError(f"No downloadable imageinfo for {title!r}")
            info=info_list[0]
            url=info.get("url")
            if not url:
                raise RuntimeError(f"No media URL returned for {title!r}")
            ext=pathlib.Path(urllib.parse.urlparse(url).path).suffix or ".jpg"
            dest=out/f"{i:02d}{ext}"
            media_response=session.get(url,timeout=60)
            media_response.raise_for_status()
            dest.write_bytes(media_response.content)
            downloaded.append({
                "commons_title":title,
                "path":str(dest),
                "source":url,
                "metadata":info.get("extmetadata",{})
            })
            item["path"]=str(dest)

    content_path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    (out/"credits.json").write_text(json.dumps(downloaded,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")

if __name__=="__main__":
    main()
