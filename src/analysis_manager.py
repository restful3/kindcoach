"""
분석 결과 관리 시스템
모든 분석 유형의 결과를 저장, 로드, 관리하는 클래스
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path
import glob


class AnalysisManager:
    """분석 결과를 종합적으로 관리하는 클래스"""
    
    def __init__(self, results_dir: str = "data/analysis_results"):
        """
        분석 관리자 초기화
        
        Args:
            results_dir: 분석 결과 저장 디렉터리
        """
        self.results_dir = Path(results_dir)
        self.results_dir.mkdir(parents=True, exist_ok=True)
        
        # 공통 디렉터리 (하위 호환성)
        self.shared_dir = self.results_dir / "shared"
        self.shared_dir.mkdir(exist_ok=True)
        
        # 지원하는 분석 유형
        self.analysis_types = {
            "comprehensive": {
                "name": "종합 분석",
                "description": "교사-아동 대화의 전면적인 분석과 상세한 코칭 피드백",
                "icon": "📊"
            },
            "quick_feedback": {
                "name": "빠른 피드백",
                "description": "즉석에서 핵심적인 피드백을 간단하게 제공",
                "icon": "⚡"
            },
            "child_development": {
                "name": "아동 발달 분석",
                "description": "발달 심리학 관점에서 아동의 현재 상태를 전문적으로 분석",
                "icon": "👶"
            },
            "coaching_tips": {
                "name": "상황별 코칭 팁",
                "description": "구체적인 교사 코칭 가이드와 실무 팁 제공",
                "icon": "💡"
            },
            "sentiment_interpretation": {
                "name": "감정 해석",
                "description": "감정 분석 결과를 교육적 관점에서 해석하고 활용 방안 제시",
                "icon": "😊"
            }
        }
    
    def create_new_analysis(self, conversation_id: str, transcription_data: Dict[str, Any], 
                          teacher_child_analysis: Dict[str, Any], 
                          metadata: Optional[Dict[str, Any]] = None,
                          username: Optional[str] = None) -> Dict[str, Any]:
        """
        새로운 분석 세션을 생성합니다.
        
        Args:
            conversation_id: 대화 ID
            transcription_data: 전사 데이터
            teacher_child_analysis: 교사-아동 구분 분석
            
        Returns:
            Dict: 생성된 분석 세션 데이터
        """
        analysis_data = {
            "conversation_id": conversation_id,
            "created_at": datetime.now().isoformat(),
            "last_updated": datetime.now().isoformat(),
            "username": username,
            "metadata": metadata or {},
            "transcription": transcription_data,
            "teacher_child_analysis": teacher_child_analysis,
            "analyses": {
                # 각 분석 유형별 결과 저장
                "comprehensive": None,
                "quick_feedback": None,
                "child_development": None,
                "coaching_tips": None,
                "sentiment_interpretation": None
            },
            "analysis_status": {
                # 각 분석의 완료 상태
                "comprehensive": False,
                "quick_feedback": False,
                "child_development": False,
                "coaching_tips": False,
                "sentiment_interpretation": False
            }
        }
        
        # 초기 데이터 저장
        self._save_analysis_data(conversation_id, analysis_data)
        
        return analysis_data
    
    def update_analysis_result(self, conversation_id: str, analysis_type: str, 
                             result: Dict[str, Any]) -> bool:
        """
        특정 분석 유형의 결과를 업데이트합니다.
        
        Args:
            conversation_id: 대화 ID
            analysis_type: 분석 유형 ('comprehensive', 'quick_feedback' 등)
            result: 분석 결과
            
        Returns:
            bool: 업데이트 성공 여부
        """
        try:
            # 기존 데이터 로드
            analysis_data = self.load_analysis(conversation_id)
            if not analysis_data:
                return False
            
            # 분석 결과 업데이트
            analysis_data["analyses"][analysis_type] = result
            analysis_data["analysis_status"][analysis_type] = result.get("success", False)
            analysis_data["last_updated"] = datetime.now().isoformat()
            
            # 저장
            return self._save_analysis_data(conversation_id, analysis_data)
            
        except Exception as e:
            print(f"분석 결과 업데이트 실패: {e}")
            return False
    
    def load_analysis(self, conversation_id: str, username: str = None) -> Optional[Dict[str, Any]]:
        """
        저장된 분석 데이터를 로드합니다.
        
        Args:
            conversation_id: 대화 ID
            username: 사용자명 (선택사항)
            
        Returns:
            Optional[Dict]: 분석 데이터 (없으면 None)
        """
        # 사용자별 디렉터리에서 먼저 찾기
        if username:
            user_file_path = self.results_dir / username / f"{conversation_id}.json"
            if user_file_path.exists():
                try:
                    with open(user_file_path, 'r', encoding='utf-8') as f:
                        return json.load(f)
                except Exception as e:
                    print(f"분석 데이터 로드 실패: {e}")
        
        # 기본 디렉터리에서 찾기 (하위 호환성)
        default_file_path = self.results_dir / f"{conversation_id}.json"
        if default_file_path.exists():
            try:
                with open(default_file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"분석 데이터 로드 실패: {e}")
        
        return None
    
    def get_analysis_result(self, conversation_id: str, analysis_type: str, username: str = None) -> Optional[Dict[str, Any]]:
        """
        특정 분석 유형의 결과를 가져옵니다.
        
        Args:
            conversation_id: 대화 ID
            analysis_type: 분석 유형
            username: 사용자명 (선택사항)
            
        Returns:
            Optional[Dict]: 분석 결과 (없으면 None)
        """
        analysis_data = self.load_analysis(conversation_id, username=username)
        if not analysis_data:
            return None
        
        return analysis_data.get("analyses", {}).get(analysis_type)
    
    def is_analysis_completed(self, conversation_id: str, analysis_type: str, username: str = None) -> bool:
        """
        특정 분석이 완료되었는지 확인합니다.
        
        Args:
            conversation_id: 대화 ID  
            analysis_type: 분석 유형
            username: 사용자명 (선택사항)
            
        Returns:
            bool: 완료 여부
        """
        analysis_data = self.load_analysis(conversation_id, username=username)
        if not analysis_data:
            return False
        
        return analysis_data.get("analysis_status", {}).get(analysis_type, False)
    
    def get_analysis_status(self, conversation_id: str) -> Dict[str, bool]:
        """
        모든 분석 유형의 완료 상태를 가져옵니다.
        
        Args:
            conversation_id: 대화 ID
            
        Returns:
            Dict[str, bool]: 분석 유형별 완료 상태
        """
        analysis_data = self.load_analysis(conversation_id)
        if not analysis_data:
            return {analysis_type: False for analysis_type in self.analysis_types.keys()}
        
        return analysis_data.get("analysis_status", {})
    
    def get_all_analyses(self, username: str = None) -> List[Dict[str, Any]]:
        """
        모든 저장된 분석 목록을 가져옵니다.
        
        Args:
            username: 특정 사용자의 분석만 가져올 경우 사용자명
        
        Returns:
            List[Dict]: 분석 목록 (최신순)
        """
        analyses = []
        
        try:
            if username:
                # 특정 사용자의 분석만 가져오기
                user_dir = self.results_dir / username
                if user_dir.exists():
                    json_files = list(user_dir.glob("*.json"))
                else:
                    json_files = []
            else:
                # 모든 분석 가져오기 (사용자별 디렉터리와 기본 디렉터리 모두)
                json_files = list(self.results_dir.glob("*.json"))
                
                # 사용자별 디렉터리도 검색
                for user_dir in self.results_dir.iterdir():
                    if user_dir.is_dir() and user_dir.name != "shared":
                        json_files.extend(list(user_dir.glob("*.json")))
            
            for file_path in json_files:
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        
                        # 요약 정보 생성
                        summary = {
                            "conversation_id": data.get("conversation_id"),
                            "created_at": data.get("created_at"),
                            "last_updated": data.get("last_updated"),
                            "username": data.get("username"),
                            "metadata": data.get("metadata", {}),
                            "transcript_preview": self._get_transcript_preview(data),
                            "completed_analyses": sum(1 for status in data.get("analysis_status", {}).values() if status),
                            "total_analyses": len(self.analysis_types),
                            "analysis_status": data.get("analysis_status", {}),
                            "file_path": str(file_path)
                        }
                        analyses.append(summary)
                        
                except Exception as e:
                    print(f"파일 읽기 오류 {file_path}: {e}")
                    continue
            
            # 최신순 정렬
            analyses.sort(key=lambda x: x.get("created_at", ""), reverse=True)
            
        except Exception as e:
            print(f"분석 목록 조회 실패: {e}")
        
        return analyses
    
    def delete_analysis(self, conversation_id: str, username: str = None) -> bool:
        """
        분석 데이터를 삭제합니다.
        
        Args:
            conversation_id: 대화 ID
            username: 사용자명 (선택사항)
            
        Returns:
            bool: 삭제 성공 여부
        """
        try:
            deleted = False
            deleted_files = []
            
            # 사용자별 디렉터리에서 삭제 시도
            if username:
                user_file_path = self.results_dir / username / f"{conversation_id}.json"
                if user_file_path.exists():
                    user_file_path.unlink()
                    deleted_files.append(str(user_file_path))
                    deleted = True
            
            # 기본 디렉터리에서도 삭제 시도 (하위 호환성)
            default_file_path = self.results_dir / f"{conversation_id}.json"
            if default_file_path.exists():
                default_file_path.unlink()
                deleted_files.append(str(default_file_path))
                deleted = True
            
            if deleted:
                print(f"✅ 분석 삭제 성공: {conversation_id} (삭제된 파일: {len(deleted_files)}개)")
            else:
                print(f"⚠️ 삭제할 파일 없음: {conversation_id}")
            
            return deleted
            
        except Exception as e:
            print(f"❌ 분석 삭제 실패: {e}")
            import traceback
            print(f"상세 오류: {traceback.format_exc()}")
            return False
    
    def search_analyses(self, keyword: str) -> List[Dict[str, Any]]:
        """
        키워드로 분석 결과를 검색합니다.
        
        Args:
            keyword: 검색 키워드
            
        Returns:
            List[Dict]: 검색 결과
        """
        all_analyses = self.get_all_analyses()
        
        if not keyword:
            return all_analyses
        
        keyword_lower = keyword.lower()
        filtered_analyses = []
        
        for analysis in all_analyses:
            # 전사 미리보기, 사용자명, 메타데이터에서 키워드 검색
            preview = analysis.get("transcript_preview", "").lower()
            username = analysis.get("username", "").lower()
            metadata = analysis.get("metadata", {})
            child_name = metadata.get("child_name", "").lower()
            description = metadata.get("description", "").lower()
            
            if (keyword_lower in preview or 
                keyword_lower in username or
                keyword_lower in child_name or
                keyword_lower in description):
                filtered_analyses.append(analysis)
        
        return filtered_analyses
    
    def _save_analysis_data(self, conversation_id: str, data: Dict[str, Any]) -> bool:
        """분석 데이터를 파일에 저장합니다."""
        # 사용자별 디렉터리 구조 생성
        username = data.get('username')
        if username:
            user_dir = self.results_dir / username
            user_dir.mkdir(exist_ok=True)
            file_path = user_dir / f"{conversation_id}.json"
        else:
            # 사용자가 없는 경우 기본 디렉터리 사용 (하위 호환성)
            file_path = self.results_dir / f"{conversation_id}.json"
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"분석 데이터 저장 실패: {e}")
            return False
    
    def _get_transcript_preview(self, data: Dict[str, Any], max_length: int = 100) -> str:
        """전사본의 미리보기 텍스트를 생성합니다."""
        transcript = data.get("transcription", {}).get("transcript", "")
        
        if len(transcript) <= max_length:
            return transcript
        
        return transcript[:max_length] + "..."
    
    def get_analysis_types(self) -> Dict[str, Dict[str, str]]:
        """지원하는 분석 유형 목록을 반환합니다."""
        return self.analysis_types.copy()
    
    def export_analysis(self, conversation_id: str, format_type: str = "json") -> Optional[str]:
        """
        분석 결과를 내보냅니다.
        
        Args:
            conversation_id: 대화 ID
            format_type: 내보내기 형식 ('json', 'txt')
            
        Returns:
            Optional[str]: 내보낸 파일 경로
        """
        analysis_data = self.load_analysis(conversation_id)
        if not analysis_data:
            return None
        
        try:
            if format_type == "json":
                export_path = self.results_dir / f"{conversation_id}_export.json"
                with open(export_path, 'w', encoding='utf-8') as f:
                    json.dump(analysis_data, f, ensure_ascii=False, indent=2)
                return str(export_path)
            
            elif format_type == "txt":
                export_path = self.results_dir / f"{conversation_id}_export.txt"
                with open(export_path, 'w', encoding='utf-8') as f:
                    self._write_text_report(f, analysis_data)
                return str(export_path)
            
        except Exception as e:
            print(f"분석 내보내기 실패: {e}")
        
        return None
    
    def _write_text_report(self, file, data: Dict[str, Any]):
        """텍스트 형식으로 분석 보고서를 작성합니다."""
        file.write(f"KindCoach 분석 보고서\n")
        file.write(f"=" * 50 + "\n\n")
        file.write(f"대화 ID: {data.get('conversation_id', 'N/A')}\n")
        file.write(f"분석 일시: {data.get('created_at', 'N/A')}\n")
        file.write(f"최종 수정: {data.get('last_updated', 'N/A')}\n\n")
        
        # 전사본
        transcript = data.get("transcription", {}).get("transcript", "")
        if transcript:
            file.write("📝 대화 전사\n")
            file.write("-" * 20 + "\n")
            file.write(transcript + "\n\n")
        
        # 각 분석 결과
        analyses = data.get("analyses", {})
        for analysis_type, result in analyses.items():
            if result and result.get("success"):
                analysis_info = self.analysis_types.get(analysis_type, {})
                file.write(f"{analysis_info.get('icon', '📋')} {analysis_info.get('name', analysis_type)}\n")
                file.write("-" * 30 + "\n")
                
                if analysis_type == "comprehensive":
                    file.write(result.get("analysis", "") + "\n\n")
                elif analysis_type == "quick_feedback":
                    file.write(result.get("feedback", "") + "\n\n")
                elif analysis_type == "child_development":
                    file.write(result.get("development_analysis", "") + "\n\n")
                elif analysis_type == "coaching_tips":
                    file.write(result.get("coaching_tips", "") + "\n\n")
                elif analysis_type == "sentiment_interpretation":
                    file.write(result.get("interpretation", "") + "\n\n")