#!/usr/bin/env python3
import argparse, json, math, os, pathlib, subprocess, textwrap

W,H=1080,1920
FPS=30

def run(cmd):
    if cmd and cmd[0]=="ffmpeg" and "-nostdin" not in cmd:
        cmd=[cmd[0],"-nostdin",*cmd[1:]]
    print("+"," ".join(cmd),flush=True)
    subprocess.run(cmd,check=True)

def probe_duration(path):
    p=subprocess.run(
        ["ffprobe","-v","error","-show_entries","format=duration","-of","default=nw=1:nk=1",path],
        capture_output=True,text=True,check=True
    )
    return float(p.stdout.strip())

def srt_time(t):
    ms=int(round(t*1000)); h=ms//3600000; ms%=3600000
    m=ms//60000; ms%=60000; s=ms//1000; ms%=1000
    return f"{h:02}:{m:02}:{s:02},{ms:03}"

def make_srt(text,duration,out):
    chunks=textwrap.wrap(text,width=42,break_long_words=False,break_on_hyphens=False) or [text]
    step=max(duration/len(chunks),1.0)
    with open(out,"w",encoding="utf-8") as f:
        for i,c in enumerate(chunks,1):
            start=(i-1)*step; end=min(i*step,duration)
            f.write(f"{i}\n{srt_time(start)} --> {srt_time(end)}\n{c}\n\n")

def ffpath(path):
    return pathlib.Path(path).as_posix().replace("\\","/").replace(":","\\:").replace("'","\\'")

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--content",required=True)
    ap.add_argument("--voice-model",default=os.environ.get("PIPER_VOICE_MODEL",""))
    ap.add_argument("--voice-config",default=os.environ.get("PIPER_VOICE_CONFIG",""))
    ap.add_argument("--out",default="out")
    args=ap.parse_args()

    out=pathlib.Path(args.out); out.mkdir(parents=True,exist_ok=True)
    data=json.loads(pathlib.Path(args.content).read_text(encoding="utf-8"))
    narration=(data.get("narration") or "").strip()
    if not narration:
        raise SystemExit("narration vacía")
    if not args.voice_model:
        raise SystemExit("PIPER_VOICE_MODEL missing")

    wav=str(out/"voice.wav")
    cmd=["piper","--model",args.voice_model,"--output_file",wav]
    if args.voice_config:
        cmd += ["--config",args.voice_config]
    p=subprocess.Popen(cmd,stdin=subprocess.PIPE,text=True)
    p.communicate(narration)
    if p.returncode:
        raise SystemExit(p.returncode)

    duration=probe_duration(wav)
    srt=str(out/"subtitles.srt")
    make_srt(narration,duration,srt)

    series=(data.get("series") or "Tu Perro Feliz").strip()
    hook=(data.get("hook") or "").strip()
    cta=(data.get("cta") or "Síguenos para aprender cada día a entender y educar mejor a tu perro.").strip()

    for name,text in [("series.txt",series),("hook.txt",hook),("cta.txt",cta)]:
        (out/name).write_text(text+"\n",encoding="utf-8")

    bgs=[]
    for item in data.get("media") or []:
        pth=item.get("path") if isinstance(item,dict) else None
        if pth and pathlib.Path(pth).exists():
            bgs.append(pth)
    bgs=bgs[:5]

    video=str(out/"video.mp4")
    subtitle_filter=(
        f"subtitles={ffpath(srt)}:"
        "force_style='FontName=DejaVu Sans,FontSize=18,Outline=2,Shadow=0,Alignment=2,MarginV=120'"
    )
    branding=(
        f",drawtext=textfile='{ffpath(out/'series.txt')}':font='DejaVu Sans':"
        "fontsize=42:fontcolor=white:box=1:boxcolor=black@0.45:boxborderw=12:"
        "x=(w-text_w)/2:y=70"
    )
    hook_end=min(4.5,max(2.5,duration*0.12))
    hook_overlay=(
        f",drawtext=textfile='{ffpath(out/'hook.txt')}':font='DejaVu Sans':"
        "fontsize=44:fontcolor=white:box=1:boxcolor=black@0.68:boxborderw=14:"
        f"x=(w-text_w)/2:y=155:enable='between(t,0,{hook_end:.2f})'"
        if hook else ""
    )
    cta_start=max(0.0,duration-5.5)
    cta_overlay=(
        f",drawtext=textfile='{ffpath(out/'cta.txt')}':font='DejaVu Sans':"
        "fontsize=42:fontcolor=white:box=1:boxcolor=black@0.72:boxborderw=14:"
        f"x=(w-text_w)/2:y=h-360:enable='gte(t,{cta_start:.2f})'"
    )

    if bgs:
        target_seg=4.5 if duration<=60 else 5.5
        beat_count=max(len(bgs),min(12,int(math.ceil(duration/target_seg))))
        seg=duration/beat_count
        beat_bgs=[bgs[i%len(bgs)] for i in range(beat_count)]
        cmd=["ffmpeg","-y"]
        for bg in beat_bgs:
            cmd += ["-loop","1","-framerate",str(FPS),"-t",f"{seg:.3f}","-i",bg]
        audio_index=len(beat_bgs)
        cmd += ["-i",wav]
        parts=[]; labels=[]
        for i in range(len(beat_bgs)):
            label=f"v{i}"; labels.append(f"[{label}]")
            zexpr="min(zoom+0.0010,1.14)" if i%2==0 else "if(eq(on,1),1.14,max(zoom-0.0010,1.0))"
            xexpr="iw/2-(iw/zoom/2)" if i%2==0 else "iw/2-(iw/zoom/2)+sin(on/35)*18"
            parts.append(
                f"[{i}:v]scale=1200:2134:force_original_aspect_ratio=increase,"
                f"crop=1200:2134,zoompan=z='{zexpr}':x='{xexpr}':y='ih/2-(ih/zoom/2)':"
                f"d=1:s={W}x{H}:fps={FPS},setsar=1,trim=duration={seg:.3f},setpts=PTS-STARTPTS[{label}]"
            )
        parts.append("".join(labels)+f"concat=n={len(beat_bgs)}:v=1:a=0[base]")
        parts.append(f"[base]{subtitle_filter}{branding}{hook_overlay}{cta_overlay}[vout]")
        cmd += [
            "-filter_complex",";".join(parts),"-map","[vout]","-map",f"{audio_index}:a",
            "-t",f"{duration:.3f}","-c:v","libx264","-preset","medium","-crf","21",
            "-c:a","aac","-b:a","192k","-pix_fmt","yuv420p","-movflags","+faststart",video
        ]
        run(cmd)
    else:
        vf=f"{subtitle_filter}{branding}{hook_overlay}{cta_overlay}"
        run([
            "ffmpeg","-y","-f","lavfi","-i",f"color=c=0x111111:s={W}x{H}:r={FPS}",
            "-i",wav,"-t",f"{duration:.3f}","-vf",vf,
            "-c:v","libx264","-preset","medium","-crf","21",
            "-c:a","aac","-b:a","192k","-pix_fmt","yuv420p","-movflags","+faststart",video
        ])

    (out/"caption.txt").write_text(
        (data.get("caption","")+"\n\n"+" ".join(data.get("hashtags",[]))).strip()+"\n",
        encoding="utf-8"
    )
    (out/"sources.json").write_text(
        json.dumps(data.get("sources",[]),ensure_ascii=False,indent=2)+"\n",
        encoding="utf-8"
    )
    print(video)

if __name__=="__main__":
    main()
