"""
프롬프트 편집을 위한 Streamlit UI 컴포넌트
도메인 전문가가 직접 프롬프트를 수정할 수 있는 인터페이스 제공
"""

import streamlit as st
import json
from datetime import datetime
from typing import Dict, Any, Optional
from src.prompt_manager import PromptManager


class PromptEditor:
    """프롬프트 편집 UI 클래스"""
    
    def __init__(self):
        """프롬프트 편집기 초기화"""
        if 'prompt_manager' not in st.session_state:
            st.session_state.prompt_manager = PromptManager()
        
        self.prompt_manager = st.session_state.prompt_manager
    
    def render_prompt_management_page(self):
        """프롬프트 관리 메인 페이지 렌더링"""
        st.markdown("# 🛠️ 프롬프트 관리")
        st.markdown("---")
        
        # 안내 메시지
        st.info("""
        **프롬프트 관리 시스템**
        
        이 도구를 통해 AI가 사용하는 프롬프트를 직접 수정할 수 있습니다.
        - 🎯 **실시간 편집**: 프롬프트 변경 후 즉시 적용
        - 🔄 **백업 & 복원**: 안전한 버전 관리
        - ✅ **검증 시스템**: 프롬프트 유효성 자동 확인
        """)
        
        # 탭 구성
        tab1, tab2, tab3 = st.tabs(["📝 프롬프트 편집", "🔄 백업 관리", "📊 사용 현황"])
        
        with tab1:
            self._render_prompt_editor_tab()
        
        with tab2:
            self._render_backup_management_tab()
        
        with tab3:
            self._render_usage_stats_tab()
    
    def _render_prompt_editor_tab(self):
        """프롬프트 편집 탭 렌더링"""
        st.markdown("### 📝 프롬프트 편집")
        
        # 프롬프트 선택
        prompts = self.prompt_manager.get_all_prompts()
        
        if not prompts:
            st.error("프롬프트 데이터를 로드할 수 없습니다.")
            return
        
        # 프롬프트 목록
        prompt_options = {}
        for prompt_id, prompt_info in prompts.items():
            display_name = f"{prompt_info['name']} ({prompt_id})"
            prompt_options[display_name] = prompt_id
        
        selected_display = st.selectbox(
            "편집할 프롬프트 선택:",
            options=list(prompt_options.keys()),
            key="prompt_selector"
        )
        
        if not selected_display:
            return
        
        selected_prompt_id = prompt_options[selected_display]
        prompt_info = prompts[selected_prompt_id]
        
        # 프롬프트 정보 표시
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(f"**이름:** {prompt_info['name']}")
            st.markdown(f"**설명:** {prompt_info['description']}")
        
        with col2:
            st.markdown(f"**마지막 수정:** {prompt_info.get('last_modified', 'N/A')}")
            st.markdown(f"**수정자:** {prompt_info.get('modified_by', 'N/A')}")
        
        # 필수 변수 표시
        if 'required_variables' in prompt_info:
            required_vars = prompt_info['required_variables']
            st.markdown("**필수 변수:**")
            for var in required_vars:
                st.code(f"{{{var}}}", language=None)
        
        st.markdown("---")
        
        # 프롬프트 편집기
        current_template = prompt_info['template']
        
        st.markdown("### ✏️ 프롬프트 편집")
        
        new_template = st.text_area(
            "프롬프트 템플릿:",
            value=current_template,
            height=400,
            key=f"editor_{selected_prompt_id}",
            help="프롬프트를 직접 편집하세요. 필수 변수들을 반드시 포함해야 합니다."
        )
        
        # 실시간 검증
        if new_template != current_template:
            validation_result = self.prompt_manager.validate_prompt(selected_prompt_id, new_template)
            
            if validation_result['valid']:
                st.success("✅ 프롬프트 형식이 올바릅니다.")
            else:
                st.error("❌ 프롬프트에 문제가 있습니다:")
                for error in validation_result['errors']:
                    st.error(f"• {error}")
            
            # 경고사항 표시
            for warning in validation_result.get('warnings', []):
                st.warning(f"⚠️ {warning}")
        
        # 저장 버튼
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("💾 변경사항 저장", type="primary", key=f"save_{selected_prompt_id}"):
                self._save_prompt_changes(selected_prompt_id, new_template)
        
        with col2:
            if st.button("🔄 원본으로 되돌리기", key=f"reset_{selected_prompt_id}"):
                st.rerun()
        
        with col3:
            if st.button("🧪 테스트 실행", key=f"test_{selected_prompt_id}"):
                self._test_prompt(selected_prompt_id, new_template)
    
    def _save_prompt_changes(self, prompt_id: str, new_template: str):
        """프롬프트 변경사항 저장"""
        try:
            # 검증 실행
            validation_result = self.prompt_manager.validate_prompt(prompt_id, new_template)
            
            if not validation_result['valid']:
                st.error("❌ 저장할 수 없습니다. 프롬프트를 확인해주세요.")
                for error in validation_result['errors']:
                    st.error(f"• {error}")
                return
            
            # 수정자 정보 가져오기
            current_user = st.session_state.get('username', 'admin')
            
            # 프롬프트 업데이트
            success = self.prompt_manager.update_prompt(
                prompt_id=prompt_id,
                new_template=new_template,
                modified_by=current_user
            )
            
            if success:
                st.success("✅ 프롬프트가 성공적으로 저장되었습니다!")
                st.info("💡 변경사항은 즉시 적용됩니다. 다음 분석부터 새로운 프롬프트가 사용됩니다.")
                
                # 세션 상태의 프롬프트 매니저 새로고침
                st.session_state.prompt_manager.reload_prompts()
                
                # 페이지 새로고침으로 변경사항 반영
                st.rerun()
            else:
                st.error("❌ 저장 중 오류가 발생했습니다.")
                
        except Exception as e:
            st.error(f"❌ 저장 실패: {str(e)}")
    
    def _test_prompt(self, prompt_id: str, template: str):
        """프롬프트 테스트 실행"""
        st.markdown("### 🧪 프롬프트 테스트")
        
        # 샘플 데이터 생성
        sample_data = self._get_sample_data(prompt_id)
        
        if not sample_data:
            st.warning("이 프롬프트는 테스트 데이터가 준비되지 않았습니다.")
            return
        
        try:
            # 템플릿에 샘플 데이터 적용
            formatted_prompt = template.format(**sample_data)
            
            st.markdown("**생성된 프롬프트:**")
            st.code(formatted_prompt, language=None)
            
            # 토큰 수 추정
            estimated_tokens = len(formatted_prompt.split()) * 1.3
            st.info(f"📊 추정 토큰 수: {int(estimated_tokens)}개")
            
            if estimated_tokens > 3000:
                st.warning("⚠️ 토큰 수가 많습니다. GPT-4o-mini 제한을 고려해주세요.")
            
        except KeyError as e:
            st.error(f"❌ 변수 오류: {str(e)} 변수를 찾을 수 없습니다.")
        except Exception as e:
            st.error(f"❌ 테스트 실패: {str(e)}")
    
    def _get_sample_data(self, prompt_id: str) -> Optional[Dict[str, Any]]:
        """프롬프트별 샘플 데이터 반환"""
        sample_data = {
            "conversation_analysis": {
                "transcript": "교사: 안녕하세요, 오늘 기분이 어때요?\\n아이: 좋아요! 블록 놀이 하고 싶어요.\\n교사: 그래요? 어떤 블록으로 뭘 만들고 싶나요?",
                "teacher_info": "발화 시간: 65%, 단어 수: 24개",
                "child_info": "발화 시간: 35%, 단어 수: 18개", 
                "sentiment_analysis": "전체적으로 긍정적인 감정 (0.8), 교사 중성적(0.1), 아동 매우 긍정적(0.9)"
            },
            "quick_feedback": {
                "transcript": "교사: 안녕하세요, 오늘 기분이 어때요?\\n아이: 좋아요! 블록 놀이 하고 싶어요.\\n교사: 그래요? 어떤 블록으로 뭘 만들고 싶나요?"
            },
            "child_development": {
                "transcript": "교사: 안녕하세요, 오늘 기분이 어때요?\\n아이: 좋아요! 블록 놀이 하고 싶어요.",
                "child_utterances": "[2.1s] 좋아요! 블록 놀이 하고 싶어요.\\n[5.3s] 큰 성 만들래요."
            },
            "coaching_tips": {
                "situation": "아이가 다른 친구와 장난감을 나누지 않으려고 할 때",
                "transcript": "교사: 친구와 함께 놀면 더 재미있을 거예요.\\n아이: 싫어요, 내 거예요!"
            },
            "sentiment_interpretation": {
                "sentiment_data": "긍정: 0.6, 중성: 0.3, 부정: 0.1",
                "context": "자유놀이 시간 중 교사-아동 상호작용"
            }
        }
        
        return sample_data.get(prompt_id)
    
    def _render_backup_management_tab(self):
        """백업 관리 탭 렌더링"""
        st.markdown("### 🔄 백업 관리")
        
        # 현재 백업 상태
        backups = self.prompt_manager.get_backup_list()
        
        if not backups:
            st.info("📁 백업 파일이 없습니다.")
            return
        
        st.markdown(f"**총 {len(backups)}개의 백업 파일이 있습니다.**")
        
        # 백업 목록 표시
        for i, backup in enumerate(backups):
            with st.expander(f"📄 {backup['filename']} - {backup['created']}"):
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.markdown(f"**생성일시:** {backup['created']}")
                
                with col2:
                    st.markdown(f"**파일크기:** {backup['size']:,} bytes")
                
                with col3:
                    if st.button(f"복원", key=f"restore_{i}"):
                        self._restore_backup(backup['filename'])
    
    def _restore_backup(self, backup_filename: str):
        """백업에서 복원"""
        try:
            success = self.prompt_manager.restore_from_backup(backup_filename)
            
            if success:
                st.success(f"✅ {backup_filename}에서 성공적으로 복원되었습니다!")
                # 세션 상태 새로고침
                st.session_state.prompt_manager.reload_prompts()
                st.rerun()
            else:
                st.error("❌ 복원에 실패했습니다.")
                
        except Exception as e:
            st.error(f"❌ 복원 실패: {str(e)}")
    
    def _render_usage_stats_tab(self):
        """사용 현황 탭 렌더링"""
        st.markdown("### 📊 프롬프트 사용 현황")
        
        prompts = self.prompt_manager.get_all_prompts()
        
        if not prompts:
            st.info("프롬프트 데이터가 없습니다.")
            return
        
        # 프롬프트별 정보 테이블
        prompt_data = []
        for prompt_id, info in prompts.items():
            template_length = len(info['template'])
            estimated_tokens = int(len(info['template'].split()) * 1.3)
            
            prompt_data.append({
                "프롬프트": info['name'],
                "ID": prompt_id,
                "길이": f"{template_length:,} 문자",
                "추정 토큰": f"{estimated_tokens:,}개",
                "마지막 수정": info.get('last_modified', 'N/A'),
                "수정자": info.get('modified_by', 'N/A')
            })
        
        # 데이터프레임으로 표시
        import pandas as pd
        df = pd.DataFrame(prompt_data)
        st.dataframe(df)
        
        # 통계 정보
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("총 프롬프트 수", len(prompts))
        
        with col2:
            total_chars = sum(len(info['template']) for info in prompts.values())
            st.metric("총 문자 수", f"{total_chars:,}")
        
        with col3:
            total_tokens = sum(int(len(info['template'].split()) * 1.3) for info in prompts.values())
            st.metric("총 추정 토큰", f"{total_tokens:,}")