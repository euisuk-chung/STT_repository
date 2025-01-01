# STT Module for Local and YouTube Audio

## 개요

이 프로젝트는 [faster-whisper](https://github.com/guillaumekln/faster-whisper) 와 [OpenAI Whisper API](https://platform.openai.com/docs/guides/speech-to-text)를 활용하여 오디오를 텍스트로 변환(STT)하는 기능을 제공합니다.


- **로컬 오디오**와 **YouTube 오디오**를 간편하게 전사  
- 출력 포맷(`.txt`, `.srt`, `.json`) 지원  
- GPU(CUDA) 환경에서 빠른 처리  
- 확장(배치 처리, 실시간 스트리밍 등)에 용이  

---


## 디렉터리 구조

```plaintext
D:.
│   .env
│   .gitignore
│   LICENSE
│   Pipfile
│   Pipfile.lock
│   README.md
│   youtube_faster_whisper.ipynb  <-- (예시: 최상위에 위치, 빠른 시연용)
│
├── config
│       config.yaml
│       paths.json
│
├── contents             <-- 내부용(고급 설정) 노트북
│       local_faster_whisper.ipynb
│       openai_whisper_stt.ipynb
│       youtube_faster_whisper.ipynb
│
├── outputs              <-- 전사 결과 저장 폴더
│   ├── local_text
│   │       sample_sound.txt
│   └── youtube_text
│           오늘 이 뉴스_  추석 코앞 _13호 태풍_ 발동_어디로 가나_ 한중일 _촉각.txt
│
├── samples              <-- 외부공개용(간단 예시) 노트북
│   ├── downloaded
│   │       sample_sound.mp3
│   │       오늘 이 뉴스_  추석 코앞 _13호 태풍_ 발동_어디로 가나_ 한중일 _촉각.mp3
│   ├── local
│   │       local_whisper_sample.ipynb
│   └── youtube
│           youtube_faster_whisper_sample.ipynb
│
└── stt_module           <-- 실제 STT 관련 코드(파이썬 모듈)
        faster_whisper_utils.py
        openai_whisper_utils.py
        post_processing.py
        __init__.py
```

---

## 설치 및 실행

### 1) 파이썬 환경 세팅

- **Pipenv 사용 시**:
    
    ```bash
    pipenv install   # Pipfile & Pipfile.lock 기반 설치
    pipenv shell     # 가상환경 진입
    
    ```
    
- **또는 requirements.txt 사용 시**(필요하다면 직접 생성):
    
    ```bash
    pip install -r requirements.txt
    
    ```
    

### 2) `.env` 파일 설정

- `.env` 파일이 없다면, `.env.example` 혹은 직접 작성:
    
    ```bash
    OPENAI_API_KEY=sk-xxxx-xxxx-xxxx
    
    ```
    
- GPU(CUDA) 사용을 원한다면, `torch` 버전과 CUDA 버전 호환 체크

### 3) Jupyter Notebook 실행

```bash
jupyter notebook

```

- `samples/` 폴더 내 간단 예시 노트북(`youtube_faster_whisper_sample.ipynb`, `local_whisper_sample.ipynb`)을 실행해보거나,
- `contents/` 폴더 내 고급 노트북(`youtube_faster_whisper.ipynb`, `local_faster_whisper.ipynb`, `openai_whisper_stt.ipynb`)을 시도해볼 수 있습니다.

---

## 주요 기능

1. **오디오 전사 (faster-whisper)**
    - `stt_module/faster_whisper_utils.py` 내 함수(`download_audio_from_youtube`, `transcribe_with_faster_whisper`) 활용
    - GPU가 있는 환경에서는 `cuda`, 없는 환경에서는 `cpu`로 처리
2. **오디오 전사 (OpenAI Whisper API)**
    - `stt_module/openai_whisper_utils.py` 내 함수(`transcribe_with_openai_whisper`) 활용
    - `.env`에서 `OPENAI_API_KEY`를 불러옴
3. **출력 포맷**
    - `.txt`, `.srt`, `.json` 지원
    - 한글/영어 텍스트 후처리(`post_processing.py`), 파일명 정리(`clean_filename`) 등

---

## 추가 개발 계획

- **Batch Processing**: 여러 URL이나 오디오 파일을 자동으로 순회하며 전사
- **실시간 스트리밍**: 라이브 음원을 Websocket/RTMP 등으로 받아 전사
- **UI/웹앱 연동**: Streamlit, Gradio 등을 이용한 웹 기반 인터페이스 추가
- **Docker 배포**: GPU 환경 일관성을 위한 Dockerfile 구성

---

## 라이선스

- 이 프로젝트는 [MIT License](https://chatgpt.com/g/g-p-67753835531081919b7041904a080cf6-stt-project/c/LICENSE)를 따릅니다.