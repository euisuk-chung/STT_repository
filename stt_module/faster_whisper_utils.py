"""
faster_whisper_utils.py

faster-whisper 라이브러리를 사용해 오디오 파일(로컬/YouTube)에서 텍스트를 추출하는 유틸리티 함수들.
"""

import os
import re
from pathlib import Path

import torch
import validators
from faster_whisper import WhisperModel
from tqdm.auto import tqdm
from yt_dlp import YoutubeDL

from .post_processing import (clean_filename, format_timestamp,
                              post_process_text, remove_existing_files)


def download_audio_from_youtube(url, out_dir):
    """
    yt-dlp를 통해 YouTube 오디오를 mp3로 다운로드.
    out_dir 내 기존 파일 제거 후 다운로드 진행.
    """
    if not validators.url(url):
        raise ValueError(f"유효하지 않은 URL입니다: {url}")

    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    print(f"[INFO] Removing existing files in {out_dir}...")
    remove_existing_files(out_dir)

    print(f"[INFO] Downloading audio from {url} ...")
    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": f"{out_dir}/%(title)s.%(ext)s",
        "postprocessors": [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "192",
        }],
        "progress_hooks": [lambda d: tqdm.write(f"{d['status']} - {d.get('filename', 'Unknown file')}")]
    }

    with YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(url, download=True)
        file_path = ydl.prepare_filename(info_dict)
        mp3_file_path = Path(file_path).with_suffix(".mp3")
        clean_file_path = mp3_file_path.parent / f"{clean_filename(mp3_file_path.stem)}.mp3"
        mp3_file_path.rename(clean_file_path)

    print(f"[INFO] File downloaded to {clean_file_path}!")
    return str(clean_file_path)

def transcribe_with_faster_whisper(
    audio_path,
    model_name="large-v2",
    beam_size=5,
    temperature=0.0,
    output_formats=["txt"],
    output_dir="outputs",
):
    """
    faster-whisper를 사용해 오디오 파일을 텍스트로 변환.
    :param audio_path: 전사할 오디오 파일 경로 (str)
    :param model_name: faster-whisper 모델명 (e.g. large-v2, medium, etc.)
    :param beam_size: beam search size
    :param temperature: decoding temperature
    :param output_formats: 결과 저장 포맷 (["txt", "srt", "json"] 등)
    :param output_dir: 결과물을 저장할 디렉터리
    """

    # Device 설정
    device = "cuda" if torch.cuda.is_available() else "cpu"
    compute_type = "float16" if device == "cuda" else "int8"
    model = WhisperModel(model_name, device=device, compute_type=compute_type)

    file_path = Path(audio_path)
    if not file_path.exists():
        raise FileNotFoundError(f"[ERROR] 해당 오디오 파일이 존재하지 않습니다: {file_path}")

    print(f"[INFO] Transcribing {file_path.name} using {model_name} on {device}...")

    # Transcribe
    segments, info = model.transcribe(
        str(file_path),
        beam_size=beam_size,
        temperature=temperature
    )
    detected_language = info.language
    language_probability = info.language_probability
    print(f"[INFO] Detected language: {detected_language} (Prob = {language_probability:.2f})")

    # 후처리
    full_text = " ".join([seg.text for seg in segments])
    processed_text = post_process_text(full_text, lang=detected_language)

    # 결과 저장
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    for fmt in output_formats:
        out_file = output_dir / f"{file_path.stem}.{fmt}"

        if fmt == "txt":
            with open(out_file, "w", encoding="utf-8") as f:
                f.write(processed_text)

        elif fmt == "srt":
            with open(out_file, "w", encoding="utf-8") as f:
                for i, seg in enumerate(segments, start=1):
                    f.write(f"{i}\n")
                    f.write(f"{format_timestamp(seg.start)} --> {format_timestamp(seg.end)}\n")
                    # 각 segment별 후처리
                    segment_text = post_process_text(seg.text, lang=detected_language)
                    f.write(f"{segment_text}\n\n")

        elif fmt == "json":
            import json
            json_output = {
                "transcription": processed_text,
                "segments": []
            }
            for i, seg in enumerate(segments, start=1):
                json_output["segments"].append({
                    "id": i,
                    "start": seg.start,
                    "end": seg.end,
                    "text": post_process_text(seg.text, lang=detected_language)
                })
            with open(out_file, "w", encoding="utf-8") as f:
                json.dump(json_output, f, ensure_ascii=False, indent=2)

        print(f"[INFO] Saved {fmt.upper()} file at: {out_file}")

    return processed_text
