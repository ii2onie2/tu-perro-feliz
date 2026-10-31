# Tu Perro Feliz

Cadena de producción gratuita para generar vídeos verticales para TikTok @tuperrofeliz.

## Arquitectura

Contenido verificado -> GitHub -> GitHub Actions -> Piper TTS -> FFmpeg -> MP4 1080x1920 -> preparación para Buffer (publicación desactivada sin autorización independiente).

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

## Buffer migration / état de publication

- Buffer remplace Metricool comme destination envisagée de planification, sous réserve de validation de la connexion et des droits du compte.
- La génération MP4 et le dépôt des artefacts GitHub ne constituent pas une publication TikTok.
- Aucun appel API Buffer, création de brouillon, programmation ou publication n'est autorisé par cette migration.
- Vérifier manuellement la connexion TikTok/Buffer, les capacités et quotas du compte, puis obtenir une autorisation distincte avant toute action externe.
- Les contrôles éditoriaux, licences, attributions, étiquetage IA et qualité MP4 restent obligatoires.
- Retour arrière : fermer la PR sans fusion, ou revert du commit si fusion ultérieure.
