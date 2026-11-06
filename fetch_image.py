import sys
import json
import pathlib
import random
import shutil

def get_random_dog_image():
    assets_dir = pathlib.Path("assets/dogs")
    if not assets_dir.exists():
        print("❌ Dossier assets/dogs introuvable.")
        return None
        
    images = list(assets_dir.glob("*.jpg"))
    if not images:
        print("❌ Aucune image dans assets/dogs.")
        return None
    
    # Lire la dernière image utilisée pour éviter les doublons
    last_image_file = pathlib.Path("last_image.txt")
    last_image = ""
    if last_image_file.exists():
        last_image = last_image_file.read_text().strip()
    
    # Filtrer pour éviter la dernière image
    candidates = [img for img in images if img.name != last_image]
    if not candidates:
        candidates = images
        
    selected = random.choice(candidates)
    
    # Sauvegarder le nom pour la prochaine fois
    last_image_file.write_text(selected.name)
    
    print(f"✅ Image locale sélectionnée : {selected.name}")
    return selected

def update_json(json_path, image_path):
    path = pathlib.Path(json_path)
    data = json.loads(path.read_text(encoding="utf-8"))
    
    media_dir = pathlib.Path("media")
    media_dir.mkdir(exist_ok=True)
    final_path = media_dir / "image_01.jpg"
    
    shutil.copy(image_path, final_path)
    
    data["media"] = [{"path": str(final_path)}]
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print("✅ JSON mis à jour avec l'image locale.")

if __name__ == "__main__":
    json_file = sys.argv[1]
    
    image_path = get_random_dog_image()
    
    if image_path:
        update_json(json_file, image_path)
    else:
        print("❌ Impossible de trouver une image. Arrêt.")
        sys.exit(1)
