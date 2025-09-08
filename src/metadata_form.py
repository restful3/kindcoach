"""
KindCoach 메타데이터 입력 폼
분석 의뢰 시 메타데이터를 수집하는 UI 컴포넌트
"""

import streamlit as st
from datetime import datetime, date, time
from typing import Dict, Any, Optional


def render_metadata_form(username: str, audio_duration_seconds: Optional[float] = None) -> Optional[Dict[str, Any]]:
    """
    메타데이터 입력 폼을 렌더링합니다.
    
    Args:
        username: 현재 로그인된 사용자명
        audio_duration_seconds: 오디오 파일의 길이 (초), 있으면 자동으로 시간 계산
        
    Returns:
        Optional[Dict[str, Any]]: 입력된 메타데이터 또는 None
    """
    st.markdown("### 📝 분석 정보 입력")
    st.info("분석 결과를 체계적으로 관리하기 위해 다음 정보를 입력해주세요.")
    
    with st.form("metadata_form", clear_on_submit=False):
        col1, col2 = st.columns(2)
        
        with col1:
            # 아동 정보
            child_name = st.text_input(
                "👶 아동명",
                placeholder="예: 김민수",
                help="분석 대상 아동의 이름을 입력하세요."
            )
            
            child_age = st.selectbox(
                "🎂 아동 나이",
                options=["", "만 3세", "만 4세", "만 5세", "만 6세", "기타"],
                help="아동의 나이를 선택하세요."
            )
            
            if child_age == "기타":
                child_age_custom = st.text_input("나이 직접 입력", placeholder="예: 만 3세 6개월")
                if child_age_custom:
                    child_age = child_age_custom
        
        with col2:
            # 녹취 정보
            recording_date = st.date_input(
                "📅 녹취 날짜",
                value=date.today(),
                help="대화가 녹음된 날짜를 선택하세요."
            )
            
            # 오디오 길이가 있으면 자동 계산된 시간 표시, 없으면 수동 입력
            if audio_duration_seconds is not None:
                # 오디오 길이를 시간 형식으로 변환
                hours = int(audio_duration_seconds // 3600)
                minutes = int((audio_duration_seconds % 3600) // 60)
                seconds = int(audio_duration_seconds % 60)
                
                # 자동 추출된 길이 표시
                st.markdown(f"**⏱️ 녹취 길이 (자동 추출):** {hours:02d}:{minutes:02d}:{seconds:02d}")
                st.caption("파일에서 자동으로 추출된 녹취 길이입니다.")
                
                # 세션에 녹취 시간 정보 저장 (메타데이터에 포함할 용도)
                recording_duration = audio_duration_seconds
                
                # 녹취 시작 시간 입력 (기본값: 오전 9시)
                recording_time = st.time_input(
                    "🕐 녹취 시작 시간",
                    value=time(9, 0),  # 기본값: 오전 9시
                    help="대화가 시작된 시간을 선택하세요. (녹취 길이는 자동으로 계산됩니다)"
                )
            else:
                # 기존 방식: 수동 시간 입력
                recording_time = st.time_input(
                    "🕐 녹취 시간",
                    value=time(9, 0),  # 기본값: 오전 9시
                    help="대화가 녹음된 시간을 선택하세요."
                )
                recording_duration = None  # 길이 정보 없음
        
        # 전체 폭 컨테이너
        st.markdown("---")
        
        # 상황 정보
        situation_type = st.selectbox(
            "📍 상황 유형",
            options=[
                "", 
                "자유놀이", 
                "집단활동", 
                "간식시간", 
                "정리시간", 
                "독서활동", 
                "미술활동", 
                "야외활동", 
                "개별상담", 
                "기타"
            ],
            help="대화가 이루어진 상황을 선택하세요."
        )
        
        if situation_type == "기타":
            situation_custom = st.text_input("상황 직접 입력", placeholder="예: 블록놀이 중")
            if situation_custom:
                situation_type = situation_custom
        
        # 설명
        description = st.text_area(
            "📝 추가 설명 (선택사항)",
            placeholder="예: 새 학기 적응 과정에서의 대화, 특별한 상황이나 배경 설명",
            height=80,
            help="이 분석과 관련된 추가 정보나 특별한 상황을 기록하세요."
        )
        
        # 분석 목적
        analysis_purpose = st.multiselect(
            "🎯 분석 목적",
            options=[
                "소통 기법 개선",
                "아동 발달 상태 파악",
                "감정 조절 지도",
                "언어 발달 지원",
                "행동 관찰 및 지도",
                "부모 상담 준비",
                "교육 계획 수립",
                "기타"
            ],
            help="이 분석을 통해 달성하고자 하는 목적을 선택하세요. (복수 선택 가능)"
        )
        
        # 제출 버튼
        submitted = st.form_submit_button(
            "✅ 메타데이터 저장 및 분석 시작",
            width='stretch',
            type="primary"
        )
        
        if submitted:
            # 필수 필드 검증
            if not child_name.strip():
                st.error("🚫 아동명을 입력해주세요.")
                return None
            
            if not child_age:
                st.error("🚫 아동 나이를 선택해주세요.")
                return None
            
            if not situation_type:
                st.error("🚫 상황 유형을 선택해주세요.")
                return None
            
            # 메타데이터 구성
            metadata = {
                "child_name": child_name.strip(),
                "child_age": child_age,
                "recording_date": recording_date.isoformat(),
                "recording_time": recording_time.isoformat(),
                "recording_datetime": datetime.combine(recording_date, recording_time).isoformat(),
                "recording_duration_seconds": recording_duration,  # 녹취 길이 (초)
                "situation_type": situation_type,
                "description": description.strip() if description else "",
                "analysis_purpose": analysis_purpose,
                "created_by": username,
                "created_at": datetime.now().isoformat()
            }
            
            # 녹취 길이가 있으면 종료 시간도 계산해서 저장
            if recording_duration is not None:
                from datetime import timedelta
                start_datetime = datetime.combine(recording_date, recording_time)
                end_datetime = start_datetime + timedelta(seconds=recording_duration)
                metadata["recording_end_time"] = end_datetime.time().isoformat()
                metadata["recording_end_datetime"] = end_datetime.isoformat()
            
            # 성공 메시지
            st.success("✅ 메타데이터가 저장되었습니다. 분석을 시작합니다!")
            
            return metadata
    
    return None


def display_metadata_summary(metadata: Dict[str, Any]) -> None:
    """
    입력된 메타데이터의 요약을 표시합니다.
    
    Args:
        metadata: 메타데이터 딕셔너리
    """
    if not metadata:
        return
    
    st.markdown("### 📋 분석 정보 요약")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"**👶 아동명:** {metadata.get('child_name', 'N/A')}")
        st.markdown(f"**🎂 나이:** {metadata.get('child_age', 'N/A')}")
        st.markdown(f"**📅 날짜:** {metadata.get('recording_date', 'N/A')}")
    
    with col2:
        st.markdown(f"**🕐 시작 시간:** {metadata.get('recording_time', 'N/A')}")
        
        # 녹취 길이 표시
        duration_seconds = metadata.get('recording_duration_seconds')
        if duration_seconds is not None:
            hours = int(duration_seconds // 3600)
            minutes = int((duration_seconds % 3600) // 60)
            seconds = int(duration_seconds % 60)
            st.markdown(f"**⏱️ 녹취 길이:** {hours:02d}:{minutes:02d}:{seconds:02d}")
            
            # 종료 시간도 있으면 표시
            if metadata.get('recording_end_time'):
                st.markdown(f"**🕐 종료 시간:** {metadata.get('recording_end_time', 'N/A')}")
        
        st.markdown(f"**📍 상황:** {metadata.get('situation_type', 'N/A')}")
        st.markdown(f"**👤 분석자:** {metadata.get('created_by', 'N/A')}")
    
    if metadata.get('analysis_purpose'):
        st.markdown(f"**🎯 목적:** {', '.join(metadata['analysis_purpose'])}")
    
    if metadata.get('description'):
        st.markdown(f"**📝 설명:** {metadata['description']}")


def get_metadata_display_name(metadata: Dict[str, Any]) -> str:
    """
    메타데이터를 기반으로 표시용 이름을 생성합니다.
    
    Args:
        metadata: 메타데이터 딕셔너리
        
    Returns:
        str: 표시용 이름
    """
    child_name = metadata.get('child_name', '익명')
    recording_date = metadata.get('recording_date', '')
    situation = metadata.get('situation_type', '')
    
    if recording_date and situation:
        return f"{child_name} - {situation} ({recording_date})"
    elif recording_date:
        return f"{child_name} ({recording_date})"
    else:
        return child_name


def filter_analyses_by_metadata(analyses: list, filter_criteria: Dict[str, Any]) -> list:
    """
    메타데이터 기준으로 분석 결과를 필터링합니다.
    
    Args:
        analyses: 분석 결과 목록
        filter_criteria: 필터링 조건
        
    Returns:
        list: 필터링된 분석 결과 목록
    """
    if not filter_criteria:
        return analyses
    
    filtered = []
    
    for analysis in analyses:
        metadata = analysis.get('metadata', {})
        
        # 사용자명 필터
        if filter_criteria.get('username'):
            if analysis.get('username') != filter_criteria['username']:
                continue
        
        # 아동명 필터
        if filter_criteria.get('child_name'):
            if filter_criteria['child_name'].lower() not in metadata.get('child_name', '').lower():
                continue
        
        # 상황 유형 필터
        if filter_criteria.get('situation_type'):
            if filter_criteria['situation_type'] != metadata.get('situation_type'):
                continue
        
        # 날짜 범위 필터
        if filter_criteria.get('date_from') or filter_criteria.get('date_to'):
            recording_date = metadata.get('recording_date')
            if recording_date:
                if filter_criteria.get('date_from') and recording_date < filter_criteria['date_from']:
                    continue
                if filter_criteria.get('date_to') and recording_date > filter_criteria['date_to']:
                    continue
        
        filtered.append(analysis)
    
    return filtered