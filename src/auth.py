"""
KindCoach 인증 모듈
로그인, 세션 관리, 보안 기능 제공
"""

import streamlit as st
import bcrypt
import time
from typing import Dict, Optional


class AuthManager:
    """인증 관리 클래스"""
    
    def __init__(self, admin_username: str, admin_password: str):
        """
        인증 관리자 초기화
        
        Args:
            admin_username: 관리자 사용자명
            admin_password: 관리자 비밀번호 (평문)
        """
        self.admin_username = admin_username
        self.admin_password_hash = self._hash_password(admin_password)
        
        # 세션 타임아웃 설정 (30분)
        self.session_timeout = 30 * 60  # seconds
        
    def _hash_password(self, password: str) -> str:
        """비밀번호를 해싱합니다."""
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')
    
    def _verify_password(self, password: str, hashed: str) -> bool:
        """비밀번호를 검증합니다."""
        return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
    
    def authenticate(self, username: str, password: str) -> bool:
        """
        사용자 인증을 수행합니다.
        
        Args:
            username: 사용자명
            password: 비밀번호
            
        Returns:
            bool: 인증 성공 여부
        """
        if username == self.admin_username:
            return self._verify_password(password, self.admin_password_hash)
        return False
    
    def login(self, username: str, password: str) -> bool:
        """
        로그인을 수행하고 세션을 설정합니다.
        
        Args:
            username: 사용자명  
            password: 비밀번호
            
        Returns:
            bool: 로그인 성공 여부
        """
        if self.authenticate(username, password):
            st.session_state.authenticated = True
            st.session_state.username = username
            st.session_state.login_time = time.time()
            return True
        return False
    
    def logout(self):
        """로그아웃을 수행하고 세션을 정리합니다."""
        if 'authenticated' in st.session_state:
            del st.session_state.authenticated
        if 'username' in st.session_state:
            del st.session_state.username
        if 'login_time' in st.session_state:
            del st.session_state.login_time
    
    def is_authenticated(self) -> bool:
        """
        현재 사용자의 인증 상태를 확인합니다.
        
        Returns:
            bool: 인증된 상태 여부
        """
        if not st.session_state.get('authenticated', False):
            return False
        
        # 세션 타임아웃 확인
        login_time = st.session_state.get('login_time', 0)
        if time.time() - login_time > self.session_timeout:
            self.logout()
            return False
        
        return True
    
    def get_current_user(self) -> Optional[str]:
        """
        현재 로그인한 사용자명을 반환합니다.
        
        Returns:
            Optional[str]: 사용자명 또는 None
        """
        if self.is_authenticated():
            return st.session_state.get('username')
        return None
    
    def update_session(self):
        """세션의 활동 시간을 갱신합니다."""
        if self.is_authenticated():
            st.session_state.login_time = time.time()


def render_login_page(auth_manager: AuthManager) -> bool:
    """
    로그인 페이지를 렌더링합니다.
    
    Args:
        auth_manager: 인증 관리자 인스턴스
        
    Returns:
        bool: 로그인 성공 여부
    """
    st.markdown('<div class="main-header">', unsafe_allow_html=True)
    st.title("🤖❤️ KindCoach")
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # 모바일 최적화된 로그인 폼
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("### 🔐 로그인")
        st.info("KindCoach에 접속하려면 로그인이 필요합니다.")
        
        with st.form("login_form", clear_on_submit=True):
            username = st.text_input(
                "👤 사용자명", 
                placeholder="사용자명을 입력하세요",
                key="login_username"
            )
            password = st.text_input(
                "🔑 비밀번호", 
                type="password",
                placeholder="비밀번호를 입력하세요",
                key="login_password"
            )
            
            # 모바일 친화적인 로그인 버튼
            login_button = st.form_submit_button(
                "🚀 로그인", 
                use_container_width=True,
                type="primary"
            )
            
            if login_button:
                if not username or not password:
                    st.error("🚫 사용자명과 비밀번호를 모두 입력해주세요.")
                    return False
                
                # 로그인 시도
                if auth_manager.login(username, password):
                    st.success("✅ 로그인 성공! 잠시만 기다려주세요...")
                    time.sleep(1)  # 성공 메시지를 보여주기 위한 잠시 대기
                    st.rerun()  # 페이지 새로고침
                    return True
                else:
                    st.error("❌ 잘못된 사용자명 또는 비밀번호입니다.")
                    return False
    
    # 하단 도움말
    st.markdown("---")
    with st.expander("💡 도움말"):
        st.markdown("""
        **KindCoach란?**
        - AI 기반 유아교육 코칭 플랫폼
        - 교사-아동 대화 분석 및 피드백 제공
        - 음성 인식 및 AI 분석 기술 활용
        
        **로그인 문제가 있으신가요?**
        - 관리자에게 문의해주세요
        - 올바른 사용자명과 비밀번호를 입력했는지 확인하세요
        """)
    
    return False


def render_logout_button(auth_manager: AuthManager):
    """
    로그아웃 버튼을 렌더링합니다.
    
    Args:
        auth_manager: 인증 관리자 인스턴스
    """
    current_user = auth_manager.get_current_user()
    
    if current_user:
        # 상단 우측에 사용자 정보와 로그아웃 버튼 표시
        col1, col2 = st.columns([4, 1])
        
        with col2:
            st.markdown(f"👤 **{current_user}**")
            if st.button("🚪 로그아웃", key="logout_button"):
                auth_manager.logout()
                st.success("👋 로그아웃되었습니다.")
                time.sleep(1)
                st.rerun()