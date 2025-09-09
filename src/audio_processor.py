"""
AssemblyAI 기반 오디오 처리 모듈
한국어 음성 인식 및 화자 분리 기능 제공
"""

import os
import assemblyai as aai
from typing import Dict, List, Any, Optional
import requests
import tempfile
from datetime import datetime
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from src.logging_config import get_logger, log_performance, log_api_call

# 로거 설정
logger = get_logger(__name__)


class AudioProcessor:
    def __init__(self, api_key: str = None):
        """AssemblyAI API 키로 초기화"""
        logger.info("AudioProcessor 초기화 시작")
        
        self.api_key = api_key or os.getenv("ASSEMBLYAI_API_KEY")
        if not self.api_key:
            logger.error("ASSEMBLYAI_API_KEY가 설정되지 않았습니다.")
            raise ValueError("ASSEMBLYAI_API_KEY가 설정되지 않았습니다.")
        
        logger.info(f"AssemblyAI API 키 확인됨 (길이: {len(self.api_key)}자)")
        
        try:
            aai.settings.api_key = self.api_key
            self.config = aai.TranscriptionConfig(
                language_code="ko",  # 한국어 설정
                speaker_labels=True,  # 화자 분리 활성화
                # 한국어에서 지원되지 않는 기능들 제거
                # auto_highlights=True,  # 중요 구간 자동 감지 (한국어 미지원)
                # sentiment_analysis=True,  # 감정 분석 (한국어 미지원)
                # entity_detection=True,  # 개체명 인식 (한국어 미지원)
            )
            logger.info("AssemblyAI 설정 완료 (한국어, 화자분리 활성화)")
        except Exception as e:
            logger.error(f"AssemblyAI 설정 실패: {str(e)}")
            raise
        
        logger.info("AudioProcessor 초기화 완료")
    
    def transcribe_audio(self, audio_file) -> Dict[str, Any]:
        """
        오디오 파일을 전사하고 화자를 구분합니다.
        
        Args:
            audio_file: 업로드된 오디오 파일 (Streamlit UploadedFile)
            
        Returns:
            Dict: 전사 결과와 화자 정보
        """
        logger.info("오디오 전사 시작")
        logger.info(f"파일명: {audio_file.name}, 크기: {audio_file.size} bytes")
        
        try:
            # 임시 파일로 저장
            logger.info("임시 파일 생성 중...")
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_file:
                tmp_file.write(audio_file.read())
                tmp_file_path = tmp_file.name
            
            logger.info(f"임시 파일 생성 완료: {tmp_file_path}")
            
            # AssemblyAI로 전사 시작
            logger.info("AssemblyAI 전사 시작...")
            start_time = datetime.now()
            
            transcriber = aai.Transcriber()
            transcript = transcriber.transcribe(tmp_file_path, config=self.config)
            
            end_time = datetime.now()
            processing_time = (end_time - start_time).total_seconds()
            
            # API 호출 로그
            log_api_call(
                service="AssemblyAI",
                endpoint="transcript",
                duration=processing_time,
                status="success",
                file_size=audio_file.size,
                audio_duration=transcript.audio_duration,
                confidence=transcript.confidence
            )
            
            logger.info(f"AssemblyAI 전사 완료 (처리 시간: {processing_time:.2f}초)")
            
            # 임시 파일 정리
            os.unlink(tmp_file_path)
            logger.info("임시 파일 정리 완료")
            
            if transcript.status == aai.TranscriptStatus.error:
                logger.error(f"전사 실패: {transcript.error}")
                return {
                    "success": False,
                    "error": f"전사 실패: {transcript.error}",
                    "transcript": None
                }
            
            logger.info(f"전사 성공 - 신뢰도: {transcript.confidence:.2f}, 오디오 길이: {transcript.audio_duration}초")
            
            # 화자 구간 추출
            logger.info("화자 구간 추출 중...")
            speaker_segments = self._extract_speaker_segments(transcript)
            logger.info(f"화자 구간 {len(speaker_segments)}개 추출 완료")
            
            # 결과 정리
            result = {
                "success": True,
                "transcript": transcript.text,
                "confidence": transcript.confidence,
                "audio_duration": transcript.audio_duration,
                "speakers": speaker_segments,
                "highlights": [],  # 한국어에서 지원되지 않음
                "sentiment": [],   # 한국어에서 지원되지 않음
                "entities": [],    # 한국어에서 지원되지 않음
                "processed_at": datetime.now().isoformat(),
                "processing_time_seconds": processing_time
            }
            
            logger.info(f"전사 결과 정리 완료 - 전사본 길이: {len(transcript.text)}자")
            return result
            
        except Exception as e:
            logger.error(f"오디오 처리 중 오류 발생: {str(e)}")
            logger.exception("상세 오류 정보:")
            return {
                "success": False,
                "error": f"오디오 처리 중 오류 발생: {str(e)}",
                "transcript": None
            }
    
    def _extract_speaker_segments(self, transcript) -> List[Dict[str, Any]]:
        """화자별 발화 구간을 추출합니다."""
        logger.info("화자 구간 추출 시작")
        
        if not hasattr(transcript, 'utterances') or not transcript.utterances:
            logger.warning("화자 구간 데이터가 없습니다.")
            return []
        
        segments = []
        for i, utterance in enumerate(transcript.utterances):
            segment = {
                "speaker": f"화자 {utterance.speaker}",
                "text": utterance.text,
                "start_time": utterance.start / 1000,  # ms to seconds
                "end_time": utterance.end / 1000,
                "confidence": utterance.confidence,
                "words": len(utterance.text.split()) if utterance.text else 0
            }
            segments.append(segment)
            
            if i < 3:  # 처음 3개 구간만 로그 출력
                logger.info(f"구간 {i+1}: 화자 {utterance.speaker}, 길이 {segment['end_time'] - segment['start_time']:.1f}초, 신뢰도 {utterance.confidence:.2f}")
        
        if len(segments) > 3:
            logger.info(f"... 총 {len(segments)}개 구간 추출됨")
        
        logger.info(f"화자 구간 추출 완료: {len(segments)}개")
        return segments
    
    def _extract_highlights(self, transcript) -> List[Dict[str, Any]]:
        """중요한 구간을 추출합니다."""
        if not hasattr(transcript, 'auto_highlights') or not transcript.auto_highlights:
            return []
        
        highlights = []
        for highlight in transcript.auto_highlights.results:
            highlights.append({
                "text": highlight.text,
                "count": highlight.count,
                "rank": highlight.rank,
                "timestamps": [
                    {
                        "start_time": ts.start / 1000,
                        "end_time": ts.end / 1000
                    }
                    for ts in highlight.timestamps
                ]
            })
        
        return highlights
    
    def _extract_sentiment(self, transcript) -> List[Dict[str, Any]]:
        """감정 분석 결과를 추출합니다."""
        if not hasattr(transcript, 'sentiment_analysis_results') or not transcript.sentiment_analysis_results:
            return []
        
        sentiments = []
        for sentiment in transcript.sentiment_analysis_results:
            sentiments.append({
                "text": sentiment.text,
                "sentiment": sentiment.sentiment,
                "confidence": sentiment.confidence,
                "start_time": sentiment.start / 1000,
                "end_time": sentiment.end / 1000
            })
        
        return sentiments
    
    def _extract_entities(self, transcript) -> List[Dict[str, Any]]:
        """개체명 인식 결과를 추출합니다."""
        if not hasattr(transcript, 'entities') or not transcript.entities:
            return []
        
        entities = []
        for entity in transcript.entities:
            entities.append({
                "text": entity.text,
                "entity_type": entity.entity_type,
                "start_time": entity.start / 1000,
                "end_time": entity.end / 1000
            })
        
        return entities
    
    def get_speaker_statistics(self, segments: List[Dict[str, Any]]) -> Dict[str, Any]:
        """화자별 통계를 계산합니다."""
        if not segments:
            return {}
        
        speaker_stats = {}
        total_duration = sum(seg["end_time"] - seg["start_time"] for seg in segments)
        total_words = sum(seg["words"] for seg in segments)
        
        for segment in segments:
            speaker = segment["speaker"]
            if speaker not in speaker_stats:
                speaker_stats[speaker] = {
                    "total_time": 0,
                    "total_words": 0,
                    "utterances": 0,
                    "avg_confidence": 0
                }
            
            duration = segment["end_time"] - segment["start_time"]
            speaker_stats[speaker]["total_time"] += duration
            speaker_stats[speaker]["total_words"] += segment["words"]
            speaker_stats[speaker]["utterances"] += 1
            speaker_stats[speaker]["avg_confidence"] += segment["confidence"]
        
        # 통계 정리
        for speaker, stats in speaker_stats.items():
            stats["time_percentage"] = (stats["total_time"] / total_duration * 100) if total_duration > 0 else 0
            stats["word_percentage"] = (stats["total_words"] / total_words * 100) if total_words > 0 else 0
            stats["avg_confidence"] = stats["avg_confidence"] / stats["utterances"] if stats["utterances"] > 0 else 0
            stats["avg_words_per_utterance"] = stats["total_words"] / stats["utterances"] if stats["utterances"] > 0 else 0
        
        return speaker_stats
    
    def is_teacher_child_conversation(self, segments: List[Dict[str, Any]]) -> Dict[str, Any]:
        """교사-아동 대화인지 판단하고 역할을 분류합니다."""
        if len(segments) < 2:
            return {"is_teacher_child": False, "reason": "화자가 2명 미만입니다."}
        
        speaker_stats = self.get_speaker_statistics(segments)
        speakers = list(speaker_stats.keys())
        
        if len(speakers) != 2:
            return {"is_teacher_child": False, "reason": f"화자가 {len(speakers)}명입니다. 교사-아동 대화는 2명이어야 합니다."}
        
        # 발화 패턴 분석으로 교사/아동 구분
        speaker1, speaker2 = speakers
        stats1, stats2 = speaker_stats[speaker1], speaker_stats[speaker2]
        
        # 교사는 일반적으로 더 많이, 더 길게 말함
        if stats1["avg_words_per_utterance"] > stats2["avg_words_per_utterance"]:
            teacher, child = speaker1, speaker2
        else:
            teacher, child = speaker2, speaker1
        
        return {
            "is_teacher_child": True,
            "teacher": teacher,
            "child": child,
            "teacher_stats": speaker_stats[teacher],
            "child_stats": speaker_stats[child]
        }