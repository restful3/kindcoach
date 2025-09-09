"""
KindCoach 로깅 설정 모듈
통합된 로깅 설정을 제공합니다.
"""

import logging
import os
from datetime import datetime
from pathlib import Path


def setup_logging(log_level=logging.INFO, log_to_file=True):
    """
    KindCoach 애플리케이션의 로깅을 설정합니다.
    
    Args:
        log_level: 로그 레벨 (기본값: INFO)
        log_to_file: 파일로 로그 저장 여부 (기본값: True)
    """
    # 로그 디렉터리 생성
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # 로그 포맷 설정
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    date_format = '%Y-%m-%d %H:%M:%S'
    
    # 기본 로깅 설정
    logging.basicConfig(
        level=log_level,
        format=log_format,
        datefmt=date_format,
        handlers=[]
    )
    
    # 루트 로거 가져오기
    root_logger = logging.getLogger()
    
    # 콘솔 핸들러 추가
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_formatter = logging.Formatter(log_format, date_format)
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)
    
    # 파일 핸들러 추가 (선택사항)
    if log_to_file:
        # 일별 로그 파일
        today = datetime.now().strftime('%Y-%m-%d')
        log_file = log_dir / f"kindcoach_{today}.log"
        
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(log_level)
        file_formatter = logging.Formatter(log_format, date_format)
        file_handler.setFormatter(file_formatter)
        root_logger.addHandler(file_handler)
        
        # 에러 전용 로그 파일
        error_log_file = log_dir / f"kindcoach_errors_{today}.log"
        error_handler = logging.FileHandler(error_log_file, encoding='utf-8')
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(file_formatter)
        root_logger.addHandler(error_handler)
    
    # 외부 라이브러리 로그 레벨 조정
    logging.getLogger('httpx').setLevel(logging.WARNING)
    logging.getLogger('httpcore').setLevel(logging.WARNING)
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    
    # KindCoach 관련 로거들 설정
    kindcoach_loggers = [
        'src.ai_analyzer',
        'src.audio_processor', 
        'src.analysis_manager',
        'src.main',
        'src.prompt_manager',
        'src.auth'
    ]
    
    for logger_name in kindcoach_loggers:
        logger = logging.getLogger(logger_name)
        logger.setLevel(log_level)
    
    return root_logger


def get_logger(name: str) -> logging.Logger:
    """
    지정된 이름의 로거를 반환합니다.
    
    Args:
        name: 로거 이름
        
    Returns:
        logging.Logger: 설정된 로거
    """
    return logging.getLogger(name)


def log_function_call(func_name: str, **kwargs):
    """
    함수 호출을 로그로 기록합니다.
    
    Args:
        func_name: 함수 이름
        **kwargs: 함수 매개변수
    """
    logger = get_logger('function_calls')
    params = ', '.join([f"{k}={v}" for k, v in kwargs.items()])
    logger.info(f"함수 호출: {func_name}({params})")


def log_performance(operation: str, duration: float, **metadata):
    """
    성능 메트릭을 로그로 기록합니다.
    
    Args:
        operation: 작업 이름
        duration: 소요 시간 (초)
        **metadata: 추가 메타데이터
    """
    logger = get_logger('performance')
    meta_str = ', '.join([f"{k}={v}" for k, v in metadata.items()])
    logger.info(f"성능: {operation} - {duration:.2f}초 ({meta_str})")


def log_api_call(service: str, endpoint: str, duration: float, status: str, **metadata):
    """
    API 호출을 로그로 기록합니다.
    
    Args:
        service: 서비스 이름 (예: OpenAI, AssemblyAI)
        endpoint: API 엔드포인트
        duration: 응답 시간 (초)
        status: 응답 상태
        **metadata: 추가 메타데이터
    """
    logger = get_logger('api_calls')
    meta_str = ', '.join([f"{k}={v}" for k, v in metadata.items()])
    logger.info(f"API 호출: {service} {endpoint} - {duration:.2f}초, 상태: {status} ({meta_str})")


# 기본 로깅 설정 적용
setup_logging()
