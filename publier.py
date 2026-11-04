import sys
import json
import os
import requests

API_KEY = os.environ.get("BUFFER_API_KEY")
CHANNELS = {
    "tal": "6ae070412f1f5ed648e8137f",
    "perro": "6ae072482f1f5ed648e82143"
}

def creer_post(chaine, json_path, url_video):
    if chaine not in CHANNELS:
        print(f"Erreur: chaîne '{chaine}' inconnue.")
        sys.exit(1)
        
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    caption = data.get("caption", "")
    hashtags = " ".join(data.get("hashtags", []))
    texte_final = f"{caption}\n\n{hashtags}".strip()
    texte_final_escaped = texte_final.replace('"""', '\\"\\"\\"')
    
    q = f'''
    mutation {{
      createPost(input: {{
        text: """{texte_final_escaped}"""
        channelId: "{CHANNELS[chaine]}"
        schedulingType: automatic
        mode: addToQueue
        assets: [{{ video: {{ url: "{url_video}" }} }}]
      }}) {{
        ... on PostActionSuccess {{ post {{ id status dueAt }} }}
        ... on MutationError {{ message }}
      }}
    }}
    '''
    
    r = requests.post('https://api.buffer.com', headers={'Authorization': f'Bearer {API_KEY}'}, json={'query': q})
    print(json.dumps(r.json(), indent=2))

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: python publier.py <tal|perro> <json_path> <url_video>")
        sys.exit(1)
    creer_post(sys.argv[1], sys.argv[2], sys.argv[3])
