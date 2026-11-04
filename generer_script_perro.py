import sys
import json
import ollama
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

def generer_contenu(sujet):
    print(f"Génération du script chien pour : {sujet}...")
    prompt_system = """Eres un experto en perros y redactor para el canal de TikTok español "Tu Perro Feliz".
Tu objetivo es crear un guion de 60 segundos con un consejo útil, cariñoso y práctico sobre perros.

REGLAS:
- La narración debe estar en español y tener unas 120-150 palabras.
- Debe empezar con un gancho fuerte y terminar con una pregunta para la comunidad.
- El gancho (hook) debe ser impactante.
- Para el campo media_prompt, encuentra palabras clave en INGLÉS para buscar una foto de perro (ej: "happy golden retriever playing")."""

    try:
        response = ollama.chat(
            model='llama3.2:3b',
            messages=[
                {'role': 'system', 'content': prompt_system},
                {'role': 'user', 'content': f'Génère le script pour le sujet : {sujet}'}
            ],
            format=schema,
            options={'temperature': 0.7}
        )
        contenu = json.loads(response['message']['content'])
        return contenu
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
        print("Usage: python generer_script_perro.py <sujet> <nom_fichier.json>")
        sys.exit(1)
    data = generer_contenu(sys.argv[1])
    sauvegarder_json(data, sys.argv[2])
