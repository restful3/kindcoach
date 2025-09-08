#!/bin/bash

# KindCoach 실행 스크립트
# 포트 관리, 가상환경 설정, 애플리케이션 실행을 자동화

set -e  # 에러 발생시 스크립트 종료

PORT=8501
VENV_DIR=".venv"
REQUIREMENTS_FILE="requirements.txt"
MAIN_APP="src/main.py"

echo "🤖❤️ KindCoach 실행 스크립트"
echo "=================================="

# 1. 포트 8501 사용 중인 프로세스 확인 및 종료
echo "📡 포트 $PORT 상태 확인 중..."
PORT_PID=$(lsof -ti:$PORT 2>/dev/null || echo "")

if [ ! -z "$PORT_PID" ]; then
    echo "⚠️  포트 $PORT이 사용 중입니다. 프로세스 ID: $PORT_PID"
    echo "🔄 해당 프로세스를 종료합니다..."
    kill -9 $PORT_PID 2>/dev/null || echo "프로세스 종료 실패 (이미 종료되었을 수 있음)"
    sleep 2
    echo "✅ 포트 $PORT 정리 완료"
else
    echo "✅ 포트 $PORT 사용 가능"
fi

# 2. 가상환경 확인 및 생성
echo "🐍 가상환경 상태 확인 중..."

if [ ! -d "$VENV_DIR" ]; then
    echo "📦 가상환경이 없습니다. 생성 중..."
    python3 -m venv $VENV_DIR
    echo "✅ 가상환경 생성 완료"
else
    echo "✅ 가상환경 발견됨"
fi

# 3. 가상환경 활성화
echo "🔌 가상환경 활성화 중..."
source $VENV_DIR/bin/activate

# Python 버전 확인
PYTHON_VERSION=$(python --version)
echo "🐍 사용 중인 Python: $PYTHON_VERSION"

# 4. 의존성 패키지 설치 확인
if [ -f "$REQUIREMENTS_FILE" ]; then
    echo "📋 패키지 의존성 확인 중..."
    
    # pip가 최신인지 확인
    echo "🔄 pip 업그레이드 중..."
    pip install --upgrade pip > /dev/null 2>&1
    
    # requirements.txt 기반 패키지 설치
    echo "📦 패키지 설치 중..."
    pip install -r $REQUIREMENTS_FILE
    echo "✅ 패키지 설치 완료"
else
    echo "⚠️  $REQUIREMENTS_FILE 파일을 찾을 수 없습니다."
    echo "패키지 설치를 건너뜁니다."
fi

# 5. 환경 변수 파일 확인
if [ ! -f ".env" ]; then
    echo "⚠️  .env 파일이 없습니다."
    echo "💡 env_example을 .env로 복사하고 API 키를 설정하세요:"
    echo "   cp env_example .env"
    echo "   # .env 파일을 편집하여 실제 API 키를 입력"
fi

# 6. 메인 애플리케이션 파일 확인
if [ ! -f "$MAIN_APP" ]; then
    echo "❌ 메인 애플리케이션 파일 '$MAIN_APP'을 찾을 수 없습니다."
    exit 1
fi

# 7. Streamlit 애플리케이션 실행
echo "🚀 KindCoach 애플리케이션 시작 중..."
echo "🌐 브라우저에서 http://localhost:$PORT 로 접속하세요"
echo "🛑 종료하려면 Ctrl+C를 누르세요"
echo "=================================="

# Streamlit 실행 (환경 변수로 포트 설정)
export STREAMLIT_SERVER_PORT=$PORT
streamlit run $MAIN_APP

# 스크립트 종료시 정리
echo ""
echo "👋 KindCoach 애플리케이션이 종료되었습니다."
echo "감사합니다! 🤖❤️"