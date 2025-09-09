"""
OpenAI GPT-4o-mini 기반 대화 분석 모듈
교사-아동 상호작용 분석 및 코칭 피드백 생성
"""

import os
import openai
from typing import Dict, List, Any, Optional
import json
from datetime import datetime
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from src.prompt_manager import PromptManager
from src.logging_config import get_logger, log_performance, log_api_call

# 로거 설정
logger = get_logger(__name__)


class AIAnalyzer:
    def __init__(self, api_key: str = None):
        """OpenAI API 키로 초기화"""
        logger.info("AIAnalyzer 초기화 시작")
        
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            logger.error("OPENAI_API_KEY가 설정되지 않았습니다.")
            raise ValueError("OPENAI_API_KEY가 설정되지 않았습니다.")
        
        logger.info(f"OpenAI API 키 확인됨 (길이: {len(self.api_key)}자)")
        
        try:
            self.client = openai.OpenAI(api_key=self.api_key)
            self.model = "gpt-4o-mini"
            logger.info(f"OpenAI 클라이언트 초기화 완료 (모델: {self.model})")
        except Exception as e:
            logger.error(f"OpenAI 클라이언트 초기화 실패: {str(e)}")
            raise
        
        try:
            self.prompt_manager = PromptManager()
            prompts = self.prompt_manager.get_all_prompts()
            logger.info(f"PromptManager 초기화 완료 (프롬프트 {len(prompts)}개 로드됨)")
        except Exception as e:
            logger.error(f"PromptManager 초기화 실패: {str(e)}")
            raise
        
        logger.info("AIAnalyzer 초기화 완료")
    
    def analyze_conversation(
        self, 
        transcript: str, 
        speaker_segments: List[Dict[str, Any]],
        teacher_child_info: Dict[str, Any],
        sentiment_data: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        교사-아동 대화를 종합적으로 분석합니다.
        
        Args:
            transcript: 전체 대화 전사본
            speaker_segments: 화자별 발화 구간
            teacher_child_info: 교사/아동 구분 정보
            sentiment_data: 감정 분석 결과
            
        Returns:
            Dict: 분석 결과와 코칭 피드백
        """
        logger.info("종합 대화 분석 시작")
        logger.info(f"전사본 길이: {len(transcript)}자")
        logger.info(f"화자 구간 수: {len(speaker_segments)}개")
        logger.info(f"교사-아동 정보: {teacher_child_info.get('is_teacher_child', False)}")
        
        try:
            # 교사와 아동 정보 준비
            logger.info("화자 정보 포맷팅 중...")
            teacher_info = self._format_speaker_info(
                teacher_child_info.get("teacher_stats", {}), 
                "교사"
            )
            child_info = self._format_speaker_info(
                teacher_child_info.get("child_stats", {}), 
                "아동"
            )
            logger.info(f"교사 정보 길이: {len(teacher_info)}자")
            logger.info(f"아동 정보 길이: {len(child_info)}자")
            
            # 감정 분석 정보 포맷
            sentiment_analysis = self._format_sentiment_data(sentiment_data)
            logger.info(f"감정 분석 데이터: {len(sentiment_analysis)}자")
            
            # 프롬프트 구성
            logger.info("프롬프트 템플릿 로드 중...")
            prompt_template = self.prompt_manager.get_prompt("conversation_analysis")
            if not prompt_template:
                logger.error("종합 분석 프롬프트를 찾을 수 없습니다.")
                raise ValueError("종합 분석 프롬프트를 찾을 수 없습니다.")
            
            logger.info("프롬프트 구성 중...")
            prompt = prompt_template.format(
                transcript=transcript,
                teacher_info=teacher_info,
                child_info=child_info,
                sentiment_analysis=sentiment_analysis
            )
            logger.info(f"최종 프롬프트 길이: {len(prompt)}자")
            
            # GPT-4o-mini 분석 요청
            logger.info("OpenAI API 호출 시작...")
            start_time = datetime.now()
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "당신은 유아교육과 아동 심리학 분야의 전문가입니다. 교사들에게 따뜻하고 실용적인 코칭을 제공합니다."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=2000
            )
            
            end_time = datetime.now()
            processing_time = (end_time - start_time).total_seconds()
            
            # API 호출 로그
            log_api_call(
                service="OpenAI",
                endpoint="chat/completions",
                duration=processing_time,
                status="success",
                model=self.model,
                prompt_tokens=response.usage.prompt_tokens,
                completion_tokens=response.usage.completion_tokens,
                total_tokens=response.usage.total_tokens
            )
            
            logger.info(f"OpenAI API 응답 완료 (처리 시간: {processing_time:.2f}초)")
            logger.info(f"토큰 사용량 - 프롬프트: {response.usage.prompt_tokens}, 완성: {response.usage.completion_tokens}, 총합: {response.usage.total_tokens}")
            
            analysis_result = response.choices[0].message.content
            logger.info(f"분석 결과 길이: {len(analysis_result)}자")
            
            result = {
                "success": True,
                "analysis": analysis_result,
                "analysis_type": "comprehensive",
                "processed_at": datetime.now().isoformat(),
                "model_used": self.model,
                "processing_time_seconds": processing_time,
                "token_usage": {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                }
            }
            
            logger.info("종합 대화 분석 완료")
            return result
            
        except openai.APIError as e:
            logger.error(f"OpenAI API 호출 실패 (종합 분석): {str(e)}")
            return {
                "success": False,
                "error": f"OpenAI API 호출 실패 (종합 분석): {str(e)}",
                "analysis": None
            }
        except Exception as e:
            logger.error(f"AI 분석 중 오류 발생: {str(e)}")
            logger.exception("상세 오류 정보:")
            return {
                "success": False,
                "error": f"AI 분석 중 오류 발생: {str(e)}",
                "analysis": None
            }
    
    def get_quick_feedback(self, transcript: str) -> Dict[str, Any]:
        """
        빠른 피드백을 제공합니다.
        
        Args:
            transcript: 대화 전사본
            
        Returns:
            Dict: 간단한 피드백 결과
        """
        logger.info("빠른 피드백 분석 시작")
        logger.info(f"전사본 길이: {len(transcript)}자")
        
        try:
            prompt_template = self.prompt_manager.get_prompt("quick_feedback")
            if not prompt_template:
                logger.error("빠른 피드백 프롬프트를 찾을 수 없습니다.")
                raise ValueError("빠른 피드백 프롬프트를 찾을 수 없습니다.")
            
            prompt = prompt_template.format(transcript=transcript)
            logger.info(f"빠른 피드백 프롬프트 길이: {len(prompt)}자")
            
            logger.info("OpenAI API 호출 시작 (빠른 피드백)...")
            start_time = datetime.now()
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "유아교육 전문가로서 교사들에게 격려적이고 실용적인 피드백을 제공합니다."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.6,
                max_tokens=800
            )
            
            end_time = datetime.now()
            processing_time = (end_time - start_time).total_seconds()
            
            # API 호출 로그
            log_api_call(
                service="OpenAI",
                endpoint="chat/completions",
                duration=processing_time,
                status="success",
                model=self.model,
                analysis_type="quick_feedback",
                prompt_tokens=response.usage.prompt_tokens,
                completion_tokens=response.usage.completion_tokens,
                total_tokens=response.usage.total_tokens
            )
            
            logger.info(f"빠른 피드백 API 응답 완료 (처리 시간: {processing_time:.2f}초)")
            logger.info(f"토큰 사용량: {response.usage.total_tokens}개")
            
            feedback = response.choices[0].message.content
            logger.info(f"피드백 결과 길이: {len(feedback)}자")
            
            result = {
                "success": True,
                "feedback": feedback,
                "feedback_type": "quick",
                "processed_at": datetime.now().isoformat(),
                "processing_time_seconds": processing_time,
                "token_usage": {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                }
            }
            
            logger.info("빠른 피드백 분석 완료")
            return result
            
        except openai.APIError as e:
            logger.error(f"OpenAI API 호출 실패 (빠른 피드백): {str(e)}")
            return {
                "success": False,
                "error": f"OpenAI API 호출 실패 (빠른 피드백): {str(e)}",
                "feedback": None
            }
        except Exception as e:
            logger.error(f"빠른 피드백 생성 중 오류 발생: {str(e)}")
            logger.exception("상세 오류 정보:")
            return {
                "success": False,
                "error": f"빠른 피드백 생성 중 오류 발생: {str(e)}",
                "feedback": None
            }
    
    def analyze_child_development(
        self, 
        transcript: str, 
        child_segments: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        아동 발달 관점에서 분석합니다.
        
        Args:
            transcript: 전체 대화
            child_segments: 아동 발화 구간들
            
        Returns:
            Dict: 발달 분석 결과
        """
        try:
            # 아동 발화만 추출
            child_utterances = "\n".join([
                f"[{seg['start_time']:.1f}s] {seg['text']}" 
                for seg in child_segments
            ])
            
            prompt_template = self.prompt_manager.get_prompt("child_development")
            if not prompt_template:
                raise ValueError("아동 발달 분석 프롬프트를 찾을 수 없습니다.")
            
            prompt = prompt_template.format(
                transcript=transcript,
                child_utterances=child_utterances
            )
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "아동 발달 전문가로서 과학적이고 체계적인 발달 분석을 제공합니다."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.5,
                max_tokens=1500
            )
            
            development_analysis = response.choices[0].message.content
            
            return {
                "success": True,
                "development_analysis": development_analysis,
                "child_utterance_count": len(child_segments),
                "processed_at": datetime.now().isoformat()
            }
            
        except openai.APIError as e:
            return {
                "success": False,
                "error": f"OpenAI API 호출 실패 (발달 분석): {str(e)}",
                "development_analysis": None
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"발달 분석 중 오류 발생: {str(e)}",
                "development_analysis": None
            }
    
    def get_coaching_tips(self, transcript: str, situation: str = "일반적인 교사-아동 상호작용") -> Dict[str, Any]:
        """
        상황별 코칭 팁을 제공합니다.
        
        Args:
            transcript: 대화 내용
            situation: 상황 설명
            
        Returns:
            Dict: 코칭 팁 결과
        """
        try:
            prompt_template = self.prompt_manager.get_prompt("coaching_tips")
            if not prompt_template:
                raise ValueError("코칭 팁 프롬프트를 찾을 수 없습니다.")
            
            prompt = prompt_template.format(
                situation=situation,
                transcript=transcript
            )
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "교사 코칭 전문가로서 실용적이고 적용 가능한 조언을 제공합니다."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=1200
            )
            
            coaching_tips = response.choices[0].message.content
            
            return {
                "success": True,
                "coaching_tips": coaching_tips,
                "situation": situation,
                "processed_at": datetime.now().isoformat()
            }
            
        except openai.APIError as e:
            return {
                "success": False,
                "error": f"OpenAI API 호출 실패 (코칭 팁): {str(e)}",
                "coaching_tips": None
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"코칭 팁 생성 중 오류 발생: {str(e)}",
                "coaching_tips": None
            }
    
    def interpret_sentiment(
        self, 
        sentiment_data: List[Dict[str, Any]], 
        context: str
    ) -> Dict[str, Any]:
        """
        감정 분석 결과를 교육적 관점에서 해석합니다.
        
        Args:
            sentiment_data: 감정 분석 데이터
            context: 대화 맥락
            
        Returns:
            Dict: 감정 해석 결과
        """
        try:
            sentiment_formatted = self._format_sentiment_data(sentiment_data)
            
            prompt_template = self.prompt_manager.get_prompt("sentiment_interpretation")
            if not prompt_template:
                raise ValueError("감정 해석 프롬프트를 찾을 수 없습니다.")
            
            prompt = prompt_template.format(
                sentiment_data=sentiment_formatted,
                context=context
            )
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "감정과 소통 전문가로서 교사의 감정 인식과 대응 능력 향상을 돕습니다."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.6,
                max_tokens=1000
            )
            
            sentiment_interpretation = response.choices[0].message.content
            
            return {
                "success": True,
                "sentiment_interpretation": sentiment_interpretation,
                "processed_at": datetime.now().isoformat()
            }
            
        except openai.APIError as e:
            return {
                "success": False,
                "error": f"OpenAI API 호출 실패 (감정 해석): {str(e)}",
                "sentiment_interpretation": None
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"감정 해석 중 오류 발생: {str(e)}",
                "sentiment_interpretation": None
            }
    
    def _format_speaker_info(self, stats: Dict[str, Any], role: str) -> str:
        """화자 정보를 텍스트로 포맷합니다."""
        if not stats:
            return f"{role}: 정보 없음"
        
        return f"""
{role}:
- 총 발화 시간: {stats.get('total_time', 0):.1f}초 ({stats.get('time_percentage', 0):.1f}%)
- 총 단어 수: {stats.get('total_words', 0)}개 ({stats.get('word_percentage', 0):.1f}%)
- 발화 횟수: {stats.get('utterances', 0)}회
- 평균 신뢰도: {stats.get('avg_confidence', 0):.2f}
- 발화당 평균 단어 수: {stats.get('avg_words_per_utterance', 0):.1f}개
"""
    
    def _format_sentiment_data(self, sentiment_data: Optional[List[Dict[str, Any]]]) -> str:
        """감정 분석 데이터를 텍스트로 포맷합니다."""
        if not sentiment_data:
            return "감정 분석 데이터 없음"
        
        formatted = []
        for item in sentiment_data:
            formatted.append(
                f"[{item.get('start_time', 0):.1f}s] "
                f"{item.get('sentiment', 'unknown')} "
                f"(신뢰도: {item.get('confidence', 0):.2f}) "
                f"- \"{item.get('text', '')}\""
            )
        
        return "\n".join(formatted)
    
    def generate_summary_report(self, analysis_results: Dict[str, Any]) -> str:
        """분석 결과들을 종합한 요약 리포트를 생성합니다."""
        try:
            summary_prompt = f"""
다음 분석 결과들을 바탕으로 교사를 위한 종합 요약 리포트를 작성해주세요:

## 분석 결과들
{json.dumps(analysis_results, ensure_ascii=False, indent=2)}

## 요약 리포트 요구사항
1. 핵심 인사이트 3가지
2. 우선 개선 영역 2가지  
3. 구체적 실행 계획 3가지
4. 격려 메시지

간결하고 실용적으로 작성해주세요.
"""
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "교육 컨설턴트로서 분석 결과를 실행 가능한 리포트로 정리합니다."},
                    {"role": "user", "content": summary_prompt}
                ],
                temperature=0.6,
                max_tokens=800
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            return f"요약 리포트 생성 중 오류 발생: {str(e)}"