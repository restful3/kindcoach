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


class AudioProcessor:
    def __init__(self, api_key: str = None):
        """AssemblyAI API 키로 초기화"""
        self.api_key = api_key or os.getenv("ASSEMBLYAI_API_KEY")
        if not self.api_key:
            raise ValueError("ASSEMBLYAI_API_KEY가 설정되지 않았습니다.")
        
        aai.settings.api_key = self.api_key
        self.config = aai.TranscriptionConfig(
            language_code="ko",  # 한국어 설정
            speaker_labels=True,  # 화자 분리 활성화
            # 한국어에서 지원되지 않는 기능들 제거
            # auto_highlights=True,  # 중요 구간 자동 감지 (한국어 미지원)
            # sentiment_analysis=True,  # 감정 분석 (한국어 미지원)
            # entity_detection=True,  # 개체명 인식 (한국어 미지원)
        )
    
    def transcribe_audio(self, audio_file) -> Dict[str, Any]:
        """
        오디오 파일을 전사하고 화자를 구분합니다.
        
        Args:
            audio_file: 업로드된 오디오 파일 (Streamlit UploadedFile)
            
        Returns:
            Dict: 전사 결과와 화자 정보
        """
        try:
            # 임시 파일로 저장
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_file:
                tmp_file.write(audio_file.read())
                tmp_file_path = tmp_file.name
            
            # AssemblyAI로 전사 시작
            transcriber = aai.Transcriber()
            transcript = transcriber.transcribe(tmp_file_path, config=self.config)
            
            # 임시 파일 정리
            os.unlink(tmp_file_path)
            
            if transcript.status == aai.TranscriptStatus.error:
                return {
                    "success": False,
                    "error": f"전사 실패: {transcript.error}",
                    "transcript": None
                }
            
            # 결과 정리
            result = {
                "success": True,
                "transcript": transcript.text,
                "confidence": transcript.confidence,
                "audio_duration": transcript.audio_duration,
                "speakers": self._extract_speaker_segments(transcript),
                "highlights": [],  # 한국어에서 지원되지 않음
                "sentiment": [],   # 한국어에서 지원되지 않음
                "entities": [],    # 한국어에서 지원되지 않음
                "processed_at": datetime.now().isoformat()
            }
            
            return result
            
        except Exception as e:
            return {
                "success": False,
                "error": f"오디오 처리 중 오류 발생: {str(e)}",
                "transcript": None
            }
    
    def _extract_speaker_segments(self, transcript) -> List[Dict[str, Any]]:
        """화자별 발화 구간을 추출합니다."""
        if not hasattr(transcript, 'utterances') or not transcript.utterances:
            return []
        
        segments = []
        for utterance in transcript.utterances:
            segments.append({
                "speaker": f"화자 {utterance.speaker}",
                "text": utterance.text,
                "start_time": utterance.start / 1000,  # ms to seconds
                "end_time": utterance.end / 1000,
                "confidence": utterance.confidence,
                "words": len(utterance.text.split()) if utterance.text else 0
            })
        
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