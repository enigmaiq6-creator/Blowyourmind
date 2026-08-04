import re
import difflib
import whisper


def transcribe_with_words(audio_path: str, model_name: str = 'small', language: str | None = None):
    model = whisper.load_model(model_name)
    result = model.transcribe(audio_path, word_timestamps=True, language=language)

    fps = 30
    words = []
    for seg in result['segments']:
        for w in seg.get('words', []):
            text = w['word'].strip()
            if text:
                words.append({
                    'text': text,
                    'start': round(w['start'], 3),
                    'end': round(w['end'], 3),
                })

    return {'fps': fps, 'words': words}


def transcribe_to_srt(audio_path: str, srt_path: str, model_name: str = 'base', language: str | None = None):
    model = whisper.load_model(model_name)
    result = model.transcribe(audio_path, language=language)

    lines = []
    for i, seg in enumerate(result['segments'], start=1):
        start = _fmt_srt(seg['start'])
        end = _fmt_srt(seg['end'])
        text = seg['text'].strip()
        lines.append(str(i))
        lines.append(f'{start} --> {end}')
        lines.append(text)
        lines.append('')

    with open(srt_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
    return srt_path


def _normalize_word(w: str) -> str:
    return re.sub(r'[^a-zA-Z0-9\']', '', w).lower()


def _align_words(whisper_words: list[dict], correct_words: list[str]) -> list[dict]:
    """Align Whisper word timings to correct script words using difflib."""
    whisper_texts = [_normalize_word(w['text']) for w in whisper_words]
    correct_texts = [_normalize_word(w) for w in correct_words]

    matcher = difflib.SequenceMatcher(None, whisper_texts, correct_texts)
    opcodes = matcher.get_opcodes()

    aligned = []
    wi = 0
    for tag, i1, i2, j1, j2 in opcodes:
        if tag == 'equal':
            for k in range(i2 - i1):
                entry = whisper_words[wi + k].copy()
                entry['text'] = correct_words[j1 + k]
                aligned.append(entry)
            wi += (i2 - i1)
        elif tag == 'replace':
            ws = whisper_words[wi:wi + (i2 - i1)]
            cs = correct_words[j1:j2]
            for k in range(len(cs)):
                idx = min(k, len(ws) - 1) if ws else 0
                if ws:
                    entry = ws[idx].copy()
                    entry['text'] = cs[k]
                    aligned.append(entry)
            wi += (i2 - i1)
        elif tag == 'delete':
            wi += (i2 - i1)
        elif tag == 'insert':
            for k in range(j1, j2):
                aligned.append({
                    'text': correct_words[k],
                    'start': aligned[-1]['end'] if aligned else 0.0,
                    'end': (aligned[-1]['end'] + 0.3) if aligned else 0.3,
                })

    return aligned


KEYWORD_COLOR = '&H00FFE0F0&'  # ASS BGR: amarillo/crema brillante para resaltar

_MONEY_WORDS = {
    'dólar', 'dólares', 'dolar', 'dolares', 'usd', 'millón', 'millones', 'millon',
    'mil', 'billón', 'billones', 'billon', 'trillón', 'trillones', 'euro', 'euros',
    'pesos', 'mxn', 'eur', 'peso', 'centavo', 'centavos', 'bitcoin', 'cripto',
    'millones', 'billones', 'ganancia', 'ganancias', 'beneficio', 'beneficios',
    'fortuna', 'riqueza', 'deuda', 'interés', 'interes', 'precio', 'precios',
    'valor', 'acciones', 'accion', 'inversión', 'inversion', 'rendimiento',
    'impuesto', 'impuestos', 'deducción', 'deduccion', 'exención', 'exencion',
    'paraiso', 'paraíso', 'capital', 'activo', 'activos', 'pasivo', 'pasivos',
}


def _is_keyword(word: str) -> bool:
    """True for numbers, currencies and money/finance terms (highlighted on screen)."""
    cleaned = re.sub(r'[^\w]', '', word).lower()
    if re.search(r'\d', cleaned):
        return True
    return cleaned in _MONEY_WORDS


def _style_word(word: str) -> str:
    escaped = word.replace('{', '\\{').replace('}', '\\}')
    if _is_keyword(word):
        return f'{{\\c{KEYWORD_COLOR}}}{escaped}{{\\c}}'
    return escaped


def transcribe_to_ass_word(
    audio_path: str,
    ass_path: str,
    model_name: str = 'small',
    language: str | None = None,
    max_words: int = 3,
    correct_text: str | None = None,
    scene_word_boundaries: list[int] | None = None,
):
    model = whisper.load_model(model_name)
    result = model.transcribe(audio_path, word_timestamps=True, language=language)

    all_words = []
    for seg in result['segments']:
        seg_words_list = seg.get('words', [])
        for w in seg_words_list:
            text = w['word'].strip()
            if text:
                all_words.append({
                    'text': text,
                    'start': w['start'],
                    'end': w['end'],
                })

    if correct_text and all_words:
        correct_words = re.findall(r"\b[\w']+\b", correct_text)
        if correct_words:
            all_words = _align_words(all_words, correct_words)

    lines = [
        '[Script Info]',
        'ScriptType: v4.00+',
        'PlayResX: 1080',
        'PlayResY: 1920',
        'ScaledBorderAndShadow: yes',
        '',
        '[V4+ Styles]',
        'Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding',
        'Style: Default,Arial,48,&H00FFFFFF,&H00FFFFFF,&H00000000,&H00000000,-1,0,0,0,100,100,0,0,1,2,1,2,40,40,400,1',
        '',
        '[Events]',
        'Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text',
    ]

    scene_boundary_set = set(scene_word_boundaries) if scene_word_boundaries else set()

    chunks = []
    for idx, w in enumerate(all_words):
        is_scene_start = (idx + 1) in scene_boundary_set
        if not chunks:
            chunks.append([w])
        elif is_scene_start:
            chunks.append([w])
        else:
            last = chunks[-1][-1]
            gap = w['start'] - last['end']
            if len(chunks[-1]) >= max_words or gap >= 0.35:
                chunks.append([w])
            else:
                chunks[-1].append(w)

    fps = 30
    frame_dur = 1.0 / fps

    for chunk in chunks:
        words_text = ' '.join(_style_word(w['text']) for w in chunk)
        start_s = round(chunk[0]['start'] / frame_dur) * frame_dur
        end_s = round(chunk[-1]['end'] / frame_dur) * frame_dur
        if end_s <= start_s:
            end_s = start_s + frame_dur
        lines.append(f'Dialogue: 0,{_fmt_ass(start_s)},{_fmt_ass(end_s)},Default,,0,0,0,,{words_text}')

    with open(ass_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
    return ass_path


def _fmt_srt(seconds: float) -> str:
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    ms = int((seconds - int(seconds)) * 1000)
    return f'{h:02d}:{m:02d}:{s:02d},{ms:03d}'


def _fmt_ass(seconds: float) -> str:
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    cs = int((seconds - int(seconds)) * 100)
    return f'{h}:{m:02d}:{s:02d}.{cs:02d}'
