"""
openai_whisper_utils.py

OpenAI Whisper API를 통해 오디오 파일을 전사하는 함수.
"""

import os
from pathlib import Path

import openai
from dotenv import load_dotenv

from .post_processing import post_process_text


def transcribe_with_openai_whisper(
    audio_path,
    model="whisper-1",
    response_format="text",
    output_formats=["txt"],
    output_dir="outputs/openai_text",
    language=None,
    temperature=0.0
):
    """
    OpenAI Whisper API를 통해 오디오 파일을 전사.
    :param audio_path: 전사할 오디오 파일 경로 (str)
    :param model: "whisper-1"
    :param response_format: "text", "json", "verbose_json", "srt" (OpenAI가 지원하는 포맷)
    :param output_formats: 결과 저장 포맷 ["txt", "json", ...] (일관성을 위해 별도 처리)
    :param output_dir: 출력 디렉터리
    :param language: 언어 (예: "ko", "en"). None이면 자동감지
    :param temperature: decoding temperature
    """

    # 환경 변수 로드
    load_dotenv()
    openai.api_key = os.getenv("OPENAI_API_KEY")
    if not openai.api_key:
        raise ValueError("[ERROR] OPENAI_API_KEY가 설정되지 않았습니다. .env를 확인하세요.")

    file_path = Path(audio_path)
    if not file_path.exists():
        raise FileNotFoundError(f"[ERROR] 파일이 존재하지 않습니다: {file_path}")

    # OpenAI API 요청
    print(f"[INFO] Transcribing with OpenAI Whisper API: {file_path.name}, model={model}")
    with open(file_path, "rb") as audio_file:
        response = openai.Audio.transcribe(
            file=audio_file,
            model=model,
            response_format=response_format,
            temperature=temperature,
            language=language
        )

    # response_format="text"일 경우 response는 문자열
    # response_format="json" 또는 "verbose_json"일 경우 response는 파이썬 dict
    if isinstance(response, str):
        raw_text = response
    else:
        # json, verbose_json 등
        # "text" 필드를 확인하거나, 필요 구조를 파싱
        raw_text = response.get("text", "")

    processed_text = post_process_text(raw_text, lang=language if language else "en")

    # 결과 저장
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    base_name = file_path.stem

    for fmt in output_formats:
        out_file = output_dir / f"{base_name}.{fmt}"
        if fmt == "txt":
            with open(out_file, "w", encoding="utf-8") as f:
                f.write(processed_text)
        elif fmt == "json":
            import json
            json_output = {"transcription": processed_text}
            with open(out_file, "w", encoding="utf-8") as f:
                json.dump(json_output, f, ensure_ascii=False, indent=2)
        # 필요 시 srt나 다른 포맷도 추가 처리
        print(f"[INFO] Saved {fmt.upper()} file at: {out_file}")

    return processed_text
