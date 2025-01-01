"""
post_processing.py

공통 전처리, 파일 이름 정리, SRT 타임스탬프 포맷 등 모듈.
"""

import os
import re
from pathlib import Path


def clean_filename(filename):
    """
    파일명 정리: 한글/영문/숫자/공백/마침표/하이픈/언더스코어 외 모두 제거,
    연속된 언더스코어 하나로 축소 등.
    """
    filename = re.sub(r"\([^)]*\)", "", filename)                      # 괄호와 그 내용 제거
    filename = re.sub(r"[^\w\s\-_가-힣.]", "_", filename)              # 허용되지 않는 문자 -> _
    filename = re.sub(r"_{2,}", "_", filename)                        # 연속된 _ -> 하나로
    return filename.strip().strip("_")

def remove_existing_files(directory):
    """
    지정된 디렉터리 내 기존 파일 모두 삭제.
    """
    dir_path = Path(directory)
    for file in dir_path.glob("*"):
        if file.is_file():
            file.unlink()
            print(f"[INFO] Removed existing file: {file.name}")

def format_timestamp(seconds):
    """
    seconds를 SRT 형식 (HH:MM:SS,mmm)으로 변환
    """
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    ms = int((seconds - int(seconds)) * 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"

def post_process_text(text, lang="en"):
    """
    공통 전처리 함수.
    언어별로 적절히 처리(예: 한글 문장 끝에 마침표, 영어 문장 처리 등).
    """
    text = remove_extra_spaces(text)
    if lang.startswith("ko"):
        return normalize_korean_text(text)
    else:
        return normalize_english_text(text)

def remove_extra_spaces(text):
    # 다중 공백, 탭, 줄바꿈 제거
    return re.sub(r"\s+", " ", text).strip()

def normalize_korean_text(text):
    """
    한글 문장 전처리 예시:
    - 연속된 구두점 제거
    - 종결어미 뒤에 마침표 혹은 줄바꿈
    """
    text = re.sub(r"([.!?])\1+", r"\1", text)
    ending_patterns = r"(습니다|니다|세요|네요|어요|아요|죠|지요|에요|예요|입니까|합니까|할까요|말입니다|바랍니다|싶습니다)"
    text = re.sub(f"{ending_patterns}(?![\s.!?])", r"\1. ", text)
    text = re.sub(r"([.!?])(?=\S)", r"\1\n", text)
    return text.strip()

def normalize_english_text(text):
    """
    영어 문장 전처리 예시:
    - 연속된 구두점(!!, ??) 축소
    - 문장 첫 글자 대문자화 등
    """
    text = re.sub(r"([.!?])\1+", r"\1", text) 
    sentences = text.split(". ")
    sentences = [s.capitalize().strip() for s in sentences]
    return ". ".join(sentences)
