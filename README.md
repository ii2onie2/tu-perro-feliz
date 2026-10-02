# Tu Perro Feliz

Cadena de producción gratuita para generar vídeos verticales para TikTok @tuperrofeliz.

## Arquitectura

Contenido verificado -> GitHub -> GitHub Actions -> Piper TTS -> FFmpeg -> MP4 1080x1920 -> publicación mediante Metricool.

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
