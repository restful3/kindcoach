# 🤖❤️ KindCoach

**AI-Powered Coaching Platform for Kindergarten Teachers**

*Every Child Deserves Kindness - 모든 아이는 사랑받을 자격이 있습니다*

---

## 🌟 프로젝트 소개

KindCoach는 어린이집 선생님들이 아이들과 더 따뜻하고 효과적으로 소통할 수 있도록 도와주는 AI 기반 코칭 플랫폼입니다. 

### 🎯 핵심 가치
- 👶 **아동 중심**: 모든 아이의 건강한 발달 지원
- 🎓 **교사 성장**: 개인화된 맞춤형 코칭 제공
- ❤️ **따뜻한 소통**: 사랑과 이해를 바탕으로 한 상호작용
- 🤖 **AI 지원**: 과학적이고 객관적인 분석과 피드백

---

## ✨ 주요 기능

### 🎙️ **오디오 파일 분석**
- 교사-아동 대화 음성 인식 및 텍스트 변환 (AssemblyAI)
- 화자 구분을 통한 정확한 상호작용 분석
- AI 기반 종합 분석 및 개선 제안 (OpenAI GPT-4o-mini)

### 📱 **모바일 최적화**
- 반응형 웹 인터페이스 (Streamlit)
- 터치 친화적 UI/UX
- 작은 화면에서도 최적화된 레이아웃

### 🤖 **다양한 AI 분석**
- 종합 코칭 분석 및 피드백
- 빠른 피드백 제공
- 아동 발달 관점 분석
- 상황별 코칭 팁 제공
- 감정 분석 및 해석

---

## 🛠️ 기술 스택

### **Frontend**
- **Streamlit**: 직관적인 웹 애플리케이션 인터페이스

### **AI & Analytics**
- **AssemblyAI**: 고정밀 한국어 음성인식 + 화자분리
- **OpenAI GPT-4o-mini**: 고급 대화 분석 및 코칭 가이드 생성
- **Python**: 데이터 처리 및 분석 엔진

### **Infrastructure**
- **Python 3.10**: 백엔드 개발 언어
- **Git**: 버전 관리

---

## 🚀 빠른 시작

### 1. 저장소 클론
```bash
git clone <repository-url>
cd kindcoach
```

### 2. 가상환경 설정
```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
```

### 3. 의존성 설치
```bash
pip install -r requirements.txt
```

### 4. 환경변수 설정
```bash
cp env_example .env
# .env 파일을 열어 API 키를 설정하세요
```

`.env` 파일 예시:
```bash
ASSEMBLYAI_API_KEY=your_assemblyai_api_key
OPENAI_API_KEY=your_openai_api_key
STREAMLIT_SERVER_PORT=8501
```

### 5. 애플리케이션 실행
```bash
streamlit run src/main.py
```

브라우저에서 `http://localhost:8501`로 접속하여 KindCoach를 사용하세요! 🎉

---

## 📁 프로젝트 구조

```
kindcoach/
├── 📄 README.md              # 프로젝트 소개
├── 📄 CLAUDE.md             # Claude Code 설정 파일
├── 📄 requirements.txt       # Python 패키지 목록
├── 📄 env_example           # 환경변수 템플릿
├── 📄 .env                  # 환경변수 설정 (실제 API 키)
├── 📁 .venv/                # Python 가상환경
├── 📁 src/                  # 소스 코드
│   ├── 🐍 main.py           # Streamlit 메인 앱
│   ├── 🎙️ audio_processor.py # AssemblyAI 음성 처리 모듈
│   ├── 🤖 ai_analyzer.py    # OpenAI AI 분석 엔진
│   └── 🛠️ utils.py          # 공통 유틸리티 함수
├── 📁 config/               # 설정 파일
│   └── 📝 prompts.py        # AI 프롬프트 템플릿
├── 📁 data/                 # 데이터 저장소
│   ├── 📄 sample_audio/     # 샘플 오디오 파일
│   └── 📊 analysis_results/ # 분석 결과 JSON 파일
├── 📁 tests/                # 테스트 코드 (예정)
└── 📁 docs/                 # 문서 (예정)
```

---

## 🎨 주요 화면

### 🎙️ **음성 파일 업로드**
- 드래그 앤 드롭 파일 업로드
- 지원 형식: WAV, MP3, M4A, FLAC, OGG, WMA, AAC (최대 50MB)
- 파일 정보 및 예상 처리 시간 표시

### 📊 **분석 결과 대시보드**
- **요약 탭**: 대화 시간, 단어 수, 화자별 통계
- **전사 탭**: 화자 구분된 대화 전사본, 타임스탬프 포함
- **AI 분석 탭**: 종합 코칭 피드백, 추가 분석 옵션
- **통계 탭**: 발화 패턴 시각화, 균형 분석

### 🤖 **AI 분석 기능**
- 교사-아동 상호작용 품질 평가 (10점 만점)
- 교사의 강점 및 개선점 분석
- 구체적인 개선 제안 및 대안 응답 예시
- 아동 발달 수준 분석
- 상황별 코칭 팁 제공

---