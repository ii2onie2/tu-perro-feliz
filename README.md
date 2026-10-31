# Tu Perro Feliz

Cadena de producción gratuita para generar vídeos verticales para TikTok @tuperrofeliz.

## Arquitectura

Contenido verificado -> GitHub -> GitHub Actions -> Piper TTS -> FFmpeg -> MP4 1080x1920 -> programación y publicación mediante Buffer tras los controles obligatorios.

## Principios

- cero VPS
- cero servicio de vídeo de pago
- tres vídeos diarios
- narración en español
- subtítulos incrustados
- imágenes reutilizables de Wikimedia Commons con créditos conservados
- educación basada en refuerzo positivo, bienestar y prevención
- los contenidos de salud no sustituyen el consejo veterinario
- cualquier consejo de salud o seguridad debe apoyarse en fuentes veterinarias o institucionales fiables

## Parrilla diaria

- 10:00 — Tu perro feliz: cachorro, llegada a casa, rutinas, socialización y convivencia.
- 16:00 — Buenos modales: educación, llamada, correa, mordisqueo, saltos, calma y buenos hábitos.
- 19:00 — ¿Sabías esto de tu perro?: lenguaje corporal, enriquecimiento, curiosidades, mitos y bienestar.

## Archivos diarios

content/YYYY-MM-DD.json
content/YYYY-MM-DD-educacion.json
content/YYYY-MM-DD-sabias.json

## Salidas

videos/YYYY-MM-DD.mp4
videos/YYYY-MM-DD-educacion.mp4
videos/YYYY-MM-DD-sabias.mp4

## Infraestructura

GitHub Actions + Piper + FFmpeg + Wikimedia Commons.
No requiere VPS ni suscripción de generación de vídeo.

## Buffer — canal de programmation et publication

- Buffer est la seule destination cible de programmation et de publication TikTok pour ce projet.
- La connexion des deux chaînes et l'autorisation de programmation/publication ont été confirmées par le propriétaire.
- La mise en production dépend toujours de contrôles réussis : contenu exact, provenance et droits des médias, crédits, mentions IA, qualité du MP4, détection de doublons et confirmation de l'état distant.
- Ne pas créer de brouillon, programmer ou publier un contenu qui échoue à un contrôle; ne jamais présenter un rendu local comme une publication distante.
- Préserver l'idempotence, tracer les identifiants distants et permettre une reprise sans double publication.
- Aucun secret ou identifiant n'est consigné dans ce dépôt.
