#!/usr/bin/env python3
"""
KindCoach 오디오 처리 테스트 스크립트
샘플 오디오 파일로 전체 워크플로우 테스트
"""

import os
import sys
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent
sys.path.append(str(project_root))

from src.audio_processor import AudioProcessor
from src.ai_analyzer import AIAnalyzer
from src.utils import load_environment, validate_audio_file, format_duration

def test_audio_processing():
    """샘플 오디오 파일로 전체 처리 과정 테스트"""
    print("🤖❤️ KindCoach 오디오 처리 테스트")
    print("=" * 50)
    
    # 1. 환경 설정 확인
    try:
        env_vars = load_environment()
        print("✅ 환경 변수 로드 성공")
    except Exception as e:
        print(f"❌ 환경 변수 오류: {e}")
        return
    
    # 2. 샘플 파일 경로 설정
    sample_file_path = "/home/restful3/workspace/kindcoach/data/sample_audio/sample_audio.m4a"
    
    if not os.path.exists(sample_file_path):
        print(f"❌ 샘플 파일을 찾을 수 없습니다: {sample_file_path}")
        return
    
    print(f"📁 샘플 파일: {sample_file_path}")
    
    # 파일 크기 확인
    file_size = os.path.getsize(sample_file_path)
    print(f"📊 파일 크기: {file_size / (1024*1024):.1f} MB")
    
    # 3. AudioProcessor 초기화
    try:
        audio_processor = AudioProcessor(env_vars["assemblyai_key"])
        print("✅ AudioProcessor 초기화 성공")
    except Exception as e:
        print(f"❌ AudioProcessor 초기화 실패: {e}")
        return
    
    # 4. AI Analyzer 초기화
    try:
        ai_analyzer = AIAnalyzer(env_vars["openai_key"])
        print("✅ AIAnalyzer 초기화 성공")
    except Exception as e:
        print(f"❌ AIAnalyzer 초기화 실패: {e}")
        return
    
    # 5. 오디오 파일을 파일 객체처럼 처리하기 위한 래퍼 클래스
    class AudioFileWrapper:
        def __init__(self, file_path):
            self.file_path = file_path
            self.name = os.path.basename(file_path)
            self.size = os.path.getsize(file_path)
            self._file = None
        
        def read(self):
            with open(self.file_path, 'rb') as f:
                return f.read()
        
        def seek(self, position):
            pass  # Streamlit의 seek 호출 처리
    
    # 6. 오디오 전사 시작
    print("\n🎙️ 오디오 전사 시작...")
    print("⏳ AssemblyAI 처리 중... (시간이 걸릴 수 있습니다)")
    
    try:
        audio_file = AudioFileWrapper(sample_file_path)
        transcription_result = audio_processor.transcribe_audio(audio_file)
        
        if not transcription_result["success"]:
            print(f"❌ 전사 실패: {transcription_result['error']}")
            return
        
        print("✅ 음성 전사 완료!")
        print(f"📝 전사본 길이: {len(transcription_result['transcript'])} 문자")
        print(f"⏱️ 오디오 길이: {format_duration(transcription_result.get('audio_duration', 0))}")
        print(f"🎯 평균 신뢰도: {transcription_result.get('confidence', 0):.2f}")
        print(f"👥 화자 수: {len(transcription_result.get('speakers', []))}")
        
        # 전사본 일부 출력
        transcript_preview = transcription_result['transcript'][:200] + "..." if len(transcription_result['transcript']) > 200 else transcription_result['transcript']
        print(f"\n📄 전사본 미리보기:\n{transcript_preview}")
        
    except Exception as e:
        print(f"❌ 전사 처리 중 오류: {e}")
        return
    
    # 7. 화자 분석
    print("\n👥 화자 분석...")
    try:
        speaker_segments = transcription_result["speakers"]
        teacher_child_analysis = audio_processor.is_teacher_child_conversation(speaker_segments)
        
        if not teacher_child_analysis["is_teacher_child"]:
            print(f"⚠️ 교사-아동 대화가 아닙니다: {teacher_child_analysis['reason']}")
        else:
            print("✅ 교사-아동 대화로 확인됨")
            print(f"👩‍🏫 교사: {teacher_child_analysis['teacher']}")
            print(f"👶 아동: {teacher_child_analysis['child']}")
            
            teacher_stats = teacher_child_analysis.get('teacher_stats', {})
            child_stats = teacher_child_analysis.get('child_stats', {})
            
            print(f"\n📊 발화 통계:")
            print(f"  교사 발화 시간: {teacher_stats.get('time_percentage', 0):.1f}%")
            print(f"  아동 발화 시간: {child_stats.get('time_percentage', 0):.1f}%")
            print(f"  교사 단어 비율: {teacher_stats.get('word_percentage', 0):.1f}%")
            print(f"  아동 단어 비율: {child_stats.get('word_percentage', 0):.1f}%")
        
    except Exception as e:
        print(f"❌ 화자 분석 중 오류: {e}")
        return
    
    # 8. AI 분석 (빠른 피드백만 테스트)
    print("\n🤖 AI 분석 시작...")
    try:
        quick_feedback = ai_analyzer.get_quick_feedback(transcription_result["transcript"])
        
        if quick_feedback["success"]:
            print("✅ AI 빠른 피드백 완료!")
            print("\n" + "="*50)
            print("💡 AI 피드백 결과:")
            print("="*50)
            print(quick_feedback["feedback"])
        else:
            print(f"❌ AI 분석 실패: {quick_feedback.get('error', '알 수 없는 오류')}")
    
    except Exception as e:
        print(f"❌ AI 분석 중 오류: {e}")
    
    print("\n🎉 테스트 완료!")

if __name__ == "__main__":
    test_audio_processing()