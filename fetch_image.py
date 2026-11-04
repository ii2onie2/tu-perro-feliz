import sys
import json
import urllib.request
import urllib.parse
import pathlib

# URL de secours : La Reddition de Bailén (peinture historique espagnole, Domaine Public)
FALLBACK_URL = "https://upload.wikimedia.org/wikipedia/commons/thumb/3/3b/La_rendici%C3%B3n_de_Bail%C3%A9n.jpg/1280px-La_rendici%C3%B3n_de_Bail%C3%A9n.jpg"

def get_image_url(query):
    search_url = "https://commons.wikimedia.org/w/api.php?" + urllib.parse.urlencode({
        "action": "query", "format": "json", "generator": "search",
        "gsrsearch": query + " filetype:bitmap", "gsrnamespace": "6", "gsrlimit": "5",
        "prop": "imageinfo", "iiprop": "url|extmetadata"
    })
    
    req = urllib.request.Request(search_url, headers={'User-Agent': 'TalDiaBot/1.0'})
    try:
        with urllib.request.urlopen(req) as response:
            data = json.load(response)
            
        pages = data.get("query", {}).get("pages", {})
        for page in pages.values():
            info = page.get("imageinfo", [{}])[0]
            ext = info.get("extmetadata", {})
            license_short = ext.get("LicenseShortName", {}).get("value", "")
            
            if "Public domain" in license_short or "CC0" in license_short:
                return info.get("url")
    except Exception as e:
        print(f"Erreur lors de la recherche : {e}")
        
    return None

def download_and_update(json_path, image_url):
    path = pathlib.Path(json_path)
    data = json.loads(path.read_text(encoding="utf-8"))
    
    media_dir = pathlib.Path("media")
    media_dir.mkdir(exist_ok=True)
    image_path = media_dir / "image_01.jpg"
    
    print(f"Téléchargement : {image_url}")
    req = urllib.request.Request(image_url, headers={'User-Agent': 'TalDiaBot/1.0'})
    try:
        with urllib.request.urlopen(req) as response, open(image_path, 'wb') as out_file:
            out_file.write(response.read())
            
        data["media"] = [{"path": str(image_path)}]
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        print("✅ JSON mis à jour avec le chemin de l'image.")
        return True
    except Exception as e:
        print(f"❌ Erreur de téléchargement : {e}")
        return False

if __name__ == "__main__":
    json_file = sys.argv[1]
    with open(json_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    prompt = data.get("media_prompt", "history painting")
    print(f"Recherche d'image pour : {prompt}")
    
    image_url = get_image_url(prompt)
    
    if not image_url:
        print("⚠️ Aucune image trouvée, utilisation de l'image de secours.")
        image_url = FALLBACK_URL
        
    if not download_and_update(json_file, image_url):
        sys.exit(1)
