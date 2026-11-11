import sys, json, os, requests

BUFFER_API_KEY = os.environ.get("BUFFER_API_KEY")
CHANNELS = {
    "tal": "6ae070412f1f5ed648e8137f",    # Vrai ID de taldiacomohoy09
    "perro": "6ae072482f1f5ed648e82143"   # Vrai ID de tuperrofelizofficial
}

def publier(chaîne, json_path, url_video):
    if not BUFFER_API_KEY:
        print("Erreur : BUFFER_API_KEY manquante.")
        sys.exit(1)

    channel_id = CHANNELS.get(chaîne)
    if not channel_id:
        print(f"Erreur : chaîne '{chaîne}' inconnue.")
        sys.exit(1)

    try:
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        print(f"Erreur lecture JSON : {e}")
        sys.exit(1)

    # Lecture du texte
    caption = data.get("caption") or data.get("narration") or data.get("script") or ""
    hashtags = data.get("hashtags", "#TalDíaComoHoy #Historia #España")
    texte_final = f"{caption}\n\n{hashtags}".strip()
    
    # Échappement du texte
    texte_echappe = json.dumps(texte_final)

    # Requête GraphQL Buffer avec les DEUX champs obligatoires
    query = f"""
    mutation {{
      createPost(input: {{
        channelId: "{channel_id}",
        text: {texte_echappe},
        schedulingType: automatic,
        mode: addToQueue,
        assets: {{
          video: {{
            url: "{url_video}"
          }}
        }}
      }}) {{
        ... on PostActionSuccess {{
          post {{
            id
            status
            dueAt
          }}
        }}
        ... on MutationError {{
          message
        }}
      }}
    }}
    """

    headers = {
        "Authorization": f"Bearer {BUFFER_API_KEY}",
        "Content-Type": "application/json"
    }

    print(f"Envoi à Buffer (chaîne: {chaîne})...")
    response = requests.post("https://api.buffer.com/graphql", json={"query": query}, headers=headers)

    if response.status_code == 200:
        data = response.json()
        if "errors" in data:
            print(f"❌ Erreur GraphQL Buffer : {data['errors'][0]['message']}")
            sys.exit(1)
        else:
            print("✅ Succès :", data)
    else:
        print(f"❌ Erreur Buffer (HTTP {response.status_code}) : {response.text}")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: python publier.py <tal|perro> <json_path> <url_video>")
        sys.exit(1)
    
    publier(sys.argv[1], sys.argv[2], sys.argv[3])
