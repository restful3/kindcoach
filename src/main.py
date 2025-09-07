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
from src.utils import (
    load_environment, validate_audio_file, format_duration,
    calculate_speaking_balance, generate_conversation_id,
    save_analysis_result, format_analysis_for_display,
    create_mobile_layout_config, estimate_processing_time
)


class KindCoachApp:
    def __init__(self):
        """KindCoach 애플리케이션 초기화"""
        self.setup_page_config()
        self.load_custom_css()
        self.initialize_session_state()
        
        try:
            self.env_vars = load_environment()
            self.audio_processor = AudioProcessor(self.env_vars["assemblyai_key"])
            self.ai_analyzer = AIAnalyzer(self.env_vars["openai_key"])
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
                    # 파일 정보 표시
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
                    
                    # 분석 시작 버튼
                    if st.button("🚀 분석 시작", type="primary", use_container_width=True):
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
            
            # 결과 저장
            conversation_id = generate_conversation_id(transcription_result["transcript"])
            
            complete_results = {
                "conversation_id": conversation_id,
                "transcription": transcription_result,
                "teacher_child_analysis": teacher_child_analysis,
                "ai_analysis": ai_analysis,
                "processed_at": datetime.now().isoformat()
            }
            
            # 세션에 저장
            st.session_state.analysis_results = complete_results
            st.session_state.current_conversation_id = conversation_id
            
            # 파일로 저장
            save_analysis_result(complete_results, conversation_id)
            
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
        
        # 빠른 피드백
        if st.button("⚡ 빠른 피드백 보기", use_container_width=True):
            quick_feedback = self.ai_analyzer.get_quick_feedback(transcription["transcript"])
            if quick_feedback["success"]:
                st.markdown("#### 💡 빠른 피드백")
                analysis_content = format_analysis_for_display(quick_feedback)
                st.markdown(f'<div class="ai-analysis-content">{analysis_content}</div>', unsafe_allow_html=True)
    
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
        if st.button("📥 전사본 다운로드", use_container_width=True):
            transcript_text = transcription["transcript"]
            st.download_button(
                label="💾 텍스트 파일로 다운로드",
                data=transcript_text,
                file_name=f"transcript_{st.session_state.current_conversation_id}.txt",
                mime="text/plain",
                use_container_width=True
            )
    
    def render_ai_analysis_tab(self, results):
        """AI 분석 탭 렌더링"""
        st.markdown("### 🤖 AI 코칭 분석")
        
        ai_analysis = results["ai_analysis"]
        
        if not ai_analysis.get("success"):
            st.error(f"AI 분석 실패: {ai_analysis.get('error', '알 수 없는 오류')}")
            return
        
        # 분석 결과 표시 (다크 테마 대응)
        analysis_content = format_analysis_for_display(ai_analysis)
        st.markdown(f'<div class="ai-analysis-content">{analysis_content}</div>', unsafe_allow_html=True)
        
        # 추가 분석 옵션
        st.markdown("#### 🔍 추가 분석")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("👶 아동 발달 분석", use_container_width=True):
                with st.spinner("아동 발달을 분석 중..."):
                    teacher_child = results["teacher_child_analysis"]
                    child_segments = [
                        seg for seg in results["transcription"]["speakers"]
                        if seg["speaker"] == teacher_child.get("child", "")
                    ]
                    
                    dev_analysis = self.ai_analyzer.analyze_child_development(
                        results["transcription"]["transcript"],
                        child_segments
                    )
                    
                    if dev_analysis["success"]:
                        with st.expander("👶 아동 발달 분석 결과", expanded=True):
                            analysis_content = format_analysis_for_display(dev_analysis)
                            st.markdown(f'<div class="ai-analysis-content">{analysis_content}</div>', unsafe_allow_html=True)
        
        with col2:
            if st.button("💡 상황별 코칭 팁", use_container_width=True):
                with st.spinner("코칭 팁을 생성 중..."):
                    coaching_tips = self.ai_analyzer.get_coaching_tips(
                        results["transcription"]["transcript"]
                    )
                    
                    if coaching_tips["success"]:
                        with st.expander("💡 코칭 팁", expanded=True):
                            analysis_content = format_analysis_for_display(coaching_tips)
                            st.markdown(f'<div class="ai-analysis-content">{analysis_content}</div>', unsafe_allow_html=True)
    
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
            
            st.plotly_chart(fig, use_container_width=True)
        
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
            
            st.plotly_chart(fig, use_container_width=True)
        
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
        # 헤더 렌더링
        self.render_header()
        
        # 메인 컨테이너
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


def main():
    """메인 함수"""
    app = KindCoachApp()
    app.run()


if __name__ == "__main__":
    main()