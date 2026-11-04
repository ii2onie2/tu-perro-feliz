import sys
import json
import pathlib
import os
import base64
import requests
import urllib.request
import urllib.parse

FALLBACK_URL = "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d9/Collage_of_Nine_Dogs.jpg/1280px-Collage_of_Nine_Dogs.jpg"
MODEL_NAME = "gemini-2.5-flash-image" 

def generate_with_gemini(prompt, output_path):
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("⚠️ Pas de clé GEMINI_API_KEY.")
        return False
    
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL_NAME}:generateContent?key={api_key}"
    payload = {
        "contents": [{"parts": [{"text": f"Genera una foto realista y colorida (formato vertical 9:16) de un perro feliz sobre: {prompt}. Sin texto en la imagen."}]}],
        "generationConfig": {"responseModalities": ["IMAGE"]}
    }
    
    print(f"Appel à l'API Gemini ({MODEL_NAME})...")
    try:
        response = requests.post(url, json=payload, headers={"Content-Type": "application/json"})
        
        if response.status_code != 200:
            print(f"❌ Code HTTP {response.status_code} : {response.text[:200]}")
            return False
            
        data = response.json()
        candidates = data.get("candidates", [])
        if not candidates:
            print("❌ Aucun candidat dans la réponse.")
            return False
            
        parts = candidates[0].get("content", {}).get("parts", [])
        for part in parts:
            if "inlineData" in part:
                img_data = base64.b64decode(part["inlineData"]["data"])
                with open(output_path, "wb") as f:
                    f.write(img_data)
                print("✅ Image générée par Gemini Nano Banana.")
                return True
                
        print("❌ Gemini n'a pas renvoyé d'image dans la réponse.")
        return False
    except Exception as e:
        print(f"❌ Erreur API Gemini : {e}")
        return False

def download_fallback(output_path):
    print(f"Téléchargement de l'image de secours : {FALLBACK_URL}")
    try:
        req = urllib.request.Request(FALLBACK_URL, headers={'User-Agent': 'TuPerroBot/1.0'})
        with urllib.request.urlopen(req) as response, open(output_path, 'wb') as out_file:
            out_file.write(response.read())
        print("✅ Image de secours téléchargée.")
        return True
    except Exception as e:
        print(f"❌ Impossible de télécharger l'image de secours : {e}")
        return False

def update_json(json_path, image_path):
    path = pathlib.Path(json_path)
    data = json.loads(path.read_text(encoding="utf-8"))
    data["media"] = [{"path": str(image_path)}]
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

if __name__ == "__main__":
    json_file = sys.argv[1]
    with open(json_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    prompt = data.get("media_prompt", "un perro jugando en el parque")
    
    media_dir = pathlib.Path("media")
    media_dir.mkdir(exist_ok=True)
    image_path = media_dir / "image_01.jpg"
    
    # 1. ON ESSAIE GEMINI EN PREMIER
    success = generate_with_gemini(prompt, image_path)
    
    # 2. Si Gemini échoue, on prend l'image de secours (Wikimedia)
    if not success:
        print("Bascule sur l'image de secours (Wikimedia).")
        download_fallback(image_path)
    
    update_json(json_file, image_path)
    print("✅ JSON mis à jour avec le chemin de l'image.")
