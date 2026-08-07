import subprocess
import json
import random
from pathlib import Path


def get_duration(file_path: str) -> float:
    cmd = [
        'ffprobe', '-v', 'error',
        '-show_entries', 'format=duration',
        '-of', 'json',
        file_path,
    ]
    r = subprocess.run(cmd, capture_output=True, text=True, check=True)
    return float(json.loads(r.stdout)['format']['duration'])


def compose_scene(video_path: str, audio_path: str, duration: float, output: str, width: int = 1080, height: int = 1920) -> str:
    """Denoise, smooth motion, mux audio (video is trimmed to match audio length)."""
    Path(output).parent.mkdir(parents=True, exist_ok=True)
    subprocess.run([
        'ffmpeg', '-y',
        '-i', video_path,
        '-i', audio_path,
        '-filter_complex', (
            '[0:v]hqdn3d=luma_spatial=2:chroma_spatial=1:luma_tmp=0:chroma_tmp=0,'
            'minterpolate=mi_mode=mci:mc_mode=obmc:vsbmc=1:fps=60,'
            'fps=30,'
            'setpts=1.5*PTS,'
            f'scale={width}:{height}:force_original_aspect_ratio=decrease,'
            f'pad={width}:{height}:(ow-iw)/2:(oh-ih)/2:color=white,'
            'unsharp=luma_msize_x=5:luma_msize_y=5:luma_amount=0.5,'
            'setsar=1[v];'
            '[1:a]dynaudnorm=p=0.95:m=100[a]'
        ),
        '-map', '[v]',
        '-map', '[a]',
        '-c:v', 'libx264',
        '-preset', 'veryfast',
        '-crf', '20',
        '-r', '30',
        '-t', str(duration),
        '-c:a', 'aac',
        '-b:a', '192k',
        output,
    ], check=True, capture_output=True, text=True)
    return output


def _build_zoompan_exprs(pattern: str, total_frames: int, nf: int, duration: float, width: int, height: int) -> tuple[str, str, str, float, float]:
    """
    Returns (z_expr, x_expr, y_expr, zoom_max, rotation_rad) for the zoompan filter.
    Ken Burns clásico: zoom lento, lineal y centrado (sin pan, rotación ni parallax).
    """
    t_norm = f'on/{nf}' if nf > 0 else '0'
    zoom_max = 0.08
    rotation = 0.0

    if pattern == 'zoom-out':
        z = f'1+{zoom_max}*(1-{t_norm})'
    else:
        z = f'1+{zoom_max}*{t_norm}'

    x = '(iw - iw/zoom)/2'
    y = '(ih - ih/zoom)/2'

    return z, x, y, zoom_max, rotation


def compose_scene_from_image(image_path: str, audio_path: str, duration: float, output: str, pattern_idx: int = 0, width: int = 1080, height: int = 1920, audio_codec: str = 'aac') -> str:
    """Create a video from a static image with Ken Burns zoom, avoiding ffmpeg hangs."""
    Path(output).parent.mkdir(parents=True, exist_ok=True)
    
    # Scale to fill screen and crop excess
    vf_fill = f"scale='max({width},iw*{height}/ih)':'max({height},ih*{width}/iw)',crop={width}:{height}"
    
    # Simple continuous zoom
    zoom_expr = "1.0 + 0.0015*on"
    pos_expr = "x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'"
    
    # We use d=1 so zoompan outputs exactly 1 frame per input frame.
    # Combined with -loop 1, this works perfectly and avoids infinite buffering deadlocks.
    vf = f"{vf_fill},zoompan=z='{zoom_expr}':d=1:{pos_expr}:s={width}x{height},format=yuv420p"

    # We use -t instead of -shortest to forcefully stop at the exact duration
    subprocess.run([
        'ffmpeg', '-y', '-loop', '1',
        '-i', image_path,
        '-i', audio_path,
        '-vf', vf,
        '-r', '30',
        '-fps_mode', 'cfr',
        '-t', str(duration),
        '-c:v', 'libx264',
        '-preset', 'veryfast',
        '-crf', '20',
        '-c:a', audio_codec,
        '-b:a', '192k',
        '-v', 'error',
        output,
    ], check=True, capture_output=True, text=True)
    return output


def compose_scene_from_images(image_paths: list[str], audio_path: str, duration: float, output: str, pattern_start: int = 0, width: int = 1080, height: int = 1920) -> str:
    """Create a video from multiple images with classic Ken Burns zoom, splitting audio equally and concatenating."""
    n = len(image_paths)
    if n == 1:
        return compose_scene_from_image(image_paths[0], audio_path, duration, output, pattern_idx=pattern_start, width=width, height=height)

    Path(output).parent.mkdir(parents=True, exist_ok=True)
    fps = 30
    seg_duration = duration / n
    segments = []
    stem = Path(output).stem

    for i, img_path in enumerate(image_paths):
        seg_video = str(Path(output).parent / f'{stem}_seg{i}.mp4')
        seg_audio = str(Path(output).parent / f'{stem}_aud{i}.wav')

        subprocess.run([
            'ffmpeg', '-y',
            '-i', audio_path,
            '-ss', str(i * seg_duration),
            '-t', str(seg_duration),
            seg_audio,
        ], check=True, capture_output=True, text=True)

        compose_scene_from_image(img_path, seg_audio, seg_duration, seg_video, pattern_idx=pattern_start + i, width=width, height=height, audio_codec='pcm_s16le')
        segments.append(seg_video)

    return concat_videos_audio(segments, output, transition_duration=0.4)


TRANSITION_TYPES = [
    'fade', 'fadeblack', 'dissolve', 'zoomin',
]

CTA_TEXT = 'FOLLOW ME TO LEARN MORE'


def _ass_ts(seconds: float) -> str:
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    cs = int((seconds - int(seconds)) * 100)
    return f'{h}:{m:02d}:{s:02d}.{cs:02d}'


def _append_cta(ass_path: str, total_duration: float) -> str:
    """Adds a big "SUBSCRIBE" subtitle in the last seconds of the video."""
    with open(ass_path, 'r', encoding='utf-8') as f:
        content = f.read()

    if 'Style: CTA' not in content:
        cta_style = (
            'Style: CTA,Arial Black,64,&H0000FF00,&H00FFFFFF,&H00000000,&H00FFFFFF,'
            '-1,0,0,0,100,100,0,0,1,3,1,2,40,40,400,1'
        )
        content = content.replace(
            '[V4+ Styles]',
            f'[V4+ Styles]\n{cta_style}',
            1,
        )

    start = max(0.0, total_duration - 3.0)
    if not content.rstrip().endswith('}'):
        content = content.rstrip() + '\n'
    content = content.rstrip('\n')
    content += f'\nDialogue: 0,{_ass_ts(start)},{_ass_ts(total_duration)},CTA,,0,0,0,,{CTA_TEXT}'

    with open(ass_path, 'w', encoding='utf-8') as f:
        f.write(content)
    return ass_path


def concat_videos_audio(video_paths: list[str], output: str, transition_duration: float = 0.0) -> str:
    """Concatenate videos sequentially with varied cinematic transitions."""
    Path(output).parent.mkdir(parents=True, exist_ok=True)

    n = len(video_paths)
    if n == 1:
        cmd = [
            'ffmpeg', '-y',
            '-i', video_paths[0],
            '-c:v', 'copy',
            '-c:a', 'copy',
            output,
        ]
        subprocess.run(cmd, check=True, capture_output=True, text=True)
        return output

    inputs = []
    for v in video_paths:
        inputs.extend(['-i', v])

    if transition_duration <= 0:
        video_inputs = ''.join(f'[{i}:v]' for i in range(n))
        audio_inputs = ''.join(f'[{i}:a]' for i in range(n))
        filter_chain = f'{video_inputs}concat=n={n}:v=1:a=0[v];{audio_inputs}concat=n={n}:v=0:a=1[ain];[ain]dynaudnorm=p=0.95:m=100[a]'
        cmd = [
            'ffmpeg', '-y', *inputs,
            '-filter_complex', filter_chain,
            '-map', '[v]',
            '-map', '[a]',
            '-c:v', 'libx264',
            '-preset', 'fast',
            '-crf', '16',
            '-r', '30',
            '-c:a', 'aac',
            '-b:a', '192k',
            '-shortest',
            output,
        ]
        subprocess.run(cmd, check=True, capture_output=True, text=True)
        return output

    durations = [get_duration(v) for v in video_paths]
    td = transition_duration

    chain = []
    xfade_types = []
    for i in range(1, n):
        t_type = random.choice(TRANSITION_TYPES)
        xfade_types.append(t_type)
        pair_td = min(td, durations[i] * 0.25, durations[i - 1] * 0.25)
        offset = sum(durations[:i]) - i * td
        src_v = f'[{i-1}:v]' if i == 1 else f'[v{i-1}]'
        src_a = f'[{i-1}:a]' if i == 1 else f'[a{i-1}]'
        chain.append(
            f'{src_v}[{i}:v]xfade=transition={t_type}:duration={pair_td}:offset={offset}[v{i}]'
        )
        chain.append(
            f'{src_a}[{i}:a]acrossfade=d={pair_td}:c1=tri:c2=tri[a{i}]'
        )
    chain.append(f'[v{n-1}]format=yuv420p[v]')
    chain.append(f'[a{n-1}]dynaudnorm=p=0.95:m=100, aformat=sample_rates=44100:channel_layouts=stereo[a]')

    filter_chain = ';'.join(chain)

    cmd = [
        'ffmpeg', '-y', *inputs,
        '-filter_complex', filter_chain,
        '-map', '[v]',
        '-map', '[a]',
        '-c:v', 'libx264',
        '-preset', 'fast',
        '-crf', '16',
        '-r', '30',
        '-c:a', 'aac',
        '-b:a', '192k',
        output,
    ]
    subprocess.run(cmd, check=True, capture_output=True, text=True)
    return output


def compose_final(
    video_path: str,
    subs_path: str,
    output: str,
    width: int = 1080,
    height: int = 1920,
) -> str:
    """Final pass: fade in/out, loudness -14 LUFS, music bed w/ sidechain,
    color consistency, sharpening, subtitles + CTA, fast-start H.264."""
    Path(output).parent.mkdir(parents=True, exist_ok=True)

    total = get_duration(video_path)
    fade_in = 0.3
    fade_out = 0.6
    fade_out_start = max(0.0, total - fade_out)

    _append_cta(subs_path, total)
    escaped = subs_path.replace('\\', '/').replace(':', '\\:')

    # --- Video chain: consistent look + fades + subtitles/CTA ---
    video_chain = (
        f'[0:v]eq=contrast=1.04:saturation=1.06:brightness=-0.01,'
        f'unsharp=luma_msize_x=5:luma_msize_y=5:luma_amount=0.5,'
        f'fade=t=out:st={fade_out_start}:d={fade_out},'
        f'ass=\'{escaped}\'[v]'
    )

    audio_chain = (
        f'[0:a]dynaudnorm=p=0.95:m=100,'
        f'loudnorm=I=-14:TP=-1.5:LRA=11,'
        f'afade=t=in:st=0:d={fade_in},'
        f'afade=t=out:st={fade_out_start}:d={fade_out}[a]'
    )
    inputs = ['-i', video_path]

    filter_complex = f'{video_chain};{audio_chain}'

    cmd = [
        'ffmpeg', '-y', *inputs,
        '-filter_complex', filter_complex,
        '-map', '[v]',
        '-map', '[a]',
        '-c:v', 'libx264',
        '-preset', 'fast',
        '-crf', '18',
        '-profile:v', 'high',
        '-pix_fmt', 'yuv420p',
        '-c:a', 'aac',
        '-b:a', '192k',
        '-movflags', '+faststart',
        output,
    ]
    subprocess.run(cmd, check=True, capture_output=True, text=True)
    return output
