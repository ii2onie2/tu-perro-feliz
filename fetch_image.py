import sys
import json
import urllib.request
import pathlib
import os
import base64
import requests

FALLBACK_URL = "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d9/Collage_of_Nine_Dogs.jpg/1280px-Collage_of_Nine_Dogs.jpg"

def generate_with_gemini(prompt, output_path):
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key: return False
    
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-image:generateContent?key={api_key}"
    payload = {
        "contents": [{
            "parts": [{"text": f"Genera una foto realista vertical (formato 9:16) de un perro sobre: {prompt}. Sin texto."}]
        }]
    }
    
    try:
        response = requests.post(url, json=payload)
        data = response.json()
        for part in data["candidates"][0]["content"]["parts"]:
            if "inlineData" in part:
                img_data = base64.b64decode(part["inlineData"]["data"])
                with open(output_path, "wb") as f:
                    f.write(img_data)
                print("✅ Image générée par Gemini.")
                return True
        return False
    except Exception as e:
        print(f"❌ Erreur Gemini : {e}")
        return False

def download_fallback(image_url, output_path):
    req = urllib.request.Request(image_url, headers={'User-Agent': 'TalDiaBot/1.0'})
    with urllib.request.urlopen(req) as response, open(output_path, 'wb') as out_file:
        out_file.write(response.read())
    return True

def update_json(json_path, image_path):
    path = pathlib.Path(json_path)
    data = json.loads(path.read_text(encoding="utf-8"))
    data["media"] = [{"path": str(image_path)}]
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

if __name__ == "__main__":
    json_file = sys.argv[1]
    with open(json_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    prompt = data.get("media_prompt", "un perro feliz")
    media_dir = pathlib.Path("media")
    media_dir.mkdir(exist_ok=True)
    image_path = media_dir / "image_01.jpg"
    
    if not generate_with_gemini(prompt, image_path):
        download_fallback(FALLBACK_URL, image_path)
    
    update_json(json_file, image_path)
