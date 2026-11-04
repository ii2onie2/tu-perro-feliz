import sys
import json
import urllib.request
import urllib.parse
import pathlib

# URL de secours (on garde le collage de chiens)
FALLBACK_URL = "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d9/Collage_of_Nine_Dogs.jpg/1280px-Collage_of_Nine_Dogs.jpg"

def get_images_urls(query, limit=3):
    urls = []
    search_url = "https://commons.wikimedia.org/w/api.php?" + urllib.parse.urlencode({
        "action": "query", "format": "json", "generator": "search",
        "gsrsearch": query + " dog filetype:bitmap", "gsrnamespace": "6", "gsrlimit": "15", # On cherche 15 images pour en avoir 3 bonnes
        "prop": "imageinfo", "iiprop": "url|extmetadata"
    })
    
    req = urllib.request.Request(search_url, headers={'User-Agent': 'TuPerroBot/1.0'})
    try:
        with urllib.request.urlopen(req) as response:
            data = json.load(response)
            
        pages = data.get("query", {}).get("pages", {})
        for page in pages.values():
            if len(urls) >= limit:
                break
            info = page.get("imageinfo", [{}])[0]
            ext = info.get("extmetadata", {})
            license_short = ext.get("LicenseShortName", {}).get("value", "")
            
            if "Public domain" in license_short or "CC0" in license_short:
                urls.append(info.get("url"))
    except Exception as e:
        print(f"Erreur recherche Wikimedia: {e}")
    return urls

def download_and_update(json_path, image_urls):
    path = pathlib.Path(json_path)
    data = json.loads(path.read_text(encoding="utf-8"))
    media_dir = pathlib.Path("media")
    media_dir.mkdir(exist_ok=True)
    
    media_entries = []
    for i, url in enumerate(image_urls):
        image_path = media_dir / f"image_0{i+1}.jpg"
        print(f"Téléchargement de l'image {i+1} : {url}")
        req = urllib.request.Request(url, headers={'User-Agent': 'TuPerroBot/1.0'})
        try:
            with urllib.request.urlopen(req) as response, open(image_path, 'wb') as out_file:
                out_file.write(response.read())
            media_entries.append({"path": str(image_path)})
        except Exception as e:
            print(f"❌ Erreur téléchargement image {i+1} : {e}")
            
    if not media_entries:
        print("⚠️ Aucune image téléchargée, on utilise le fallback.")
        image_path = media_dir / "image_01.jpg"
        req = urllib.request.Request(FALLBACK_URL, headers={'User-Agent': 'TuPerroBot/1.0'})
        with urllib.request.urlopen(req) as response, open(image_path, 'wb') as out_file:
            out_file.write(response.read())
        media_entries = [{"path": str(image_path)}]
        
    data["media"] = media_entries
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"✅ JSON mis à jour avec {len(media_entries)} images.")

if __name__ == "__main__":
    json_file = sys.argv[1]
    with open(json_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    prompt = data.get("media_prompt", "happy dog")
    print(f"Recherche de 3 images pour : {prompt}")
    
    image_urls = get_images_urls(prompt, limit=3)
    
    if len(image_urls) < 3:
        print("⚠️ Moins de 3 images trouvées, on complète avec le fallback.")
        while len(image_urls) < 3:
            image_urls.append(FALLBACK_URL)
            
    download_and_update(json_file, image_urls)
