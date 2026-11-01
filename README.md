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

## Buffer — canal de programación y publicación

- Buffer es el destino previsto para programar y publicar contenido de TikTok de este proyecto.
- **Estado: NO VERIFICADO.** Esta PR no demuestra que las dos cuentas de TikTok estén conectadas a Buffer ni que exista autorización para programar o publicar.
- **Verificación GraphQL:** cuando se disponga de acceso autorizado, consultar en modo de solo lectura los canales disponibles, comprobar su correspondencia exacta con cada cuenta de TikTok y determinar las capacidades y el modo real de publicación. Consultar previamente la documentación vigente de la API.
- **Pruebas que deben conservarse:** fecha y hora UTC, resultado de la consulta, correspondencia de canales, modo observado, restricciones y decisión expresa del propietario. Guardar los identificadores de canales en un archivo de pruebas con acceso restringido. No registrar tokens ni secretos.
- **Distinción obligatoria:** una conexión operativa a Buffer no demuestra que la publicación automática esté disponible ni que esté autorizada.
- **Controles obligatorios:** contenido verificado, procedencia y derechos de los medios, créditos, declaraciones sobre IA, calidad del MP4, prevención de duplicados y comprobación del estado remoto.
- **Bloqueo:** no crear borradores remotos, programar ni publicar hasta disponer de pruebas suficientes y autorización expresa del propietario.
- **Idempotencia:** conservar la trazabilidad de las operaciones y evitar publicaciones duplicadas.
- **Alcance:** esta PR es exclusivamente documental. No activa ninguna automatización ni publicación en Buffer.
