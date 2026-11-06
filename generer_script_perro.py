import sys
import json
import ollama
import datetime
from pathlib import Path

schema = {
    "type": "object",
    "properties": {
        "date": {"type": "string"},
        "hook": {"type": "string"},
        "narration": {"type": "string"},
        "caption": {"type": "string"},
        "hashtags": {"type": "array", "items": {"type": "string"}},
        "media_prompt": {"type": "string"}
    },
    "required": ["date", "hook", "narration", "caption", "hashtags", "media_prompt"]
}

def generer_contenu(format_type):
    print(f"Génération du script ({format_type})...")
    
    if format_type == "education":
        prompt_system = "Eres un educador canino. Crea un guion de 60 segundos con un consejo práctico de educación."
    elif format_type == "sante":
        prompt_system = "Eres un veterinario. Crea un guion de 60 segundos con un consejo de salud."
    else:
        prompt_system = "Eres un etólogo canino. Crea un guion de 60 segundos para explicar un comportamiento."

    prompt_system += "\nREGLA: La narración debe estar en español y tener unas 120-150 palabras. Devuelve el JSON exacto."

    try:
        response = ollama.chat(
            model='llama3.2:3b',
            messages=[
                {'role': 'system', 'content': prompt_system},
                {'role': 'user', 'content': 'Génère le script.'}
            ],
            format=schema,
            options={'temperature': 0.8}
        )
        # Ici on sécurise le parsing du JSON
        try:
            data = json.loads(response['message']['content'])
            return data
        except json.JSONDecodeError:
            print("❌ Erreur : L'IA a renvoyé un texte qui n'est pas du JSON valide.")
            sys.exit(1)
            
    except Exception as e:
        print(f"\n❌ ERREUR OLLAMA (Connexion échouée) : {e}\n")
        sys.exit(1)

def sauvegarder_json(data, nom_fichier):
    json_final = {
        "date": data.get("date", datetime.datetime.now().strftime("%Y-%m-%d")),
        "series": "Tu Perro Feliz",
        "hook": data.get("hook", "Consejo canino"),
        "narration": data.get("narration", "Consejo para tu perro."),
        "caption": data.get("caption", "Consejo del día."),
        "hashtags": data.get("hashtags", ["#Perros"]),
        "media": [],
        "format": "educational_short",
        "duration_target": "60-75s"
    }
    chemin = Path(nom_fichier)
    chemin.parent.mkdir(parents=True, exist_ok=True)
    chemin.write_text(json.dumps(json_final, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"✅ Fichier sauvegardé : {chemin}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(1)
        
    heure = datetime.datetime.now(datetime.timezone.utc).hour
    
    if heure < 10:
        target_format = "education"
    elif heure < 16:
        target_format = "sante"
    else:
        target_format = "comportement"
        
    print(f"Heure UTC : {heure}h. Format choisi : {target_format}")
    data = generer_contenu(target_format)
    sauvegarder_json(data, sys.argv[1])
