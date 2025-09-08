"""
공통 유틸리티 함수 모음
환경 변수 관리, 파일 처리, 데이터 변환 등
"""

import os
import json
from typing import Dict, Any, List, Optional, Union
from datetime import datetime
import pandas as pd
from dotenv import load_dotenv
import tempfile
import hashlib
from mutagen import File
import io


def load_environment():
    """환경 변수를 로드하고 검증합니다."""
    load_dotenv()
    
    required_vars = ["ASSEMBLYAI_API_KEY", "OPENAI_API_KEY", "ADMIN_USERNAME", "ADMIN_PASSWORD"]
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        raise ValueError(f"다음 환경 변수가 설정되지 않았습니다: {', '.join(missing_vars)}")
    
    return {
        "assemblyai_key": os.getenv("ASSEMBLYAI_API_KEY"),
        "openai_key": os.getenv("OPENAI_API_KEY"),
        "streamlit_port": os.getenv("STREAMLIT_SERVER_PORT", "8501"),
        "admin_username": os.getenv("ADMIN_USERNAME"),
        "admin_password": os.getenv("ADMIN_PASSWORD")
    }


def validate_audio_file(uploaded_file) -> Dict[str, Any]:
    """업로드된 오디오 파일을 검증합니다."""
    if uploaded_file is None:
        return {"valid": False, "error": "파일이 업로드되지 않았습니다."}
    
    # 파일 크기 확인 (50MB 제한)
    max_size = 50 * 1024 * 1024  # 50MB in bytes
    if uploaded_file.size > max_size:
        return {"valid": False, "error": f"파일 크기가 너무 큽니다. 최대 {max_size//1024//1024}MB까지 지원됩니다."}
    
    # 지원되는 파일 형식 확인
    supported_formats = ['.wav', '.mp3', '.m4a', '.flac', '.ogg', '.wma', '.aac']
    file_extension = os.path.splitext(uploaded_file.name)[1].lower()
    
    if file_extension not in supported_formats:
        return {
            "valid": False, 
            "error": f"지원되지 않는 파일 형식입니다. 지원 형식: {', '.join(supported_formats)}"
        }
    
    return {
        "valid": True,
        "filename": uploaded_file.name,
        "size": uploaded_file.size,
        "format": file_extension
    }


def format_duration(seconds: float) -> str:
    """초를 분:초 형식으로 변환합니다."""
    if seconds < 0:
        return "00:00"
    
    minutes = int(seconds // 60)
    remaining_seconds = int(seconds % 60)
    return f"{minutes:02d}:{remaining_seconds:02d}"


def format_timestamp(timestamp: float) -> str:
    """타임스탬프를 읽기 쉬운 형식으로 변환합니다."""
    return format_duration(timestamp)


def calculate_speaking_balance(speaker_stats: Dict[str, Any]) -> Dict[str, Any]:
    """화자간 발화 균형을 계산합니다."""
    if len(speaker_stats) != 2:
        return {"balanced": False, "reason": "화자가 2명이 아닙니다."}
    
    speakers = list(speaker_stats.keys())
    time_percentages = [speaker_stats[speaker]["time_percentage"] for speaker in speakers]
    word_percentages = [speaker_stats[speaker]["word_percentage"] for speaker in speakers]
    
    # 균형 계산 (50:50에서 얼마나 벗어났는지)
    time_imbalance = abs(time_percentages[0] - 50)
    word_imbalance = abs(word_percentages[0] - 50)
    
    # 불균형 정도 평가
    balance_score = 100 - max(time_imbalance, word_imbalance)
    
    if balance_score >= 80:
        balance_level = "매우 균형적"
    elif balance_score >= 60:
        balance_level = "균형적"
    elif balance_score >= 40:
        balance_level = "약간 불균형"
    else:
        balance_level = "매우 불균형"
    
    dominant_speaker = speakers[0] if time_percentages[0] > time_percentages[1] else speakers[1]
    
    return {
        "balanced": balance_score >= 60,
        "balance_score": balance_score,
        "balance_level": balance_level,
        "time_imbalance": time_imbalance,
        "word_imbalance": word_imbalance,
        "dominant_speaker": dominant_speaker,
        "time_distribution": dict(zip(speakers, time_percentages)),
        "word_distribution": dict(zip(speakers, word_percentages))
    }


def generate_conversation_id(transcript: str) -> str:
    """대화 내용을 바탕으로 고유 ID를 생성합니다."""
    content_hash = hashlib.md5(transcript.encode()).hexdigest()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"conv_{timestamp}_{content_hash[:8]}"


def save_analysis_result(result: Dict[str, Any], conversation_id: str) -> str:
    """분석 결과를 파일로 저장합니다."""
    try:
        # 저장 경로 생성
        save_dir = os.path.join("data", "analysis_results")
        os.makedirs(save_dir, exist_ok=True)
        
        # 파일명 생성
        filename = f"{conversation_id}.json"
        filepath = os.path.join(save_dir, filename)
        
        # 메타데이터 추가
        result["metadata"] = {
            "conversation_id": conversation_id,
            "saved_at": datetime.now().isoformat(),
            "version": "1.0"
        }
        
        # JSON 파일로 저장
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        return filepath
        
    except Exception as e:
        print(f"분석 결과 저장 중 오류: {str(e)}")
        return None


def load_analysis_result(conversation_id: str) -> Optional[Dict[str, Any]]:
    """저장된 분석 결과를 불러옵니다."""
    try:
        filepath = os.path.join("data", "analysis_results", f"{conversation_id}.json")
        
        if not os.path.exists(filepath):
            return None
        
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
            
    except Exception as e:
        print(f"분석 결과 로드 중 오류: {str(e)}")
        return None


def create_segments_dataframe(segments: List[Dict[str, Any]]) -> pd.DataFrame:
    """발화 구간을 DataFrame으로 변환합니다."""
    if not segments:
        return pd.DataFrame()
    
    df = pd.DataFrame(segments)
    
    # 시간 형식 변환
    if 'start_time' in df.columns:
        df['start_time_formatted'] = df['start_time'].apply(format_duration)
    if 'end_time' in df.columns:
        df['end_time_formatted'] = df['end_time'].apply(format_duration)
    
    # 발화 길이 계산
    if 'start_time' in df.columns and 'end_time' in df.columns:
        df['duration'] = df['end_time'] - df['start_time']
        df['duration_formatted'] = df['duration'].apply(format_duration)
    
    return df


def get_conversation_insights(segments: List[Dict[str, Any]]) -> Dict[str, Any]:
    """대화에서 기본적인 인사이트를 추출합니다."""
    if not segments:
        return {}
    
    df = create_segments_dataframe(segments)
    
    insights = {
        "total_segments": len(segments),
        "total_duration": sum(seg.get('end_time', 0) - seg.get('start_time', 0) for seg in segments),
        "total_words": sum(seg.get('words', 0) for seg in segments),
        "average_segment_duration": df['duration'].mean() if 'duration' in df.columns else 0,
        "average_words_per_segment": df['words'].mean() if 'words' in df.columns else 0,
        "confidence_scores": {
            "average": df['confidence'].mean() if 'confidence' in df.columns else 0,
            "min": df['confidence'].min() if 'confidence' in df.columns else 0,
            "max": df['confidence'].max() if 'confidence' in df.columns else 0
        }
    }
    
    # 화자별 통계
    if 'speaker' in df.columns:
        speaker_insights = df.groupby('speaker').agg({
            'words': ['sum', 'mean'],
            'duration': ['sum', 'mean'],
            'confidence': 'mean'
        }).round(2)
        
        insights["speaker_breakdown"] = speaker_insights.to_dict()
    
    return insights


def format_analysis_for_display(analysis: Dict[str, Any]) -> str:
    """분석 결과를 표시용 텍스트로 포맷합니다."""
    if not analysis.get("success"):
        return f"❌ 분석 실패: {analysis.get('error', '알 수 없는 오류')}"
    
    formatted_text = ""
    
    # 분석 내용 포맷
    if "analysis" in analysis:
        formatted_text += analysis["analysis"]
    elif "feedback" in analysis:
        formatted_text += analysis["feedback"]
    elif "development_analysis" in analysis:
        formatted_text += analysis["development_analysis"]
    elif "coaching_tips" in analysis:
        formatted_text += analysis["coaching_tips"]
    elif "sentiment_interpretation" in analysis:
        formatted_text += analysis["sentiment_interpretation"]
    
    # 메타데이터 추가
    if "processed_at" in analysis:
        processed_time = datetime.fromisoformat(analysis["processed_at"].replace('Z', '+00:00'))
        formatted_text += f"\n\n---\n*분석 완료: {processed_time.strftime('%Y-%m-%d %H:%M:%S')}*"
    
    if "model_used" in analysis:
        formatted_text += f" | *모델: {analysis['model_used']}*"
    
    return formatted_text


def create_mobile_layout_config(screen_width: int = 768) -> Dict[str, Any]:
    """모바일 화면 크기에 따른 레이아웃 설정을 생성합니다."""
    if screen_width < 480:  # 작은 모바일
        return {
            "columns": [1],  # 단일 컬럼
            "sidebar_width": 0,  # 사이드바 비활성화
            "font_size": "small",
            "chart_height": 300,
            "max_items_per_page": 5
        }
    elif screen_width < 768:  # 일반 모바일
        return {
            "columns": [1],
            "sidebar_width": 0,
            "font_size": "medium", 
            "chart_height": 400,
            "max_items_per_page": 8
        }
    elif screen_width < 1024:  # 태블릿
        return {
            "columns": [1, 1],  # 2컬럼
            "sidebar_width": 250,
            "font_size": "medium",
            "chart_height": 450,
            "max_items_per_page": 10
        }
    else:  # 데스크톱
        return {
            "columns": [1, 2, 1],  # 3컬럼
            "sidebar_width": 300,
            "font_size": "large",
            "chart_height": 500,
            "max_items_per_page": 15
        }


def sanitize_filename(filename: str) -> str:
    """파일명을 안전하게 정리합니다."""
    import re
    # 위험한 문자들 제거
    safe_filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
    # 길이 제한 (100자)
    if len(safe_filename) > 100:
        name, ext = os.path.splitext(safe_filename)
        safe_filename = name[:100-len(ext)] + ext
    
    return safe_filename


def get_file_info(filepath: str) -> Dict[str, Any]:
    """파일 정보를 가져옵니다."""
    try:
        stat = os.stat(filepath)
        return {
            "exists": True,
            "size": stat.st_size,
            "size_mb": round(stat.st_size / (1024 * 1024), 2),
            "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
            "created": datetime.fromtimestamp(stat.st_ctime).isoformat()
        }
    except (OSError, FileNotFoundError):
        return {"exists": False}


def estimate_processing_time(file_size_mb: float) -> int:
    """파일 크기를 바탕으로 처리 시간을 추정합니다 (초 단위)."""
    # 대략적인 추정: 1MB당 10초
    base_time = max(10, file_size_mb * 10)
    return int(base_time)


def extract_audio_duration(uploaded_file) -> Optional[float]:
    """
    업로드된 오디오 파일에서 길이 정보를 빠르게 추출합니다.
    
    Args:
        uploaded_file: Streamlit UploadedFile 객체
        
    Returns:
        Optional[float]: 오디오 길이 (초 단위), 실패시 None
    """
    try:
        # 파일 포인터를 처음으로 이동
        uploaded_file.seek(0)
        
        # 파일 데이터를 메모리에서 처리
        file_data = uploaded_file.read()
        
        # 파일 포인터를 다시 처음으로 리셋 (다른 함수에서 사용할 수 있도록)
        uploaded_file.seek(0)
        
        # BytesIO 객체로 변환하여 mutagen에서 처리 가능하게 함
        audio_file = io.BytesIO(file_data)
        
        # mutagen을 사용해 메타데이터 읽기
        audio_info = File(audio_file)
        
        if audio_info is not None and hasattr(audio_info, 'info') and hasattr(audio_info.info, 'length'):
            return float(audio_info.info.length)
        
        return None
        
    except Exception as e:
        print(f"오디오 길이 추출 실패: {str(e)}")
        return None


def format_audio_duration_to_time(duration_seconds: float) -> str:
    """
    오디오 길이(초)를 시:분:초 형식으로 변환합니다.
    
    Args:
        duration_seconds: 길이 (초)
        
    Returns:
        str: HH:MM:SS 형식의 시간
    """
    if duration_seconds <= 0:
        return "00:00:00"
    
    hours = int(duration_seconds // 3600)
    minutes = int((duration_seconds % 3600) // 60)
    seconds = int(duration_seconds % 60)
    
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"