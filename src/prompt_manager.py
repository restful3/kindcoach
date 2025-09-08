"""
프롬프트 관리 시스템
도메인 전문가가 직접 프롬프트를 수정할 수 있도록 하는 관리 클래스
"""

import json
import os
import shutil
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path


class PromptManager:
    """AI 프롬프트를 동적으로 관리하는 클래스"""
    
    def __init__(self, prompts_file: str = "config/prompts.json", backup_dir: str = "config/backups"):
        """
        프롬프트 관리자 초기화
        
        Args:
            prompts_file: 프롬프트 JSON 파일 경로
            backup_dir: 백업 파일 저장 디렉터리
        """
        self.prompts_file = Path(prompts_file)
        self.backup_dir = Path(backup_dir)
        self.backup_dir.mkdir(exist_ok=True)
        
        # 프롬프트 파일이 없으면 기본 프롬프트로 초기화
        if not self.prompts_file.exists():
            self._initialize_default_prompts()
        
        self.prompts = self._load_prompts()
    
    def _initialize_default_prompts(self):
        """기본 프롬프트로 JSON 파일 초기화"""
        from config.prompts import (
            CONVERSATION_ANALYSIS_PROMPT,
            QUICK_FEEDBACK_PROMPT,
            CHILD_DEVELOPMENT_ANALYSIS_PROMPT,
            COACHING_TIPS_PROMPT,
            SENTIMENT_INTERPRETATION_PROMPT
        )
        
        default_prompts = {
            "conversation_analysis": {
                "name": "종합 대화 분석",
                "description": "교사-아동 대화의 전면적인 분석과 상세한 코칭 피드백을 제공합니다.",
                "template": CONVERSATION_ANALYSIS_PROMPT,
                "required_variables": ["transcript", "teacher_info", "child_info", "sentiment_analysis"],
                "last_modified": datetime.now().isoformat(),
                "modified_by": "system"
            },
            "quick_feedback": {
                "name": "빠른 피드백",
                "description": "즉석에서 핵심적인 피드백을 간단하게 제공합니다.",
                "template": QUICK_FEEDBACK_PROMPT,
                "required_variables": ["transcript"],
                "last_modified": datetime.now().isoformat(),
                "modified_by": "system"
            },
            "child_development": {
                "name": "아동 발달 분석",
                "description": "발달 심리학 관점에서 아동의 현재 상태를 전문적으로 분석합니다.",
                "template": CHILD_DEVELOPMENT_ANALYSIS_PROMPT,
                "required_variables": ["transcript", "child_utterances"],
                "last_modified": datetime.now().isoformat(),
                "modified_by": "system"
            },
            "coaching_tips": {
                "name": "코칭 팁",
                "description": "상황별 구체적인 교사 코칭 가이드와 실무 팁을 제공합니다.",
                "template": COACHING_TIPS_PROMPT,
                "required_variables": ["situation", "transcript"],
                "last_modified": datetime.now().isoformat(),
                "modified_by": "system"
            },
            "sentiment_interpretation": {
                "name": "감정 해석",
                "description": "감정 분석 결과를 교육적 관점에서 해석하고 활용 방안을 제시합니다.",
                "template": SENTIMENT_INTERPRETATION_PROMPT,
                "required_variables": ["sentiment_data", "context"],
                "last_modified": datetime.now().isoformat(),
                "modified_by": "system"
            }
        }
        
        self._save_prompts(default_prompts)
    
    def _load_prompts(self) -> Dict[str, Any]:
        """프롬프트 파일을 로드합니다."""
        try:
            with open(self.prompts_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"프롬프트 로드 실패: {e}")
            return {}
    
    def _save_prompts(self, prompts: Dict[str, Any]):
        """프롬프트를 파일에 저장합니다."""
        # 디렉터리가 없으면 생성
        self.prompts_file.parent.mkdir(exist_ok=True)
        
        try:
            with open(self.prompts_file, 'w', encoding='utf-8') as f:
                json.dump(prompts, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"프롬프트 저장 실패: {e}")
    
    def get_prompt(self, prompt_id: str) -> Optional[str]:
        """특정 프롬프트의 템플릿을 가져옵니다."""
        if prompt_id in self.prompts:
            return self.prompts[prompt_id]["template"]
        return None
    
    def get_prompt_info(self, prompt_id: str) -> Optional[Dict[str, Any]]:
        """특정 프롬프트의 전체 정보를 가져옵니다."""
        return self.prompts.get(prompt_id)
    
    def get_all_prompts(self) -> Dict[str, Any]:
        """모든 프롬프트 정보를 가져옵니다."""
        return self.prompts.copy()
    
    def update_prompt(self, prompt_id: str, new_template: str, modified_by: str = "admin") -> bool:
        """
        프롬프트를 업데이트합니다.
        
        Args:
            prompt_id: 프롬프트 ID
            new_template: 새로운 프롬프트 템플릿
            modified_by: 수정자 정보
            
        Returns:
            bool: 업데이트 성공 여부
        """
        if prompt_id not in self.prompts:
            return False
        
        # 백업 생성
        self._create_backup()
        
        # 프롬프트 업데이트
        self.prompts[prompt_id]["template"] = new_template
        self.prompts[prompt_id]["last_modified"] = datetime.now().isoformat()
        self.prompts[prompt_id]["modified_by"] = modified_by
        
        # 파일에 저장
        self._save_prompts(self.prompts)
        
        return True
    
    def validate_prompt(self, prompt_id: str, template: str) -> Dict[str, Any]:
        """
        프롬프트 템플릿의 유효성을 검증합니다.
        
        Returns:
            Dict: 검증 결과 (valid: bool, errors: List[str], warnings: List[str])
        """
        result = {"valid": True, "errors": [], "warnings": []}
        
        if prompt_id not in self.prompts:
            result["valid"] = False
            result["errors"].append(f"알 수 없는 프롬프트 ID: {prompt_id}")
            return result
        
        prompt_info = self.prompts[prompt_id]
        required_vars = prompt_info.get("required_variables", [])
        
        # 필수 변수 확인
        for var in required_vars:
            var_pattern = f"{{{var}}}"
            if var_pattern not in template:
                result["errors"].append(f"필수 변수 누락: {var_pattern}")
                result["valid"] = False
        
        # 템플릿 길이 확인 (대략적인 토큰 수 계산)
        estimated_tokens = len(template.split()) * 1.3  # 대략적인 토큰 추정
        if estimated_tokens > 3000:  # GPT-4o-mini 제한 고려
            result["warnings"].append(f"프롬프트가 너무 길 수 있습니다 (추정 토큰: {int(estimated_tokens)})")
        
        # 빈 템플릿 확인
        if not template.strip():
            result["valid"] = False
            result["errors"].append("템플릿이 비어있습니다.")
        
        return result
    
    def _create_backup(self):
        """현재 프롬프트 파일의 백업을 생성합니다."""
        if not self.prompts_file.exists():
            return
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_filename = f"prompts_backup_{timestamp}.json"
        backup_path = self.backup_dir / backup_filename
        
        try:
            shutil.copy2(self.prompts_file, backup_path)
            
            # 백업 파일이 너무 많으면 오래된 것 삭제 (최근 10개만 유지)
            self._cleanup_old_backups()
            
        except Exception as e:
            print(f"백업 생성 실패: {e}")
    
    def _cleanup_old_backups(self, keep_count: int = 10):
        """오래된 백업 파일들을 정리합니다."""
        try:
            backup_files = list(self.backup_dir.glob("prompts_backup_*.json"))
            backup_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
            
            # 오래된 백업 파일 삭제
            for old_backup in backup_files[keep_count:]:
                old_backup.unlink()
                
        except Exception as e:
            print(f"백업 정리 실패: {e}")
    
    def get_backup_list(self) -> List[Dict[str, Any]]:
        """사용 가능한 백업 파일 목록을 가져옵니다."""
        try:
            backup_files = list(self.backup_dir.glob("prompts_backup_*.json"))
            backup_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
            
            backups = []
            for backup_file in backup_files:
                stat = backup_file.stat()
                backups.append({
                    "filename": backup_file.name,
                    "path": str(backup_file),
                    "created": datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S"),
                    "size": stat.st_size
                })
            
            return backups
        except Exception as e:
            print(f"백업 목록 조회 실패: {e}")
            return []
    
    def restore_from_backup(self, backup_filename: str) -> bool:
        """백업 파일에서 프롬프트를 복원합니다."""
        backup_path = self.backup_dir / backup_filename
        
        if not backup_path.exists():
            return False
        
        try:
            # 현재 파일 백업 (복원 실패시를 대비)
            self._create_backup()
            
            # 백업 파일로 복원
            shutil.copy2(backup_path, self.prompts_file)
            
            # 메모리의 프롬프트도 다시 로드
            self.prompts = self._load_prompts()
            
            return True
            
        except Exception as e:
            print(f"백업 복원 실패: {e}")
            return False
    
    def reload_prompts(self):
        """프롬프트 파일을 다시 로드합니다."""
        self.prompts = self._load_prompts()