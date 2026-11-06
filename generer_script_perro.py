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

def generer_contenu(sujet, format_type):
    print(f"Génération du script ({format_type}) pour : {sujet}...")
    
    if format_type == "education":
        prompt_system = "Eres un educador canino. Crea un guion de 60 segundos con un consejo práctico de educación o obediencia."
    elif format_type == "sante":
        prompt_system = "Eres un veterinario. Crea un guion de 60 segundos con un consejo de salud, alimentación o cuidado para perros."
    else: # comportement
        prompt_system = "Eres un etólogo canino. Crea un guion de 60 segundos para explicar un comportamiento curioso o cómo manejar un problema de conducta."

    prompt_system += """
    REGLAS:
    - La narración debe estar en español y tener unas 120-150 palabras.
    - El gancho (hook) debe ser impactante y captar la atención de inmediato.
    - Los hashtags deben ser relevantes.
    - Para media_prompt, encuentra palabras clave en INGLÉS para buscar una foto de perro (ej: "happy golden retriever")."""

    try:
        response = ollama.chat(
            model='llama3.2:3b',
            messages=[
                {'role': 'system', 'content': prompt_system},
                {'role': 'user', 'content': f'Génère le script pour : {sujet}'}
            ],
            format=schema,
            options={'temperature': 0.8}
        )
        try:
            return json.loads(response["message"]["content"])
        except json.JSONDecodeError:
            print("Erreur de format JSON. L'IA a répondu un texte invalide.")
            sys.exit(1)
    except Exception as e:
        print(f"\n❌ ERREUR OLLAMA : {e}\n")
        sys.exit(1)

def sauvegarder_json(data, nom_fichier):
    json_final = {
        "date": data["date"],
        "series": "Tu Perro Feliz",
        "hook": data["hook"],
        "narration": data["narration"],
        "caption": data["caption"],
        "hashtags": data["hashtags"],
        "media": [],
        "format": "educational_short",
        "duration_target": "60-75s"
    }
    chemin = Path(nom_fichier)
    chemin.parent.mkdir(parents=True, exist_ok=True)
    chemin.write_text(json.dumps(json_final, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"✅ Fichier sauvegardé : {chemin}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        sys.exit(1)
        
    heure = datetime.datetime.now(datetime.timezone.utc).hour
    
    if heure < 10:
        format_type = "education"
        sujet = "Un conseil d'éducation canine"
    elif heure < 16:
        format_type = "sante"
        sujet = "Un conseil de santé ou d'alimentation"
    else:
        format_type = "comportement"
        sujet = "Comprendre le comportement de son chien"
        
    print(f"Heure UTC : {heure}h. Format choisi : {format_type}")
    data = generer_contenu(sujet, format_type)
    sauvegarder_json(data, sys.argv[2])
