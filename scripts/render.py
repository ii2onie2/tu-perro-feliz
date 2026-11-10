import argparse, json, math, os, pathlib, subprocess, textwrap, re, sys, asyncio

# Installation automatique d'edge-tts
try:
    import edge_tts
except ImportError:
    subprocess.run([sys.executable, "-m", "pip", "install", "edge-tts"], check=True)
    import edge_tts

def probe_duration(path):
    p = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", path],
        capture_output=True, text=True, check=True
    )
    return float(p.stdout.strip())

def make_srt(text, duration, out):
    chunks = textwrap.wrap(text, width=42, break_long_words=False, break_on_hyphens=False) or [text]
    if not chunks:
        chunks = [" "]
    lines = []
    step = duration / len(chunks)
    for i, chunk in enumerate(chunks):
        start = i * step
        end = (i + 1) * step
        lines.append(f"{i+1}")
        lines.append(f"{math.floor(start/3600):02d}:{math.floor((start%3600)/60):02d}:{math.floor(start%60):02d},{math.floor((start%1)*1000):03d} --> {math.floor(end/3600):02d}:{math.floor((end%3600)/60):02d}:{math.floor(end%60):02d},{math.floor((end%1)*1000):03d}")
        lines.append(chunk)
        lines.append("")
    pathlib.Path(out).write_text("\n".join(lines), encoding="utf-8")

def ffpath(p):
    return str(p).replace("'", "'\\''").replace(":", "\\:")

async def generate_audio(text, output_path):
    # Voix espagnole (Espagne) naturelle pour les chiens
    # Autres options : "es-ES-ElviraNeural" (femme), "es-MX-JorgeNeural" (Mexique)
    voice = "es-ES-AlvaroNeural"
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(output_path)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--content", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    out = pathlib.Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    data = json.loads(pathlib.Path(args.content).read_text(encoding="utf-8"))

    narration = (data.get("narration") or data.get("script") or "").strip()
    if not narration:
        raise SystemExit("Narration vide")
    narration = re.sub(r'\s+', ' ', narration).strip()

    wav = str(out / "voice.mp3")

    print("Génération audio avec Edge TTS...")
    asyncio.run(generate_audio(narration, wav))
    print("Audio généré.")

    duration = probe_duration(wav)
    srt = str(out / "subtitles.srt")
    make_srt(narration, duration, srt)

    series = (data.get("series_name") or data.get("series") or "Tu Perro Feliz").strip()
    hook = (data.get("hook") or "").strip()
    date_label = (data.get("date") or "").strip()
    if date_label:
        try:
            from datetime import datetime
            d = datetime.strptime(date_label, "%Y-%m-%d")
            date_label = d.strftime("%d/%m/%Y")
        except:
            pass

    hook_file = out / "hook.txt"
    cta_file = out / "cta.txt"
    series_file = out / "series.txt"
    date_file = out / "date.txt"

    hook_file.write_text(hook + "\n", encoding="utf-8")
    cta_file.write_text("Sígueme para más consejos sobre tu perro.", encoding="utf-8") # CTA adapté
    series_file.write_text(series + "\n", encoding="utf-8")
    date_file.write_text(date_label + "\n", encoding="utf-8")

    hook_end = max(3.0, duration * 0.15)
    cta_start = max(0.0, duration - 3.5)

    video_out = out / "video.mp4"

    image_path = data.get("image", "assets/history/sources/current.jpg")
    if not os.path.exists(image_path):
        image_path = "media/image_01.jpg"
        if not os.path.exists(image_path):
            raise SystemExit(f"Image introuvable : {image_path}")

    cmd_ffmpeg = [
        "ffmpeg", "-y", "-loop", "1", "-i", image_path,
        "-i", wav,
        "-filter_complex",
        f"[0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,"
        f"drawtext=textfile='{ffpath(series_file)}':font='DejaVu Sans':fontcolor=white@0.8:fontsize=24:"
        f"x=(w-text_w)/2:y=70,"
        f"drawtext=textfile='{ffpath(date_file)}':font='DejaVu Sans':fontcolor=white@0.8:fontsize=28:"
        f"x=(w-text_w)/2:y=120,"
        f"drawtext=textfile='{ffpath(hook_file)}':font='DejaVu Sans':fontcolor=white:fontsize=54:"
        f"box=1:boxcolor=black@0.6:boxborderw=20:"
        f"x=(w-text_w)/2:y=155:enable='between(t,0,{hook_end:.2f})',"
        f"drawtext=textfile='{ffpath(cta_file)}':font='DejaVu Sans':fontcolor=white:fontsize=40:"
        f"box=1:boxcolor=black@0.6:boxborderw=15:"
        f"x=(w-text_w)/2:y=h-360:enable='gte(t,{cta_start:.2f})'"
        f"[v]",
        "-map", "[v]", "-map", "1:a",
        "-c:v", "libx264", "-crf", "25", "-preset", "veryfast",
        "-c:a", "aac", "-b:a", "128k",
        "-shortest", "-t", f"{duration:.2f}",
        str(video_out)
    ]
    subprocess.run(cmd_ffmpeg, check=True)

    (out / "caption.txt").write_text(narration, encoding="utf-8")
    (out / "sources.json").write_text(json.dumps([], ensure_ascii=False), encoding="utf-8")
    print(f"Vidéo générée avec Edge TTS : {video_out}")

if __name__ == "__main__":
    main()
