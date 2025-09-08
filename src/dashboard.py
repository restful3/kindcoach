"""
KindCoach 개인 대시보드
사용자별 분석 통계 및 인사이트 제공
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from typing import Dict, List, Any
from collections import Counter, defaultdict


def render_personal_dashboard(analysis_manager, username: str):
    """
    개인 대시보드를 렌더링합니다.
    
    Args:
        analysis_manager: AnalysisManager 인스턴스
        username: 현재 사용자명
    """
    st.markdown("# 📊 개인 대시보드")
    st.markdown(f"**👤 {username}**님의 분석 활동 현황")
    st.markdown("---")
    
    # 사용자 분석 데이터 가져오기
    user_analyses = analysis_manager.get_all_analyses(username=username)
    
    if not user_analyses:
        st.info("""
        📝 아직 분석 데이터가 없습니다.
        
        음성 파일을 업로드하고 분석을 시작해보세요!
        대시보드에서 다음과 같은 정보를 확인할 수 있습니다:
        - 📈 분석 활동 통계
        - 👶 아동별 분석 현황  
        - 📅 시간대별 분석 패턴
        - 🎯 분석 목적별 분류
        """)
        return
    
    # 대시보드 탭 구성
    tab1, tab2, tab3, tab4 = st.tabs(["📈 활동 개요", "👶 아동별 현황", "📅 시간 분석", "🎯 목적별 분석"])
    
    with tab1:
        render_activity_overview(user_analyses)
    
    with tab2:
        render_child_analysis(user_analyses)
    
    with tab3:
        render_time_analysis(user_analyses)
    
    with tab4:
        render_purpose_analysis(user_analyses)


def render_activity_overview(analyses: List[Dict[str, Any]]):
    """활동 개요 탭 렌더링"""
    st.markdown("### 📈 분석 활동 개요")
    
    # 기본 통계
    total_analyses = len(analyses)
    completed_analyses = sum(1 for a in analyses if a.get('completed_analyses', 0) == a.get('total_analyses', 5))
    
    # 최근 30일 분석
    now = datetime.now()
    recent_analyses = []
    for analysis in analyses:
        created_at = analysis.get('created_at', '')
        if created_at:
            try:
                created_date = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                if (now - created_date).days <= 30:
                    recent_analyses.append(analysis)
            except:
                continue
    
    # 메트릭 카드
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="📋 총 분석 수",
            value=total_analyses,
            help="지금까지 수행한 전체 분석 건수"
        )
    
    with col2:
        st.metric(
            label="✅ 완료된 분석",
            value=completed_analyses,
            help="모든 분석 유형이 완료된 건수"
        )
    
    with col3:
        completion_rate = (completed_analyses / total_analyses * 100) if total_analyses > 0 else 0
        st.metric(
            label="🎯 완료율",
            value=f"{completion_rate:.1f}%",
            help="전체 분석 중 완료된 비율"
        )
    
    with col4:
        st.metric(
            label="📅 최근 30일",
            value=len(recent_analyses),
            help="지난 30일간 수행한 분석 건수"
        )
    
    st.markdown("---")
    
    # 월별 분석 추이
    if len(analyses) > 1:
        st.markdown("### 📅 월별 분석 추이")
        
        # 월별 데이터 집계
        monthly_data = defaultdict(int)
        for analysis in analyses:
            created_at = analysis.get('created_at', '')
            if created_at:
                try:
                    created_date = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                    month_key = created_date.strftime('%Y-%m')
                    monthly_data[month_key] += 1
                except:
                    continue
        
        if monthly_data:
            # 데이터프레임 생성
            df_monthly = pd.DataFrame([
                {'월': month, '분석 수': count}
                for month, count in sorted(monthly_data.items())
            ])
            
            # 차트 생성
            fig = px.line(
                df_monthly, 
                x='월', 
                y='분석 수',
                title="월별 분석 활동 추이",
                markers=True
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig)


def render_child_analysis(analyses: List[Dict[str, Any]]):
    """아동별 현황 탭 렌더링"""
    st.markdown("### 👶 아동별 분석 현황")
    
    # 아동별 분석 집계
    child_stats = defaultdict(lambda: {
        'count': 0,
        'situations': set(),
        'purposes': set(),
        'latest_date': None,
        'ages': set()
    })
    
    for analysis in analyses:
        metadata = analysis.get('metadata', {})
        child_name = metadata.get('child_name', '알 수 없음')
        child_age = metadata.get('child_age', '')
        situation = metadata.get('situation_type', '')
        purposes = metadata.get('analysis_purpose', [])
        created_at = analysis.get('created_at', '')
        
        child_stats[child_name]['count'] += 1
        if situation:
            child_stats[child_name]['situations'].add(situation)
        if purposes:
            child_stats[child_name]['purposes'].update(purposes)
        if child_age:
            child_stats[child_name]['ages'].add(child_age)
        
        if created_at:
            try:
                date = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                if (child_stats[child_name]['latest_date'] is None or 
                    date > child_stats[child_name]['latest_date']):
                    child_stats[child_name]['latest_date'] = date
            except:
                continue
    
    if not child_stats:
        st.info("아직 아동별 데이터가 없습니다.")
        return
    
    # 아동별 분석 수 차트
    child_names = list(child_stats.keys())
    child_counts = [child_stats[name]['count'] for name in child_names]
    
    fig = px.bar(
        x=child_names,
        y=child_counts,
        title="아동별 분석 건수",
        labels={'x': '아동명', 'y': '분석 수'}
    )
    fig.update_layout(height=400)
    st.plotly_chart(fig)
    
    # 아동별 상세 정보
    st.markdown("### 👶 아동별 상세 정보")
    
    for child_name, stats in child_stats.items():
        with st.expander(f"👶 {child_name} ({stats['count']}회 분석)", expanded=False):
            col1, col2 = st.columns(2)
            
            with col1:
                if stats['ages']:
                    st.markdown(f"**🎂 나이**: {', '.join(stats['ages'])}")
                
                st.markdown(f"**📊 분석 횟수**: {stats['count']}회")
                
                if stats['latest_date']:
                    latest_str = stats['latest_date'].strftime('%Y-%m-%d %H:%M')
                    st.markdown(f"**📅 최근 분석**: {latest_str}")
            
            with col2:
                if stats['situations']:
                    situations_list = list(stats['situations'])
                    st.markdown(f"**📍 상황 유형**: {', '.join(situations_list)}")
                
                if stats['purposes']:
                    purposes_list = list(stats['purposes'])
                    st.markdown(f"**🎯 분석 목적**: {', '.join(purposes_list[:3])}{'...' if len(purposes_list) > 3 else ''}")
            
            # 빠른 액션 버튼들
            col1, col2 = st.columns(2)
            with col1:
                if st.button(f"📊 분석 보기", key=f"view_{child_name}_{stats['count']}", width='stretch'):
                    st.info(f"'{child_name}' 아동의 분석 내역을 분석 히스토리에서 확인하세요.")
            
            with col2:
                if st.button(f"🗑️ 모든 기록 삭제", key=f"delete_all_{child_name}_{stats['count']}", 
                           width='stretch', type="secondary"):
                    st.warning(f"⚠️ '{child_name}' 아동의 모든 분석 기록을 삭제하시겠습니까? 이 작업은 되돌릴 수 없습니다!")
                    st.info("💡 개별 분석 삭제는 '분석 히스토리' 탭에서 가능합니다.")


def render_time_analysis(analyses: List[Dict[str, Any]]):
    """시간 분석 탭 렌더링"""
    st.markdown("### 📅 시간별 분석 패턴")
    
    # 시간별 데이터 수집
    time_data = {
        'hour': [],
        'weekday': [],
        'date': []
    }
    
    for analysis in analyses:
        metadata = analysis.get('metadata', {})
        recording_time = metadata.get('recording_time', '')
        recording_date = metadata.get('recording_date', '')
        
        if recording_time:
            try:
                time_obj = datetime.fromisoformat(recording_time.replace('Z', ''))
                time_data['hour'].append(time_obj.hour)
            except:
                continue
        
        if recording_date:
            try:
                date_obj = datetime.fromisoformat(recording_date).date()
                time_data['weekday'].append(date_obj.weekday())
                time_data['date'].append(date_obj)
            except:
                continue
    
    # 시간대별 분포
    if time_data['hour']:
        st.markdown("#### 🕐 시간대별 녹음 분포")
        hour_counts = Counter(time_data['hour'])
        
        # 24시간 데이터 준비 (0-23시)
        hour_labels = [f"{h:02d}:00" for h in range(24)]
        hour_values = [hour_counts.get(h, 0) for h in range(24)]
        
        fig = px.bar(
            x=hour_labels,
            y=hour_values,
            title="시간대별 녹음 빈도",
            labels={'x': '시간', 'y': '녹음 수'}
        )
        fig.update_layout(height=400)
        st.plotly_chart(fig)
    
    # 요일별 분포  
    if time_data['weekday']:
        st.markdown("#### 📅 요일별 녹음 분포")
        weekday_counts = Counter(time_data['weekday'])
        weekday_names = ['월요일', '화요일', '수요일', '목요일', '금요일', '토요일', '일요일']
        weekday_values = [weekday_counts.get(i, 0) for i in range(7)]
        
        fig = px.bar(
            x=weekday_names,
            y=weekday_values,
            title="요일별 녹음 빈도",
            labels={'x': '요일', 'y': '녹음 수'}
        )
        fig.update_layout(height=400)
        st.plotly_chart(fig)


def render_purpose_analysis(analyses: List[Dict[str, Any]]):
    """목적별 분석 탭 렌더링"""
    st.markdown("### 🎯 분석 목적별 현황")
    
    # 목적별 데이터 수집
    purpose_counts = Counter()
    situation_purpose = defaultdict(set)
    
    for analysis in analyses:
        metadata = analysis.get('metadata', {})
        purposes = metadata.get('analysis_purpose', [])
        situation = metadata.get('situation_type', '기타')
        
        for purpose in purposes:
            purpose_counts[purpose] += 1
            situation_purpose[situation].add(purpose)
    
    if not purpose_counts:
        st.info("분석 목적 데이터가 없습니다.")
        return
    
    # 분석 목적별 파이 차트
    st.markdown("#### 🎯 분석 목적 분포")
    
    labels = list(purpose_counts.keys())
    values = list(purpose_counts.values())
    
    fig = px.pie(
        values=values,
        names=labels,
        title="분석 목적별 비율"
    )
    fig.update_layout(height=500)
    st.plotly_chart(fig)
    
    # 상황별 목적 매트릭스
    st.markdown("#### 📍 상황별 분석 목적")
    
    if situation_purpose:
        # 매트릭스 데이터 준비
        situations = list(situation_purpose.keys())
        all_purposes = list(set().union(*situation_purpose.values()))
        
        matrix_data = []
        for situation in situations:
            for purpose in all_purposes:
                count = 1 if purpose in situation_purpose[situation] else 0
                matrix_data.append({
                    '상황': situation,
                    '분석목적': purpose,
                    '빈도': count
                })
        
        if matrix_data:
            df_matrix = pd.DataFrame(matrix_data)
            pivot_df = df_matrix.pivot(index='상황', columns='분석목적', values='빈도')
            
            fig = px.imshow(
                pivot_df,
                title="상황별 분석 목적 매트릭스",
                color_continuous_scale='Blues'
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig)
    
    # 목적별 상세 정보
    st.markdown("#### 📊 목적별 상세 통계")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**🔝 상위 분석 목적**")
        for i, (purpose, count) in enumerate(purpose_counts.most_common(5), 1):
            percentage = count / sum(purpose_counts.values()) * 100
            st.markdown(f"{i}. **{purpose}**: {count}회 ({percentage:.1f}%)")
    
    with col2:
        st.markdown("**📈 분석 목적 통계**")
        st.markdown(f"• 총 분석 목적 수: {len(purpose_counts)}개")
        st.markdown(f"• 평균 목적 수: {sum(purpose_counts.values()) / len(purpose_counts):.1f}회")
        st.markdown(f"• 가장 인기있는 목적: {purpose_counts.most_common(1)[0][0]}")