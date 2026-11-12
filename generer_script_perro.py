import sys, json, os, datetime, requests

def get_format():
    now_utc = datetime.datetime.now(datetime.timezone.utc)
    h = now_utc.hour
    if h < 12: return "consejo"
    elif h < 16: return "sabias"
    else: return "detalle"

def call_ollama(prompt):
    url = "http://localhost:11434/api/generate"
    payload = {
        "model": "llama3.2:3b",
        "prompt": prompt,
        "stream": False,
        "options": {"temperature": 0.7}
    }
    try:
        r = requests.post(url, json=payload, timeout=300)
        r.raise_for_status()
        return r.json().get("response", "").strip()
    except Exception as e:
        print(f"Erreur Ollama: {e}")
        return ""

def is_french(text):
    french_words = ["bonjour", "salut", "aujourd'hui", "je ", "vous ", "nous ", "est ", "une ", "des ", "les ", "dans ", "pour "]
    text_lower = text.lower()
    for word in french_words:
        if word in text_lower:
            return True
    return False

def main():
    if len(sys.argv) < 2:
        print("Usage: python generer_script_perro.py <output.json>")
        return

    output_file = sys.argv[1]
    fmt = get_format()
    print(f"Heure UTC : {datetime.datetime.now(datetime.timezone.utc).hour}h. Format choisi : {fmt}")

    rules = (
        "RÈGLE ABSOLUE 1 : Écris UNIQUEMENT en espagnol d'Espagne. N'utilise AUCUN mot de français. "
        "Si tu utilises un mot français, la vidéo sera rejetée.\n"
        "RÈGLE ABSOLUE 2 : N'utilise AUCUN mot en anglais, AUCUN symbole mathématique, AUCUNE émoticône.\n"
        "RÈGLE ABSOLUE 3 : La narration DOIT faire au moins 150 mots."
    )

    if fmt == "consejo":
        prompt = f"Eres un educador canino español. Escribe una narración TikTok con un consejo útil sobre la educación o el comportamiento de los perros. Sé cautivador. {rules}"
        series_name = "Consejo Canino"
    elif fmt == "sabias":
        prompt = f"Eres un veterinario español. Escribe una narración TikTok '¿Sabías que...?' sobre un hecho sorprendente sobre los perros. No repitas el mismo tema que el consejo de la mañana. Sé cautivador. {rules}"
        series_name = "¿Sabías que...?"
    else:
        prompt = f"Eres un etólogo canino español. Escribe una narración TikTok 'El detalle que casi nadie ve...' sobre un detalle poco conocido del comportamiento o la historia de los perros. Sé cautivador. {rules}"
        series_name = "El detalle que casi nadie ve"

    print("Génération du script...")
    text = call_ollama(prompt)

    if is_french(text):
        print("⚠️ Texte en français détecté, régénération en espagnol...")
        text = call_ollama(prompt + " IMPORTANT : Escribe en ESPAÑOL, no en francés.")

    if not text:
        text = "No se pudo generar el texto. Inténtalo de nuevo más tarde."

    text = text.replace('"', "'").replace('“', "'").replace('”', "'").replace('’', "'")

    if len(text.split()) < 120:
        print("⚠️ Texte trop court, on ajoute une conclusion.")
        text += "\n\nRecuerda que cada perro es único y merece todo nuestro cariño y atención."

    data = {
        "narration": text,
        "series_name": series_name,
        "hook": "Descubre el secreto de tu perro",
        "date": datetime.date.today().strftime("%Y-%m-%d")
    }

    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"✅ Fichier sauvegardé : {output_file}")

if __name__ == "__main__":
    main()
