import assemblyai as aai
import os
import json


def _milliseconds_to_seconds(value):
    if value is None:
        return None
    return round(float(value) / 1000, 2)


def _build_segments(transcript):
    try:
        sentences = transcript.get_sentences()
    except Exception:
        sentences = None

    if sentences:
        return [
            {
                "text": sentence.text,
                "start": _milliseconds_to_seconds(sentence.start),
                "end": _milliseconds_to_seconds(sentence.end),
            }
            for sentence in sentences
            if getattr(sentence, "text", "").strip()
        ]

    words = getattr(transcript, "words", None) or []
    segments = []
    current_words = []
    current_start = None
    current_end = None

    for word in words:
        text = getattr(word, "text", "").strip()
        if not text:
            continue

        if current_start is None:
            current_start = getattr(word, "start", None)

        current_words.append(text)
        current_end = getattr(word, "end", current_end)

        if text.endswith((".", "!", "?")) or len(current_words) >= 25:
            segments.append({
                "text": " ".join(current_words),
                "start": _milliseconds_to_seconds(current_start),
                "end": _milliseconds_to_seconds(current_end),
            })
            current_words = []
            current_start = None
            current_end = None

    if current_words:
        segments.append({
            "text": " ".join(current_words),
            "start": _milliseconds_to_seconds(current_start),
            "end": _milliseconds_to_seconds(current_end),
        })

    if segments:
        return segments

    return [{
        "text": transcript.text,
        "start": None,
        "end": None,
    }] if getattr(transcript, "text", None) else []


def main(filelink):    
    aai.settings.api_key = "ce8209cdfb214d80b63881d941a2b015"
    transcriber = aai.Transcriber()
    file_path=os.path.join(os.getcwd(),"data","processed")
    os.makedirs(file_path, exist_ok=True)
    transcript = transcriber.transcribe(filelink)
    segments = _build_segments(transcript)

    transcript_path=os.path.join(file_path,"transcript.txt")
    segments_path=os.path.join(file_path,"transcript_segments.json")

    with open(transcript_path, "w", encoding="utf-8") as file:
        file.write("\n".join(segment["text"] for segment in segments) or transcript.text)

    with open(segments_path, "w", encoding="utf-8") as file:
        json.dump(segments, file, indent=2)

    return transcript_path
