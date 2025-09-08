"""
KindCoach - AI 기반 유아교육 코칭 플랫폼
Streamlit 메인 애플리케이션 (모바일 최적화)
"""

import streamlit as st
import os
import sys
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from io import BytesIO
import json

# 프로젝트 루트 디렉터리를 Python 경로에 추가
current_dir = os.path.dirname(__file__)
project_root = os.path.dirname(current_dir)
sys.path.append(project_root)

from src.audio_processor import AudioProcessor
from src.ai_analyzer import AIAnalyzer
from src.auth import AuthManager, render_login_page, render_logout_button
from src.prompt_editor import PromptEditor
from src.analysis_manager import AnalysisManager
from src.metadata_form import render_metadata_form, display_metadata_summary
from src.dashboard import render_personal_dashboard
from src.utils import (
    load_environment, validate_audio_file, format_duration,
    calculate_speaking_balance, generate_conversation_id,
    save_analysis_result, format_analysis_for_display,
    create_mobile_layout_config, estimate_processing_time,
    extract_audio_duration, format_audio_duration_to_time
)


class KindCoachApp:
    def __init__(self):
        """KindCoach 애플리케이션 초기화"""
        self.setup_page_config()
        self.load_custom_css()
        self.initialize_session_state()
        
        try:
            self.env_vars = load_environment()
            self.auth_manager = AuthManager(
                self.env_vars["admin_username"], 
                self.env_vars["admin_password"]
            )
            self.audio_processor = AudioProcessor(self.env_vars["assemblyai_key"])
            self.ai_analyzer = AIAnalyzer(self.env_vars["openai_key"])
            self.prompt_editor = PromptEditor()
            self.analysis_manager = AnalysisManager()
        except ValueError as e:
            st.error(f"⚠️ 환경 설정 오류: {e}")
            st.info("💡 .env 파일에 API 키를 설정해주세요.")
            st.stop()
    
    def setup_page_config(self):
        """Streamlit 페이지 기본 설정"""
        st.set_page_config(
            page_title="🤖❤️ KindCoach",
            page_icon="❤️",
            layout="wide",
            initial_sidebar_state="collapsed",  # 모바일에서 사이드바 숨김
            menu_items={
                'Get Help': None,
                'Report a bug': None,
                'About': "KindCoach - AI 기반 유아교육 코칭 플랫폼"
            }
        )
    
    def load_custom_css(self):
        """모바일 최적화 CSS 적용 (다크 테마 지원)"""
        st.markdown("""
        <style>
        /* 다크/라이트 테마 감지 */
        [data-testid="stAppViewContainer"] {
            --text-color: var(--text-color-primary, #262730);
            --bg-color: var(--background-color-primary, #ffffff);
            --card-bg: var(--background-color-secondary, #f0f2f6);
        }
        
        @media (prefers-color-scheme: dark) {
            [data-testid="stAppViewContainer"] {
                --text-color: #fafafa;
                --bg-color: #0e1117;
                --card-bg: #262730;
            }
        }
        
        /* Streamlit 다크 테마 감지 */
        .stApp[data-theme="dark"] {
            --text-color: #fafafa;
            --bg-color: #0e1117;
            --card-bg: #262730;
        }
        
        .stApp[data-theme="light"] {
            --text-color: #262730;
            --bg-color: #ffffff;
            --card-bg: #f0f2f6;
        }
        
        /* 모바일 최적화 스타일 */
        .main-header {
            text-align: center;
            padding: 1rem 0;
            background: linear-gradient(90deg, #FF6B6B, #4ECDC4);
            -webkit-background-clip: text;
            background-clip: text;
            -webkit-text-fill-color: transparent;
            font-size: clamp(1.5rem, 5vw, 2.5rem);
            font-weight: bold;
            margin-bottom: 1rem;
        }
        
        .subtitle {
            text-align: center;
            color: var(--text-color);
            opacity: 0.7;
            font-size: clamp(0.9rem, 3vw, 1.1rem);
            margin-bottom: 2rem;
        }
        
        /* 카드 스타일 - 다크 테마 대응 */
        .info-card {
            background: var(--card-bg);
            color: var(--text-color);
            padding: 1.5rem;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            margin: 1rem 0;
            border-left: 4px solid #4ECDC4;
        }
        
        .metric-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white !important;
            padding: 1rem;
            border-radius: 10px;
            text-align: center;
            margin: 0.5rem 0;
        }
        
        .metric-card h4, .metric-card p {
            color: white !important;
        }
        
        .speaker-card {
            background: var(--card-bg);
            color: var(--text-color);
            padding: 1rem;
            border-radius: 8px;
            margin: 0.5rem 0;
            border-left: 3px solid #007bff;
        }
        
        .speaker-card h4, .speaker-card p {
            color: var(--text-color) !important;
        }
        
        /* 대화 전사본 스타일 - 다크 테마 대응 */
        .transcript-teacher {
            background: var(--card-bg);
            color: var(--text-color) !important;
            padding: 1rem;
            margin: 0.5rem 0;
            border-radius: 8px;
            border-left: 4px solid #2196f3;
        }
        
        .transcript-child {
            background: var(--card-bg);
            color: var(--text-color) !important;
            padding: 1rem;
            margin: 0.5rem 0;
            border-radius: 8px;
            border-left: 4px solid #9c27b0;
        }
        
        /* AI 분석 결과 텍스트 - 다크 테마 대응 */
        .ai-analysis-content {
            color: var(--text-color) !important;
            line-height: 1.6;
        }
        
        .ai-analysis-content h1,
        .ai-analysis-content h2,
        .ai-analysis-content h3,
        .ai-analysis-content h4,
        .ai-analysis-content p,
        .ai-analysis-content li,
        .ai-analysis-content span,
        .ai-analysis-content strong {
            color: var(--text-color) !important;
        }
        
        /* 모바일 반응형 */
        @media (max-width: 768px) {
            .stContainer > div {
                padding: 1rem !important;
            }
            
            .info-card {
                padding: 1rem;
                margin: 0.5rem 0;
            }
            
            .metric-card {
                padding: 0.8rem;
                font-size: 0.9rem;
            }
        }
        
        /* 업로드 영역 스타일 */
        .upload-area {
            border: 2px dashed #4ECDC4;
            border-radius: 10px;
            padding: 2rem;
            text-align: center;
            background: var(--card-bg);
            margin: 1rem 0;
        }
        
        /* 진행 상태 표시 */
        .status-processing {
            color: #ffa500 !important;
            font-weight: bold;
        }
        
        .status-success {
            color: #28a745 !important;
            font-weight: bold;
        }
        
        .status-error {
            color: #dc3545 !important;
            font-weight: bold;
        }
        
        /* Streamlit 기본 텍스트 색상 보정 */
        .stMarkdown, .stText {
            color: var(--text-color) !important;
        }
        
        /* 확장자(expander) 내부 텍스트 */
        .streamlit-expanderContent {
            color: var(--text-color) !important;
        }
        
        .streamlit-expanderContent p,
        .streamlit-expanderContent h1,
        .streamlit-expanderContent h2,
        .streamlit-expanderContent h3,
        .streamlit-expanderContent h4,
        .streamlit-expanderContent li {
            color: var(--text-color) !important;
        }
        </style>
        """, unsafe_allow_html=True)
    
    def initialize_session_state(self):
        """세션 상태 초기화"""
        if 'analysis_results' not in st.session_state:
            st.session_state.analysis_results = {}
        if 'current_conversation_id' not in st.session_state:
            st.session_state.current_conversation_id = None
        if 'processing_status' not in st.session_state:
            st.session_state.processing_status = None
    
    def render_header(self):
        """헤더 렌더링"""
        st.markdown('<h1 class="main-header">🤖❤️ KindCoach</h1>', unsafe_allow_html=True)
        st.markdown(
            '<p class="subtitle">AI 기반 유아교육 코칭 플랫폼<br>'
            '<em>모든 아이는 사랑받을 자격이 있습니다</em></p>', 
            unsafe_allow_html=True
        )
    
    def render_file_upload(self):
        """파일 업로드 섹션"""
        st.markdown("### 🎙️ 음성 파일 업로드")
        
        with st.container():
            uploaded_file = st.file_uploader(
                "교사-아동 대화 음성 파일을 업로드하세요",
                type=['wav', 'mp3', 'm4a', 'flac', 'ogg', 'wma', 'aac'],
                help="최대 50MB까지 지원됩니다. 좋은 품질의 분석을 위해 명료한 음성 파일을 업로드해주세요."
            )
            
            if uploaded_file is not None:
                validation = validate_audio_file(uploaded_file)
                
                if validation["valid"]:
                    # 오디오 길이 자동 추출
                    audio_duration = extract_audio_duration(uploaded_file)
                    
                    # 파일 정보 표시 (오디오 길이 포함)
                    if audio_duration is not None:
                        col1, col2, col3, col4 = st.columns(4)
                    else:
                        col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.markdown(f"""
                        <div class="metric-card">
                            <h4>📄 파일명</h4>
                            <p>{validation['filename']}</p>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with col2:
                        file_size_mb = validation['size'] / (1024 * 1024)
                        st.markdown(f"""
                        <div class="metric-card">
                            <h4>📊 크기</h4>
                            <p>{file_size_mb:.1f} MB</p>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with col3:
                        estimated_time = estimate_processing_time(file_size_mb)
                        st.markdown(f"""
                        <div class="metric-card">
                            <h4>⏱️ 예상 시간</h4>
                            <p>약 {estimated_time}초</p>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    # 오디오 길이가 추출되면 표시
                    if audio_duration is not None:
                        with col4:
                            duration_formatted = format_audio_duration_to_time(audio_duration)
                            st.markdown(f"""
                            <div class="metric-card">
                                <h4>🎵 오디오 길이</h4>
                                <p>{duration_formatted}</p>
                            </div>
                            """, unsafe_allow_html=True)
                        
                        st.success(f"✅ 오디오 길이가 자동으로 추출되었습니다: {duration_formatted}")
                    else:
                        st.warning("⚠️ 오디오 길이 자동 추출에 실패했습니다. 메타데이터에서 수동으로 입력하세요.")
                    
                    # 메타데이터 입력 폼 (오디오 길이 정보 전달)
                    st.markdown("---")
                    current_user = self.auth_manager.get_current_user()
                    metadata = render_metadata_form(current_user, audio_duration)
                    
                    # 메타데이터가 입력되면 세션에 저장하고 분석 시작
                    if metadata:
                        st.session_state.current_metadata = metadata
                        self.process_audio_file(uploaded_file)
                
                else:
                    st.error(f"❌ {validation['error']}")
        
        return uploaded_file
    
    def process_audio_file(self, uploaded_file):
        """오디오 파일 처리 및 분석"""
        # 진행 상황 표시
        progress_bar = st.progress(0)
        status_placeholder = st.empty()
        
        try:
            # 1단계: 음성 전사
            status_placeholder.markdown('<p class="status-processing">🎙️ 음성을 텍스트로 변환 중...</p>', unsafe_allow_html=True)
            progress_bar.progress(20)
            
            # 파일 포인터를 처음으로 리셋
            uploaded_file.seek(0)
            transcription_result = self.audio_processor.transcribe_audio(uploaded_file)
            
            if not transcription_result["success"]:
                st.error(f"음성 전사 실패: {transcription_result['error']}")
                return
            
            progress_bar.progress(60)
            
            # 2단계: 교사-아동 대화 분석
            status_placeholder.markdown('<p class="status-processing">👥 화자 구분 및 역할 분석 중...</p>', unsafe_allow_html=True)
            
            speaker_segments = transcription_result["speakers"]
            teacher_child_analysis = self.audio_processor.is_teacher_child_conversation(speaker_segments)
            
            if not teacher_child_analysis["is_teacher_child"]:
                st.warning(f"⚠️ {teacher_child_analysis['reason']}")
                return
            
            progress_bar.progress(80)
            
            # 3단계: AI 분석
            status_placeholder.markdown('<p class="status-processing">🤖 AI가 대화를 분석하고 코칭 피드백을 생성 중...</p>', unsafe_allow_html=True)
            
            ai_analysis = self.ai_analyzer.analyze_conversation(
                transcription_result["transcript"],
                speaker_segments,
                teacher_child_analysis,
                transcription_result.get("sentiment", [])
            )
            
            progress_bar.progress(100)
            status_placeholder.markdown('<p class="status-success">✅ 분석 완료!</p>', unsafe_allow_html=True)
            
            # 결과 저장 (새로운 AnalysisManager 사용)
            conversation_id = generate_conversation_id(transcription_result["transcript"])
            
            # 새 분석 세션 생성 (메타데이터 포함)
            current_user = self.auth_manager.get_current_user()
            metadata = st.session_state.get('current_metadata', {})
            
            analysis_data = self.analysis_manager.create_new_analysis(
                conversation_id, transcription_result, teacher_child_analysis,
                metadata=metadata, username=current_user
            )
            
            # 종합 분석 결과 저장
            self.analysis_manager.update_analysis_result(
                conversation_id, "comprehensive", ai_analysis
            )
            
            # 세션에 저장 (기존 호환성 유지)
            complete_results = {
                "conversation_id": conversation_id,
                "transcription": transcription_result,
                "teacher_child_analysis": teacher_child_analysis,
                "ai_analysis": ai_analysis,
                "processed_at": datetime.now().isoformat()
            }
            st.session_state.analysis_results = complete_results
            st.session_state.current_conversation_id = conversation_id
            st.session_state.analysis_data = analysis_data  # 새로운 분석 데이터
            
            # 결과 표시
            st.success("🎉 분석이 성공적으로 완료되었습니다!")
            
            # 진행 바와 상태 메시지 제거
            progress_bar.empty()
            status_placeholder.empty()
            
        except Exception as e:
            st.error(f"처리 중 오류 발생: {str(e)}")
            progress_bar.empty()
            status_placeholder.empty()
    
    def render_analysis_results(self):
        """분석 결과 표시"""
        if not st.session_state.analysis_results:
            st.info("📤 음성 파일을 업로드하고 분석을 시작해보세요!")
            return
        
        results = st.session_state.analysis_results
        
        # 탭으로 결과 구성 (모바일 친화적)
        tab1, tab2, tab3, tab4 = st.tabs(["📊 요약", "📝 전사", "🤖 AI 분석", "📈 통계"])
        
        with tab1:
            self.render_summary_tab(results)
        
        with tab2:
            self.render_transcript_tab(results)
        
        with tab3:
            self.render_ai_analysis_tab(results)
        
        with tab4:
            self.render_statistics_tab(results)
    
    def render_summary_tab(self, results):
        """요약 탭 렌더링"""
        st.markdown("### 📊 분석 요약")
        
        # 메타데이터 표시
        metadata = st.session_state.get('current_metadata')
        if metadata:
            display_metadata_summary(metadata)
            st.markdown("---")
        
        transcription = results["transcription"]
        teacher_child = results["teacher_child_analysis"]
        
        # 기본 정보 카드
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(f"""
            <div class="info-card">
                <h4>⏱️ 대화 시간</h4>
                <p>{format_duration(transcription.get('audio_duration', 0))}</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            total_words = sum(seg.get('words', 0) for seg in transcription.get('speakers', []))
            st.markdown(f"""
            <div class="info-card">
                <h4>💬 총 단어 수</h4>
                <p>{total_words}개</p>
            </div>
            """, unsafe_allow_html=True)
        
        # 화자별 정보
        if teacher_child.get("is_teacher_child"):
            st.markdown("#### 👥 화자 분석")
            
            teacher_stats = teacher_child.get("teacher_stats", {})
            child_stats = teacher_child.get("child_stats", {})
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown(f"""
                <div class="speaker-card">
                    <h4>👩‍🏫 교사</h4>
                    <p>발화 시간: {teacher_stats.get('time_percentage', 0):.1f}%</p>
                    <p>단어 비율: {teacher_stats.get('word_percentage', 0):.1f}%</p>
                    <p>평균 신뢰도: {teacher_stats.get('avg_confidence', 0):.2f}</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"""
                <div class="speaker-card">
                    <h4>👶 아동</h4>
                    <p>발화 시간: {child_stats.get('time_percentage', 0):.1f}%</p>
                    <p>단어 비율: {child_stats.get('word_percentage', 0):.1f}%</p>
                    <p>평균 신뢰도: {child_stats.get('avg_confidence', 0):.2f}</p>
                </div>
                """, unsafe_allow_html=True)
        
        # 분석 진행 상황
        conversation_id = results.get("conversation_id")
        if conversation_id:
            st.markdown("#### 📊 분석 진행 상황")
            status = self.analysis_manager.get_analysis_status(conversation_id)
            
            col1, col2 = st.columns(2)
            for i, (analysis_type, analysis_info) in enumerate(self.analysis_manager.get_analysis_types().items()):
                is_completed = status.get(analysis_type, False)
                
                target_col = col1 if i % 2 == 0 else col2
                with target_col:
                    status_icon = "✅" if is_completed else "⏳"
                    st.markdown(f"{status_icon} {analysis_info['icon']} {analysis_info['name']}")
            
            completed_count = sum(1 for completed in status.values() if completed)
            total_count = len(status)
            progress = completed_count / total_count if total_count > 0 else 0
            
            st.progress(progress)
            st.markdown(f"**완료된 분석**: {completed_count}/{total_count}개")
    
    def render_transcript_tab(self, results):
        """전사 탭 렌더링"""
        st.markdown("### 📝 대화 전사")
        
        transcription = results["transcription"]
        segments = transcription.get("speakers", [])
        
        if not segments:
            st.warning("전사된 내용이 없습니다.")
            return
        
        # 화자별 색상 매핑
        teacher_child = results["teacher_child_analysis"]
        teacher_name = teacher_child.get("teacher", "화자 A")
        child_name = teacher_child.get("child", "화자 B")
        
        st.markdown("#### 🎭 화자별 대화")
        
        for segment in segments:
            speaker = segment["speaker"]
            text = segment["text"]
            start_time = format_duration(segment.get("start_time", 0))
            confidence = segment.get("confidence", 0)
            
            # 화자에 따른 스타일링
            if speaker == teacher_name:
                icon = "👩‍🏫"
                css_class = "transcript-teacher"
            else:
                icon = "👶"
                css_class = "transcript-child"
            
            st.markdown(f"""
            <div class="{css_class}">
                <strong>{icon} {speaker}</strong> <small>({start_time}, 신뢰도: {confidence:.2f})</small><br>
                {text}
            </div>
            """, unsafe_allow_html=True)
        
        # 전체 전사본 다운로드
        if st.button("📥 전사본 다운로드", width='stretch'):
            transcript_text = transcription["transcript"]
            st.download_button(
                label="💾 텍스트 파일로 다운로드",
                data=transcript_text,
                file_name=f"transcript_{st.session_state.current_conversation_id}.txt",
                mime="text/plain",
                width='stretch'
            )
    
    def render_ai_analysis_tab(self, results):
        """AI 분석 탭 렌더링 - 분석 유형별 독립 탭"""
        st.markdown("### 🤖 AI 코칭 분석")
        
        conversation_id = results.get("conversation_id")
        if not conversation_id:
            st.error("대화 ID를 찾을 수 없습니다.")
            return
        
        # 분석 유형별 탭 생성
        analysis_types = self.analysis_manager.get_analysis_types()
        tab_names = [f"{info['icon']} {info['name']}" for info in analysis_types.values()]
        tabs = st.tabs(tab_names)
        
        analysis_type_keys = list(analysis_types.keys())
        
        for i, (tab, analysis_type) in enumerate(zip(tabs, analysis_type_keys)):
            with tab:
                self._render_single_analysis_tab(
                    conversation_id, analysis_type, analysis_types[analysis_type], results
                )
    
    def _render_single_analysis_tab(self, conversation_id: str, analysis_type: str, 
                                   analysis_info: dict, results: dict):
        """개별 분석 유형 탭 렌더링"""
        st.markdown(f"#### {analysis_info['icon']} {analysis_info['name']}")
        st.markdown(f"*{analysis_info['description']}*")
        
        # 분석 완료 상태 확인 (현재 사용자 정보 포함)
        current_user = self.auth_manager.get_current_user()
        is_completed = self.analysis_manager.is_analysis_completed(conversation_id, analysis_type, username=current_user)
        cached_result = self.analysis_manager.get_analysis_result(conversation_id, analysis_type, username=current_user)
        
        # 상태 표시
        if is_completed and cached_result:
            st.success("✅ 분석 완료 - 저장된 결과를 표시합니다")
        else:
            st.info("⏳ 아직 분석되지 않았습니다")
        
        col1, col2 = st.columns([3, 1])
        
        with col2:
            # 분석 실행/재실행 버튼
            if is_completed:
                button_text = "🔄 재분석"
                button_type = "secondary"
            else:
                button_text = "▶️ 분석 실행"
                button_type = "primary"
            
            if st.button(button_text, key=f"analyze_{analysis_type}", 
                        type=button_type, width='stretch'):
                self._execute_analysis(conversation_id, analysis_type, results)
                st.rerun()
        
        # 분석 결과 표시
        if is_completed and cached_result:
            with col1:
                st.markdown("**분석 완료 시간:** " + 
                          cached_result.get("processed_at", "N/A")[:19].replace("T", " "))
            
            # 결과 내용 표시
            if cached_result.get("success"):
                result_content = self._format_analysis_result(analysis_type, cached_result)
                if result_content:
                    st.markdown("---")
                    st.markdown(f'<div class="ai-analysis-content">{result_content}</div>', 
                              unsafe_allow_html=True)
            else:
                st.error(f"❌ 분석 실패: {cached_result.get('error', '알 수 없는 오류')}")
        elif not is_completed:
            st.markdown("위의 '분석 실행' 버튼을 클릭하여 분석을 시작하세요.")
    
    def _execute_analysis(self, conversation_id: str, analysis_type: str, results: dict):
        """특정 분석 유형을 실행합니다"""
        analysis_name = self.analysis_manager.get_analysis_types()[analysis_type]['name']
        
        with st.spinner(f"{analysis_name} 실행 중..."):
            try:
                st.info(f"🔄 {analysis_name}을 시작합니다...")
                result = None
                
                if analysis_type == "comprehensive":
                    # 종합 분석 (이미 완료된 상태이므로 기존 결과 사용)
                    result = results.get("ai_analysis")
                    if result:
                        st.info("📋 기존 종합 분석 결과를 사용합니다.")
                
                elif analysis_type == "quick_feedback":
                    st.info("⚡ 빠른 피드백을 생성하고 있습니다...")
                    transcript = results["transcription"]["transcript"]
                    if not transcript.strip():
                        raise ValueError("전사본이 비어있어 분석할 수 없습니다.")
                    result = self.ai_analyzer.get_quick_feedback(transcript)
                
                elif analysis_type == "child_development":
                    st.info("👶 아동 발달 분석을 수행하고 있습니다...")
                    teacher_child = results["teacher_child_analysis"]
                    
                    # 아동 화자 ID 확인 및 개선
                    child_speaker_id = teacher_child.get("child", "")
                    if not child_speaker_id:
                        # 대안: 가장 적게 말한 화자를 아동으로 추정
                        speakers = results["transcription"]["speakers"]
                        if speakers:
                            speaker_stats = {}
                            for seg in speakers:
                                speaker_id = seg["speaker"]
                                if speaker_id not in speaker_stats:
                                    speaker_stats[speaker_id] = {"time": 0, "words": 0}
                                speaker_stats[speaker_id]["time"] += seg.get("end_time", 0) - seg.get("start_time", 0)
                                speaker_stats[speaker_id]["words"] += len(seg["text"].split())
                            
                            # 가장 적게 말한 화자를 아동으로 추정
                            child_speaker_id = min(speaker_stats.keys(), 
                                                 key=lambda x: speaker_stats[x]["time"])
                            st.info(f"🔍 화자 {child_speaker_id}를 아동으로 추정하여 분석합니다.")
                    
                    child_segments = [
                        seg for seg in results["transcription"]["speakers"]
                        if seg["speaker"] == child_speaker_id
                    ]
                    
                    if not child_segments:
                        st.warning("⚠️ 아동 발화를 찾을 수 없어 전체 대화를 기준으로 분석합니다.")
                        child_segments = results["transcription"]["speakers"]
                    
                    result = self.ai_analyzer.analyze_child_development(
                        results["transcription"]["transcript"], child_segments
                    )
                
                elif analysis_type == "coaching_tips":
                    st.info("💡 코칭 팁을 생성하고 있습니다...")
                    # 메타데이터에서 상황 정보 가져오기
                    metadata = st.session_state.get('current_metadata', {})
                    situation = metadata.get('situation_type', "일반적인 교사-아동 상호작용")
                    
                    result = self.ai_analyzer.get_coaching_tips(
                        results["transcription"]["transcript"], situation
                    )
                
                elif analysis_type == "sentiment_interpretation":
                    st.info("😊 감정 분석 해석을 수행하고 있습니다...")
                    sentiment_data = results["transcription"].get("sentiment", [])
                    if not sentiment_data:
                        st.warning("⚠️ 감정 분석 데이터가 없어 기본 해석을 제공합니다.")
                        sentiment_data = []
                    
                    duration = results['transcription'].get('audio_duration', 0)
                    context = f"교사-아동 상호작용 ({duration}초)"
                    result = self.ai_analyzer.interpret_sentiment(sentiment_data, context)
                
                # 결과 처리
                if result and result.get("success"):
                    st.info("💾 분석 결과를 저장하고 있습니다...")
                    success = self.analysis_manager.update_analysis_result(
                        conversation_id, analysis_type, result
                    )
                    if success:
                        st.success(f"✅ {analysis_name}이 완료되고 저장되었습니다!")
                        # 세션 상태 업데이트로 UI 즉시 반영
                        if 'analysis_data' in st.session_state:
                            # 현재 세션의 분석 데이터도 업데이트
                            current_user = self.auth_manager.get_current_user()
                            updated_data = self.analysis_manager.load_analysis(conversation_id, username=current_user)
                            if updated_data:
                                st.session_state.analysis_data = updated_data
                    else:
                        st.error("❌ 분석 결과 저장에 실패했습니다.")
                elif result and not result.get("success"):
                    error_msg = result.get("error", "알 수 없는 오류")
                    st.error(f"❌ {analysis_name} 실행 실패: {error_msg}")
                else:
                    st.error(f"❌ {analysis_name}을 실행할 수 없습니다. 데이터를 확인해주세요.")
                    
            except Exception as e:
                st.error(f"❌ {analysis_name} 실행 중 오류 발생: {str(e)}")
                # 디버깅을 위한 상세 로그 (개발 환경에서만)
                import traceback
                st.error(f"상세 오류: {traceback.format_exc()}")
    
    def _format_analysis_result(self, analysis_type: str, result: dict) -> str:
        """분석 유형에 따라 결과를 포맷팅합니다"""
        if analysis_type == "comprehensive":
            return format_analysis_for_display(result)
        elif analysis_type == "quick_feedback":
            return format_analysis_for_display(result)
        elif analysis_type == "child_development":
            return format_analysis_for_display(result)
        elif analysis_type == "coaching_tips":
            return format_analysis_for_display(result)
        elif analysis_type == "sentiment_interpretation":
            return format_analysis_for_display(result)
        
        return "결과를 표시할 수 없습니다."
    
    def render_statistics_tab(self, results):
        """통계 탭 렌더링"""
        st.markdown("### 📈 대화 통계")
        
        transcription = results["transcription"]
        teacher_child = results["teacher_child_analysis"]
        segments = transcription.get("speakers", [])
        
        if not segments:
            st.warning("통계를 생성할 데이터가 없습니다.")
            return
        
        # 발화 시간 분포 차트
        if teacher_child.get("is_teacher_child"):
            teacher_stats = teacher_child.get("teacher_stats", {})
            child_stats = teacher_child.get("child_stats", {})
            
            # 파이 차트
            labels = ['교사', '아동']
            values = [
                teacher_stats.get('time_percentage', 0),
                child_stats.get('time_percentage', 0)
            ]
            colors = ['#2196f3', '#9c27b0']
            
            fig = go.Figure(data=[go.Pie(
                labels=labels,
                values=values,
                marker_colors=colors,
                textinfo='label+percent',
                textfont_size=12
            )])
            
            fig.update_layout(
                title="👥 발화 시간 비율",
                height=300,
                showlegend=True
            )
            
            st.plotly_chart(fig)
        
        # 발화 패턴 시각화
        if len(segments) > 1:
            df_segments = pd.DataFrame([
                {
                    'speaker': seg['speaker'],
                    'start_time': seg.get('start_time', 0),
                    'duration': seg.get('end_time', 0) - seg.get('start_time', 0),
                    'words': seg.get('words', 0)
                }
                for seg in segments
            ])
            
            # 시간별 발화 패턴
            fig = px.scatter(
                df_segments,
                x='start_time',
                y='speaker',
                size='duration',
                color='speaker',
                hover_data=['words'],
                title="📊 시간별 발화 패턴"
            )
            
            fig.update_layout(
                height=300,
                xaxis_title="시간 (초)",
                yaxis_title="화자"
            )
            
            st.plotly_chart(fig)
        
        # 통계 요약
        col1, col2, col3 = st.columns(3)
        
        with col1:
            avg_confidence = sum(seg.get('confidence', 0) for seg in segments) / len(segments) if segments else 0
            st.metric("🎯 평균 신뢰도", f"{avg_confidence:.2f}")
        
        with col2:
            total_utterances = len(segments)
            st.metric("💬 총 발화 횟수", total_utterances)
        
        with col3:
            if teacher_child.get("is_teacher_child"):
                balance = calculate_speaking_balance({
                    teacher_child.get("teacher", "교사"): teacher_child.get("teacher_stats", {}),
                    teacher_child.get("child", "아동"): teacher_child.get("child_stats", {})
                })
                st.metric("⚖️ 발화 균형", f"{balance.get('balance_score', 0):.0f}점")
    
    def render_sidebar(self):
        """사이드바 렌더링 (데스크톱용)"""
        with st.sidebar:
            st.markdown("### 🛠️ 설정")
            
            # 테마 선택 (향후 구현)
            st.selectbox("🎨 테마", ["기본", "다크", "컬러풀"], disabled=True)
            
            # 언어 선택 (향후 구현)
            st.selectbox("🌐 언어", ["한국어", "English"], disabled=True)
            
            st.markdown("---")
            
            st.markdown("### ℹ️ 도움말")
            
            with st.expander("📖 사용법"):
                st.markdown("""
                1. **음성 파일 업로드**: 교사와 아동의 대화가 담긴 음성 파일을 업로드하세요.
                2. **분석 시작**: '분석 시작' 버튼을 클릭하여 AI 분석을 진행하세요.
                3. **결과 확인**: 탭을 통해 전사본, AI 분석, 통계를 확인하세요.
                4. **추가 분석**: 아동 발달 분석이나 코칭 팁 등 추가 분석을 요청할 수 있습니다.
                """)
            
            with st.expander("🔧 지원 파일 형식"):
                st.markdown("""
                - WAV, MP3, M4A
                - FLAC, OGG, WMA, AAC
                - 최대 파일 크기: 50MB
                """)
            
            st.markdown("---")
            st.markdown(
                "Made with ❤️ by KindCoach Team\n\n"
                "© 2024 KindCoach. All rights reserved."
            )
    
    def run(self):
        """메인 애플리케이션 실행"""
        # 인증 확인
        if not self.auth_manager.is_authenticated():
            # 로그인 페이지 표시
            render_login_page(self.auth_manager)
            return
        
        # 세션 활동 시간 업데이트
        self.auth_manager.update_session()
        
        # 로그아웃 버튼 표시
        render_logout_button(self.auth_manager)
        
        # 헤더 렌더링
        self.render_header()
        
        # 메인 네비게이션 탭
        tab1, tab2, tab3, tab4 = st.tabs(["🎯 음성 분석", "📊 개인 대시보드", "📚 분석 히스토리", "🛠️ 프롬프트 관리"])
        
        with tab1:
            # 기존 메인 기능
            main_container = st.container()
            
            with main_container:
                # 파일 업로드
                uploaded_file = self.render_file_upload()
                
                # 구분선
                if uploaded_file or st.session_state.analysis_results:
                    st.markdown("---")
                
                # 분석 결과
                self.render_analysis_results()
            
            # 사이드바 (데스크톱에서만 표시)
            if st.session_state.get('screen_width', 1024) > 768:
                self.render_sidebar()
        
        with tab2:
            # 개인 대시보드
            current_user = self.auth_manager.get_current_user()
            render_personal_dashboard(self.analysis_manager, current_user)
        
        with tab3:
            # 분석 히스토리 페이지
            self.render_analysis_history()
        
        with tab4:
            # 프롬프트 관리 페이지
            self.prompt_editor.render_prompt_management_page()

    def render_analysis_history(self):
        """분석 히스토리 페이지 렌더링"""
        st.markdown("# 📚 분석 히스토리")
        st.markdown("---")
        
        # 안내 메시지
        st.info("""
        **분석 히스토리 관리**
        
        과거에 수행된 모든 분석 결과를 확인하고 관리할 수 있습니다.
        - 🔍 **검색**: 키워드로 분석 결과 검색
        - 📄 **불러오기**: 저장된 분석 결과 다시 보기
        - 🗑️ **삭제**: 불필요한 분석 결과 제거
        """)
        
        # 고급 검색 필터
        current_user = self.auth_manager.get_current_user()
        
        with st.expander("🔧 고급 검색 옵션", expanded=False):
            col1, col2 = st.columns(2)
            
            with col1:
                show_only_my_analyses = st.checkbox(
                    "내 분석만 보기", 
                    value=True,
                    help=f"'{current_user}'의 분석 결과만 표시합니다."
                )
                
                child_name_filter = st.text_input(
                    "👶 아동명 필터",
                    placeholder="예: 김민수",
                    key="child_name_filter"
                )
            
            with col2:
                situation_filter = st.selectbox(
                    "📍 상황 필터",
                    options=["전체", "자유놀이", "집단활동", "간식시간", "정리시간", 
                            "독서활동", "미술활동", "야외활동", "개별상담", "기타"],
                    key="situation_filter"
                )
                
                # 날짜 범위 필터
                date_col1, date_col2 = st.columns(2)
                with date_col1:
                    date_from = st.date_input("📅 시작일", value=None, key="date_from")
                with date_col2:
                    date_to = st.date_input("📅 종료일", value=None, key="date_to")
        
        # 기본 검색
        col1, col2 = st.columns([3, 1])
        with col1:
            search_keyword = st.text_input(
                "🔍 키워드 검색 (전사 내용, 아동명, 설명 등)",
                placeholder="예: 블록놀이, 인사, 칭찬 등...",
                key="history_search"
            )
        
        with col2:
            st.markdown("<div style='margin-top: 25px;'></div>", unsafe_allow_html=True)
            if st.button("🔍 검색", width='stretch'):
                st.rerun()
        
        # 분석 목록 가져오기
        username_filter = current_user if show_only_my_analyses else None
        
        if search_keyword or child_name_filter or situation_filter != "전체" or date_from or date_to:
            # 필터링된 검색
            all_analyses = self.analysis_manager.get_all_analyses(username=username_filter)
            
            # 추가 필터 적용
            filter_criteria = {}
            if search_keyword:
                filter_criteria['search_keyword'] = search_keyword
            if child_name_filter:
                filter_criteria['child_name'] = child_name_filter
            if situation_filter != "전체":
                filter_criteria['situation_type'] = situation_filter
            if date_from:
                filter_criteria['date_from'] = date_from.isoformat()
            if date_to:
                filter_criteria['date_to'] = date_to.isoformat()
            
            # 메타데이터 기반 필터링 적용
            from src.metadata_form import filter_analyses_by_metadata
            analyses = filter_analyses_by_metadata(all_analyses, filter_criteria)
            
            # 키워드 검색도 적용
            if search_keyword:
                analyses = self.analysis_manager.search_analyses(search_keyword)
                if username_filter:
                    analyses = [a for a in analyses if a.get('username') == username_filter]
                analyses = filter_analyses_by_metadata(analyses, filter_criteria)
            
            st.markdown(f"### 🔍 필터링된 결과 ({len(analyses)}개)")
        else:
            analyses = self.analysis_manager.get_all_analyses(username=username_filter)
            st.markdown(f"### 📋 분석 목록 ({len(analyses)}개)")
        
        if not analyses:
            if search_keyword:
                st.warning("🔍 검색 결과가 없습니다. 다른 키워드로 검색해보세요.")
            else:
                st.info("📝 아직 저장된 분석 결과가 없습니다. 음성 분석을 먼저 실행해주세요.")
            return
        
        # 분석 목록 표시
        for i, analysis in enumerate(analyses):
            metadata = analysis.get('metadata', {})
            child_name = metadata.get('child_name', '알 수 없음')
            situation = metadata.get('situation_type', '알 수 없음')
            
            # 제목에 메타데이터 정보 포함
            title = f"👶 {child_name} - {situation} ({analysis.get('created_at', 'N/A')[:19].replace('T', ' ')})"
            
            with st.expander(title, expanded=False):
                # 메타데이터 요약 표시
                if metadata:
                    from src.metadata_form import display_metadata_summary
                    display_metadata_summary(metadata)
                    st.markdown("---")
                
                col1, col2, col3 = st.columns([2, 1, 1])
                
                with col1:
                    st.markdown("**전사 미리보기:**")
                    st.markdown(f"_{analysis.get('transcript_preview', '미리보기 없음')}_")
                    
                    # 분석 완료 상태
                    completed = analysis.get('completed_analyses', 0)
                    total = analysis.get('total_analyses', 5)
                    progress = completed / total if total > 0 else 0
                    
                    st.markdown(f"**분석 진행도**: {completed}/{total}개 완료")
                    st.progress(progress)
                
                with col2:
                    st.markdown("**생성일시:**")
                    st.markdown(analysis.get('created_at', 'N/A')[:19].replace('T', ' '))
                    
                    st.markdown("**마지막 수정:**")
                    st.markdown(analysis.get('last_updated', 'N/A')[:19].replace('T', ' '))
                
                with col3:
                    # 불러오기 버튼
                    if st.button(
                        "📂 불러오기", 
                        key=f"load_{analysis['conversation_id']}",
                        width='stretch',
                        type="primary"
                    ):
                        self._load_analysis_from_history(analysis['conversation_id'])
                    
                    # 삭제 버튼 - 바로 실행
                    if st.button(
                        "🗑️ 삭제", 
                        key=f"delete_{analysis['conversation_id']}",
                        width='stretch',
                        type="secondary"
                    ):
                        # 즉시 삭제 실행
                        current_user = self.auth_manager.get_current_user()
                        success = self.analysis_manager.delete_analysis(analysis['conversation_id'], username=current_user)
                        
                        if success:
                            metadata = analysis.get('metadata', {})
                            child_name = metadata.get('child_name', '알 수 없음')
                            st.success(f"✅ **{child_name}**의 분석이 삭제되었습니다!")
                            
                            # 현재 세션 클리어 (삭제된 분석과 관련된 경우)
                            if (st.session_state.get('current_conversation_id') == analysis['conversation_id'] or
                                st.session_state.get('analysis_results', {}).get('conversation_id') == analysis['conversation_id']):
                                st.session_state.analysis_results = {}
                                st.session_state.current_conversation_id = None
                                if 'analysis_data' in st.session_state:
                                    del st.session_state.analysis_data
                                if 'current_metadata' in st.session_state:
                                    del st.session_state.current_metadata
                            
                            # 즉시 페이지 새로고침
                            st.rerun()
                        else:
                            st.error("❌ 삭제 실패: 파일을 찾을 수 없습니다.")
                
                # 분석 상태 상세 표시
                status = analysis.get('analysis_status', {})
                if status:
                    st.markdown("**분석 상태 상세:**")
                    status_cols = st.columns(len(status))
                    
                    analysis_types = self.analysis_manager.get_analysis_types()
                    for j, (analysis_type, is_completed) in enumerate(status.items()):
                        with status_cols[j]:
                            analysis_info = analysis_types.get(analysis_type, {})
                            icon = analysis_info.get('icon', '📋')
                            name = analysis_info.get('name', analysis_type)
                            status_icon = "✅" if is_completed else "⏳"
                            st.markdown(f"{status_icon} {icon}")
                            st.caption(name)
    
    def _load_analysis_from_history(self, conversation_id: str):
        """히스토리에서 분석 결과를 불러옵니다"""
        try:
            # 분석 데이터 로드
            analysis_data = self.analysis_manager.load_analysis(conversation_id)
            
            if not analysis_data:
                st.error("❌ 분석 데이터를 찾을 수 없습니다.")
                return
            
            # 세션 상태에 로드
            transcription = analysis_data.get("transcription", {})
            teacher_child_analysis = analysis_data.get("teacher_child_analysis", {})
            
            # 종합 분석 결과 가져오기 (기존 호환성)
            comprehensive_analysis = analysis_data.get("analyses", {}).get("comprehensive")
            
            if comprehensive_analysis:
                complete_results = {
                    "conversation_id": conversation_id,
                    "transcription": transcription,
                    "teacher_child_analysis": teacher_child_analysis,
                    "ai_analysis": comprehensive_analysis,
                    "processed_at": analysis_data.get("created_at")
                }
                
                st.session_state.analysis_results = complete_results
                st.session_state.current_conversation_id = conversation_id
                st.session_state.analysis_data = analysis_data
                
                st.success(f"✅ 분석 결과 '{conversation_id}'를 불러왔습니다!")
                st.info("💡 '🎯 음성 분석' 탭으로 이동하여 결과를 확인하세요.")
            else:
                st.warning("⚠️ 이 분석에는 종합 분석 결과가 없습니다.")
            
        except Exception as e:
            st.error(f"❌ 분석 결과 로드 실패: {str(e)}")
    


def main():
    """메인 함수"""
    app = KindCoachApp()
    app.run()


if __name__ == "__main__":
    main()