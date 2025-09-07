# ==============================================================================
# 1. 임포트 및 기본 설정
# ==============================================================================

# ------------------------------------------------------------------------------
# 표준 라이브러리 (Standard Library)
# ------------------------------------------------------------------------------
# 데이터 구조 및 타입
import csv  # CSV (쉼표로 구분된 값) 형식의 파일을 읽고 쓰기 위한 모듈 (결과 내보내기용)
import json  # JSON(JavaScript Object Notation) 데이터 구조를 파싱하고 생성하기 위한 모듈 (VMAF 로그, ffprobe 출력 처리용)
from collections import OrderedDict  # 아이템이 삽입된 순서를 기억하는 딕셔너리 클래스
from dataclasses import dataclass, field  # 상용구 코드 없이 클래스를 단순하게 작성하기 위한 데이터 클래스 데코레이터
from typing import Any, Dict, List, Tuple  # 타입 힌트(type hint)를 지원하기 위한 모듈

# 시스템, 프로세스, 동시성 관리
import logging  # 애플리케이션의 정보, 경고, 오류 등 이벤트 스트림을 로그 파일에 기록하기 위한 모듈
import multiprocessing  # CPU 집약적 인코딩 작업을 별도의 프로세스에서 병렬로 실행하여 처리 속도를 높이기 위한 모듈
import os  # 운영 체제 서비스와 상호작용하기 위한 모듈 (파일 경로 조작, 디렉토리 생성/삭제, 프로세스 ID 획득 등)
import shlex  # 쉘(shell)과 유사한 문법으로 문자열을 파싱하는 모듈 (FFmpeg 명령어 문자열을 인자 리스트로 안전하게 분리하는 데 사용)
import shutil  # 파일 및 디렉토리 관련 고수준 작업을 제공하는 모듈 (임시 디렉토리 생성 및 삭제 등)
import subprocess  # 새로운 프로세스를 생성하고 입출력 파이프에 연결하며 반환 코드를 얻기 위한 모듈 (FFmpeg/FFprobe 실행용)
import threading  # 스레드 기반 병렬 처리를 위한 모듈 (GUI 응답성을 유지하며 백그라운드 작업 수행 시 사용)
from concurrent.futures import ThreadPoolExecutor, as_completed  # 스레드 풀을 사용하여 비동기 호출을 실행하기 위한 고수준 인터페이스

# 유틸리티 및 기타
import math  # 기본적인 수학 함수를 제공하는 모듈 (벡터 계산, 정규화 등에 사용)
import re  # 정규 표현식(Regular Expression) 작업을 위한 모듈 (FFmpeg 로그에서 특정 텍스트 패턴 추출용)
import statistics  # 수학적 통계 함수(평균, 표준편차 등)를 계산하기 위한 모듈 (VMAF 점수 분석용)
import time  # 시간 관련 기능을 제공하는 모듈 (작업 소요 시간 측정, 스레드 지연 등)
import zipfile  # ZIP 아카이브를 읽고 쓰기 위한 모듈 (다운로드한 FFmpeg 빌드 압축 해제용)
from datetime import datetime, timedelta  # 날짜와 시간을 조작하기 위한 클래스를 제공하는 모듈

# GUI 프레임워크
import tkinter as tk  # Python 표준 GUI 툴킷 Tcl/Tk에 대한 인터페이스
from tkinter import ttk, filedialog, messagebox, scrolledtext  # ttk(테마 위젯), 파일 대화상자, 메시지 박스, 스크롤 텍스트 위젯



# ------------------------------------------------------------------------------
# 서드파티 라이브러리 (Third-Party Libraries)
# ------------------------------------------------------------------------------
# 시각화
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk  # Matplotlib 그래프를 Tkinter 애플리케이션에 임베드하기 위한 클래스
from matplotlib.figure import Figure  # Matplotlib의 최상위 컨테이너로, 그래프의 모든 요소를 담는 그림(figure) 객체

# 네트워킹 및 시스템 정보
import psutil  # 실행 중인 프로세스와 시스템 활용도(CPU, 메모리, 디스크 등)에 대한 정보를 가져오는 모듈 (물리 CPU 코어 수 확인용)
import requests  # HTTP 요청을 보내기 위한 모듈 (FFmpeg, VMAF 모델 등 웹 리소스 다운로드용)



# ------------------------------------------------------------------------------
# 로깅 기본 설정
# ------------------------------------------------------------------------------
# 애플리케이션 실행 중 발생하는 로그를 'Video Encoding Optimizer.log' 파일에 추가(append) 모드로 기록.
# 로그 형식: [시간] - [로그 레벨] - [메시지]
logging.basicConfig(
    level=logging.INFO,
    filename="Video Encoding Optimizer.log",
    filemode="a",
    format="%(asctime)s - %(levelname)s - %(message)s",
)



# ==============================================================================
# 상수 정의
# ==============================================================================
# 애플리케이션 설정 상수
APP_CONFIG = {
    # ==============================================================================
    # 1. 핵심 동작 및 기본값
    # ==============================================================================
    "default_sample_duration": 10.0,  # 기본 샘플 지속 시간 (초)
    "default_target_vmaf": 95.0,      # 기본 목표 VMAF 값
    "default_vmaf_threshold": 90.0,   # 기본 VMAF 임계값
    "default_parallel_jobs": 4,       # 기본 병렬 작업 수

    # ==============================================================================
    # 2. 성능 및 자원 관리
    # ==============================================================================
    "max_parallel_jobs": 8,           # NVENC 최대 병렬 작업 수
    "chunk_size": 10000,              # 프레임 처리 청크 크기
    "memory_check_interval": 5,       # 메모리 체크 간격 (청크 단위)
    "progress_update_interval": 4,    # 진행률 업데이트 간격 (워커 단위)
    "max_eta_display_seconds": 86400, # ETA 표시 최대 시간 (24시간)

    # ==============================================================================
    # 3. 장면 분석 알고리즘
    # ==============================================================================
    "overlap_keyframes": 2,           # 병렬 분석 시 키프레임 중첩 수
    "min_data_points_for_iqr": 10,    # IQR 아웃라이어 제거 최소 데이터 포인트 수
    "q1_percentile": 0.15,            # Q1 계산용 하위 백분율
    "q3_percentile": 0.85,            # Q3 계산용 상위 백분율
    "iqr_multiplier": 3.0,            # IQR 아웃라이어 제거 승수

    # ==============================================================================
    # 4. 시스템 및 외부 연동
    # ==============================================================================
    "data_folder_name": "VEO_Resource",  # 리소스 데이터 폴더명
    "max_filename_length": 200,       # 최대 파일명 길이 (임시 디렉토리 생성용)
    "ffmpeg_download_url": "https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip",  # FFmpeg 다운로드 URL
    "vmaf_repo_api_url": "https://api.github.com/repos/Netflix/vmaf/contents/model",  # VMAF 모델 저장소 API URL
    "max_download_workers": 16,       # VMAF 모델 병렬 다운로드에 사용할 최대 스레드 수
    "subprocess_timeout": 2,          # 서브프로세스 종료 대기 시간 (초)
    "subprocess_poll_interval": 0.1,  # 서브프로세스 상태 확인 간격 (초)

    # ==============================================================================
    # 5. GUI 및 표시 형식
    # ==============================================================================
    "window_size": (800, 600),        # 메인 윈도우 크기 (너비, 높이)
    "time_selector_window_size": (400, 150),  # 시간 선택 윈도우 크기 (너비, 높이)
    "preview_window_size": (800, 600),  # 미리보기 윈도우 크기 (너비, 높이)
    "vmaf_model_selector_window_size": (360, 320),  # VMAF 모델 선택 윈도우 크기 (너비, 높이)
    "advanced_settings_window_size": (700, 300),  # 고급 설정 윈도우 크기 (너비, 높이)
    "graph_window_size": (900, 700),  # 그래프 윈도우 크기 (너비, 높이)
    "log_window_size": (700, 500),    # 로그 윈도우 크기 (너비, 높이)
    "command_window_size": (700, 200),# 명령어 윈도우 크기 (너비, 높이)
    "tooltip_offset": 25,             # 툴팁 오프셋 (픽셀)
    "tooltip_padding": 40,            # 툴팁 패딩 (픽셀)
    "metric_formats": {
        "vmaf": ".6f",                # VMAF 점수 (소수점 6자리)
        "vmaf_1_low": ".6f",          # VMAF 하위 1% 점수 (소수점 6자리)
        "psnr": ".4f",                # PSNR 점수 (소수점 4자리)
        "ssim": ".6f",                # SSIM 점수 (소수점 6자리)
        "block_score": ".7f",         # 블록 점수 (소수점 7자리)
        "size_mb": ".4f",             # 파일 크기 (소수점 4자리)
        "efficiency": ".6f",          # 효율성 (소수점 6자리)
    },

    # ==============================================================================
    # 6. 수치 정밀도 관련 상수
    # ==============================================================================
    "numerical_tolerance": {
        "relative": 1e-6,  # 상대 오차 허용치 (상대적 정밀도 기준)
        "absolute": 1e-8,  # 절대 오차 허용치 (절대적 정밀도 기준)
        "convergence": 1e-4,  # 수렴 판정 허용치 (최적화 알고리즘의 수렴 여부 판정)
    },

    # ==============================================================================
    # 7. 메시지 박스 관련 상수
    # ==============================================================================
    "message_titles": {
        "error": "Error",  # 일반적인 오류 상황을 알리는 메시지 박스의 제목
        "warning": "Warning",  # 사용자에게 잠재적인 문제를 경고하는 메시지 박스의 제목
        "info": "Information",  # 사용자에게 단순 정보를 제공하는 메시지 박스의 제목
        "input_error": "Input Error",  # 사용자가 입력한 값(예: 품질 범위)에 오류가 있을 때 표시되는 메시지 박스의 제목
        "selection_error": "Selection Error",  # 사용자가 항목(예: 결과 테이블의 행, 코덱)을 잘못 선택했을 때 표시되는 메시지 박스의 제목
    },

    "message_texts": {
        # 비디오 파일이 선택되지 않았거나 지정된 경로에 파일이 없을 때 사용되는 메시지
        "file_not_found": "Please select a valid video file.",

        # 인코딩 코덱이 선택되지 않은 상태에서 작업을 시작하려 할 때의 메시지
        "codec_not_selected": "Please select a codec.",

        # 수동 샘플 시간 범위가 설정되지 않았거나, 종료 시간이 시작 시간보다 빠를 때의 메시지
        "invalid_time_range": "Manual sample time has not been set or is invalid. Please use the 'Set Range...' button.",

        # 품질(CRF/CQ 등) 설정 범위가 유효하지 않을 때(예: 시작 값이 종료 값보다 클 때)의 메시지
        "invalid_quality_range": "Quality range is invalid.",

        # 'Target VMAF' 모드에서 목표 VMAF 값이 0-100 범위를 벗어났을 때의 메시지
        "invalid_target_vmaf": "Target VMAF must be between 0 and 100.",

        # 프리셋 범위 설정 시, 시작 프리셋이 종료 프리셋보다 느린(순서상 뒤에 있는) 값일 경우의 메시지
        "invalid_preset_order": "Preset start value cannot be slower than the end value.",

        # .format()을 사용하여 동적인 값을 메시지에 포함시켜야 할 때 사용되는 범용 오류 메시지 템플릿
        "invalid_setting_value": "Invalid setting value: {}",
    },

    # ==============================================================================
    # 8. 프로그램 정보 상수
    # ==============================================================================
    "about_info": {
        "program": "Video Encoding Optimizer",          # 프로그램 이름
        "version": "1.1.0",                             # 버전
        "updated": "2025-09-07",                        # 업데이트 날짜
        "license": "GNU General Public License v3.0",   # 라이선스
        "developer": "(Github) IZH318",                 # 개발자 정보
        "website": "https://github.com/IZH318",         # 웹사이트
    },

    # ==============================================================================
    # 9. 파일 확장자 및 형식 정의
    # ==============================================================================
    "supported_video_extensions": (
        "*.mp4 *.mkv *.avi *.mov *.webm *.flv *.mpg *.mpeg *.wmv *.vob *.mts *.m2ts *.ts"
    ),

    "file_type_filters": [
        ("Supported Media Files", "*.mp4 *.mkv *.avi *.mov *.webm *.flv *.mpg *.mpeg *.wmv *.vob *.mts *.m2ts *.ts"),
        ("All files", "*.*"),
    ],

    # ==============================================================================
    # 10. 디버깅
    # ==============================================================================
    "enable_debug_logging": False,     # True로 설정 시 장면 분석 결과가 JSON 파일로 저장됨
}



# 로그 메시지 템플릿
LOG_MESSAGES = {
    # FFmpeg 실행 파일이 없어 인코더 감지를 시작할 수 없을 때 UI 상태 표시줄이나 로그에 사용
    "ffmpeg_not_found": "FFmpeg not found. Cannot detect encoders.",

    # FFmpeg 인코더 감지 중 오류 발생 시, 기본 목록을 사용함을 알리는 로그
    "encoder_detection_error": "Error detecting encoders. Using default list.",

    # 사용자가 'Sample Preview' 분석 작업을 취소했을 때의 상태 메시지
    "preview_analysis_cancelled": "Preview analysis cancelled.",

    # 병렬 장면 분석이 유의미한 데이터를 반환하지 못해, 더 안정적인 순차 분석으로 전환될 때의 로그
    "parallel_analysis_fallback": "Parallel analysis inconclusive. Switching to sequential mode...",

    # 장면 분석 시작 시 초기 메모리 사용량을 기록하기 위한 로그. (디버깅용)
    "memory_usage_info": "Initial memory usage: {:.2f} MB",

    # 장면 분석 완료 후 최종 메모리 사용량과 변화량을 기록하기 위한 로그. (디버깅용)
    "memory_usage_final": "Final memory usage: {:.2f} MB (Change: {+.2f} MB)",

    # IQR(사분위수 범위)을 이용한 아웃라이어 제거가 적용되었을 때, 제거된 데이터 포인트 수를 기록하는 로그
    "iqr_outlier_removed": "IQR outlier removal applied. {} data points were trimmed.",

    # IQR 아웃라이어 제거 후 남은 데이터가 없을 경우, 원본 데이터를 사용함을 알리는 로그
    "iqr_empty_data": "IQR outlier trimming resulted in empty data set. Using original data.",

    # IQR 처리 시작 시 통계 정보를 기록하는 로그
    "iqr_processing_start": "IQR processing started - Original data points: {}, Q1: {:.2f}, Q3: {:.2f}, IQR: {:.2f}, Bounds: [{:.2f}, {:.2f}]",

    # IQR 처리 완료 시 결과를 기록하는 로그
    "iqr_processing_complete": "IQR processing completed - Final data points: {}, Removed: {}, Reason: {}",

    # IQR 처리가 적용되지 않은 경우의 로그
    "iqr_processing_skipped": "IQR processing skipped - Reason: {}",

    # IQR이 0인 경우의 로그
    "iqr_zero_detected": "IQR is 0 (Q1: {:.2f}, Q3: {:.2f}) - All values are similar, no outlier removal applied",

    # IQR 아웃라이어 제거 상세 정보
    "iqr_outlier_details": "IQR outliers removed - Seconds: {}, Values: {} (outside bounds [{:.0f}, {:.0f}])",

    # 프로그램 시작/종료 관련 로그
    "program_start": "Video Encoding Optimizer started - Version: {}, Date: {}",
    "program_shutdown": "Video Encoding Optimizer shutting down - Session duration: {:.2f} seconds",
    "program_exit": "Video Encoding Optimizer exited normally",

    # 사용자 액션 관련 로그
    "file_selected": "Video file selected: {} (Size: {:.2f} MB)",
    "settings_changed": "Settings changed - Codec: {}, Mode: {}, Quality: {}",
    "optimization_started": "Optimization started - Target: {}, Jobs: {}, Duration: {}s",
    "optimization_completed": "Optimization completed - Total tests: {}, Duration: {:.2f}s, Best result: {}",
    "optimization_cancelled": "Optimization cancelled by user - Completed tests: {}",

    # 파일 처리 관련 로그
    "temp_dir_created": "Temporary directory created: {}",
    "temp_dir_cleaned": "Temporary directory cleaned: {}",
    "export_started": "Export started - Format: {}, File: {}",
    "export_completed": "Export completed - File: {} (Size: {:.2f} MB)",

    # 성능 메트릭 관련 로그
    "performance_summary": "Performance summary - Avg encoding time: {:.2f}s, Avg VMAF: {:.2f}, Best efficiency: {:.2f}",
    "system_info": "System info - CPU cores: {}, Memory: {:.2f} GB, OS: {}",

    # 비디오의 시작 타임스탬프가 0이 아닐 때(예: M2TS/TS 파일), 감지된 오프셋을 기록하는 로그
    "time_offset_detected": "Detected time offset: {}s. Normalizing timestamps to start from 0.",

    # ffprobe를 통해 비디오의 색상 정보를 성공적으로 읽어왔을 때의 로그
    "color_info_probed": "Probed color info for {}: {}",

    # 멀티프로세싱 워커에서 예외가 발생하여 'error' 상태를 반환했을 때의 로그
    "worker_error": "Worker Error: {}",

    # FFmpeg/FFprobe 서브프로세스가 0이 아닌 종료 코드를 반환하며 실패했을 때의 상세 로그
    "ffmpeg_process_failed": "FFmpeg process failed with code {}.\nCMD: {}\nStderr: {}",

    # 취소 가능한 서브프로세스 실행 래퍼(`_run_cancellable_subprocess`) 내에서 예외가 발생했을 때의 로그
    "subprocess_exception": "Exception in _run_cancellable_subprocess: {}",

    # 타임스탬프 정규화(`_normalize_seconds_map`) 과정에서 오류가 발생했을 때의 로그
    "seconds_map_normalization_error": "Error during seconds_map normalization: {}",

    # FFmpeg 인코더 감지 프로세스가 실패했을 때의 로그
    "ffmpeg_encoder_detection_failed": "FFmpeg process failed detecting encoders: {}",

    # FFmpeg 인코더 감지 중 시스템 수준(OS)의 오류가 발생했을 때의 로그
    "system_error_encoder_detection": "System error detecting FFmpeg encoders: {}",

    # FFmpeg 인코더 감지 중 예상치 못한 기타 오류가 발생했을 때의 로그
    "unexpected_error_encoder_detection": "Unexpected error detecting FFmpeg encoders: {}",

    # 비디오 색상 정보 조회(ffprobe) 프로세스가 실패했을 때의 로그
    "color_info_ffmpeg_failed": "FFmpeg process failed probing color info for {}. Defaults will be used. Error: {}",

    # 비디오 색상 정보 조회 중 시스템 수준(OS)의 오류가 발생했을 때의 로그
    "color_info_system_error": "System error probing color info for {}. Defaults will be used. Error: {}",

    # 'Sample Preview'를 위한 자동 장면 분석 중 오류가 발생했을 때의 로그
    "preview_analysis_failed": "Failed to analyze for preview: {}",

    # ffplay를 이용한 샘플 미리보기 실행에 실패했을 때의 로그
    "ffplay_launch_failed": "Failed to start ffplay preview: {}",

    # FFmpeg 자동 다운로드 및 설치 과정에서 오류가 발생했을 때의 로그
    "ffmpeg_download_failed": "FFmpeg download failed: {}",

    # 병렬 장면 분석 시, 개별 ffprobe 워커가 실패했을 때의 로그
    "indexed_ffprobe_worker_failed": "Indexed ffprobe worker failed for interval {}: {}",

    # 병렬 장면 분석에서 유효한 프레임을 전혀 찾지 못했을 때의 로그
    "no_frames_found_parallel": "No frames found during indexed parallel analysis for {}. Falling back to sequential.",

    # 병렬 장면 분석 결과, 유효한 데이터(초당 프레임 크기)가 없을 때의 로그
    "parallel_frame_analysis_no_data": "Parallel frame size analysis for {} yielded no valid data. Falling back to reliable sequential analysis.",
}



# ==============================================================================
# 2. 데이터 클래스 및 헬퍼
# ==============================================================================
# 인코딩 작업을 위한 데이터 클래스
@dataclass
class EncodingTask:
    """
    단일 인코딩 및 분석 작업에 필요한 모든 매개변수를 구조화하여 저장하는 데이터 클래스.
    
    FFmpeg 명령어 생성, 결과 분석, 파일 경로 관리 등에 필요한 모든 정보를
    하나의 객체에 통합하여 관리함으로써 코드의 가독성과 유지보수성을 향상시킴.
    """
    ffmpeg_path: str # ffmpeg.exe 실행 파일의 전체 절대 경로
    sample_path: str # 인코딩 및 분석의 기준이 되는 원본 샘플 영상 파일의 경로
    temp_dir: str # 인코딩 결과물, 로그 파일 등 임시 파일들을 저장할 디렉토리 경로
    codec: str # 사용할 비디오 코덱 이름 (예: 'libx265', 'h264_nvenc')
    preset: str # 인코딩 속도/압축률 트레이드오프를 결정하는 프리셋 (예: 'slow', 'medium')
    crf: int # CRF(Constant Rate Factor) 또는 그에 상응하는 품질 제어 값 (CQ, QP 등)
    audio_option: str # 오디오 스트림 처리 방식 지정 ('Copy Audio', 'Remove Audio')
    adv_opts: Dict[str, Any] # 사용자 정의 고급 인코딩 옵션을 담고 있는 딕셔너리

    metrics: Dict[str, bool] = field(default_factory=dict) # PSNR, SSIM 등 추가적인 품질 메트릭의 계산 여부를 지정하는 딕셔너리
    vmaf_model_path: str = "" # 사용할 특정 VMAF 모델 파일의 경로 (지정하지 않으면 FFmpeg 내장 모델 사용)
    color_info: Dict[str, str] = field(default_factory=dict) # 비디오의 색상 정보(색공간, 색상 프라이머리, 전송 특성 등)를 담고 있는 딕셔너리

    @property
    def encoded_filename(self) -> str:
        """
        이 작업으로 생성될 인코딩된 결과물의 파일명을 생성.
        
        파일명 형식: encoded_{preset}_{crf}.mkv
        예시: encoded_slow_23.mkv, encoded_medium_28.mkv
        """
        return f"encoded_{self.preset}_{self.crf}.mkv"

    @property
    def encoded_path(self) -> str:
        """
        인코딩된 결과물의 전체 절대 경로를 반환.
        
        임시 디렉토리와 인코딩된 파일명을 결합하여 완전한 파일 경로를 생성함.
        """
        return os.path.join(self.temp_dir, self.encoded_filename)

    @property
    def vmaf_log_filename(self) -> str:
        """
        VMAF 분석 결과(JSON)를 저장할 로그 파일의 이름을 생성.
        
        파일명 형식: vmaf_{preset}_{crf}.json
        예시: vmaf_slow_23.json, vmaf_medium_28.json
        """
        return f"vmaf_{self.preset}_{self.crf}.json"

    @property
    def vmaf_log_path(self) -> str:
        """
        VMAF 분석 결과 로그 파일의 전체 절대 경로를 반환.
        
        임시 디렉토리와 VMAF 로그 파일명을 결합하여 완전한 파일 경로를 생성함.
        """
        return os.path.join(self.temp_dir, self.vmaf_log_filename)

# 파일 경로에 사용하기 안전한 문자열로 변환하는 헬퍼 함수
def sanitize_for_path(text):
    """
    문자열을 파일 시스템에서 안전하게 사용할 수 있도록 정규화.
    
    공백을 밑줄로 변환하고, 파일명으로 부적합한 특수문자들을 제거하여 Windows 환경에서 파일 시스템 오류를 방지함.
    
    Args:
        text (str): 정규화할 원본 문자열
        
    Returns:
        str: 경로에 사용 가능한 안전한 문자열 (최대 길이 제한 적용)
    """
    # 문자열 정규화 (공백 및 특수문자 제거)
    text = re.sub(r'\s+', '_', text) # 하나 이상의 연속된 공백 문자를 '_'로 대체
    text = re.sub(r'[^\w\-_.]', '', text) # 단어 문자(\w), 밑줄, 하이픈, 점을 제외한 모든 문자를 제거
    
    # 최종 문자열을 최대 길이에 맞게 잘라 반환
    return text[:APP_CONFIG['max_filename_length']] # 보안 및 경로 길이 제한을 위해 최대 길이로 자름

def _get_subprocess_startupinfo():
    """
    Windows 환경에서 subprocess 실행 시 콘솔 창을 숨기는 STARTUPINFO 객체를 설정.
    
    FFmpeg 등의 명령줄 도구 실행 시 불필요한 콘솔 창이 나타나지 않도록 하여 사용자 경험을 개선함.
    
    Returns:
        subprocess.STARTUPINFO or None: Windows 환경에서는 STARTUPINFO 객체, 다른 환경에서는 None
    """
    # Windows 환경일 경우에만 콘솔 창을 숨기는 설정 적용
    if os.name == 'nt': # 운영 체제가 Windows인 경우에만 적용
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW # 프로세스 생성 시 창을 숨기는 플래그 설정
        return startupinfo
    
    # 그 외 운영체제에서는 기본값(None)을 반환
    return None # Windows가 아닌 경우 None을 반환하여 기본 동작을 따르도록 함

# Tkinter 위젯에 마우스를 올렸을 때 툴팁 표시하는 헬퍼 클래스
class ToolTip:
    """
    Tkinter 위젯에 마우스 호버 시 툴팁을 표시하는 기능을 제공하는 클래스.

    마우스가 위젯 위에 올라가면 설명 텍스트가 포함된 팝업 창을 표시하고, 마우스가 벗어나면 자동으로 숨김.
    콤보박스 클릭 등 다양한 GUI 상호작용 상황에서 안정적으로 동작하도록 여러 이벤트를 처리함.
    """

    def __init__(self, widget, text):
        """
        ToolTip 객체를 초기화하고 위젯에 마우스 이벤트를 바인딩.

        Args:
            widget: 툴팁을 적용할 대상 Tkinter 위젯
            text: 툴팁에 표시할 설명 문자열
        """
        self.widget = widget  # 툴팁을 적용할 대상 Tkinter 위젯
        self.text = text  # 툴팁에 표시할 문자열
        self.tooltip_window = None  # 툴팁을 표시하는 Toplevel 창 객체에 대한 참조
        
        self.widget.bind("<Enter>", self.show_tooltip)  # 마우스 커서가 위젯 영역에 진입할 때 툴팁 표시
        self.widget.bind("<Leave>", self.hide_tooltip)  # 마우스 커서가 위젯 영역에서 이탈할 때 툴팁 숨김
        # 콤보박스와 같이 복잡한 위젯에서 <Leave> 이벤트가 누락될 수 있는 경우에 대비하여 추가 이벤트를 바인딩함.
        self.widget.bind("<ButtonPress>", self.hide_tooltip) # 위젯 클릭 시 툴팁 숨김
        self.widget.bind("<FocusOut>", self.hide_tooltip) # 위젯이 포커스를 잃을 때 툴팁 숨김

    def show_tooltip(self, event=None):
        """
        마우스 커서 근처에 제목 표시줄이 없는 Toplevel 창을 생성하고 툴팁 텍스트를 표시.

        마우스가 위젯 위에 올라갔을 때 호출되며, 사용자에게 도움말 정보를 제공하는 작은 팝업 창을 생성함.
        호출 시점에 기존 툴팁이 남아있으면 먼저 제거하여 중복 생성을 방지함.

        Args:
            event: 마우스 이벤트 객체 (사용되지 않음)
        """
        # 이벤트 누락으로 인해 기존 툴팁 윈도우가 남아있는 경우를 대비하여 먼저 제거
        if self.tooltip_window:
            self.tooltip_window.destroy()
            self.tooltip_window = None

        # 툴팁이 표시될 화면상의 좌표를 계산
        x, y, _, _ = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + APP_CONFIG['tooltip_offset'] # 위젯의 전역 좌표를 기준으로 툴팁 위치 계산
        y += self.widget.winfo_rooty() + APP_CONFIG['tooltip_offset']

        # 툴팁을 담을 Toplevel 창을 생성하고 설정
        self.tooltip_window = tk.Toplevel(self.widget)
        self.tooltip_window.wm_overrideredirect(True) # 창 관리자 장식(제목 표시줄, 테두리 등) 제거
        self.tooltip_window.wm_geometry(f"+{x}+{y}") # 계산된 위치에 창 배치
        
        # 툴팁 텍스트를 표시할 라벨을 생성하고 창에 배치
        label = tk.Label(self.tooltip_window, text=self.text, justify='left',
                         background="#ffffe0", relief='solid', borderwidth=1,
                         font=("tahoma", "8", "normal"))
        label.pack(ipadx=1)

    def hide_tooltip(self, event=None):
        """
        표시된 툴팁 창을 제거.

        마우스가 위젯에서 벗어났을 때 호출되며, 툴팁 창을 안전하게 제거함.
        창이 존재하는 경우에만 제거 작업을 수행하여 오류를 방지함.

        Args:
            event: 마우스 이벤트 객체 (사용되지 않음)
        """
        # 툴팁 창이 존재하는 경우에만 창을 제거
        tw = self.tooltip_window
        self.tooltip_window = None # 참조를 먼저 None으로 설정하여 중복 호출을 방지
        if tw:
            tw.destroy()



# ==============================================================================
# 3. GUI 팝업 윈도우 클래스
# ==============================================================================
# 애플리케이션의 모든 팝업 창 위한 기본 클래스
class BaseToplevel(tk.Toplevel):
    """
    애플리케이션 내 Toplevel 창들의 공통 속성(제목, 모달 동작, 중앙 정렬 등)을 정의하는 기본 클래스.

    모든 팝업 창이 공통적으로 가져야 할 기능들을 제공하며, 창의 중앙 정렬, 모달 동작, 제목 설정 등을 표준화함으로써 일관된 사용자 경험을 제공함.
    """

    def __init__(self, parent, title, width, height):
        """
        BaseToplevel 객체를 초기화하고 기본 속성을 설정.

        Args:
            parent: 부모 Tkinter 위젯
            title: 창 제목
            width: 창 너비
            height: 창 높이
        """
        super().__init__(parent)

        # 창을 만들자마자 숨김 (설정 중 깜빡임을 방지하고 최종 상태만 보여주기 위함)
        self.withdraw()

        # 창의 기본 속성(제목, 부모 종속성, 모달 동작)을 설정
        self.title(title)
        self.transient(parent)  # 부모 창에 종속되도록 설정
        self.grab_set()  # 모달 창으로 설정 (부모 창과 상호작용 차단)

        # 창을 부모 창의 중앙에 위치시키는 메서드를 호출
        self.center_window(parent, width, height)

        # 모든 설정이 완료된 후 창을 다시 화면에 표시
        self.deiconify()

    def center_window(self, parent, w, h):
        """
        창을 부모 창의 정중앙에 위치시키는 메서드.

        팝업 창이 부모 창의 정확한 중앙에 표시되도록 위치를 계산하고 설정함.
        부모 창의 크기와 위치를 기준으로 하여 사용자가 팝업 창을 쉽게 찾을 수 있도록 함.

        Args:
            parent: 부모 Tkinter 위젯 (위치 계산의 기준)
            w: 팝업 창의 너비
            h: 팝업 창의 높이
        """
        # 창 상태 업데이트 및 최소 크기 설정
        self.update_idletasks()  # 위젯 업데이트 완료 대기
        self.minsize(w, h)  # 최소 크기 설정

        # 부모 창의 위치와 크기 정보 가져오기
        px, py = parent.winfo_x(), parent.winfo_y()  # 부모 창의 위치
        pw, ph = parent.winfo_width(), parent.winfo_height()  # 부모 창의 크기

        # 부모 창을 기준으로 중앙 좌표 계산
        x = px + (pw // 2) - (w // 2)  # 중앙 X 좌표 계산
        y = py + (ph // 2) - (h // 2)  # 중앙 Y 좌표 계산

        # 계산된 위치와 크기를 현재 창에 적용
        self.geometry(f'{w}x{h}+{x}+{y}')  # 창 크기와 위치 설정


# FFmpeg 실행 로그를 보여주는 창 클래스
class LogViewerWindow(BaseToplevel):
    """
    FFmpeg 명령어 실행 시 생성된 로그를 표시하는 전용 팝업 창 클래스.

    인코딩 작업 중 발생한 FFmpeg 로그를 사용자가 읽기 쉽게 스크롤 가능한 텍스트 영역에 표시하며, 로그 내용의 수정을 방지하여 데이터 무결성을 보장함.
    """

    def __init__(self, parent, log_content):
        """
        LogViewerWindow 객체를 초기화하고 로그 내용을 표시.

        Args:
            parent: 부모 Tkinter 위젯
            log_content: 표시할 FFmpeg 로그 내용
        """
        # 부모 클래스(BaseToplevel)를 초기화하여 창의 기본 속성을 설정
        super().__init__(
            parent,
            "FFmpeg Command Log",
            APP_CONFIG["log_window_size"][0],
            APP_CONFIG["log_window_size"][1],
        )

        # 로그 내용을 표시할 스크롤 가능한 텍스트 영역 위젯을 생성하고 배치
        text_area = scrolledtext.ScrolledText(
            self, wrap=tk.WORD, width=100, height=30, font=("Consolas", 9)
        )
        text_area.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)

        # 텍스트 영역에 전달받은 로그 내용을 삽입하고, 수정 불가능하도록 읽기 전용으로 설정
        text_area.insert(tk.INSERT, log_content)
        text_area.config(state=tk.DISABLED)

        # 창을 닫는 'Close' 버튼을 생성하고 배치
        close_button = ttk.Button(self, text="Close", command=self.destroy)
        close_button.pack(pady=(0, 10))


# 인코딩 결과를 그래프로 시각화하는 창 클래스
class GraphWindow(BaseToplevel):
    """
    Matplotlib을 사용하여 인코딩 결과 데이터를 2D 산점도(scatter plot)로 시각화하는 창 클래스.
    
    다양한 인코딩 설정(프리셋, CRF 등)에 따른 품질 메트릭(VMAF, PSNR, SSIM 등)과
    파일 크기 간의 관계를 직관적인 그래프로 표시함.

    사용자는 X축과 Y축을 자유롭게 선택하여 원하는 관점에서 데이터를 분석할 수 있으며,
    파레토 프론트와 같은 최적화 지점도 시각적으로 확인 가능함.
    """
    def __init__(self, parent, results, formats):
        """
        GraphWindow 객체를 초기화하고 그래프 데이터를 설정.
        
        Args:
            parent: 부모 Tkinter 위젯
            results: 그래프로 시각화할 인코딩 결과 데이터 리스트
            formats: 각 메트릭의 표시 형식을 정의하는 딕셔너리
        """
        super().__init__(parent, "Results Graph", APP_CONFIG['graph_window_size'][0], APP_CONFIG['graph_window_size'][1])
        self.results = results # 그래프로 시각화할 원본 데이터 (결과 딕셔너리의 리스트)
        self.formats = formats # 툴팁에 숫자 서식을 지정하기 위한 딕셔너리

        # 그래프의 X, Y축으로 선택 가능한 메트릭 목록. (표시 이름: (내부 데이터 키, 값이 높을수록 좋은지 여부))
        # 각 메트릭은 (데이터_키, 높을수록_좋은지_여부) 형태의 튜플로 정의됨
        self.plot_options = {
            "CRF": ('crf', False),           # CRF 값 (낮을수록 좋음)
            "VMAF Score": ('vmaf', True),    # VMAF 점수 (높을수록 좋음)
            "VMAF 1% Low": ('vmaf_1_low', True), # VMAF 하위 1% 점수 (높을수록 좋음)
            "Block Score": ('block_score', False), # 블록킹 점수 (낮을수록 좋음)
            "File Size (MB)": ('size_mb', False), # 파일 크기 (낮을수록 좋음)
            "Efficiency (VMAF/MB)": ('efficiency', True), # 효율성 (높을수록 좋음)
            "PSNR": ('psnr', True),          # PSNR 점수 (높을수록 좋음)
            "SSIM": ('ssim', True)           # SSIM 점수 (높을수록 좋음)
        }
        
        # X축과 Y축 선택, 파레토 프론트 표시 여부를 위한 Tkinter 제어 변수
        self.x_axis_var = tk.StringVar(value="File Size (MB)") # X축 선택 변수 (기본값: 파일 크기)
        self.y_axis_var = tk.StringVar(value="VMAF Score")     # Y축 선택 변수 (기본값: VMAF 점수)
        self.show_pareto_var = tk.BooleanVar(value=True)       # 파레토 프론트 표시 여부 (기본값: 표시)
        
        # 마우스 호버 시 툴팁 표시와 관련된 Matplotlib 객체 참조 변수
        self.tooltip_annotation = None # 툴팁 텍스트를 담는 주석 객체
        self.scatter = None # 산점도 플롯 객체
        self.fig = None # Matplotlib Figure 객체

        self.create_widgets()
        self.protocol("WM_DELETE_WINDOW", self.on_close) # 창 닫기 버튼 클릭 시 on_close 메서드 호출

    def _is_figure_valid(self):
        """
        그래프 figure 객체가 유효한지 확인하는 헬퍼 메서드.
        
        Returns:
            bool: figure 객체가 유효하면 True, 그렇지 않으면 False
        """
        return (hasattr(self, 'fig') and 
                self.fig and 
                self.fig.canvas and 
                self.fig.canvas.manager)

    def on_close(self):
        """
        창이 닫힐 때 Matplotlib 관련 이벤트 핸들러를 정리하여 메모리 누수 방지.
        
        이 메서드는 창이 닫힐 때 호출되며, Matplotlib의 이벤트 핸들러와 관련된 메모리 리소스를 안전하게 해제함.
        특히 키보드 이벤트 핸들러의 연결을 해제하여 메모리 누수와 예상치 못한 동작을 방지함.
        """
        # 그래프 창의 키보드 이벤트 핸들러를 안전하게 해제
        if self._is_figure_valid():
            handler_id = getattr(self.fig.canvas.manager, 'key_press_handler_id', None)
            if handler_id is not None:
                self.fig.canvas.mpl_disconnect(handler_id)
        
        self.destroy()

    def create_widgets(self):
        """
        그래프 창의 UI 위젯들(축 선택 콤보박스, 그래프 캔버스, 툴바 등)을 생성.
        
        이 메서드는 그래프 창의 모든 사용자 인터페이스 요소를 구성하며,
        축 선택, 파레토 프론트 표시 옵션, 그래프 캔버스, 네비게이션 툴바 등을 포함함.
        """
        # 상단 컨트롤 프레임 (X/Y축 선택)
        controls_frame = ttk.Frame(self, padding=(10, 10, 10, 0))
        controls_frame.pack(fill=tk.X)

        ttk.Label(controls_frame, text="X-Axis:").pack(side=tk.LEFT, padx=(0, 5))
        x_combo = ttk.Combobox(controls_frame, textvariable=self.x_axis_var, values=list(self.plot_options.keys()), state="readonly", width=20)
        x_combo.pack(side=tk.LEFT, padx=(0, 20))
        x_combo.bind("<<ComboboxSelected>>", self._redraw_plot) # 선택 변경 시 그래프 다시 그리기

        ttk.Label(controls_frame, text="Y-Axis:").pack(side=tk.LEFT, padx=(0, 5))
        y_combo = ttk.Combobox(controls_frame, textvariable=self.y_axis_var, values=list(self.plot_options.keys()), state="readonly", width=20)
        y_combo.pack(side=tk.LEFT, padx=(0, 20))
        y_combo.bind("<<ComboboxSelected>>", self._redraw_plot)
        
        pareto_check = ttk.Checkbutton(controls_frame, text="Show Pareto Front", variable=self.show_pareto_var, command=self._redraw_plot)
        pareto_check.pack(side=tk.LEFT, padx=(10, 0))
        ToolTip(pareto_check, "Highlights the most efficient encodes (no other point is better on both axes).")

        # Matplotlib Figure와 Tkinter용 Canvas 생성
        self.fig = Figure(figsize=(8, 6), dpi=100)
        self.ax = self.fig.add_subplot(111)

        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=10, pady=5)

        self.toolbar = NavigationToolbar2Tk(self.canvas, self) # Matplotlib 네비게이션 툴바 추가
        self.toolbar.update()
        
        # 마우스 호버 시 툴팁으로 사용될 주석(annotation) 객체를 생성하고 숨김 상태로 초기화
        self.tooltip_annotation = self.ax.annotate("", xy=(0,0), xytext=(0,0),
            textcoords="offset points",
            bbox=dict(boxstyle="round,pad=0.5", fc="yellow", alpha=0.9),
            # 툴팁 화살표를 약간 구부려 커서와의 겹침을 최소화
            arrowprops=dict(arrowstyle="->", connectionstyle="arc3,rad=0.2"))
        self.tooltip_annotation.set_visible(False)
        
        self.fig.canvas.mpl_connect("motion_notify_event", self._on_hover) # 마우스 움직임 이벤트를 _on_hover 메서드에 연결

        self._redraw_plot() # 초기 그래프 그리기

    def _redraw_plot(self, event=None):
        """
        사용자 선택에 따라 그래프를 완전히 다시 그림.
        
        이 메서드는 사용자가 X축, Y축, 또는 파레토 프론트 표시 옵션을 변경할 때 호출됨.
        선택된 축에 맞게 데이터를 재구성하고, 파레토 프론트를 계산하여 새로운 그래프를 생성함.
        
        Args:
            event: Tkinter 이벤트 객체 (사용되지 않음)
        """
        if self.x_axis_var.get() == self.y_axis_var.get():
            messagebox.showwarning("Selection Error", "X and Y axes cannot be the same.", parent=self)
            return

        # 선택된 축에 대한 정보와 데이터 추출
        x_display = self.x_axis_var.get() # 사용자가 선택한 X축 메트릭 이름
        y_display = self.y_axis_var.get() # 사용자가 선택한 Y축 메트릭 이름
        x_key, _ = self.plot_options[x_display] # X축 메트릭의 내부 데이터 키
        y_key, _ = self.plot_options[y_display] # Y축 메트릭의 내부 데이터 키
        x_vals = [r.get(x_key, 0) for r in self.results] # 모든 결과에서 X축 값 추출
        y_vals = [r.get(y_key, 0) for r in self.results] # 모든 결과에서 Y축 값 추출
        color_data = [r.get('vmaf', r.get('efficiency', 0)) for r in self.results] # 점의 색상을 결정할 데이터 (VMAF 우선, 없으면 효율성)

        # 그래프 초기화 및 산점도 생성
        self.ax.clear() # 이전 그래프 내용을 모두 지움
        self.scatter = self.ax.scatter(x_vals, y_vals, c=color_data, cmap='viridis_r', alpha=0.7) # 산점도 생성 (viridis_r 컬러맵 사용)
        
        # 그래프 제목, 라벨, 그리드 설정
        self.ax.set_title(f'{y_display} vs {x_display}') # 그래프 제목 설정
        self.ax.set_xlabel(x_display) # X축 라벨 설정
        self.ax.set_ylabel(y_display) # Y축 라벨 설정
        self.ax.grid(True) # 격자 표시 활성화
        
        # 파레토 프론트 계산 및 표시
        if self.show_pareto_var.get(): # 파레토 프론트 표시 옵션이 활성화된 경우
            pareto_x, pareto_y = self._calculate_pareto_front(x_vals, y_vals) # 파레토 프론트 계산
            if pareto_x: # 파레토 프론트가 존재하는 경우
                self.ax.plot(pareto_x, pareto_y, 'r-o', label='Pareto Front', markersize=4, linewidth=1.5, alpha=0.8) # 빨간색 선과 원으로 파레토 프론트 표시
                self.ax.legend() # 범례 표시
        
        # 툴팁 주석 객체 재생성
        self.tooltip_annotation = self.ax.annotate("", xy=(0,0), xytext=(0,0), # 빈 툴팁 주석 객체 생성
            textcoords="offset points", # 텍스트 위치를 오프셋 포인트로 설정
            bbox=dict(boxstyle="round,pad=0.5", fc="yellow", alpha=0.9), # 노란색 둥근 배경 박스
            arrowprops=dict(arrowstyle="->", connectionstyle="arc3,rad=0.2")) # 화살표 스타일 설정
        self.tooltip_annotation.set_visible(False) # 초기에는 툴팁 숨김

        self.canvas.draw() # 캔버스에 변경 사항을 반영하여 다시 그림

    def _calculate_pareto_front(self, x_vals, y_vals):
        """
        주어진 2D 데이터 포인트 집합으로부터 파레토 프론트(Pareto front)를 계산.
        
        파레토 프론트는 어떤 다른 점에 의해 모든 축에서 동시에 열등하지 않은 점들의 집합임.
        (예를 들어, VMAF는 더 높으면서 파일 크기는 더 작은 점이 존재하지 않는 점들이 파레토 프론트를 구성함.
        이는 최적화 문제에서 가장 효율적인 해들의 집합을 나타냄.)
        
        Args:
            x_vals: X축 값들의 리스트
            y_vals: Y축 값들의 리스트
            
        Returns:
            tuple: (파레토_프론트_X값들, 파레토_프론트_Y값들) 또는 빈 리스트들
        """
        # 현재 선택된 축의 특성(값이 높을수록 좋은지 여부)을 가져옴
        x_display = self.x_axis_var.get() # 현재 선택된 X축 메트릭 이름
        y_display = self.y_axis_var.get() # 현재 선택된 Y축 메트릭 이름
        _, x_higher_is_better = self.plot_options[x_display] # X축에서 값이 높을수록 좋은지 여부
        _, y_higher_is_better = self.plot_options[y_display] # Y축에서 값이 높을수록 좋은지 여부

        # X축을 기준으로 점들을 정렬
        points = sorted(zip(x_vals, y_vals), key=lambda p: p[0], reverse=x_higher_is_better)
        
        # 파레토 프론트 계산
        pareto_front = [] # 파레토 프론트에 속하는 점들을 저장할 리스트
        best_y_so_far = -float('inf') if y_higher_is_better else float('inf') # Y축 최적값 초기화

        for x, y in points: # 정렬된 점들을 순회
            is_better = (y > best_y_so_far) if y_higher_is_better else (y < best_y_so_far) # Y축 기준으로 더 좋은지 판단
            if is_better: # 더 우월한 경우
                pareto_front.append((x, y)) # 파레토 프론트에 점 추가
                best_y_so_far = y # 최적 Y값 업데이트
        
        if not pareto_front: # 파레토 프론트가 비어있는 경우
            return [], [] # 빈 리스트 반환

        return zip(*pareto_front) # x, y 좌표 리스트로 분리하여 반환.
        
    def _on_hover(self, event):
        """
        그래프의 데이터 포인트 위에 마우스를 올렸을 때 해당 점의 상세 정보를 툴팁으로 표시.
        
        이 메서드는 마우스 움직임 이벤트에 의해 호출되며, 마우스가 데이터 포인트 위에 있을 때
        해당 포인트의 모든 메트릭 정보를 상세한 툴팁으로 표시함. 마우스가 포인트에서 벗어나면
        툴팁을 자동으로 숨김.
        
        Args:
            event: Matplotlib 마우스 이벤트 객체
        """
        # 마우스가 그래프 영역 밖에 있으면 즉시 종료
        if event.inaxes != self.ax: # 마우스가 그래프 영역 밖에 있으면 툴팁 숨김
            if self.tooltip_annotation.get_visible(): # 툴팁이 현재 보이는 상태라면
                self.tooltip_annotation.set_visible(False) # 툴팁 숨김
                self.canvas.draw_idle() # 캔버스 다시 그리기
            return # 함수 종료

        is_visible = self.tooltip_annotation.get_visible() # 현재 툴팁 표시 상태 확인
        contains, ind_info = self.scatter.contains(event) # 마우스 위치에 데이터 포인트가 있는지 확인

        if contains: # 마우스가 데이터 포인트 위에 있으면
            # 포인트 정보 추출
            point_index = ind_info['ind'][0] # 마우스가 가리키는 포인트의 인덱스
            pos = self.scatter.get_offsets()[point_index] # 해당 포인트의 좌표 위치
            point_data = self.results[point_index] # 해당 포인트의 데이터

            # 툴팁 텍스트 생성
            tooltip_text = ( # 툴팁에 표시할 텍스트 구성
                f"Preset: {point_data.get('preset', '')}\n"
                f"CRF: {point_data.get('crf', 0)}\n"
                f"VMAF: {point_data.get('vmaf', 0):{self.formats['vmaf']}} (1% Low: {point_data.get('vmaf_1_low', 0):{self.formats['vmaf_1_low']}})\n"
                f"PSNR: {point_data.get('psnr', 0):{self.formats['psnr']}}\n"
                f"SSIM: {point_data.get('ssim', 0):{self.formats['ssim']}}\n"
                f"Block Score: {point_data.get('block_score', 0):{self.formats['block_score']}}\n"
                f"Size: {point_data.get('size_mb', 0):{self.formats['size_mb']}} MB\n"
                f"Efficiency: {point_data.get('efficiency', 0):{self.formats['efficiency']}}"
            )
            
            # 툴팁 위치 및 내용 설정
            self.tooltip_annotation.xy = pos # 툴팁 위치를 포인트 위치로 설정
            self.tooltip_annotation.set_text(tooltip_text) # 툴팁 텍스트 설정
            
            # 툴팁이 커서를 가리지 않도록 위치 동적 조정
            padding = APP_CONFIG['tooltip_padding'] # 툴팁과 마우스 커서 사이의 여백
            bbox = self.ax.get_window_extent() # 그래프 영역의 경계 상자
            
            if event.x > bbox.x0 + bbox.width / 2: # 마우스가 그래프 오른쪽 절반에 있으면
                x_offset = -padding; self.tooltip_annotation.set_horizontalalignment('right') # 툴팁을 왼쪽으로 배치
            else: # 마우스가 그래프 왼쪽 절반에 있으면
                x_offset = padding; self.tooltip_annotation.set_horizontalalignment('left') # 툴팁을 오른쪽으로 배치

            if event.y > bbox.y0 + bbox.height / 2: # 마우스가 그래프 아래쪽 절반에 있으면
                y_offset = -padding; self.tooltip_annotation.set_verticalalignment('top') # 툴팁을 위쪽으로 배치
            else: # 마우스가 그래프 위쪽 절반에 있으면
                y_offset = padding; self.tooltip_annotation.set_verticalalignment('bottom') # 툴팁을 아래쪽으로 배치
            
            self.tooltip_annotation.set_position((x_offset, y_offset)) # 계산된 오프셋으로 툴팁 위치 설정
            
            # 툴팁 표시
            self.tooltip_annotation.set_visible(True) # 툴팁 표시
            self.canvas.draw_idle() # 캔버스 다시 그리기

        elif is_visible: # 마우스가 포인트에서 벗어났고, 툴팁이 보이는 상태라면 툴팁 숨김
            self.tooltip_annotation.set_visible(False) # 툴팁 숨김
            self.canvas.draw_idle() # 캔버스 다시 그리기


# 전체 영상에 적용할 FFmpeg 명령어를 생성하고 보여주는 창 클래스
class CommandGeneratorWindow(BaseToplevel):
    """
    사용자가 선택한 인코딩 설정을 전체 비디오에 적용할 FFmpeg 명령어를 생성하여 보여주는 창 클래스.
    
    최적화 결과에서 선택된 설정을 기반으로 전체 비디오에 적용할 수 있는 완전한 FFmpeg 명령어를 생성하고 표시함.
    사용자는 생성된 명령어를 복사하여 터미널이나 배치 파일에서 직접 실행할 수 있음.
    """
    def __init__(self, parent, command):
        """
        CommandGeneratorWindow 객체를 초기화하고 UI를 구성.
        
        Args:
            parent: 부모 Tkinter 위젯
            command: 표시할 FFmpeg 명령어 문자열
        """
        # 부모 클래스(BaseToplevel)를 초기화하여 창의 기본 속성을 설정
        super().__init__(parent, "Generated FFmpeg Command for Full Video", APP_CONFIG['command_window_size'][0], APP_CONFIG['command_window_size'][1])

        # 상단에 안내 문구를 표시하는 라벨을 생성하고 배치
        ttk.Label(self, text="Copy the command below to run the final encode on the entire video file:").pack(padx=10, pady=(10,5))

        # FFmpeg 명령어를 표시할 스크롤 가능한 텍스트 영역을 생성하고 설정
        text_area = scrolledtext.ScrolledText(self, wrap=tk.WORD, height=5, font=("Consolas", 10))
        text_area.pack(expand=True, fill=tk.BOTH, padx=10, pady=5)
        text_area.insert(tk.INSERT, command) # 생성된 명령어를 텍스트 영역에 삽입
        text_area.config(state=tk.DISABLED) # 읽기 전용으로 설정

        # 하단 버튼들을 담을 프레임을 생성하고 배치
        button_frame = ttk.Frame(self)
        button_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        # 'Copy'와 'Close' 버튼을 프레임 내에 생성하고 배치
        ttk.Button(button_frame, text="Copy to Clipboard", command=lambda: self.copy_to_clipboard(command)).pack(side=tk.LEFT)
        ttk.Button(button_frame, text="Close", command=self.destroy).pack(side=tk.RIGHT)

    def copy_to_clipboard(self, command):
        """
        명령어를 시스템 클립보드에 복사.
        
        사용자가 'Copy to Clipboard' 버튼을 클릭했을 때 호출되며, 생성된 FFmpeg 명령어를 시스템 클립보드에 복사함.
        복사 완료 후에는 사용자에게 성공 메시지를 표시하여 피드백을 제공함.
        
        Args:
            command: 클립보드에 복사할 FFmpeg 명령어 문자열
        """
        # 클립보드의 내용을 지우고 새로운 명령어로 채움
        self.clipboard_clear() # 클립보드 내용 지우기
        self.clipboard_append(command) # 명령어를 클립보드에 추가
        
        # 사용자에게 복사가 완료되었음을 알림
        messagebox.showinfo("Copied", "Command copied to clipboard.", parent=self)


# 사용자가 수동으로 샘플 구간 설정하는 창 클래스
class ManualTimeSelectorWindow(BaseToplevel):
    """
    사용자가 시:분:초.밀리초 형식으로 샘플의 시작 및 종료 시간을 수동으로 설정하는 창 클래스.
    
    사용자가 원하는 구간을 정확하게 선택할 수 있도록 직관적인 시간 입력 인터페이스를 제공함.
    시, 분, 초, 밀리초를 각각 별도의 스핀박스로 입력받아 정확한 시간 범위를 설정할 수 있으며,
    비디오 길이를 벗어나는 값은 자동으로 조정하여 유효성을 보장함.
    """
    def __init__(self, parent, callback, video_duration, current_start_s, current_end_s):
        """
        ManualTimeSelectorWindow 객체를 초기화하고 시간 입력 UI를 구성.
        
        Args:
            parent: 부모 Tkinter 위젯
            callback: 시간 설정 완료 시 호출될 콜백 함수
            video_duration: 전체 비디오 길이 (초)
            current_start_s: 현재 설정된 시작 시간 (초)
            current_end_s: 현재 설정된 종료 시간 (초)
        """
        super().__init__(parent, "Set Manual Sample Time", APP_CONFIG['time_selector_window_size'][0], APP_CONFIG['time_selector_window_size'][1])
        self.callback = callback # 시간 설정이 완료되면 호출될 함수
        self.video_duration = video_duration # 전체 비디오 길이 (초), 입력값 검증에 사용

        # 현재 시작/종료 시간(초)을 시:분:초.밀리초 형식으로 변환하여 각 Tkinter 변수에 저장.
        s_h, s_m, s_s, s_ms = self._seconds_to_hmsms(current_start_s) # 시작 시간을 시:분:초:밀리초로 분해
        e_h, e_m, e_s, e_ms = self._seconds_to_hmsms(current_end_s) # 종료 시간을 시:분:초:밀리초로 분해

        self.start_h_var = tk.IntVar(value=s_h) # 시작 시간 - 시
        self.start_m_var = tk.IntVar(value=s_m) # 시작 시간 - 분
        self.start_s_var = tk.IntVar(value=s_s) # 시작 시간 - 초
        self.start_ms_var = tk.IntVar(value=s_ms) # 시작 시간 - 밀리초
        self.end_h_var = tk.IntVar(value=e_h) # 종료 시간 - 시
        self.end_m_var = tk.IntVar(value=e_m) # 종료 시간 - 분
        self.end_s_var = tk.IntVar(value=e_s) # 종료 시간 - 초
        self.end_ms_var = tk.IntVar(value=e_ms) # 종료 시간 - 밀리초

        self.create_widgets() # UI 위젯들 생성

    def _seconds_to_hmsms(self, seconds: float) -> Tuple[int, int, int, int]:
        """
        초 단위 시간을 (시, 분, 초, 밀리초) 튜플로 변환.
        
        소수점이 포함된 초 단위 시간을 사용자가 이해하기 쉬운
        시:분:초.밀리초 형식으로 변환함. 예를 들어, 3661.5초는 (1, 1, 1, 500)으로 변환됨.
        
        Args:
            seconds: 변환할 초 단위 시간 (소수점 포함 가능)
            
        Returns:
            Tuple[int, int, int, int]: (시, 분, 초, 밀리초) 형태의 튜플
        """
        h = int(seconds // 3600) # 시간 계산 (3600초 = 1시간)
        m = int((seconds % 3600) // 60) # 분 계산 (60초 = 1분)
        s = int(seconds % 60) # 초 계산 (60초로 나눈 나머지)
        ms = int((seconds - int(seconds)) * 1000) # 밀리초 계산 (소수점 부분을 1000배)
        
        return h, m, s, ms # (시, 분, 초, 밀리초) 튜플 반환

    def create_widgets(self):
        """
        시간 입력을 위한 스핀박스, 라벨, 버튼 등의 위젯들을 생성.
        
        시간 입력 창의 모든 UI 요소를 구성하며,
        시/분/초/밀리초 입력을 위한 스핀박스, 전체 비디오 길이 표시, 확인/취소 버튼 등을 포함함.
        """
        main_frame = ttk.Frame(self, padding=10) # 메인 프레임 생성
        main_frame.pack(fill=tk.BOTH, expand=True) # 메인 프레임 배치

        content_frame = ttk.Frame(main_frame) # 콘텐츠 프레임 생성
        content_frame.pack(fill=tk.BOTH, expand=True) # 콘텐츠 프레임 배치

        # 비디오 전체 길이 정보 표시
        duration_h, duration_m, duration_s, duration_ms = self._seconds_to_hmsms(self.video_duration) # 비디오 전체 길이를 시:분:초:밀리초로 변환
        duration_str = f"{duration_h:02}:{duration_m:02}:{duration_s:02}.{duration_ms:03}" # 시간 문자열 포맷팅
        ttk.Label(content_frame, text=f"Total Video Duration: {duration_str}").pack(anchor='w', pady=(0, 10)) # 전체 비디오 길이 표시 라벨

        # 시작 시간 입력 행
        start_row_frame = ttk.Frame(content_frame) # 시작 시간 입력을 위한 프레임
        start_row_frame.pack(fill=tk.X, anchor='w') # 시작 시간 프레임 배치
        ttk.Label(start_row_frame, text="Start Time:", width=10, anchor='w').pack(side=tk.LEFT, padx=(0, 10)) # 시작 시간 라벨
        start_time_entry = self.create_time_entry_frame(start_row_frame, self.start_h_var, self.start_m_var, self.start_s_var, self.start_ms_var) # 시작 시간 입력 위젯 생성
        start_time_entry.pack(side=tk.LEFT) # 시작 시간 입력 위젯 배치

        # 종료 시간 입력 행
        end_row_frame = ttk.Frame(content_frame) # 종료 시간 입력을 위한 프레임
        end_row_frame.pack(fill=tk.X, anchor='w', pady=(5, 0)) # 종료 시간 프레임 배치
        ttk.Label(end_row_frame, text="End Time:", width=10, anchor='w').pack(side=tk.LEFT, padx=(0, 10)) # 종료 시간 라벨
        end_time_entry = self.create_time_entry_frame(end_row_frame, self.end_h_var, self.end_m_var, self.end_s_var, self.end_ms_var) # 종료 시간 입력 위젯 생성
        end_time_entry.pack(side=tk.LEFT) # 종료 시간 입력 위젯 배치
        
        # 확인/취소 버튼 프레임
        button_frame = ttk.Frame(main_frame) # 버튼들을 담을 프레임 생성
        button_frame.pack(side=tk.BOTTOM, fill=tk.X, anchor='e', pady=(15, 0)) # 버튼 프레임을 하단에 배치
        
        inner_button_frame = ttk.Frame(button_frame) # 버튼들을 담을 내부 프레임 생성
        inner_button_frame.pack(side=tk.RIGHT) # 내부 프레임을 오른쪽에 배치
        ttk.Button(inner_button_frame, text="OK", command=self.on_ok).pack(side=tk.RIGHT) # 확인 버튼
        ttk.Button(inner_button_frame, text="Cancel", command=self.destroy).pack(side=tk.RIGHT, padx=(0, 5)) # 취소 버튼

    def create_time_entry_frame(self, parent, h_var, m_var, s_var, ms_var):
        """시, 분, 초, 밀리초를 입력받는 스핀박스 그룹을 생성하는 헬퍼 메서드."""
        frame = ttk.Frame(parent) # 시간 입력 위젯들을 담을 프레임 생성
        
        self.add_time_spinbox(frame, h_var, 99, 'H').pack(side=tk.LEFT) # 시간 스핀박스 (0-99)
        ttk.Label(frame, text=":").pack(side=tk.LEFT, padx=2) # 시간 구분자
        self.add_time_spinbox(frame, m_var, 59, 'M').pack(side=tk.LEFT) # 분 스핀박스 (0-59)
        ttk.Label(frame, text=":").pack(side=tk.LEFT, padx=2) # 분 구분자
        self.add_time_spinbox(frame, s_var, 59, 'S').pack(side=tk.LEFT) # 초 스핀박스 (0-59)
        ttk.Label(frame, text=".").pack(side=tk.LEFT, padx=2) # 초 구분자
        self.add_time_spinbox(frame, ms_var, 999, 'ms', width=4).pack(side=tk.LEFT) # 밀리초 스핀박스 (0-999)
        
        return frame # 생성된 프레임 반환

    def add_time_spinbox(self, parent, var, max_val, label, width=3):
        """개별 시간 단위(시, 분, 초 등)를 위한 스핀박스와 라벨을 생성."""
        frame = ttk.Frame(parent) # 스핀박스와 라벨을 담을 프레임 생성
        
        spinbox = ttk.Spinbox(frame, from_=0, to=max_val, textvariable=var, width=width) # 스핀박스 생성 (0부터 max_val까지)
        spinbox.pack(side=tk.LEFT) # 스핀박스 배치
        
        ttk.Label(frame, text=label).pack(side=tk.LEFT, padx=(2, 5)) # 단위 라벨 배치
        
        return frame # 생성된 프레임 반환
        
    def on_ok(self):
        """
        'OK' 버튼 클릭 시 입력된 시간을 초 단위로 변환하고 유효성 검사한 후 콜백 함수를 호출.
        
        사용자가 시간 입력을 완료하고 확인 버튼을 클릭했을 때 호출됨.
        입력된 시/분/초/밀리초 값을 초 단위로 변환하고, 비디오 길이 범위 내의 유효한 값인지 검사한 후,
        유효하면 콜백 함수를 호출하여 메인 창에 시간 정보를 전달함.
        """
        try:
            # 입력된 시, 분, 초, 밀리초를 초 단위로 변환
            start_s = (self.start_h_var.get() * 3600 + # 시작 시간을 초 단위로 변환 (시 * 3600)
                       self.start_m_var.get() * 60 + # 분 * 60
                       self.start_s_var.get() + # 초
                       self.start_ms_var.get() / 1000.0) # 밀리초 / 1000
            end_s = (self.end_h_var.get() * 3600 + # 종료 시간을 초 단위로 변환 (시 * 3600)
                     self.end_m_var.get() * 60 + # 분 * 60
                     self.end_s_var.get() + # 초
                     self.end_ms_var.get() / 1000.0) # 밀리초 / 1000

            # 비디오 길이를 벗어나는 값을 자동으로 조정
            start_s = max(0.0, start_s) # 시작 시간이 0보다 작으면 0으로 설정
            end_s = min(self.video_duration, end_s) # 종료 시간이 비디오 길이보다 크면 비디오 길이로 설정

            # 종료 시간이 시작 시간보다 빠르거나 같은 경우 오류 처리
            if end_s <= start_s:
                # 조정된 값을 UI에 다시 반영하여 사용자에게 알림
                s_h, s_m, s_s, s_ms = self._seconds_to_hmsms(start_s) # 시작 시간을 시:분:초:밀리초로 변환
                self.start_h_var.set(s_h); self.start_m_var.set(s_m); self.start_s_var.set(s_s); self.start_ms_var.set(s_ms) # 시작 시간 UI 업데이트
                
                e_h, e_m, e_s, e_ms = self._seconds_to_hmsms(end_s) # 종료 시간을 시:분:초:밀리초로 변환
                self.end_h_var.set(e_h); self.end_m_var.set(e_m); self.end_s_var.set(e_s); self.end_ms_var.set(e_ms) # 종료 시간 UI 업데이트

                messagebox.showerror("Invalid Time Range", # 오류 메시지 표시
                                     "End time must be after the start time.\n\n"
                                     "Note: Values have been automatically adjusted if they were outside the video's duration.",
                                     parent=self)
                return # 함수 종료

            # 유효한 값이면 콜백 함수를 호출하고 창을 닫음
            self.callback(start_s, end_s)
            self.destroy()

        except tk.TclError: # Tkinter 변수 오류 (잘못된 입력값 등)
            messagebox.showerror("Invalid Input", "Please enter valid numbers for time.", parent=self) # 입력 오류 메시지 표시


# VMAF 모델 파일 선택하는 창 클래스
class VMAFModelSelectorWindow(BaseToplevel):
    """
    다운로드된 VMAF 모델 파일들을 계층적 트리뷰로 보여주고 사용자가 선택할 수 있게 하는 창 클래스.
    
    VEO_Resource/vmaf_models 디렉토리에 저장된 다양한 VMAF 모델 파일들을
    트리 구조로 표시하여 사용자가 원하는 모델을 쉽게 찾고 선택할 수 있도록 함.

    모델 선택 시 콜백 함수를 통해 메인 창에 선택된 모델 경로를 전달함.
    """
    def __init__(self, parent, model_dir, callback):
        """
        VMAFModelSelectorWindow 객체를 초기화하고 모델 선택 UI를 구성.
        
        Args:
            parent: 부모 Tkinter 위젯
            model_dir: VMAF 모델 파일들이 저장된 디렉토리 경로
            callback: 모델 선택 완료 시 호출될 콜백 함수
        """
        super().__init__(parent, "Select VMAF Model", APP_CONFIG['vmaf_model_selector_window_size'][0], APP_CONFIG['vmaf_model_selector_window_size'][1])
        self.model_dir = model_dir # VMAF 모델이 저장된 디렉토리 경로
        self.callback = callback # 모델 선택 시 호출될 콜백 함수
        self.selected_path = None # 선택된 모델 파일 경로

        # Treeview 위젯과 스크롤바를 담을 프레임을 생성하고 배치
        tree_frame = ttk.Frame(self)
        tree_frame.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)

        # Treeview 위젯을 생성하고 기본 헤더를 설정
        self.tree = ttk.Treeview(tree_frame)
        self.tree.heading("#0", text="Models")
        
        # Treeview에 연결될 세로 스크롤바를 생성
        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # 스크롤바와 Treeview를 프레임 내에 배치
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)

        # Treeview 아이템 더블 클릭 이벤트를 on_select 메서드에 바인딩
        self.tree.bind("<Double-1>", self.on_select)
        
        # 파일 시스템을 탐색하여 Treeview에 모델 목록을 채움
        self.populate_tree()

        # 하단 버튼들을 담을 프레임을 생성하고 배치
        button_frame = ttk.Frame(self)
        button_frame.pack(fill=tk.X, padx=10, pady=(0,10))
        
        # 'Reset', 'OK', 'Cancel' 버튼을 생성하고 배치
        ttk.Button(button_frame, text="Reset to Default", command=self.on_reset).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="OK", command=self.on_ok).pack(side=tk.RIGHT)
        ttk.Button(button_frame, text="Cancel", command=self.destroy).pack(side=tk.RIGHT, padx=5)

    def populate_tree(self):
        """
        지정된 디렉토리를 재귀적으로 탐색하여 .json, .pkl 확장자를 가진 VMAF 모델 파일을 트리뷰에 표시.
        
        VMAF 모델 디렉토리를 재귀적으로 탐색하여 모든 하위 디렉토리와 모델 파일들을 트리 구조로 구성함.
        디렉토리는 폴더 아이콘으로, 모델 파일은 파일 아이콘으로 표시되어 사용자가 쉽게 구분할 수 있음.
        """
        nodes = {} # 디렉토리 경로와 트리 노드 ID를 매핑하는 딕셔너리
        
        for root, dirs, files in os.walk(self.model_dir): # 모델 디렉토리를 재귀적으로 탐색
            parent_path = os.path.relpath(root, self.model_dir) # 모델 디렉토리 기준 상대 경로
            parent_id = nodes.get(parent_path, "") # 부모 디렉토리의 트리 ID를 찾음
            
            # 하위 디렉토리들을 Treeview에 추가
            for d in dirs:
                dir_path = os.path.join(parent_path, d)
                if dir_path.startswith('.'): dir_path = dir_path[2:] # './' 같은 접두사 제거
                node_id = self.tree.insert(parent_id, "end", text=d, open=False) # 디렉토리 노드 추가 (닫힌 상태)
                nodes[dir_path] = node_id # 경로와 트리 ID를 매핑하여 자식 노드 추가 시 사용
            
            # 파일들을 Treeview에 추가
            for f in sorted(files):
                if f.endswith(('.json', '.pkl')): # VMAF 모델 파일만 필터링
                    # 파일 아이템의 'values' 속성에 전체 파일 경로를 저장
                    self.tree.insert(parent_id, "end", text=f, values=[os.path.join(root, f)]) # 파일 노드 추가

    def on_select(self, event):
        """사용자가 트리뷰에서 파일을 더블 클릭했을 때 실행. 선택된 파일 경로를 콜백으로 전달하고 창을 닫음."""
        item_id = self.tree.focus() # 현재 포커스된 아이템 ID 가져오기
        values = self.tree.item(item_id, "values") # 아이템의 values 속성 가져오기
        
        if values: # 'values'가 있으면 파일 항목임 (폴더는 없음)
            self.selected_path = values[0] # 선택된 파일 경로 저장
            self.callback(self.selected_path) # 콜백 함수 호출하여 선택된 경로 전달
            self.destroy() # 창 닫기
            
    def on_ok(self):
        """'OK' 버튼 클릭 시 현재 선택된 파일 경로를 콜백 함수로 전달."""
        item_id = self.tree.focus() # 현재 포커스된 아이템 ID 가져오기
        
        if item_id: # 아이템이 선택된 경우
            values = self.tree.item(item_id, "values")
            if values: # 파일이 선택된 경우
                self.on_select(None) # on_select 함수 호출하여 선택 처리
            else: # 폴더가 선택된 경우
                messagebox.showwarning("Selection Error", "Please select a model file (.json or .pkl), not a folder.", parent=self)
        else: # 아무것도 선택되지 않은 경우
             messagebox.showwarning("Selection Error", "Please select a model file.", parent=self)
    
    def on_reset(self):
        """'Reset to Default' 버튼 클릭 시 기본값으로 재설정하도록 신호를 보냄 (콜백에 None 전달)."""
        self.callback(None) # None을 전달하여 리셋을 알림
        self.destroy() # 창 닫기


# 코덱별 고급 설정을 위한 창 클래스
class AdvancedSettingsWindow(tk.Toplevel):
    """
    각 비디오 코덱에 특화된 고급 인코딩 옵션들을 동적으로 생성하여 보여주는 창.

    CODEC_CONFIG에 정의된 스키마를 기반으로 UI를 자동으로 구성하며,
    사용자가 선택한 코덱에 따라 적절한 고급 설정 옵션들을 제공함.

    설정은 카테고리별로 그룹화되어 있으며,
    각 옵션에 대한 상세한 설명을 툴팁으로 제공하여 사용자가 쉽게 이해할 수 있도록 함.
    """

    def __init__(self, parent, settings_vars, codec_config, current_codec):
        """
        동적으로 생성되는 고급 설정 창을 초기화.

        Args:
            parent: 부모 tkinter 위젯
            settings_vars: 위젯과 바인딩될 tkinter 변수들의 OrderedDict
            codec_config: CODEC_CONFIG에서 선택된 코덱의 특정 설정 딕셔너리
            current_codec: 현재 선택된 코덱의 이름 (예: "libx265")
        """
        super().__init__(parent)  # 부모 클래스(tk.Toplevel) 초기화
        self.settings_vars = settings_vars  # 설정 값을 담는 tkinter 변수 딕셔너리
        self.codec_config = codec_config  # 현재 코덱의 설정 스키마
        self.current_codec = current_codec  # 현재 코덱의 이름

        # 창의 기본 속성을 설정
        self.title(f"Advanced Settings for {current_codec}")  # 창 제목 설정
        self.transient(parent)  # 부모 창에 종속되도록 설정
        self.grab_set()  # 다른 창과 상호작용할 수 없는 모달 창으로 설정

        # UI 위젯을 생성하고, 창 닫기 이벤트를 바인딩한 후, 창을 화면 중앙에 배치
        self.create_widgets_dynamically()  # 동적으로 위젯들을 생성
        self.protocol("WM_DELETE_WINDOW", self.destroy)  # 창 닫기 버튼(X) 클릭 시 destroy 메서드 호출
        self.center_window(parent)  # 창을 부모 창의 정중앙에 배치

    def center_window(self, parent):
        """
        창을 부모 창의 중앙에 위치시킴.

        고급 설정 창이 부모 창의 정확한 중앙에 표시되도록 위치를 계산하고 설정함.
        부모 창의 크기와 위치를 기준으로 하여 사용자가 설정 창을 쉽게 찾을 수 있도록 함.

        Args:
            parent: 부모 Tkinter 위젯 (위치 계산의 기준)
        """
        self.update_idletasks()  # 위젯의 실제 크기 계산을 위해 대기
        w, h = APP_CONFIG["advanced_settings_window_size"]  # 설정에서 창 크기를 가져옴
        self.minsize(w, h)  # 창의 최소 크기 설정

        # 부모 창의 위치와 크기 정보를 가져옴
        px, py = parent.winfo_x(), parent.winfo_y()  # 부모 창의 좌상단 x, y 좌표
        pw, ph = parent.winfo_width(), parent.winfo_height()  # 부모 창의 너비와 높이

        # 부모 창을 기준으로 중앙 좌표를 계산
        x = px + (pw // 2) - (w // 2)  # 중앙 x 좌표 계산
        y = py + (ph // 2) - (h // 2)  # 중앙 y 좌표 계산

        # 계산된 위치와 크기를 현재 창에 적용
        self.geometry(f"{w}x{h}+{x}+{y}")  # 창의 크기와 위치를 최종 설정

    def create_widgets_dynamically(self):
        """
        codec_config의 'adv_options'에 정의된 스키마를 기반으로 창 레이아웃과 위젯들을 동적으로 생성.

        선택된 코덱의 설정 스키마를 분석하여 필요한 모든 UI 위젯을 자동으로 생성함.
        위젯은 카테고리별로 그룹화되어 있으며, 각 옵션의 타입에 따라
        적절한 입력 위젯(엔트리, 스핀박스, 콤보박스, 체크박스)을 생성함.
        """
        # 창의 메인 레이아웃을 위한 수평 분할 패널(PanedWindow)을 생성
        paned_window = ttk.PanedWindow(self, orient=tk.HORIZONTAL)  # 수평(좌우)으로 분할되는 패널 생성
        paned_window.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)  # 패널을 창에 채워서 배치

        # 왼쪽 패널: 카테고리 네비게이션 트리
        nav_frame = ttk.Frame(paned_window, width=200)  # 카테고리 트리를 담을 프레임 생성
        self.category_tree = ttk.Treeview(nav_frame, show="tree", selectmode="browse")  # 카테고리 목록을 보여줄 트리뷰 생성
        self.category_tree.pack(fill=tk.BOTH, expand=True)  # 트리뷰를 프레임에 채워서 배치
        self.category_tree.bind("<<TreeviewSelect>>", self.on_category_select)  # 카테고리 선택 이벤트를 메서드에 연결
        paned_window.add(nav_frame, weight=1)  # 왼쪽 패널을 PanedWindow에 추가

        # 오른쪽 패널: 실제 설정 위젯들을 담을 컨테이너
        settings_container = ttk.Frame(paned_window)  # 설정 위젯들을 담을 프레임 생성
        paned_window.add(settings_container, weight=3)  # 오른쪽 패널을 PanedWindow에 추가

        # 하단 버튼 프레임
        button_frame = ttk.Frame(self)  # 하단 버튼들을 담을 프레임 생성
        button_frame.pack(fill=tk.X, padx=10, pady=(0, 10), side=tk.BOTTOM)  # 프레임을 창 하단에 배치
        ttk.Button(button_frame, text="Reset All to Defaults", command=self.reset_defaults).pack(side=tk.LEFT)  # '리셋' 버튼 생성 및 배치
        ttk.Button(button_frame, text="OK", command=self.destroy, width=12).pack(side=tk.RIGHT)  # 'OK' 버튼 생성 및 배치

        # 동적 위젯 생성을 위한 변수들을 초기화
        self.category_frames = {}  # 카테고리별 프레임을 저장할 딕셔너리
        row_counters = {}  # 카테고리별 위젯의 행 번호를 추적할 딕셔너리
        adv_options = self.codec_config.get("adv_options", {})  # 현재 코덱의 고급 옵션 스키마를 가져옴

        # 고급 옵션이 없는 코덱의 경우, 안내 메시지를 표시하고 종료
        if not adv_options:
            ttk.Label(settings_container, text=f"No advanced options available for {self.current_codec}.").pack(padx=20, pady=20)
            return

        # 스키마를 순회하며 UI 위젯을 동적으로 생성
        for key, option_data in adv_options.items():
            category = option_data.get("category", "Miscellaneous")  # 현재 옵션의 카테고리를 가져옴 (없으면 'Miscellaneous')

            # 이 카테고리를 처음 만나는 경우, 새 프레임과 트리 항목을 생성
            if category not in self.category_frames:
                frame = ttk.Frame(settings_container, padding=10)  # 해당 카테고리의 위젯들을 담을 프레임 생성
                frame.grid(row=0, column=0, sticky="nsew")  # 모든 카테고리 프레임을 겹쳐서 배치 (tkraise로 하나만 보임)
                settings_container.grid_rowconfigure(0, weight=1)
                settings_container.grid_columnconfigure(0, weight=1)
                
                self.category_frames[category] = frame  # 생성된 프레임을 딕셔너리에 저장
                self.category_tree.insert("", "end", text=category, iid=category)  # 왼쪽 트리에 카테고리 항목 추가
                row_counters[category] = 0  # 해당 카테고리의 행 카운터 초기화

            # 위젯을 배치할 부모 프레임과 행 번호를 결정
            parent_frame = self.category_frames[category]
            parent_frame.columnconfigure(1, weight=1)  # 입력 위젯이 창 크기에 맞게 확장되도록 설정
            row = row_counters[category]

            # 위젯 생성에 필요한 정보들을 스키마에서 추출
            widget_type = option_data.get("widget", "entry")
            label_text = option_data.get("label", key)
            tooltip_text = option_data.get("tooltip", "No description available.")

            # 스키마에 정의된 위젯 타입에 따라 적절한 위젯 생성 헬퍼 메서드를 호출
            if widget_type == "entry":
                self._add_entry(parent_frame, row, label_text, key, tooltip_text)
            elif widget_type == "spinbox_int":
                self._add_spinbox(parent_frame, row, label_text, key, option_data.get("range", (0, 100)), tooltip_text, increment=1)
            elif widget_type == "spinbox_float":
                self._add_spinbox(parent_frame, row, label_text, key, option_data.get("range", (0.0, 10.0)), tooltip_text, increment=0.1)
            elif widget_type == "combobox":
                self._add_combobox(parent_frame, row, label_text, key, option_data.get("values", []), tooltip_text)
            elif widget_type == "checkbutton":
                self._add_checkbutton(parent_frame, row, label_text, key, tooltip_text)
            
            row_counters[category] += 1  # 다음 위젯을 위해 행 카운터 증가
            
        # UI 생성이 완료된 후, 첫 번째 카테고리를 기본으로 선택하고 표시
        if self.category_tree.get_children():
            first_item = self.category_tree.get_children()[0]  # 첫 번째 카테고리 항목을 가져옴
            self.category_tree.selection_set(first_item)  # 첫 번째 항목을 선택 상태로 만듦
            self.category_tree.focus(first_item)  # 첫 번째 항목에 포커스를 줌
            self.on_category_select()  # 선택된 카테고리의 프레임을 화면에 표시

    def on_category_select(self, event=None):
        """
        트리에서 선택된 카테고리에 해당하는 설정 프레임을 화면에 보여줌.

        사용자가 왼쪽 트리에서 카테고리를 선택했을 때 호출되며, 해당 카테고리에 속한
        설정 옵션들을 포함하는 프레임을 화면에 표시함. 다른 카테고리의 프레임은 자동으로 숨겨져서 UI가 깔끔하게 유지됨.

        Args:
            event: 트리 선택 이벤트 객체 (사용되지 않음)
        """
        if not self.category_tree.selection():  # 선택된 항목이 없으면 아무것도 하지 않음
            return
        
        selected_item_id = self.category_tree.selection()[0]  # 선택된 트리 아이템의 ID를 가져옴
        frame_to_show = self.category_frames[selected_item_id]  # ID에 해당하는 프레임을 딕셔너리에서 찾음
        frame_to_show.tkraise()  # 찾은 프레임을 다른 프레임들 위로 올려 화면에 보이게 함

    def reset_defaults(self):
        """
        스키마에 정의된 기본값으로 모든 tkinter 변수를 재설정.

        사용자가 'Reset All to Defaults' 버튼을 클릭했을 때 호출되며, 모든 고급 설정값을
        코덱 스키마에 정의된 기본값으로 되돌림. 이를 통해 사용자가 실험적으로 변경한 설정을 쉽게 초기화할 수 있음.
        """
        adv_options = self.codec_config.get("adv_options", {})  # 현재 코덱의 고급 옵션 스키마를 가져옴
        
        for key, option_data in adv_options.items():  # 모든 옵션을 순회
            if key in self.settings_vars:  # 해당 옵션에 대한 tkinter 변수가 존재하면
                default_value = option_data.get("default", "")  # 스키마에서 기본값을 가져옴
                self.settings_vars[key].set(default_value)  # tkinter 변수의 값을 기본값으로 설정



    # --- 위젯 생성을 위한 헬퍼 메서드들 ---
    def _add_label(self, parent, row, text, tooltip):
        """
        라벨 위젯을 생성하고 그리드에 배치하며 툴팁을 추가.

        고급 설정 UI에서 각 옵션의 설명 라벨을 생성함. 라벨은 왼쪽 열에 배치되며,
        마우스 호버 시 도움말 정보를 제공하는 툴팁이 연결됨.

        Args:
            parent: 라벨을 배치할 부모 위젯
            row: 그리드에서의 행 번호
            text: 라벨에 표시할 텍스트
            tooltip: 툴팁에 표시할 도움말 텍스트
        """
        label = ttk.Label(parent, text=text)  # 라벨 위젯 생성
        label.grid(row=row, column=0, padx=5, pady=5, sticky="w")  # 그리드 레이아웃의 0번 열에 배치
        ToolTip(label, tooltip)  # 생성된 라벨에 툴팁 기능 추가

    def _add_entry(self, parent, row, label_text, var_name, tooltip_text):
        """
        텍스트 입력 필드(Entry) 위젯을 생성하고 그리드에 배치.

        사용자가 자유롭게 텍스트를 입력할 수 있는 엔트리 위젯을 생성함.
        라벨과 함께 오른쪽 열에 배치되며, 설정값을 문자열로 저장함.

        Args:
            parent: 엔트리를 배치할 부모 위젯
            row: 그리드에서의 행 번호
            label_text: 라벨에 표시할 텍스트
            var_name: 설정값을 저장할 변수의 키 이름
            tooltip_text: 툴팁에 표시할 도움말 텍스트
        """
        self._add_label(parent, row, label_text, tooltip_text)  # 왼쪽에 설명 라벨 추가
        
        entry = ttk.Entry(parent, textvariable=self.settings_vars[var_name])  # Entry 위젯 생성
        entry.grid(row=row, column=1, padx=5, pady=5, sticky="ew")  # 그리드 레이아웃의 1번 열에 배치

    def _add_spinbox(self, parent, row, label_text, var_name, range_tuple, tooltip_text, increment):
        """
        숫자 입력을 위한 스핀박스 위젯을 생성하고 그리드에 배치.

        사용자가 지정된 범위 내에서 숫자를 선택할 수 있는 스핀박스를 생성함.
        정수 또는 실수 값을 입력할 수 있으며, 위/아래 화살표로 값을 조정할 수 있음.

        Args:
            parent: 스핀박스를 배치할 부모 위젯
            row: 그리드에서의 행 번호
            label_text: 라벨에 표시할 텍스트
            var_name: 설정값을 저장할 변수의 키 이름
            range_tuple: (최소값, 최대값) 튜플
            tooltip_text: 툴팁에 표시할 도움말 텍스트
            increment: 화살표 클릭 시 증가/감소할 값의 크기
        """
        self._add_label(parent, row, label_text, tooltip_text)  # 왼쪽에 설명 라벨 추가
        
        spinbox = ttk.Spinbox(parent, from_=range_tuple[0], to=range_tuple[1], textvariable=self.settings_vars[var_name], width=10, increment=increment)  # Spinbox 위젯 생성
        spinbox.grid(row=row, column=1, padx=5, pady=5, sticky="w")  # 그리드 레이아웃의 1번 열에 배치

    def _add_combobox(self, parent, row, label_text, var_name, values, tooltip_text):
        """
        드롭다운 선택을 위한 콤보박스 위젯을 생성하고 그리드에 배치.

        사용자가 미리 정의된 값들 중에서 하나를 선택할 수 있는 콤보박스를 생성함.
        기본값이 비어있는 경우 빈 항목을 목록에 추가하여 사용자가 설정을 건너뛸 수 있도록 함.

        Args:
            parent: 콤보박스를 배치할 부모 위젯
            row: 그리드에서의 행 번호
            label_text: 라벨에 표시할 텍스트
            var_name: 설정값을 저장할 변수의 키 이름
            values: 선택 가능한 값들의 리스트
            tooltip_text: 툴팁에 표시할 도움말 텍스트
        """
        self._add_label(parent, row, label_text, tooltip_text)  # 왼쪽에 설명 라벨 추가
        
        display_values = values  # 콤보박스에 표시할 값 목록
        if self.settings_vars[var_name].get() == "" and "" not in values:  # 기본값이 빈 문자열("")이고, 목록에 ""이 없는 경우
            display_values = [""] + values  # 목록 맨 앞에 빈 항목을 추가
            
        combo = ttk.Combobox(parent, textvariable=self.settings_vars[var_name], values=display_values, state="readonly")  # Combobox 위젯 생성
        combo.grid(row=row, column=1, padx=5, pady=5, sticky="ew")  # 그리드 레이아웃의 1번 열에 배치

    def _add_checkbutton(self, parent, row, label_text, var_name, tooltip_text):
        """
        체크박스 위젯을 생성하고 그리드에 배치하며 툴팁을 추가.

        사용자가 옵션을 켜거나 끌 수 있는 체크박스를 생성함.
        체크박스는 라벨과 입력 필드를 모두 포함하므로 2열에 걸쳐 배치되며,
        마우스 호버 시 도움말 정보를 제공하는 툴팁이 연결됨.

        Args:
            parent: 체크박스를 배치할 부모 위젯
            row: 그리드에서의 행 번호
            label_text: 체크박스에 표시할 텍스트
            var_name: 설정값을 저장할 변수의 키 이름
            tooltip_text: 툴팁에 표시할 도움말 텍스트
        """
        check = ttk.Checkbutton(parent, text=label_text, variable=self.settings_vars[var_name])  # Checkbutton 위젯 생성
        check.grid(row=row, column=0, columnspan=2, padx=5, pady=5, sticky="w")  # 그리드 레이아웃의 0, 1번 열을 모두 차지하도록 배치
        ToolTip(check, tooltip_text)  # 생성된 체크박스에 툴팁 기능 추가



# ==============================================================================
# 4. FFmpeg 명령어 빌더
# ==============================================================================
# FFmpeg 명령어를 생성하는 클래스
class FFmpegCommandBuilder:
    """
    주어진 EncodingTask의 정보를 바탕으로 다양한 FFmpeg 명령어 리스트를 동적으로 생성하는 클래스.
    """
    def __init__(self, task: EncodingTask, full_video_path: str = None):
        """
        특정 인코딩 작업을 위한 명령어 빌더를 초기화.

        Args:
            task: 모든 작업 파라미터를 담고 있는 EncodingTask 데이터클래스 인스턴스.
            full_video_path: 최종 명령어를 생성할 때 사용할 전체 비디오 파일 경로.
        """
        self.task = task # 인코딩 작업에 필요한 모든 정보를 담은 EncodingTask 객체
        self.is_for_full_video = bool(full_video_path) # 샘플 영상이 아닌 전체 영상용 명령어인지 여부
        self.video_path = full_video_path if self.is_for_full_video else os.path.basename(task.sample_path) # 명령어에 사용할 입력 비디오 경로
        self.codec_config = VideoOptimizerApp.CODEC_CONFIG.get(task.codec, {}) # 현재 코덱에 대한 설정 스키마

    def _is_libx264_vbv_option(self, ffmpeg_param: str, user_value_str: str) -> bool:
        """
        libx264의 VBV 옵션인지 확인하는 헬퍼 메서드.

        Args:
            ffmpeg_param: FFmpeg 파라미터 이름
            user_value_str: 사용자 입력 값

        Returns:
            bool: libx264의 VBV 옵션이면 True, 그렇지 않으면 False
        """
        return (self.task.codec == 'libx264' and 
                ffmpeg_param in ['vbv-maxrate', 'vbv-bufsize'] and 
                user_value_str != "0")

    def _build_advanced_params(self) -> List[str]:
        """
        코덱 스키마를 기반으로 FFmpeg 고급 파라미터 리스트를 동적으로 생성.

        사용자가 설정한 고급 옵션들을 FFmpeg 명령어에 사용할 수 있는 파라미터 형태로 변환함.
        -x264-params와 같은 묶음 파라미터와 개별 파라미터를 모두 처리하며, 설정되지 않은 옵션은 자동으로 제외됨.

        Returns:
            List[str]: FFmpeg 명령어에 사용할 고급 파라미터들의 리스트
        """
        # 필요한 변수들을 초기화
        user_options = self.task.adv_opts # 사용자가 설정한 고급 옵션들
        schema = self.codec_config.get("adv_options", {}) # 코덱별 고급 옵션 스키마
        UNSPECIFIED_VALUES = {'', 'None', 'None (default)'} # 무시할 값들(사용자가 설정하지 않음)
        param_bundle_key = self.codec_config.get("param_bundle_key") # 옵션을 하나로 묶는 파라미터 키 (예: -x264-params)
        params = [] # 생성될 파라미터들을 담을 리스트

        # 코덱 스키마의 모든 옵션을 순회하며 명령어 파라미터를 생성
        for key, option_data in schema.items():
            user_value_obj = user_options.get(key) # 사용자가 설정한 값
            user_value_str = str(user_value_obj) if user_value_obj is not None else '' # 값을 문자열로 변환

            # 사용자가 설정하지 않은 값은 건너뜀
            if user_value_str in UNSPECIFIED_VALUES:
                continue

            ffmpeg_param = option_data.get("ffmpeg_param") # 실제 FFmpeg에서 사용하는 파라미터 이름
            if not ffmpeg_param: # FFmpeg 파라미터가 정의되지 않은 옵션은 건너뜀
                continue
            
            # preset, profile 등은 별도로 처리되므로, 묶음 파라미터에서는 제외
            if param_bundle_key and ffmpeg_param in ["preset", "profile:v", "tune", "pix_fmt"]:
                continue

            is_checkbutton = option_data.get("widget") == "checkbutton" # 옵션이 체크박스인지 확인

            # 묶음 파라미터(-x264-params 등)를 사용하는 코덱의 경우
            if param_bundle_key:
                if is_checkbutton: # 체크박스는 'param=1' 또는 'param=0' 형식으로 추가
                    params.append(f"{ffmpeg_param}={'1' if user_value_obj else '0'}")
                else:
                    if self._is_libx264_vbv_option(ffmpeg_param, user_value_str): # libx264의 VBV 옵션은 특별 처리
                        params.append(f"{ffmpeg_param}={user_value_str}k") # 'k' 접미사 추가
                    else: # 그 외 옵션은 'param=value' 형식으로 추가
                        params.append(f"{ffmpeg_param}={user_value_str}")
            
            # 개별 파라미터(-key value)를 사용하는 코덱의 경우
            else:
                if is_checkbutton:
                    default_value = option_data.get("default", False)
                    if user_value_obj != default_value: # 기본값과 다를 때만 파라미터를 추가
                        params.extend([f"-{ffmpeg_param}", "1" if user_value_obj else "0"])
                else: # 그 외 옵션은 '-param', 'value' 형식으로 추가
                    params.extend([f"-{ffmpeg_param}", user_value_str])

        if not params: # 생성된 파라미터가 없으면 빈 리스트 반환
            return []

        if param_bundle_key: # 묶음 파라미터가 있는 경우
            return [param_bundle_key, ":".join(params)] # '-x264-params', 'key=value:key2=value2' 형식으로 반환
        else: # 개별 파라미터인 경우
            return params # ['-key', 'value', '-key2', 'value2'] 형식으로 반환

    def build_encode_command(self, pass_num: int = 0) -> List[str]:
        """
        주어진 패스(pass)에 대한 완전한 FFmpeg 인코딩 명령어를 구성.

        EncodingTask의 모든 설정을 바탕으로 FFmpeg 인코딩 명령어를 생성함.
        코덱별 고급 옵션, 하드웨어 가속, 2패스 인코딩, 색상 메타데이터 등을
        자동으로 처리하여 완전한 명령어를 구성함.

        Args:
            pass_num: 2패스 인코딩에서의 패스 번호 (0: 단일 패스 또는 2패스, 1: 1패스)

        Returns:
            List[str]: FFmpeg 인코딩 명령어의 각 요소들을 담은 리스트
        """
        task = self.task
        output_path = f"encoded_{task.codec}_{task.preset}_{task.crf}.mkv" if self.is_for_full_video else os.path.basename(task.encoded_path)
        rate_control_param = self.codec_config.get("rate_control", "-crf")

        # 명령어 기본 구성
        cmd = [task.ffmpeg_path, "-y", "-hide_banner", "-loglevel", "info"]

        # 스트림 분석 옵션을 -i 앞에 추가하여 분석 정확도 향상
        cmd.extend(["-analyzeduration", "20M", "-probesize", "20M"])

        # 하드웨어 가속기 초기화 (필요한 경우)
        if 'qsv' in task.codec:
            cmd.extend(["-init_hw_device", "qsv=hw", "-filter_hw_device", "hw"])
        
        # 입력 파일 지정
        cmd.extend(["-i", self.video_path])
        
        # 가변 프레임레이트(VFR) 비디오의 싱크 문제를 방지하기 위해 고정 프레임레이트(CFR)로 변환
        cmd.extend(["-fps_mode", "cfr"])
        
        # 원본 영상에서 추출한 색상 메타데이터를 명시적으로 적용하여 색상 왜곡 방지
        if task.color_info:
            for key, value in task.color_info.items():
                if value and value != "unknown": # 유효한 값이 있을 때만 옵션을 추가
                    cmd.extend([f"-{key}", value])

        # 비디오 코덱 및 프리셋 설정
        cmd.extend(["-c:v", task.codec])
        if "preset" not in self.codec_config.get("adv_options", {}): # 프리셋이 고급 옵션에 포함되지 않은 경우에만 별도로 추가
            cmd.extend(["-preset", task.preset])
        
        # 주 품질 제어 파라미터 설정 (CRF/CQ 등)
        cmd.extend([rate_control_param, str(task.crf)])
        
        # AMD AMF 코덱의 CQP 모드는 별도 플래그가 필요
        if 'amf' in task.codec and task.adv_opts.get('rc') == 'cqp':
            cmd.extend(['-rc', 'cqp'])

        # 동적으로 생성된 고급 파라미터 추가
        cmd.extend(self._build_advanced_params())

        # 사용자가 직접 입력한 커스텀 옵션 추가
        if "custom_opts" in task.adv_opts and task.adv_opts["custom_opts"]:
             cmd.extend(shlex.split(task.adv_opts["custom_opts"]))
        
        # 오디오 옵션 처리
        if task.audio_option == 'Remove Audio':
            cmd.append("-an") # 오디오 스트림 제거
        elif task.audio_option == 'Copy Audio':
            cmd.extend(["-c:a", "copy"]) # 오디오 스트림을 재인코딩 없이 복사
        
        # 2-pass 인코딩 로직 처리
        is_2pass = "is_2pass" in task.adv_opts and task.adv_opts["is_2pass"]
        if is_2pass:
            passlogfile_name = f"ffmpeg2pass_{task.preset}_{task.crf}" if not self.is_for_full_video else "ffmpeg2pass_final"
            passlogfile = os.path.join(task.temp_dir, passlogfile_name)
            cmd.extend(["-pass", str(pass_num), "-passlogfile", passlogfile]) # 1패스 또는 2패스 관련 옵션 추가
            
        if is_2pass and pass_num == 1: # 1패스인 경우, 실제 비디오 출력을 하지 않고 로그 파일만 생성
            cmd.extend(["-f", "null", "NUL" if os.name == 'nt' else "/dev/null"])
        else: # 2패스 또는 단일 패스인 경우, 최종 출력 파일 경로 지정
            cmd.append(output_path)
            
        return cmd

    def _build_analysis_command_base(self) -> List[str]:
        """
        분석(VMAF, PSNR, SSIM)을 위한 기본 FFmpeg 명령어를 생성.

        모든 품질 분석 명령어에 공통으로 사용되는 기본 구조를 생성함.
        인코딩된 파일과 원본 샘플 파일을 입력으로 받아 비교 분석할 수 있도록 기본적인 FFmpeg 옵션들을 설정함.

        Returns:
            List[str]: 분석 명령어의 기본 구조를 담은 리스트
        """
        cmd = [self.task.ffmpeg_path]
        
        # 분석의 일관성과 정확도를 위해 항상 CPU 디코딩을 사용하고, 두 개의 입력 파일을 지정
        cmd.extend(['-y', '-hide_banner', '-loglevel', 'info',
                    '-i', os.path.basename(self.task.encoded_path), # 인코딩된 파일 (첫 번째 입력)
                    '-i', os.path.basename(self.task.sample_path)]) # 원본 샘플 파일 (두 번째 입력)
        return cmd

    def build_vmaf_command(self) -> List[str]:
        """
        VMAF 점수 계산을 위한 FFmpeg 명령어를 구성.

        VMAF(Video Multi-method Assessment Fusion) 분석을 위한 FFmpeg 명령어를 생성함.
        VMAF는 Netflix에서 개발한 주관적 품질 평가 알고리즘으로, 인간의 시각적 품질 인식을 시뮬레이션함.

        Returns:
            List[str]: VMAF 분석을 위한 FFmpeg 명령어의 각 요소들을 담은 리스트
        """
        task = self.task
        libvmaf_options = f"log_fmt=json:log_path={task.vmaf_log_filename}" # VMAF 점수를 JSON 파일로 저장하도록 설정
        
        # 사용자가 VMAF 모델을 직접 지정한 경우, 해당 모델을 사용하도록 옵션 추가
        if task.vmaf_model_path and os.path.exists(task.vmaf_model_path):
            try:
                # FFmpeg 작업 디렉토리 기준 상대 경로로 변환
                relative_model_path = os.path.relpath(task.vmaf_model_path, task.temp_dir)
                safe_relative_path = relative_model_path.replace('\\', '/') # Windows 경로 구분자를 FFmpeg 호환 형식으로 변경
                libvmaf_options += f":model=path={safe_relative_path}"
            except Exception as e:
                logging.warning(f"Could not calculate relative path for VMAF model '{task.vmaf_model_path}'. Falling back to default model. Error: {e}")

        # VMAF 비교를 위한 필터 그래프를 구성
        filter_complex = f"[0:v]setpts=PTS-STARTPTS[dist];[1:v]setpts=PTS-STARTPTS[ref];[dist][ref]libvmaf={libvmaf_options}"
        
        # 기본 분석 명령어에 VMAF 필터와 옵션을 추가
        cmd = self._build_analysis_command_base()
        cmd.extend(["-vsync", "cfr", "-filter_complex", filter_complex, "-f", "null", "-"])
        return cmd

    def build_psnr_command(self) -> List[str]:
        """
        PSNR(Peak Signal-to-Noise Ratio) 계산을 위한 FFmpeg 명령어를 구성.

        PSNR 분석을 위한 FFmpeg 명령어를 생성함.
        PSNR은 원본 영상과 인코딩된 영상 간의 객관적 품질 차이를 측정하는 전통적인 품질 평가 지표임.

        Returns:
            List[str]: PSNR 분석을 위한 FFmpeg 명령어의 각 요소들을 담은 리스트
        """
        lavfi_filter = "psnr" # 사용할 필터 이름
        
        # 기본 분석 명령어에 PSNR 필터와 옵션을 추가
        cmd = self._build_analysis_command_base()
        cmd.extend(["-vsync", "cfr", "-filter_complex", lavfi_filter, "-f", "null", "-"])
        return cmd

    def build_ssim_command(self) -> List[str]:
        """
        SSIM(Structural Similarity Index) 계산을 위한 FFmpeg 명령어를 구성.

        SSIM 분석을 위한 FFmpeg 명령어를 생성함.
        SSIM은 인간의 시각 시스템이 구조적 정보에 민감하다는 특성을 반영하여
        영상의 구조적 유사성을 측정하는 품질 평가 지표임.

        Returns:
            List[str]: SSIM 분석을 위한 FFmpeg 명령어의 각 요소들을 담은 리스트
        """
        lavfi_filter = "ssim" # 사용할 필터 이름
        
        # 기본 분석 명령어에 SSIM 필터와 옵션을 추가
        cmd = self._build_analysis_command_base()
        cmd.extend(["-vsync", "cfr", "-filter_complex", lavfi_filter, "-f", "null", "-"])
        return cmd

    def build_blockdetect_command(self) -> List[str]:
        """
        블록킹 현상(깍두기) 분석을 위한 FFmpeg 명령어를 구성.

        인코딩된 영상에서 블록킹 아티팩트를 감지하기 위한 FFmpeg 명령어를 생성함.
        블록킹은 압축 과정에서 발생할 수 있는 화질 저하 현상으로, 영상의 품질을 평가하는 중요한 지표임.

        Returns:
            List[str]: 블록킹 감지 분석을 위한 FFmpeg 명령어의 각 요소들을 담은 리스트
        """
        lavfi_filter = "[0:v]blockdetect[out];[out]null" # blockdetect 필터 적용
        
        # 블록킹 분석은 인코딩된 단일 파일에 대해서만 수행
        cmd = [self.task.ffmpeg_path, '-y', '-hide_banner', '-loglevel', 'info',
               '-i', os.path.basename(self.task.encoded_path),
               "-filter_complex", lavfi_filter, "-f", "null", "-"]
        return cmd



# ==============================================================================
# 5. 멀티프로세싱 워커 함수
# ==============================================================================
def find_best_crf_for_preset(preset, codec_config, base_task_args):
    """
    하나의 프리셋에 대해 Target VMAF를 만족하는 가장 효율적인 CRF를 탐색.

    이 함수는 병렬 처리를 위해 별도의 프로세스에서 실행되며,
    주어진 프리셋에 대해 목표 VMAF 값을 달성하는 가장 낮은 CRF 값을 찾음.
    이진 탐색 알고리즘을 사용하여 효율적으로 최적값을 찾아내며, 각 CRF 값에 대한 인코딩 및 분석을 수행함.

    Args:
        preset: 테스트할 인코딩 프리셋 (예: 'fast', 'medium', 'slow')
        codec_config: 코덱별 설정 정보를 담은 딕셔너리
        base_task_args: 기본 작업 인자를 담은 딕셔너리

    Returns:
        dict: 최적 CRF 값과 관련 정보를 담은 딕셔너리
    """
    # 초기 변수 설정
    min_q, max_q = codec_config.get("quality_range", (0, 51)) # 코덱별 품질 범위 가져오기
    target_vmaf = base_task_args['target_vmaf'] # 목표 VMAF 값
    tested_crfs = {} # 이미 테스트한 CRF의 결과를 캐싱하여 중복 작업을 방지하는 딕셔너리

    # 현재 프리셋에 대한 EncodingTask를 생성하기 위해 기본 인자를 복사하고 수정
    task_args = base_task_args.copy() # 기본 작업 인자 복사
    task_args['preset'] = preset # 현재 프리셋으로 설정

    def _test_crf(crf_to_test):
        """
        CRF 테스트를 수행하고 결과를 캐싱하는 헬퍼 함수.

        주어진 CRF 값에 대해 인코딩 테스트를 수행하고, 결과를 캐싱하여 중복 테스트를 방지함.
        CRF 값이 유효 범위를 벗어나는 경우 None을 반환하여 오류를 방지함.

        Args:
            crf_to_test: 테스트할 CRF 값

        Returns:
            tuple: (VMAF 점수, 테스트 결과) 또는 (None, None) (실패 시)
        """
        crf_to_test = int(round(crf_to_test)) # CRF 값을 정수로 반올림
        if not (min_q <= crf_to_test <= max_q): # 품질 범위를 벗어나는 경우
            return None, None # 유효하지 않은 CRF 값이면 None을 반환

        # 이미 테스트한 CRF인 경우 캐시된 결과를 반환하여 중복 인코딩 방지
        if crf_to_test in tested_crfs:
            return tested_crfs[crf_to_test]

        # 새로운 인코딩 작업을 위한 Task 객체 생성
        task_args['crf'] = crf_to_test # 현재 테스트할 CRF로 업데이트
        task = EncodingTask(
            ffmpeg_path=task_args['ffmpeg_path'],
            sample_path=task_args['sample_path'],
            temp_dir=task_args['temp_dir'],
            codec=task_args['codec'],
            preset=task_args['preset'],
            crf=task_args['crf'],
            audio_option=task_args['audio_option'],
            adv_opts=task_args['adv_opts'],
            metrics=task_args['metrics'],
            vmaf_model_path=task_args['vmaf_model_path'],
            color_info=task_args['color_info']
        )

        # 실제 인코딩 및 분석 작업을 수행
        result = perform_one_test(task)

        # 작업 결과를 처리하고 캐시에 저장
        if result.get("status") == "success":
            vmaf_score = result.get("vmaf", 0) # VMAF 점수 가져오기
            tested_crfs[crf_to_test] = (vmaf_score, result) # 성공 결과를 캐시에 저장
            return vmaf_score, result # VMAF 점수와 결과 반환
        else:
            tested_crfs[crf_to_test] = (None, None) # 실패 결과를 캐시에 저장
            return None, None # 실패 시 None 반환

    # --- 탐색 시작 ---
    # 1. 경계 조건 탐색: 품질 범위의 양 끝 값을 먼저 테스트하여 탐색이 유효한지 확인
    best_result_for_preset = None # 현재 프리셋에서 찾은 최적의 결과
    v_low, res_low = _test_crf(max_q) # 가장 낮은 품질(가장 높은 CRF) 테스트
    v_high, res_high = _test_crf(min_q) # 가장 높은 품질(가장 낮은 CRF) 테스트

    # 경계값 테스트 결과가 이미 목표 VMAF를 만족하는 경우, 해당 결과를 최적 결과로 간주할 수 있음
    if v_high is not None and v_high >= target_vmaf: # 가장 높은 품질 설정이 목표를 만족하면
        best_result_for_preset = res_high # 이를 현재까지의 최적 결과로 설정
    if v_low is not None and v_low >= target_vmaf: # 가장 낮은 품질 설정조차 목표를 만족하면 (매우 드문 경우)
        best_result_for_preset = res_low # 이를 최적 결과로 갱신 (더 효율적이므로)

    # 가장 높은 품질로도 목표 VMAF에 도달할 수 없다면, 더 이상 탐색은 무의미
    if v_high is None or v_high < target_vmaf:
        return None # 탐색을 시작하기 전에 목표 달성이 불가능하다고 판단되면 None을 반환

    # 2. 이진/보간 탐색 루프
    low_q, high_q = min_q, max_q # 탐색 범위 초기화
    max_iterations = 10 # 불필요한 무한 루프를 방지하기 위한 최대 반복 횟수

    for it in range(max_iterations):
        # 탐색 범위가 충분히 좁혀지면 루프 종료
        if high_q - low_q <= 1:
            break

        # 다음으로 테스트할 중간 CRF 값을 계산 (선형 보간 우선)
        mid_q = -1 # 중간값 초기화
        if v_high is not None and v_low is not None:
            v_diff = abs(v_high - v_low) # 현재 VMAF 범위
            
            # VMAF 범위가 유의미할 경우, 선형 보간법으로 다음 CRF 값을 예측하여 수렴 속도 향상
            if v_diff > max(APP_CONFIG['numerical_tolerance']['relative'] * max(abs(v_high), abs(v_low)), APP_CONFIG['numerical_tolerance']['absolute']):
                mid_q = high_q + (low_q - high_q) * (target_vmaf - v_low) / (v_high - v_low)

        # 선형 보간이 실패했거나 불안정한 값을 반환한 경우, 안전한 이진 탐색 중앙값으로 대체
        if mid_q <= low_q or mid_q >= high_q:
            mid_q = low_q + (high_q - low_q) * 0.5

        # 계산된 중간값으로 CRF 테스트 실행
        v_mid, res_mid = _test_crf(mid_q)

        # 테스트 결과를 바탕으로 탐색 범위 업데이트
        if v_mid is not None: # 테스트가 성공한 경우
            if v_mid >= target_vmaf: # 목표 VMAF를 만족한 경우
                best_result_for_preset = res_mid # 이 결과를 최적 후보로 업데이트
                low_q = int(round(mid_q)) # 탐색 하한을 높여 더 효율적인(높은) CRF를 찾도록 함
                v_high = v_mid # VMAF 상한값 업데이트
            else: # 목표 VMAF를 만족하지 못한 경우
                high_q = int(round(mid_q)) # 탐색 상한을 낮춰 더 높은 품질(낮은 CRF)을 찾도록 함
                v_low = v_mid # VMAF 하한값 업데이트
        else: # 테스트가 실패한 경우 (예: 인코딩 오류)
            high_q = int(round(mid_q)) # 실패한 구간을 피하기 위해 탐색 상한을 낮춤

    return best_result_for_preset # 최종적으로 찾은 최적의 결과를 반환


# 단일 테스트 작업 수행하는 함수 (멀티프로세싱으로 실행됨)
def perform_one_test(task: EncodingTask):
    """
    하나의 EncodingTask에 대해 인코딩 및 모든 분석을 순차적으로 실행하고 결과를 반환.

    이 함수는 병렬 처리를 위해 별도의 프로세스에서 실행되며, 주어진 인코딩 설정에 대해 전체 워크플로우를 수행함.
    인코딩, VMAF 분석, PSNR/SSIM 계산, 블록킹 감지 등을 순차적으로 실행하고 모든 결과를 통합하여 반환함.

    Args:
        task: 실행할 인코딩 작업을 담고 있는 EncodingTask 객체

    Returns:
        dict: 인코딩 및 분석 결과를 담은 딕셔너리
    """
    # 작업 시작 시간 기록 및 초기 변수 설정
    start_time_dt = datetime.now()
    builder = FFmpegCommandBuilder(task)
    log_output = "" # 이 워커에서 실행된 모든 FFmpeg 명령어의 로그를 누적할 변수

    def run_and_log(cmd: List[str], metric_name: str = ""):
        """
        주어진 FFmpeg 명령어를 실행하고, 그 출력을 로그에 기록.

        이 함수는 FFmpeg 명령어를 실행하고 실행 결과를 로그에 기록함.
        명령어 실행 성공/실패 여부와 관계없이 모든 출력을 로그에 저장하여
        디버깅과 문제 해결에 필요한 정보를 제공함.

        Args:
            cmd: 실행할 FFmpeg 명령어 리스트
            metric_name: 실행하는 작업의 이름 (예: 'VMAF', 'PSNR', 'SSIM', 'ENCODE')

        Returns:
            str: FFmpeg의 표준 오류 출력 (로그 정보)

        Raises:
            subprocess.CalledProcessError: FFmpeg 명령어 실행이 실패한 경우
        """
        nonlocal log_output
        log_output += f"--- COMMAND ({'ENCODE' if not metric_name else metric_name}) ---\n{' '.join(shlex.quote(c) for c in cmd)}\n\n--- FFmpeg Log ---\n"
        
        try:
            # FFmpeg 서브프로세스 실행
            result = subprocess.run(
                cmd,
                check=True,
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='ignore',
                startupinfo=_get_subprocess_startupinfo(),
                cwd=task.temp_dir,
            )

            # FFmpeg의 표준 오류(stderr) 출력을 로그에 추가
            if result.stderr:
                log_output += result.stderr
            else:
                log_output += "(FFmpeg produced no log output. This is unexpected with the current loglevel.)"
            
            return result.stderr

        except subprocess.CalledProcessError as e: # 프로세스 실행 중 오류 발생 시
            # 오류 출력을 로그에 추가하고 예외를 다시 발생시켜 상위에서 처리하도록 함
            if e.stderr:
                log_output += e.stderr
            else:
                log_output += f"(FFmpeg produced no output. Process failed with return code: {e.returncode})"
            raise e
        
        finally:
            log_output += "\n\n" # 각 명령어 로그의 끝에 구분자를 추가

    try:
        # --- 1. 인코딩 실행 ---
        if task.adv_opts.get("is_2pass"): # 2-pass 인코딩인 경우
            run_and_log(builder.build_encode_command(pass_num=1)) # 1패스 실행
            run_and_log(builder.build_encode_command(pass_num=2)) # 2패스 실행
        else: # 1-pass 인코딩인 경우
            run_and_log(builder.build_encode_command(pass_num=0)) # 단일 패스 실행

        # --- 2. 품질 메트릭 분석 ---
        results = {"vmaf": 0, "psnr": 0, "ssim": 0, "vmaf_1_low": 0, "block_score": 0, "vmaf_std_dev": 0} # 결과 딕셔너리 초기화

        # VMAF 점수 계산
        try:
            run_and_log(builder.build_vmaf_command(), metric_name="VMAF") # VMAF 분석 실행
            with open(task.vmaf_log_path, 'r', encoding='utf-8') as f: # VMAF 로그 파일(JSON) 열기
                vmaf_data = json.load(f) # JSON 데이터 로드
            
            results["vmaf"] = vmaf_data['pooled_metrics']['vmaf']['mean'] # 전체 프레임의 평균 VMAF 점수 저장
            
            # VMAF 하위 1% 및 표준편차 계산
            frame_scores = [frame['metrics']['vmaf'] for frame in vmaf_data['frames']] # 모든 프레임의 VMAF 점수 리스트 추출
            if frame_scores:
                frame_scores.sort() # 점수를 오름차순으로 정렬
                one_percent_index = max(0, int(len(frame_scores) * 0.01)) # 하위 1%에 해당하는 인덱스 계산
                one_percent_low_frames = frame_scores[:one_percent_index + 1] # 하위 1% 점수들만 추출
                results["vmaf_1_low"] = sum(one_percent_low_frames) / len(one_percent_low_frames) # 하위 1% 점수들의 평균 계산

                if len(frame_scores) >= 2: # 데이터가 2개 이상일 때만 표준편차 계산 가능
                    try:
                        results["vmaf_std_dev"] = statistics.stdev(frame_scores) # VMAF 점수들의 표준편차 계산
                    except statistics.StatisticsError:
                        results["vmaf_std_dev"] = 0.0
                else:
                    results["vmaf_std_dev"] = 0.0
        except Exception as e:
            log_output += f"--- WARNING: VMAF calculation failed. Setting to 0. Error: {e} ---\n\n"

        # PSNR 계산 (사용자가 옵션을 활성화한 경우)
        if task.metrics.get('psnr'):
            try:
                stderr = run_and_log(builder.build_psnr_command(), metric_name="PSNR")
                match = re.search(r"average:(\d+\.?\d*)", stderr) # FFmpeg 로그에서 PSNR 평균값 추출
                if match:
                    results["psnr"] = float(match.group(1))
            except Exception as e:
                log_output += f"--- WARNING: PSNR calculation failed. Setting to 0. Error: {e} ---\n\n"

        # SSIM 계산 (사용자가 옵션을 활성화한 경우)
        if task.metrics.get('ssim'):
            try:
                stderr = run_and_log(builder.build_ssim_command(), metric_name="SSIM")
                match = re.search(r"All:(\d+\.?\d*)", stderr) # FFmpeg 로그에서 SSIM 전체 평균값 추출
                if match:
                    results["ssim"] = float(match.group(1))
            except Exception as e:
                log_output += f"--- WARNING: SSIM calculation failed. Setting to 0. Error: {e} ---\n\n"
        
        # 블록킹 점수 계산 (사용자가 옵션을 활성화한 경우)
        if task.metrics.get('blockdetect'):
            try:
                stderr = run_and_log(builder.build_blockdetect_command(), metric_name="BlockDetect")
                match = re.search(r"block mean:\s*(\d+\.?\d*)", stderr) # FFmpeg 로그에서 블록 평균값 추출
                if match:
                    results["block_score"] = float(match.group(1))
            except Exception as e:
                log_output += f"--- WARNING: Blockdetect analysis failed. Setting to 0. Error: {e} ---\n\n"

        # --- 3. 최종 결과 집계 ---
        # 인코딩된 파일 크기(MB) 계산
        size_mb = os.path.getsize(task.encoded_path) / (1024 * 1024)
        
        # 작업 시간 기록 및 요약 생성
        end_time_dt = datetime.now()
        duration_td = end_time_dt - start_time_dt
        time_summary = (
            f"--- TIMING ---\n"
            f"Start Time:     {start_time_dt.strftime('%Y-%m-%d %H:%M:%S')}\n"
            f"End Time:       {end_time_dt.strftime('%Y-%m-%d %H:%M:%S')}\n"
            f"Total Duration: {str(duration_td).split('.')[0]} (HH:MM:SS)\n\n"
        )
        
        # 모든 분석 결과를 종합하여 최종 딕셔너리 형태로 반환
        return {
            "preset": task.preset, "crf": task.crf,
            "vmaf": results["vmaf"], "vmaf_1_low": results["vmaf_1_low"],
            "vmaf_std_dev": results["vmaf_std_dev"],
            "psnr": results["psnr"], "ssim": results["ssim"],
            "block_score": results["block_score"],
            "size_mb": size_mb,
            "efficiency": results["vmaf"] / size_mb if size_mb > 0 else 0,
            "status": "success", "log": time_summary + log_output,
            "adv_opts_snapshot": task.adv_opts
        }
    
    # --- 4. 예외 처리 ---
    except subprocess.CalledProcessError as e:
        # FFmpeg 프로세스가 0이 아닌 종료 코드를 반환한 경우의 처리
        end_time_dt = datetime.now()
        duration_td = end_time_dt - start_time_dt
        time_summary = (
            f"--- TIMING (ERROR) ---\n"
            f"Start Time:     {start_time_dt.strftime('%Y-%m-%d %H:%M:%S')}\n"
            f"End Time:       {end_time_dt.strftime('%Y-%m-%d %H:%M:%S')}\n"
            f"Total Duration: {str(duration_td).split('.')[0]} (HH:MM:SS)\n\n"
        )
        
        # e.stderr가 비어있는(None) 경우를 대비한 안전한 처리
        stderr_output = ""
        if e.stderr:
            # bytes 타입일 경우 문자열로 디코딩
            if isinstance(e.stderr, bytes):
                stderr_output = e.stderr.decode('utf-8', errors='ignore')
            else:
                stderr_output = e.stderr

        # 사용자에게 표시될 오류 메시지 생성
        message = f"FFmpeg process failed (Preset: {task.preset}, CRF: {task.crf}): Return code {e.returncode}"
        if stderr_output:
            message += f"\nFFmpeg error: {stderr_output.strip()[:200]}..."
        
        # 현재까지 누적된 모든 로그와 타이밍 정보를 최종 결과에 포함
        final_log = time_summary + log_output
        return {"status": "error", "message": message, "log": final_log, "preset": task.preset, "crf": task.crf}
    
    except OSError as e:
        # 파일 시스템 접근 또는 프로세스 생성 관련 시스템 오류의 처리
        end_time_dt = datetime.now()
        duration_td = end_time_dt - start_time_dt
        time_summary = (
            f"--- TIMING (ERROR) ---\n"
            f"Start Time:     {start_time_dt.strftime('%Y-%m-%d %H:%M:%S')}\n"
            f"End Time:       {end_time_dt.strftime('%Y-%m-%d %H:%M:%S')}\n"
            f"Total Duration: {str(duration_td).split('.')[0]} (HH:MM:SS)\n\n"
        )
        message = f"System error during encode (Preset: {task.preset}, CRF: {task.crf}): {e}"
        final_log = time_summary + log_output
        return {"status": "error", "message": message, "log": final_log, "preset": task.preset, "crf": task.crf}
    
    except Exception as e:
        # 위에서 명시되지 않은 기타 모든 예외의 처리
        end_time_dt = datetime.now()
        duration_td = end_time_dt - start_time_dt
        time_summary = (
            f"--- TIMING (ERROR) ---\n"
            f"Start Time:     {start_time_dt.strftime('%Y-%m-%d %H:%M:%S')}\n"
            f"End Time:       {end_time_dt.strftime('%Y-%m-%d %H:%M:%S')}\n"
            f"Total Duration: {str(duration_td).split('.')[0]} (HH:MM:SS)\n\n"
        )
        message = f"Unexpected error during encode (Preset: {task.preset}, CRF: {task.crf}): {e}"
        final_log = time_summary + log_output
        return {"status": "error", "message": message, "log": final_log, "preset": task.preset, "crf": task.crf}
    
    # --- 5. 마무리 (정리 작업) ---
    finally:
        # 작업 성공/실패 여부와 관계없이 생성된 임시 파일들을 정리
        passlogfile_name = f"ffmpeg2pass_{task.preset}_{task.crf}"
        passlogfile_path = os.path.join(task.temp_dir, passlogfile_name)
        
        files_to_remove = [
            task.encoded_path,
            task.vmaf_log_path,
            passlogfile_path,
            f"{passlogfile_path}.log",
            f"{passlogfile_path}.mbtree"
        ]

        for p in files_to_remove:
            if os.path.exists(p):
                try:
                    os.remove(p)
                except OSError:
                    logging.warning(f"Could not remove temporary file: {p}")
                    pass # 파일 삭제 실패 시에도 전체 작업이 중단되지 않도록 함



# ==============================================================================
# 6. 메인 애플리케이션 클래스
# ==============================================================================
# 메인 애플리케이션 클래스
class VideoOptimizerApp:
    """
    비디오 인코딩 최적화를 위한 메인 애플리케이션 클래스.

    전체 애플리케이션의 핵심 기능을 담당하며, GUI 인터페이스, 인코딩 작업 관리, 품질 분석, 최적화 알고리즘 등을 통합하여 제공함.

    사용자가 비디오 파일을 선택하고 인코딩 설정을 조정할 수 있으며, 다양한 품질 메트릭을 기반으로 최적의 인코딩 파라미터를 찾아줌.
    """

    # 코덱별 설정을 정의하는 중앙 저장소.
    # 이 딕셔너리를 통해 각 코덱의 동작 방식(품질 제어 파라미터, 프리셋, 고급 옵션 등)을 제어.
    # 각 코덱은 다음과 같은 구조를 가짐:
    # - group: 코덱 그룹 (Software, NVIDIA NVENC, Intel QSV, AMD AMF 등)
    # - rate_control: 품질 제어 파라미터 (-crf, -cq, -global_quality 등)
    # - quality_range: 품질 값의 범위 (최소값, 최대값)
    # - param_bundle_key: 고급 옵션을 묶어서 전달할 파라미터 키 (-x264-params 등)
    # - preset_param: 프리셋 설정 파라미터
    # - preset_values: 사용 가능한 프리셋 목록
    # - adv_options: 고급 설정 옵션들의 상세 정의
    CODEC_CONFIG = {  # 코덱별 설정 구성
        # ==============================================================================
        # H.264 / AVC Encoders
        # ==============================================================================
        "libx264": {  # x264 소프트웨어 인코더 설정
            "group": "Software",
            "rate_control": "-crf",
            "quality_range": (0, 51),  # 소프트웨어 그룹, CRF 비트레이트 제어, 품질 범위
            "param_bundle_key": "-x264-params",  # x264 파라미터 묶음 키
            "preset_param": "-preset",  # 프리셋 파라미터
            "preset_values": [
                "ultrafast",
                "superfast",
                "veryfast",
                "faster",
                "fast",
                "medium",
                "slow",
                "slower",
                "veryslow",
                "placebo",
            ],  # 사용 가능한 프리셋 목록
            "adv_options": {
                "vbv_maxrate": {
                    "label": "Max Rate (kb/s):",
                    "ffmpeg_param": "vbv-maxrate",
                    "widget": "entry",
                    "default": "0",
                    "tooltip": "VBV Max Bitrate in kb/s. 0=unlimited.",
                    "category": "Rate Control",
                },
                "vbv_bufsize": {
                    "label": "Buffer Size (kb):",
                    "ffmpeg_param": "vbv-bufsize",
                    "widget": "entry",
                    "default": "0",
                    "tooltip": "VBV Buffer Size in kb/s. Use with Max Rate.",
                    "category": "Rate Control",
                },
                "crf_max": {
                    "label": "CRF Max:",
                    "ffmpeg_param": "crf-max",
                    "widget": "spinbox_int",
                    "range": (0, 51),
                    "default": "0",
                    "tooltip": "With VBV, sets a quality floor. 0=unlimited.",
                    "category": "Rate Control",
                },
                "qcomp": {
                    "label": "QComp:",
                    "ffmpeg_param": "qcomp",
                    "widget": "spinbox_float",
                    "range": (0.0, 1.0),
                    "default": "0.6",
                    "tooltip": "Quantizer Compression (0=CBR, 1=CQP).",
                    "category": "Rate Control",
                },
                "aq_mode": {
                    "label": "AQ Mode:",
                    "ffmpeg_param": "aq-mode",
                    "widget": "combobox",
                    "values": ["0", "1", "2", "3"],
                    "default": "1",
                    "tooltip": "Adaptive Quantization mode. 1: Variance, 2: Auto-variance, 3: Complexity.",
                    "category": "Rate Control",
                },
                "aq_strength": {
                    "label": "AQ Strength:",
                    "ffmpeg_param": "aq-strength",
                    "widget": "spinbox_float",
                    "range": (0.0, 3.0),
                    "default": "1.0",
                    "tooltip": "Strength of AQ. Reduces blocking in flat areas.",
                    "category": "Rate Control",
                },
                "psy_rd_strength": {
                    "label": "Psy-RD Strength:",
                    "ffmpeg_param": "psy-rd",
                    "widget": "spinbox_float",
                    "range": (0.0, 10.0),
                    "default": "1.0",
                    "tooltip": "Strength of psychovisual rate-distortion. Preserves detail/grain.",
                    "category": "Psychovisual",
                },
                "psy_rd_trellis": {
                    "label": "Psy-RD Trellis:",
                    "ffmpeg_param": "trellis",
                    "widget": "spinbox_float",
                    "range": (0.0, 10.0),
                    "default": "0.0",
                    "tooltip": "Strength of psychovisual trellis quantization.",
                    "category": "Psychovisual",
                },
                "g": {
                    "label": "Keyframe Interval:",
                    "ffmpeg_param": "keyint",
                    "widget": "spinbox_int",
                    "range": (0, 1000),
                    "default": "250",
                    "tooltip": "Max frames between keyframes (GOP size).",
                    "category": "Frame & GOP",
                },
                "min_keyint": {
                    "label": "Min Keyframe Interval:",
                    "ffmpeg_param": "min-keyint",
                    "widget": "spinbox_int",
                    "range": (0, 250),
                    "default": "25",
                    "tooltip": "Minimum interval between keyframes.",
                    "category": "Frame & GOP",
                },
                "scenecut": {
                    "label": "Scenecut:",
                    "ffmpeg_param": "scenecut",
                    "widget": "spinbox_int",
                    "range": (0, 100),
                    "default": "40",
                    "tooltip": "Scene change detection sensitivity.",
                    "category": "Frame & GOP",
                },
                "bframes": {
                    "label": "B-Frames:",
                    "ffmpeg_param": "bframes",
                    "widget": "spinbox_int",
                    "range": (0, 16),
                    "default": "3",
                    "tooltip": "Max consecutive B-frames.",
                    "category": "Frame & GOP",
                },
                "b_adapt": {
                    "label": "B-Frame Adaptive:",
                    "ffmpeg_param": "b-adapt",
                    "widget": "combobox",
                    "values": ["0", "1", "2"],
                    "default": "1",
                    "tooltip": "B-frame decision algorithm. 0: Off, 1: Fast, 2: Optimal.",
                    "category": "Frame & GOP",
                },
                "b_pyramid": {
                    "label": "B-Frame Pyramid:",
                    "ffmpeg_param": "b-pyramid",
                    "widget": "combobox",
                    "values": ["none", "strict", "normal"],
                    "default": "normal",
                    "tooltip": "Allows B-frames to be used as references.",
                    "category": "Frame & GOP",
                },
                "ref": {
                    "label": "Reference Frames:",
                    "ffmpeg_param": "ref",
                    "widget": "spinbox_int",
                    "range": (1, 16),
                    "default": "3",
                    "tooltip": "Number of reference frames. Higher improves compression at the cost of speed.",
                    "category": "Analysis & ME",
                },
                "rc_lookahead": {
                    "label": "Lookahead:",
                    "ffmpeg_param": "rc-lookahead",
                    "widget": "spinbox_int",
                    "range": (0, 250),
                    "default": "40",
                    "tooltip": "Number of frames for rate control lookahead.",
                    "category": "Analysis & ME",
                },
                "subme": {
                    "label": "Subpixel ME:",
                    "ffmpeg_param": "subme",
                    "widget": "combobox",
                    "values": [str(i) for i in range(12)],
                    "default": "7",
                    "tooltip": "Subpixel motion estimation complexity.",
                    "category": "Analysis & ME",
                },
                "me_method": {
                    "label": "ME Method:",
                    "ffmpeg_param": "me",
                    "widget": "combobox",
                    "values": ["dia", "hex", "umh", "esa", "tesa"],
                    "default": "hex",
                    "tooltip": "Motion estimation algorithm.",
                    "category": "Analysis & ME",
                },
                "tune": {
                    "label": "Tune:",
                    "ffmpeg_param": "tune",
                    "widget": "combobox",
                    "values": [
                        "film",
                        "animation",
                        "grain",
                        "stillimage",
                        "fastdecode",
                        "zerolatency",
                    ],
                    "default": "",
                    "tooltip": "Tune settings for a specific type of source material.",
                    "category": "Miscellaneous",
                },
                "profile": {
                    "label": "Profile:",
                    "ffmpeg_param": "profile:v",
                    "widget": "combobox",
                    "values": [
                        "baseline",
                        "main",
                        "high",
                        "high10",
                        "high422",
                        "high444",
                    ],
                    "default": "",
                    "tooltip": "Output stream profile constraints. Empty=auto.",
                    "category": "Miscellaneous",
                },
                "pix_fmt": {
                    "label": "Pixel Format:",
                    "ffmpeg_param": "pix_fmt",
                    "widget": "combobox",
                    "values": [
                        "yuv420p",
                        "yuvj420p",
                        "yuv422p",
                        "yuv444p",
                        "yuv420p10le",
                    ],
                    "default": "",
                    "tooltip": "Pixel format and bit depth. Empty=auto.",
                    "category": "Miscellaneous",
                },
            },
        },
        "libx264rgb": {  # x264 RGB 소프트웨어 인코더 설정
            "group": "Software",
            "rate_control": "-crf",
            "quality_range": (0, 51),  # 소프트웨어 그룹, CRF 비트레이트 제어, 품질 범위
            "preset_param": "-preset",  # 프리셋 파라미터
            "preset_values": [
                "ultrafast",
                "superfast",
                "veryfast",
                "faster",
                "fast",
                "medium",
                "slow",
                "slower",
                "veryslow",
                "placebo",
            ],  # 사용 가능한 프리셋 목록
            "adv_options": {
                "g": {
                    "label": "GOP Size:",
                    "ffmpeg_param": "g",
                    "widget": "spinbox_int",
                    "range": (0, 1000),
                    "default": "250",
                    "tooltip": "Keyframe interval. Use 1 for lossless single frames.",
                    "category": "Frame & GOP",
                },
                "tune": {
                    "label": "Tune:",
                    "ffmpeg_param": "tune",
                    "widget": "combobox",
                    "values": ["zerolatency", "fastdecode", "stillimage"],
                    "default": "",
                    "tooltip": "Tune settings for a specific type of source material.",
                    "category": "Miscellaneous",
                },
                "profile": {
                    "label": "Profile:",
                    "ffmpeg_param": "profile:v",
                    "widget": "combobox",
                    "values": ["high444"],
                    "default": "high444",
                    "tooltip": "RGB encoding requires a 4:4:4 profile.",
                    "category": "Miscellaneous",
                },
                "pix_fmt": {
                    "label": "Pixel Format:",
                    "ffmpeg_param": "pix_fmt",
                    "widget": "combobox",
                    "values": ["rgb24", "bgr24", "rgba"],
                    "default": "rgb24",
                    "tooltip": "Pixel format for lossless RGB encoding.",
                    "category": "Miscellaneous",
                },
            },
        },
        "h264_nvenc": {  # NVIDIA H.264 하드웨어 인코더 설정
            "group": "NVIDIA NVENC",
            "rate_control": "-cq",
            "quality_range": (
                0,
                51,
            ),  # NVIDIA NVENC 그룹, CQ 비트레이트 제어, 품질 범위
            "preset_param": "-preset",  # 프리셋 파라미터
            "preset_values": [
                "slow",
                "medium",
                "fast",
                "hp",
                "hq",
                "bd",
                "ll",
                "llhq",
                "llhp",
                "lossless",
                "losslesshp",
                "p1",
                "p2",
                "p3",
                "p4",
                "p5",
                "p6",
                "p7",
            ],  # 사용 가능한 프리셋 목록
            "adv_options": {
                "spatial_aq": {
                    "label": "Spatial AQ",
                    "ffmpeg_param": "spatial-aq",
                    "widget": "checkbutton",
                    "default": False,
                    "tooltip": "Enable spatial adaptive quantization.",
                    "category": "Rate Control",
                },
                "temporal_aq": {
                    "label": "Temporal AQ",
                    "ffmpeg_param": "temporal-aq",
                    "widget": "checkbutton",
                    "default": False,
                    "tooltip": "Enable temporal adaptive quantization.",
                    "category": "Rate Control",
                },
                "rc_lookahead": {
                    "label": "Lookahead:",
                    "ffmpeg_param": "rc-lookahead",
                    "widget": "spinbox_int",
                    "range": (0, 250),
                    "default": "0",
                    "tooltip": "Number of frames for rate control lookahead.",
                    "category": "Rate Control",
                },
                "g": {
                    "label": "GOP Size:",
                    "ffmpeg_param": "g",
                    "widget": "spinbox_int",
                    "range": (0, 1000),
                    "default": "250",
                    "tooltip": "Keyframe interval.",
                    "category": "Frame & GOP",
                },
                "tune": {
                    "label": "Tune:",
                    "ffmpeg_param": "tune",
                    "widget": "combobox",
                    "values": ["hq", "ll", "ull", "lossless"],
                    "default": "hq",
                    "tooltip": "Tuning profile.",
                    "category": "Miscellaneous",
                },
                "profile": {
                    "label": "Profile:",
                    "ffmpeg_param": "profile:v",
                    "widget": "combobox",
                    "values": ["baseline", "main", "high", "high444p"],
                    "default": "",
                    "tooltip": "H.264 profile. Empty=auto.",
                    "category": "Miscellaneous",
                },
                "pix_fmt": {
                    "label": "Pixel Format:",
                    "ffmpeg_param": "pix_fmt",
                    "widget": "combobox",
                    "values": ["yuv420p", "nv12", "yuv444p"],
                    "default": "yuv420p",
                    "tooltip": "Pixel format. 'nv12' is a native hardware format.",
                    "category": "Miscellaneous",
                },
            },
        },
        "h264_qsv": {  # Intel H.264 하드웨어 인코더 설정
            "group": "Intel QSV",
            "rate_control": "-global_quality",
            "quality_range": (
                1,
                51,
            ),  # Intel QSV 그룹, global_quality 비트레이트 제어, 품질 범위
            "preset_param": "-preset",  # 프리셋 파라미터
            "preset_values": [
                "veryfast",
                "faster",
                "fast",
                "medium",
                "slow",
                "slower",
                "veryslow",
            ],  # 사용 가능한 프리셋 목록
            "adv_options": {
                "look_ahead": {
                    "label": "Lookahead",
                    "ffmpeg_param": "look_ahead",
                    "widget": "checkbutton",
                    "default": False,
                    "tooltip": "Enable lookahead for better rate control decisions.",
                    "category": "Rate Control",
                },
                "look_ahead_depth": {
                    "label": "Lookahead Depth:",
                    "ffmpeg_param": "look_ahead_depth",
                    "widget": "spinbox_int",
                    "range": (0, 100),
                    "default": "0",
                    "tooltip": "Number of frames to look ahead. Default depends on driver.",
                    "category": "Rate Control",
                },
                "g": {
                    "label": "GOP Size:",
                    "ffmpeg_param": "g",
                    "widget": "spinbox_int",
                    "range": (0, 1000),
                    "default": "250",
                    "tooltip": "Keyframe interval.",
                    "category": "Frame & GOP",
                },
                "profile": {
                    "label": "Profile:",
                    "ffmpeg_param": "profile",
                    "widget": "combobox",
                    "values": ["baseline", "main", "high"],
                    "default": "",
                    "tooltip": "H.264 profile. Empty=auto.",
                    "category": "Miscellaneous",
                },
                "pix_fmt": {
                    "label": "Pixel Format:",
                    "ffmpeg_param": "pix_fmt",
                    "widget": "combobox",
                    "values": ["nv12"],
                    "default": "nv12",
                    "tooltip": "Pixel format. 'nv12' is the primary native hardware format for H.264.",
                    "category": "Miscellaneous",
                },
            },
        },
        "h264_amf": {  # AMD H.264 하드웨어 인코더 설정
            "group": "AMD AMF",
            "rate_control": "-qp_p",
            "quality_range": (0, 51),  # AMD AMF 그룹, qp_p 비트레이트 제어, 품질 범위
            "adv_options": {
                "qp_i": {
                    "label": "I-Frame QP:",
                    "ffmpeg_param": "qp_i",
                    "widget": "spinbox_int",
                    "range": (-1, 51),
                    "default": "-1",
                    "tooltip": "Constant Quantization Parameter for I-frames.",
                    "category": "Rate Control",
                },
                "qp_p": {
                    "label": "P-Frame QP:",
                    "ffmpeg_param": "qp_p",
                    "widget": "spinbox_int",
                    "range": (-1, 51),
                    "default": "-1",
                    "tooltip": "Constant Quantization Parameter for P-frames. Used as the main quality slider.",
                    "category": "Rate Control",
                },
                "qp_b": {
                    "label": "B-Frame QP:",
                    "ffmpeg_param": "qp_b",
                    "widget": "spinbox_int",
                    "range": (-1, 51),
                    "default": "-1",
                    "tooltip": "Constant Quantization Parameter for B-frames.",
                    "category": "Rate Control",
                },
                "vbaq": {
                    "label": "Enable VBAQ",
                    "ffmpeg_param": "vbaq",
                    "widget": "checkbutton",
                    "default": False,
                    "tooltip": "Enable Variance Based Adaptive Quantization.",
                    "category": "Rate Control",
                },
                "g": {
                    "label": "GOP Size:",
                    "ffmpeg_param": "g",
                    "widget": "spinbox_int",
                    "range": (0, 1000),
                    "default": "250",
                    "tooltip": "Keyframe interval.",
                    "category": "Frame & GOP",
                },
                "bf": {
                    "label": "B-Frames:",
                    "ffmpeg_param": "bf",
                    "widget": "spinbox_int",
                    "range": (-1, 16),
                    "default": "0",
                    "tooltip": "Number of consecutive B-frames.",
                    "category": "Frame & GOP",
                },
                "refs": {
                    "label": "Reference Frames:",
                    "ffmpeg_param": "refs",
                    "widget": "spinbox_int",
                    "range": (1, 16),
                    "default": "1",
                    "tooltip": "Number of reference frames.",
                    "category": "Frame & GOP",
                },
                "usage": {
                    "label": "Usage Preset:",
                    "ffmpeg_param": "usage",
                    "widget": "combobox",
                    "values": [
                        "transcoding",
                        "ultralowlatency",
                        "lowlatency",
                        "webcam",
                    ],
                    "default": "transcoding",
                    "tooltip": "Intended usage scenario preset.",
                    "category": "Miscellaneous",
                },
                "quality": {
                    "label": "Quality Preset:",
                    "ffmpeg_param": "quality",
                    "widget": "combobox",
                    "values": ["speed", "balanced", "quality"],
                    "default": "balanced",
                    "tooltip": "Speed vs Quality trade-off preset.",
                    "category": "Miscellaneous",
                },
                "profile": {
                    "label": "Profile:",
                    "ffmpeg_param": "profile",
                    "widget": "combobox",
                    "values": ["baseline", "main", "high"],
                    "default": "",
                    "tooltip": "H.264 profile. Empty=auto.",
                    "category": "Miscellaneous",
                },
                "pix_fmt": {
                    "label": "Pixel Format:",
                    "ffmpeg_param": "pix_fmt",
                    "widget": "combobox",
                    "values": ["nv12", "yuv420p"],
                    "default": "nv12",
                    "tooltip": "Pixel format. 'nv12' is a native hardware format.",
                    "category": "Miscellaneous",
                },
            },
        },
        
        # ==============================================================================
        # H.265 / HEVC Encoders
        # ==============================================================================
        "libx265": {  # x265 소프트웨어 인코더 설정
            "group": "Software",
            "rate_control": "-crf",
            "quality_range": (0, 51),  # 소프트웨어 그룹, CRF 비트레이트 제어, 품질 범위
            "param_bundle_key": "-x265-params",  # x265 파라미터 묶음 키
            "preset_param": "-preset",  # 프리셋 파라미터
            "preset_values": [
                "ultrafast",
                "superfast",
                "veryfast",
                "faster",
                "fast",
                "medium",
                "slow",
                "slower",
                "veryslow",
                "placebo",
            ],  # 사용 가능한 프리셋 목록
            "adv_options": {
                "vbv_maxrate": {
                    "label": "Max Rate (kb/s):",
                    "ffmpeg_param": "vbv-maxrate",
                    "widget": "entry",
                    "default": "0",
                    "tooltip": "VBV Max Bitrate. 0=unlimited.",
                    "category": "Rate Control",
                },
                "vbv_bufsize": {
                    "label": "Buffer Size (kb):",
                    "ffmpeg_param": "vbv-bufsize",
                    "widget": "entry",
                    "default": "0",
                    "tooltip": "VBV Buffer Size. Use with Max Rate.",
                    "category": "Rate Control",
                },
                "aq_mode": {
                    "label": "AQ Mode:",
                    "ffmpeg_param": "aq-mode",
                    "widget": "combobox",
                    "values": ["0", "1", "2", "3"],
                    "default": "2",
                    "tooltip": "Adaptive Quantization mode. 0:Off, 1:Variance, 2:Auto-variance, 3:Complexity.",
                    "category": "Rate Control",
                },
                "psy_rd": {
                    "label": "Psy-RD:",
                    "ffmpeg_param": "psy-rd",
                    "widget": "spinbox_float",
                    "range": (0.0, 5.0),
                    "default": "0.3",
                    "tooltip": "Strength of psychovisual rate distortion.",
                    "category": "Psychovisual",
                },
                "psy_rdoq": {
                    "label": "Psy-RDOQ:",
                    "ffmpeg_param": "psy-rdoq",
                    "widget": "spinbox_float",
                    "range": (0.0, 50.0),
                    "default": "0.0",
                    "tooltip": "Strength of psychovisually optimized RDOQ.",
                    "category": "Psychovisual",
                },
                "rdoq_level": {
                    "label": "RDOQ Level:",
                    "ffmpeg_param": "rdoq-level",
                    "widget": "combobox",
                    "values": ["0", "1", "2"],
                    "default": "0",
                    "tooltip": "Rate-Distortion Optimized Quantization level.",
                    "category": "Psychovisual",
                },
                "g": {
                    "label": "Keyframe Interval:",
                    "ffmpeg_param": "keyint",
                    "widget": "spinbox_int",
                    "range": (0, 1000),
                    "default": "250",
                    "tooltip": "Max frames between keyframes (GOP size).",
                    "category": "Frame & GOP",
                },
                "min_keyint": {
                    "label": "Min Keyframe Interval:",
                    "ffmpeg_param": "min-keyint",
                    "widget": "spinbox_int",
                    "range": (0, 250),
                    "default": "25",
                    "tooltip": "Minimum interval between keyframes.",
                    "category": "Frame & GOP",
                },
                "scenecut": {
                    "label": "Scenecut:",
                    "ffmpeg_param": "scenecut",
                    "widget": "spinbox_int",
                    "range": (0, 100),
                    "default": "40",
                    "tooltip": "Scene change detection sensitivity. 0=disabled.",
                    "category": "Frame & GOP",
                },
                "bframes": {
                    "label": "B-Frames:",
                    "ffmpeg_param": "bframes",
                    "widget": "spinbox_int",
                    "range": (0, 16),
                    "default": "4",
                    "tooltip": "Max consecutive B-frames.",
                    "category": "Frame & GOP",
                },
                "open_gop": {
                    "label": "Open GOP",
                    "ffmpeg_param": "open-gop",
                    "widget": "checkbutton",
                    "default": True,
                    "tooltip": "Allow frames from other GOPs to be used as references.",
                    "category": "Frame & GOP",
                },
                "ref": {
                    "label": "Reference Frames:",
                    "ffmpeg_param": "ref",
                    "widget": "spinbox_int",
                    "range": (1, 16),
                    "default": "3",
                    "tooltip": "Number of reference frames.",
                    "category": "Analysis & ME",
                },
                "rc_lookahead": {
                    "label": "Lookahead:",
                    "ffmpeg_param": "rc-lookahead",
                    "widget": "spinbox_int",
                    "range": (0, 250),
                    "default": "20",
                    "tooltip": "Number of frames for rate control lookahead.",
                    "category": "Analysis & ME",
                },
                "subme": {
                    "label": "Subpixel ME:",
                    "ffmpeg_param": "subme",
                    "widget": "combobox",
                    "values": [str(i) for i in range(8)],
                    "default": "2",
                    "tooltip": "Subpixel motion estimation complexity.",
                    "category": "Analysis & ME",
                },
                "me_method": {
                    "label": "ME Method:",
                    "ffmpeg_param": "me",
                    "widget": "combobox",
                    "values": ["dia", "hex", "umh", "star", "full"],
                    "default": "star",
                    "tooltip": "Motion estimation algorithm.",
                    "category": "Analysis & ME",
                },
                "hdr_opt": {
                    "label": "HDR Optimization",
                    "ffmpeg_param": "hdr-opt",
                    "widget": "checkbutton",
                    "default": False,
                    "tooltip": "Enable color and quantization optimizations for HDR content.",
                    "category": "Color & HDR",
                },
                "tune": {
                    "label": "Tune:",
                    "ffmpeg_param": "tune",
                    "widget": "combobox",
                    "values": [
                        "grain",
                        "stillimage",
                        "fastdecode",
                        "zerolatency",
                        "psnr",
                        "ssim",
                    ],
                    "default": "",
                    "tooltip": "Tune settings for a specific type of source material.",
                    "category": "Miscellaneous",
                },
                "profile": {
                    "label": "Profile:",
                    "ffmpeg_param": "profile:v",
                    "widget": "combobox",
                    "values": ["main", "main10", "main12", "main422-10", "main444-8"],
                    "default": "main",
                    "tooltip": "Output stream profile constraints.",
                    "category": "Miscellaneous",
                },
                "pix_fmt": {
                    "label": "Pixel Format:",
                    "ffmpeg_param": "pix_fmt",
                    "widget": "combobox",
                    "values": [
                        "yuv420p",
                        "yuv420p10le",
                        "yuv422p10le",
                        "yuv444p",
                        "yuv444p10le",
                    ],
                    "default": "",
                    "tooltip": "Pixel format and bit depth. Empty=auto.",
                    "category": "Miscellaneous",
                },
            },
        },
        "hevc_nvenc": {  # NVIDIA HEVC 하드웨어 인코더 설정
            "group": "NVIDIA NVENC",
            "rate_control": "-cq",
            "quality_range": (
                0,
                51,
            ),  # NVIDIA NVENC 그룹, CQ 비트레이트 제어, 품질 범위
            "preset_param": "-preset",  # 프리셋 파라미터
            "preset_values": [
                "slow",
                "medium",
                "fast",
                "hp",
                "hq",
                "bd",
                "ll",
                "llhq",
                "llhp",
                "lossless",
                "losslesshp",
                "p1",
                "p2",
                "p3",
                "p4",
                "p5",
                "p6",
                "p7",
            ],  # 사용 가능한 프리셋 목록
            "adv_options": {
                "spatial_aq": {
                    "label": "Spatial AQ",
                    "ffmpeg_param": "spatial-aq",
                    "widget": "checkbutton",
                    "default": False,
                    "tooltip": "Enable spatial adaptive quantization.",
                    "category": "Rate Control",
                },
                "temporal_aq": {
                    "label": "Temporal AQ",
                    "ffmpeg_param": "temporal-aq",
                    "widget": "checkbutton",
                    "default": False,
                    "tooltip": "Enable temporal adaptive quantization.",
                    "category": "Rate Control",
                },
                "rc_lookahead": {
                    "label": "Lookahead:",
                    "ffmpeg_param": "rc-lookahead",
                    "widget": "spinbox_int",
                    "range": (0, 250),
                    "default": "0",
                    "tooltip": "Number of frames for rate control lookahead.",
                    "category": "Rate Control",
                },
                "g": {
                    "label": "GOP Size:",
                    "ffmpeg_param": "g",
                    "widget": "spinbox_int",
                    "range": (0, 1000),
                    "default": "250",
                    "tooltip": "Keyframe interval.",
                    "category": "Frame & GOP",
                },
                "tune": {
                    "label": "Tune:",
                    "ffmpeg_param": "tune",
                    "widget": "combobox",
                    "values": ["hq", "ll", "ull", "lossless"],
                    "default": "hq",
                    "tooltip": "Tuning profile.",
                    "category": "Miscellaneous",
                },
                "profile": {
                    "label": "Profile:",
                    "ffmpeg_param": "profile",
                    "widget": "combobox",
                    "values": ["main", "main10", "rext"],
                    "default": "main",
                    "tooltip": "HEVC profile.",
                    "category": "Miscellaneous",
                },
                "pix_fmt": {
                    "label": "Pixel Format:",
                    "ffmpeg_param": "pix_fmt",
                    "widget": "combobox",
                    "values": ["yuv420p", "nv12", "p010le", "yuv444p"],
                    "default": "yuv420p",
                    "tooltip": "Pixel format. 'p010le' is a native 10-bit hardware format.",
                    "category": "Miscellaneous",
                },
            },
        },
        "hevc_qsv": {  # Intel HEVC 하드웨어 인코더 설정
            "group": "Intel QSV",
            "rate_control": "-global_quality",
            "quality_range": (
                1,
                51,
            ),  # Intel QSV 그룹, global_quality 비트레이트 제어, 품질 범위
            "preset_param": "-preset",  # 프리셋 파라미터
            "preset_values": [
                "veryfast",
                "faster",
                "fast",
                "medium",
                "slow",
                "slower",
                "veryslow",
            ],
            "adv_options": {
                "look_ahead": {
                    "label": "Lookahead",
                    "ffmpeg_param": "look_ahead",
                    "widget": "checkbutton",
                    "default": False,
                    "tooltip": "Enable lookahead for better rate control decisions.",
                    "category": "Rate Control",
                },  # 룩어헤드 활성화로 더 나은 비트레이트 제어 결정
                "look_ahead_depth": {
                    "label": "Lookahead Depth:",
                    "ffmpeg_param": "look_ahead_depth",
                    "widget": "spinbox_int",
                    "range": (0, 100),
                    "default": "0",
                    "tooltip": "Number of frames to look ahead.",
                    "category": "Rate Control",
                },  # 룩어헤드 프레임 수
                "extbrc": {
                    "label": "Extended BRC",
                    "ffmpeg_param": "extbrc",
                    "widget": "checkbutton",
                    "default": False,
                    "tooltip": "Enable extended bitrate control for better quality.",
                    "category": "Rate Control",
                },  # 확장 비트레이트 제어로 더 나은 품질
                "g": {
                    "label": "GOP Size:",
                    "ffmpeg_param": "g",
                    "widget": "spinbox_int",
                    "range": (0, 1000),
                    "default": "250",
                    "tooltip": "Keyframe interval.",
                    "category": "Frame & GOP",
                },  # 키프레임 간격
                "profile": {
                    "label": "Profile:",
                    "ffmpeg_param": "profile",
                    "widget": "combobox",
                    "values": ["main", "main10"],
                    "default": "main",
                    "tooltip": "HEVC profile.",
                    "category": "Miscellaneous",
                },  # HEVC 프로파일
                "pix_fmt": {
                    "label": "Pixel Format:",
                    "ffmpeg_param": "pix_fmt",
                    "widget": "combobox",
                    "values": ["nv12", "p010le"],
                    "default": "nv12",
                    "tooltip": "Pixel format. 'p010le' is the native 10-bit hardware format.",
                    "category": "Miscellaneous",
                },  # 픽셀 포맷, p010le은 10비트 하드웨어 포맷
            },
        },
        "hevc_amf": {  # AMD HEVC 하드웨어 인코더 설정
            "group": "AMD AMF",
            "rate_control": "-qp_p",
            "quality_range": (0, 51),  # AMD AMF 그룹, qp_p 비트레이트 제어, 품질 범위
            "adv_options": {
                "qp_i": {
                    "label": "I-Frame QP:",
                    "ffmpeg_param": "qp_i",
                    "widget": "spinbox_int",
                    "range": (-1, 51),
                    "default": "-1",
                    "tooltip": "Constant Quantization Parameter for I-frames. -1=auto.",
                    "category": "Rate Control",
                },  # I프레임 양자화 파라미터, -1=자동
                "qp_p": {
                    "label": "P-Frame QP:",
                    "ffmpeg_param": "qp_p",
                    "widget": "spinbox_int",
                    "range": (-1, 51),
                    "default": "-1",
                    "tooltip": "Constant Quantization Parameter for P-frames. -1=auto.",
                    "category": "Rate Control",
                },  # P프레임 양자화 파라미터, -1=자동
                "qp_b": {
                    "label": "B-Frame QP:",
                    "ffmpeg_param": "qp_b",
                    "widget": "spinbox_int",
                    "range": (-1, 51),
                    "default": "-1",
                    "tooltip": "Constant Quantization Parameter for B-frames. -1=auto.",
                    "category": "Rate Control",
                },  # B프레임 양자화 파라미터, -1=자동
                "vbaq": {
                    "label": "Enable VBAQ",
                    "ffmpeg_param": "vbaq",
                    "widget": "checkbutton",
                    "default": False,
                    "tooltip": "Enable Variance Based Adaptive Quantization.",
                    "category": "Rate Control",
                },  # 분산 기반 적응형 양자화 활성화
                "g": {
                    "label": "GOP Size:",
                    "ffmpeg_param": "g",
                    "widget": "spinbox_int",
                    "range": (0, 1000),
                    "default": "250",
                    "tooltip": "Keyframe interval.",
                    "category": "Frame & GOP",
                },  # 키프레임 간격
                "bf": {
                    "label": "B-Frames:",
                    "ffmpeg_param": "bf",
                    "widget": "spinbox_int",
                    "range": (-1, 16),
                    "default": "0",
                    "tooltip": "Number of consecutive B-frames. -1=auto.",
                    "category": "Frame & GOP",
                },  # 연속 B프레임 수, -1=자동
                "refs": {
                    "label": "Reference Frames:",
                    "ffmpeg_param": "refs",
                    "widget": "spinbox_int",
                    "range": (1, 16),
                    "default": "1",
                    "tooltip": "Number of reference frames.",
                    "category": "Frame & GOP",
                },  # 참조 프레임 수
                "header_insertion_mode": {
                    "label": "Header Insertion:",
                    "ffmpeg_param": "header_insertion_mode",
                    "widget": "combobox",
                    "values": ["disabled", "gop", "idr"],
                    "default": "disabled",
                    "tooltip": "Controls insertion of sequence and picture parameter sets.",
                    "category": "Frame & GOP",
                },  # 시퀀스 및 픽처 파라미터 세트 삽입 제어
                "usage": {
                    "label": "Usage Preset:",
                    "ffmpeg_param": "usage",
                    "widget": "combobox",
                    "values": [
                        "transcoding",
                        "ultralowlatency",
                        "lowlatency",
                        "webcam",
                    ],
                    "default": "transcoding",
                    "tooltip": "Intended usage scenario preset.",
                    "category": "Miscellaneous",
                },  # 사용 시나리오 프리셋
                "quality": {
                    "label": "Quality Preset:",
                    "ffmpeg_param": "quality",
                    "widget": "combobox",
                    "values": ["speed", "balanced", "quality"],
                    "default": "balanced",
                    "tooltip": "Speed vs Quality trade-off preset.",
                    "category": "Miscellaneous",
                },  # 속도 vs 품질 트레이드오프 프리셋
                "profile": {
                    "label": "Profile:",
                    "ffmpeg_param": "profile",
                    "widget": "combobox",
                    "values": ["main", "main10"],
                    "default": "main",
                    "tooltip": "HEVC profile.",
                    "category": "Miscellaneous",
                },  # HEVC 프로파일
                "pix_fmt": {
                    "label": "Pixel Format:",
                    "ffmpeg_param": "pix_fmt",
                    "widget": "combobox",
                    "values": ["nv12", "p010le", "yuv420p", "yuv420p10le"],
                    "default": "nv12",
                    "tooltip": "Pixel format. 'p010le' enables 10-bit encoding.",
                    "category": "Miscellaneous",
                },  # 픽셀 포맷, p010le은 10비트 인코딩 활성화
            },
        },
        
        # ==============================================================================
        # AV1 Encoders
        # ==============================================================================
        "libaom-av1": {  # libaom AV1 소프트웨어 인코더 설정
            "group": "Software",
            "rate_control": "-crf",
            "quality_range": (0, 63),  # 소프트웨어 그룹, CRF 비트레이트 제어, 품질 범위
            "adv_options": {
                "b:v": {
                    "label": "Target Bitrate (kb/s):",
                    "ffmpeg_param": "b:v",
                    "widget": "entry",
                    "default": "0",
                    "tooltip": "Target bitrate for VBR mode. Set to 0 for CRF mode.",
                    "category": "Rate Control",
                },  # VBR 모드용 목표 비트레이트, 0=CRF 모드
                "cpu_used": {
                    "label": "CPU Used:",
                    "ffmpeg_param": "cpu-used",
                    "widget": "spinbox_int",
                    "range": (0, 8),
                    "default": "1",
                    "tooltip": "CPU usage/speed control. Lower is slower and higher quality.",
                    "category": "Performance",
                },  # CPU 사용량/속도 제어, 낮을수록 느리고 품질 높음
                "row_mt": {
                    "label": "Row Multithreading",
                    "ffmpeg_param": "row-mt",
                    "widget": "checkbutton",
                    "default": True,
                    "tooltip": "Enable row-based multithreading.",
                    "category": "Performance",
                },  # 행 기반 멀티스레딩 활성화
                "tile_columns": {
                    "label": "Tile Columns (log2):",
                    "ffmpeg_param": "tile-columns",
                    "widget": "spinbox_int",
                    "range": (0, 6),
                    "default": "0",
                    "tooltip": "Number of tile columns (log2). E.g., 2 = 4 columns.",
                    "category": "Performance",
                },  # 타일 열 수 (log2), 예: 2 = 4열
                "tile_rows": {
                    "label": "Tile Rows (log2):",
                    "ffmpeg_param": "tile-rows",
                    "widget": "spinbox_int",
                    "range": (0, 6),
                    "default": "0",
                    "tooltip": "Number of tile rows (log2). E.g., 1 = 2 rows.",
                    "category": "Performance",
                },  # 타일 행 수 (log2), 예: 1 = 2행
                "enable_cdef": {
                    "label": "Enable CDEF",
                    "ffmpeg_param": "enable-cdef",
                    "widget": "checkbutton",
                    "default": True,
                    "tooltip": "Enable Constrained Directional Enhancement Filter.",
                    "category": "Analysis & ME",
                },  # 제약된 방향성 향상 필터 활성화
                "enable_restoration": {
                    "label": "Enable Restoration",
                    "ffmpeg_param": "enable-restoration",
                    "widget": "checkbutton",
                    "default": True,
                    "tooltip": "Enable Loop Restoration Filter.",
                    "category": "Analysis & ME",
                },  # 루프 복원 필터 활성화
                "tune": {
                    "label": "Tune:",
                    "ffmpeg_param": "tune",
                    "widget": "combobox",
                    "values": [
                        "ssim",
                        "psnr",
                        "vmaf_with_preprocessing",
                        "vmaf_without_preprocessing",
                    ],
                    "default": "",
                    "tooltip": "Tune for a specific quality metric.",
                    "category": "Miscellaneous",
                },  # 특정 품질 메트릭에 맞춤 조정
                "profile": {
                    "label": "Profile:",
                    "ffmpeg_param": "profile",
                    "widget": "combobox",
                    "values": ["main", "high", "professional"],
                    "default": "main",
                    "tooltip": "AV1 profile.",
                    "category": "Miscellaneous",
                },  # AV1 프로파일
                "pix_fmt": {
                    "label": "Pixel Format:",
                    "ffmpeg_param": "pix_fmt",
                    "widget": "combobox",
                    "values": ["yuv420p", "yuv420p10le", "yuv422p10le", "yuv444p10le"],
                    "default": "",
                    "tooltip": "Pixel format. AV1 is typically used with 10-bit. Empty=auto.",
                    "category": "Miscellaneous",
                },  # 픽셀 포맷, AV1은 보통 10비트 사용, 빈값=자동
            },
        },
        "svt-av1": {  # SVT-AV1 소프트웨어 인코더 설정
            "group": "Software",
            "rate_control": "-crf",
            "quality_range": (0, 63),  # 소프트웨어 그룹, CRF 비트레이트 제어, 품질 범위
            "preset_param": "-preset",  # 프리셋 파라미터
            "preset_values": [str(i) for i in range(13)],  # 0-12 프리셋 값들
            "adv_options": {
                "gop_size": {
                    "label": "GOP Size:",
                    "ffmpeg_param": "g",
                    "widget": "spinbox_int",
                    "range": (-1, 256),
                    "default": "-1",
                    "tooltip": "Keyframe interval (in frames). -1=auto.",
                    "category": "Frame & GOP",
                },  # 키프레임 간격 (프레임 단위), -1=자동
                "scm": {
                    "label": "Scene Change Detection:",
                    "ffmpeg_param": "scm",
                    "widget": "combobox",
                    "values": ["0", "1"],
                    "default": "0",
                    "tooltip": "Enable scene change detection.",
                    "category": "Miscellaneous",
                },  # 장면 변화 감지 활성화
                "film_grain": {
                    "label": "Film Grain Synthesis:",
                    "ffmpeg_param": "film-grain",
                    "widget": "spinbox_int",
                    "range": (0, 50),
                    "default": "0",
                    "tooltip": "Strength of film grain synthesis. 0=disabled.",
                    "category": "Psychovisual",
                },  # 필름 그레인 합성 강도, 0=비활성화
                "tune": {
                    "label": "Tune:",
                    "ffmpeg_param": "tune",
                    "widget": "combobox",
                    "values": ["0", "1"],
                    "default": "1",
                    "tooltip": "Tuning mode. 0: VMAF, 1: PSNR.",
                    "category": "Miscellaneous",
                },  # 튜닝 모드, 0: VMAF, 1: PSNR
                "profile": {
                    "label": "Profile:",
                    "ffmpeg_param": "profile",
                    "widget": "combobox",
                    "values": ["main", "high", "professional"],
                    "default": "main",
                    "tooltip": "AV1 profile.",
                    "category": "Miscellaneous",
                },  # AV1 프로파일
                "pix_fmt": {
                    "label": "Pixel Format:",
                    "ffmpeg_param": "pix_fmt",
                    "widget": "combobox",
                    "values": ["yuv420p", "yuv420p10le"],
                    "default": "",
                    "tooltip": "Pixel format. SVT-AV1 recommends 10-bit. Empty=auto.",
                    "category": "Miscellaneous",
                },  # 픽셀 포맷, SVT-AV1은 10비트 권장, 빈값=자동
            },
        },
        "librav1e": {  # rav1e AV1 소프트웨어 인코더 설정
            "group": "Software",
            "rate_control": "-qp",
            "quality_range": (0, 255),  # 소프트웨어 그룹, QP 비트레이트 제어, 품질 범위
            "adv_options": {
                "speed": {
                    "label": "Speed Preset:",
                    "ffmpeg_param": "speed",
                    "widget": "spinbox_int",
                    "range": (0, 10),
                    "default": "6",
                    "tooltip": "Speed level. 0 is slowest (best quality), 10 is fastest.",
                    "category": "Performance",
                },  # 속도 레벨, 0=가장 느림 (최고 품질), 10=가장 빠름
                "threads": {
                    "label": "Threads:",
                    "ffmpeg_param": "threads",
                    "widget": "spinbox_int",
                    "range": (0, 128),
                    "default": "0",
                    "tooltip": "Number of threads to use. 0 is auto.",
                    "category": "Performance",
                },  # 사용할 스레드 수, 0=자동
                "tile_columns": {
                    "label": "Tile Columns:",
                    "ffmpeg_param": "tile-columns",
                    "widget": "spinbox_int",
                    "range": (0, 64),
                    "default": "0",
                    "tooltip": "Number of tile columns.",
                    "category": "Performance",
                },  # 타일 열 수
                "tile_rows": {
                    "label": "Tile Rows:",
                    "ffmpeg_param": "tile-rows",
                    "widget": "spinbox_int",
                    "range": (0, 64),
                    "default": "0",
                    "tooltip": "Number of tile rows.",
                    "category": "Performance",
                },  # 타일 행 수
                "tune": {
                    "label": "Tune:",
                    "ffmpeg_param": "tune",
                    "widget": "combobox",
                    "values": ["psychovisual", "psnr"],
                    "default": "psychovisual",
                    "tooltip": "Tune for a quality metric. Psychovisual is recommended.",
                    "category": "Miscellaneous",
                },  # 품질 메트릭에 맞춤 조정, 심리시각적 조정 권장
                "pix_fmt": {
                    "label": "Pixel Format:",
                    "ffmpeg_param": "pix_fmt",
                    "widget": "combobox",
                    "values": ["yuv420p", "yuv420p10le", "yuv444p"],
                    "default": "",
                    "tooltip": "Pixel format. rav1e often performs well with 10-bit. Empty=auto.",
                    "category": "Miscellaneous",
                },  # 픽셀 포맷, rav1e는 10비트에서 성능이 좋음, 빈값=자동
            },
        },
        "av1_nvenc": {  # NVIDIA AV1 하드웨어 인코더 설정
            "group": "NVIDIA NVENC",
            "rate_control": "-cq",
            "quality_range": (
                0,
                51,
            ),  # NVIDIA NVENC 그룹, CQ 비트레이트 제어, 품질 범위
            "preset_param": "-preset",  # 프리셋 파라미터
            "preset_values": [
                "slow",
                "medium",
                "fast",
                "hp",
                "hq",
                "bd",
                "ll",
                "llhq",
                "llhp",
                "lossless",
                "losslesshp",
                "p1",
                "p2",
                "p3",
                "p4",
                "p5",
                "p6",
                "p7",
            ],  # 다양한 프리셋 값들
            "adv_options": {
                "spatial_aq": {
                    "label": "Spatial AQ",
                    "ffmpeg_param": "spatial-aq",
                    "widget": "checkbutton",
                    "default": False,
                    "tooltip": "Enable spatial adaptive quantization.",
                    "category": "Rate Control",
                },  # 공간 적응형 양자화 활성화
                "tune": {
                    "label": "Tune:",
                    "ffmpeg_param": "tune",
                    "widget": "combobox",
                    "values": ["hq", "ll", "ull"],
                    "default": "hq",
                    "tooltip": "Tuning profile.",
                    "category": "Miscellaneous",
                },  # 튜닝 프로파일
                "profile": {
                    "label": "Profile:",
                    "ffmpeg_param": "profile",
                    "widget": "combobox",
                    "values": ["main", "high", "professional"],
                    "default": "main",
                    "tooltip": "AV1 profile.",
                    "category": "Miscellaneous",
                },  # AV1 프로파일
                "pix_fmt": {
                    "label": "Pixel Format:",
                    "ffmpeg_param": "pix_fmt",
                    "widget": "combobox",
                    "values": ["p010le", "yuv420p"],
                    "default": "yuv420p",
                    "tooltip": "Pixel format. AV1 hardware encoding is typically 10-bit.",
                    "category": "Miscellaneous",
                },  # 픽셀 포맷, AV1 하드웨어 인코딩은 보통 10비트
            },
        },
        "av1_qsv": {  # Intel AV1 하드웨어 인코더 설정
            "group": "Intel QSV",
            "rate_control": "-global_quality",
            "quality_range": (
                1,
                51,
            ),  # Intel QSV 그룹, global_quality 비트레이트 제어, 품질 범위
            "preset_param": "-preset",  # 프리셋 파라미터
            "preset_values": [
                "veryfast",
                "faster",
                "fast",
                "medium",
                "slow",
                "slower",
                "veryslow",
            ],  # 프리셋 값들
            "adv_options": {
                "profile": {
                    "label": "Profile:",
                    "ffmpeg_param": "profile",
                    "widget": "combobox",
                    "values": ["main"],
                    "default": "main",
                    "tooltip": "AV1 profile. 'main' supports 10-bit.",
                    "category": "Miscellaneous",
                },  # AV1 프로파일, main은 10비트 지원
                "pix_fmt": {
                    "label": "Pixel Format:",
                    "ffmpeg_param": "pix_fmt",
                    "widget": "combobox",
                    "values": ["p010le"],
                    "default": "p010le",
                    "tooltip": "Pixel format. AV1 QSV requires a 10-bit hardware format.",
                    "category": "Miscellaneous",
                },  # 픽셀 포맷, AV1 QSV는 10비트 하드웨어 포맷 필요
            },
        },
        "av1_amf": {  # AMD AV1 하드웨어 인코더 설정
            "group": "AMD AMF",
            "rate_control": "-qp_p",
            "quality_range": (0, 51),  # AMD AMF 그룹, qp_p 비트레이트 제어, 품질 범위
            "adv_options": {
                "qp_i": {
                    "label": "I-Frame QP:",
                    "ffmpeg_param": "qp_i",
                    "widget": "spinbox_int",
                    "range": (0, 51),
                    "default": "22",
                    "tooltip": "Constant Quantization Parameter for I-frames.",
                    "category": "Rate Control",
                },  # I프레임 양자화 파라미터
                "qp_p": {
                    "label": "P-Frame QP:",
                    "ffmpeg_param": "qp_p",
                    "widget": "spinbox_int",
                    "range": (0, 51),
                    "default": "22",
                    "tooltip": "Constant Quantization Parameter for P-frames.",
                    "category": "Rate Control",
                },  # P프레임 양자화 파라미터
                "quality": {
                    "label": "Quality Preset:",
                    "ffmpeg_param": "quality",
                    "widget": "combobox",
                    "values": ["speed", "balanced", "quality"],
                    "default": "balanced",
                    "tooltip": "Speed vs Quality trade-off preset.",
                    "category": "Miscellaneous",
                },  # 속도 vs 품질 트레이드오프 프리셋
                "profile": {
                    "label": "Profile:",
                    "ffmpeg_param": "profile",
                    "widget": "combobox",
                    "values": ["main"],
                    "default": "main",
                    "tooltip": "AV1 profile. 'main' supports 10-bit.",
                    "category": "Miscellaneous",
                },  # AV1 프로파일, main은 10비트 지원
                "pix_fmt": {
                    "label": "Pixel Format:",
                    "ffmpeg_param": "pix_fmt",
                    "widget": "combobox",
                    "values": ["nv12", "p010le"],
                    "default": "p010le",
                    "tooltip": "Pixel format. 'p010le' enables 10-bit AV1 encoding.",
                    "category": "Miscellaneous",
                },  # 픽셀 포맷, p010le은 10비트 AV1 인코딩 활성화
            },
        },
    }



    # ==============================================================================
    # 6A. 초기화 및 UI 생성 (Initialization & UI Setup)
    # ==============================================================================

    def __init__(self, root):
        """
        VideoOptimizerApp 클래스를 초기화하고 메인 GUI를 구성.

        애플리케이션의 모든 구성 요소를 초기화하며, GUI 위젯 생성, 상태 변수 설정, FFmpeg 도구 준비 등을 수행함.
        사용자가 애플리케이션을 시작할 때 한 번만 호출됨.

        Args:
            root: Tkinter 루트 윈도우 객체
        """
        # --- 1. 기본 윈도우 설정 ---
        self.root = root  # 메인 윈도우 객체
        self.root.title("Video Encoding Optimizer")  # 윈도우 제목 설정
        self.set_window_center()  # 윈도우를 화면 중앙에 위치시킴
        self._create_menu()  # 메뉴 바 생성
        
        # 윈도우 종료 이벤트 핸들러 설정
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)

        # 프로그램 시작 로깅
        self.start_time = time.time()
        logging.info(LOG_MESSAGES['program_start'].format(
            APP_CONFIG['about_info']['version'],
            datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        ))

        # --- 2. 애플리케이션 상태 및 제어 변수 초기화 ---
        # FFmpeg 관련 경로 변수
        self.ffmpeg_path = ""  # FFmpeg 실행 파일 경로
        self.ffprobe_path = ""  # FFprobe 실행 파일 경로
        self.ffplay_path = ""  # ffplay.exe 경로 추가
        
        # 비동기 작업 및 상태 플래그
        self.optimization_thread = None  # 최적화 작업을 실행할 백그라운드 스레드
        self.is_cancelling = False  # 취소 요청 플래그
        self.is_busy = False  # 모든 비동기 작업을 포괄하는 상태 플래그
        self.is_ab_comparing = False  # A/B 비교 작업 상태를 추적하는 플래그
        self.is_previewing = False  # Sample Preview 작업 상태를 추적하는 플래그
        self.pool = None  # 멀티프로세싱 풀 객체
        
        # 시스템 및 작업 진행 관련 변수
        self.physical_cores = psutil.cpu_count(logical=False) or 1  # 시스템의 물리적 CPU 코어 수
        self.run_start_time = None  # 전체 작업 시작 시간 (ETA 계산용)
        self.completed_tasks = 0  # 완료된 인코딩 작업 수
        self.original_widget_states = {}  # 작업 중 비활성화할 위젯들의 원래 상태를 저장하는 딕셔너리

        # 시스템 정보 로깅
        try:
            import platform
            memory_gb = psutil.virtual_memory().total / (1024**3)
            logging.info(LOG_MESSAGES['system_info'].format(
                self.physical_cores,
                memory_gb,
                f"{platform.system()} {platform.release()}"
            ))
        except Exception as e:
            logging.warning(f"Failed to log system info: {e}")



        # --- 3. Tkinter 변수 및 UI 데이터 모델 초기화 ---
        # 파일 경로 및 결과 데이터 저장 변수
        self.filepath_var = tk.StringVar()  # 선택된 비디오 파일 경로
        self.all_results = []  # 모든 인코딩 결과 딕셔너리를 저장하는 리스트
        self.last_run_context = {}  # 마지막 실행의 컨텍스트(설정값)를 저장할 딕셔너리
        self.tree_item_to_result = {}  # Treeview 아이템 ID와 결과 데이터 딕셔너리를 매핑
        
        # 결과 뷰 모드 관련 변수
        self.view_mode_map = OrderedDict([ # 뷰 모드 매핑 (표시명 -> 내부값)
            ("Max Quality", "max_quality"), # 최대 품질 모드
            ("Efficiency", "efficiency") # 효율성 모드
        ])
        self.view_mode_display_var = tk.StringVar(value=list(self.view_mode_map.keys())[0]) # 현재 뷰 모드 표시 변수
        self.vmaf_threshold_var = tk.DoubleVar(value=APP_CONFIG['default_vmaf_threshold']) # VMAF 임계값

        # 샘플링 모드 관련 변수
        self.sample_mode_var = tk.StringVar(value="Auto") # 샘플링 모드 (Auto/Manual)
        self.auto_mode_type_var = tk.StringVar(value="Complex Scene") # 자동 모드 타입 (Complex Scene/Uniform)
        self.manual_start_time_s = tk.DoubleVar(value=0.0) # 수동 시작 시간 (초)
        self.manual_end_time_s = tk.DoubleVar(value=0.0) # 수동 종료 시간 (초)
        self.manual_time_display_var = tk.StringVar(value="Not Set") # 수동 시간 표시 문자열
        
        # VMAF 모델 관련 변수
        self.vmaf_model_path_var = tk.StringVar(value="[Default] vmaf_v0.6.1.json (FFmpeg built-in)") # VMAF 모델 경로 표시
        self.vmaf_model_dir = "" # VMAF 모델 디렉토리 경로

        # 추가 메트릭 계산 여부 변수
        self.calc_psnr_var = tk.BooleanVar(value=True) # PSNR 계산 여부
        self.calc_ssim_var = tk.BooleanVar(value=True) # SSIM 계산 여부
        self.calc_blockdetect_var = tk.BooleanVar(value=True) # Block Score 계산 여부

        # 장면 분석 방식 선택 변수
        self.ANALYSIS_METHOD_SINGLE = "Single-Point"
        self.ANALYSIS_METHOD_WINDOW = "Sliding Window"
        self.analysis_method_var = tk.StringVar(value=self.ANALYSIS_METHOD_WINDOW) # 기본값: 슬라이딩 윈도우

        # 인코더 선택 관련 변수
        self.encoder_group_var = tk.StringVar() # 선택된 인코더 그룹
        self.available_encoders = {} # 자동 감지된 사용 가능한 인코더 목록

        # 최적화 모드 관련 변수
        self.optimization_mode_var = tk.StringVar(value="Range Test") # 최적화 모드 (Range Test/Sweet Spot)
        self.target_vmaf_var = tk.DoubleVar(value=APP_CONFIG['default_target_vmaf']) # 목표 VMAF 값

        # 고급 설정 관련 변수
        self.adv_settings_vars = OrderedDict() # 고급 설정 값들을 저장할 딕셔너리 (코덱 변경 시 동적으로 채워짐)

        # 파일 대화상자 필터
        self.video_file_types = APP_CONFIG['file_type_filters'] # 파일 타입 필터

        # --- 4. UI 생성 및 후속 작업 시작 ---
        self.create_widgets() # UI 위젯들 생성
        self.root.after(100, self.setup_ffmpeg) # UI가 그려진 후 FFmpeg 준비 시작
        self.root.after(100, self.setup_vmaf_models) # UI가 그려진 후 VMAF 모델 준비 시작

    def set_window_center(self):
        """
        애플리케이션 창을 화면 중앙에 위치시킴.

        메인 애플리케이션 창을 사용자의 화면 중앙에 표시하도록 위치를 계산하고 설정함.
        화면 해상도와 창 크기를 고려하여 정확한 중앙 좌표를 계산함.
        """
        w, h = APP_CONFIG["window_size"]  # 창 너비와 높이
        sw, sh = self.root.winfo_screenwidth(), self.root.winfo_screenheight() # 화면 너비와 높이
        
        x, y = (sw - w) // 2, (sh - h) // 2  # 중앙 좌표 계산
        
        self.root.geometry(f"{w}x{h}+{x}+{y}")  # 창 크기와 위치 설정

    def _create_menu(self):
        """
        애플리케이션의 메인 메뉴 바를 생성.

        애플리케이션의 상단에 메뉴 바를 생성하고 구성함.
        현재는 About 메뉴만 포함되어 있으며, 향후 확장 가능한 구조로 설계됨.
        """
        menubar = tk.Menu(self.root)  # 메뉴 바 객체 생성
        self.root.config(menu=menubar)  # 윈도우에 메뉴 바 설정
        
        menubar.add_command(label="About", command=self._show_about_dialog)  # About 메뉴 항목 추가

    def create_widgets(self):
        """
        애플리케이션의 메인 UI 위젯들을 생성하고 배치.

        애플리케이션의 전체 사용자 인터페이스를 구성함.
        파일 선택, 인코딩 설정, 액션 버튼, 결과 표시 등의 모든 UI 요소를 생성하고 적절한 위치에 배치함.
        """
        # 애플리케이션의 모든 UI 요소를 담을 메인 프레임을 생성
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # 작업 중 비활성화할 위젯들을 관리할 리스트 초기화
        self.controls_to_disable = []
        
        # 각 섹션별 UI를 생성하는 헬퍼 메서드들을 순차적으로 호출
        self._setup_file_frame(main_frame)
        self._setup_settings_frame(main_frame)
        self._setup_action_frame(main_frame)
        self._setup_results_frame(main_frame)

    def _setup_file_frame(self, parent):
        """
        비디오 파일 선택과 관련된 UI 부분을 생성.

        사용자가 인코딩할 비디오 파일을 선택할 수 있는 UI 요소들을 생성함.
        파일 경로 표시 필드와 파일 선택 버튼을 포함하며, 작업 중에는 자동으로 비활성화됨.

        Args:
            parent: 부모 위젯 (메인 프레임)
        """
        # 파일 선택 섹션을 위한 프레임을 생성하고 배치
        frame = ttk.Frame(parent)
        frame.pack(fill=tk.X, pady=5)
        frame.columnconfigure(1, weight=1) # 파일 경로 Entry 위젯이 창 크기에 맞게 확장되도록 설정

        # UI 위젯들을 생성하고 그리드 레이아웃에 배치
        label = ttk.Label(frame, text="1. Select Video File")
        label.grid(row=0, column=0, sticky="w", padx=(5, 10))

        self.filepath_entry = ttk.Entry(frame, textvariable=self.filepath_var, state="readonly")
        self.filepath_entry.grid(row=0, column=1, sticky="ew", padx=(0, 5))

        self.select_button = ttk.Button(frame, text="Select Video...", command=self.select_file)
        self.select_button.grid(row=0, column=2)

        # 생성된 위젯들을 작업 중 비활성화할 목록에 추가
        self.controls_to_disable.extend([self.filepath_entry, self.select_button])

    def _setup_settings_frame(self, parent):
        """
        인코딩 설정과 관련된 모든 UI 부분을 생성.

        인코딩 작업에 필요한 모든 설정 옵션들을 포함하는 UI를 생성함.
        인코더 그룹, 코덱, 프리셋, 품질 범위, 최적화 모드, 오디오 옵션 등을 설정할 수 있는 컨트롤들을 제공함.

        Args:
            parent: 부모 위젯 (메인 프레임)
        """
        # 인코딩 설정 영역을 위한 LabelFrame 생성
        frame = ttk.LabelFrame(parent, text="2. Encoding Settings", padding=5)
        frame.pack(fill=tk.X, pady=5)

        # 설정 영역을 좌(주요 설정)와 우(샘플 선택)로 분할하기 위한 프레임
        top_frame = ttk.Frame(frame)
        top_frame.pack(fill=tk.X, expand=True)
        top_frame.columnconfigure(0, weight=1) # 왼쪽 열이 창 크기에 맞게 확장되도록 설정
        top_frame.columnconfigure(1, weight=0) # 오른쪽 열은 고정 너비를 갖도록 설정

        # --- 좌측 열: 인코딩 핵심 설정 ---
        # 인코더 그룹 및 코덱 선택 UI 구성
        row0_left = ttk.Frame(top_frame)
        row0_left.grid(row=0, column=0, sticky="ew", pady=1)
        row0_left.columnconfigure(1, weight=1)
        ttk.Label(row0_left, text="Encoder Group:").grid(row=0, column=0, sticky="w")
        
        mode_codec_subframe = ttk.Frame(row0_left)
        mode_codec_subframe.grid(row=0, column=1, sticky="ew", padx=5)
        mode_codec_subframe.columnconfigure(0, weight=1)
        mode_codec_subframe.columnconfigure(2, weight=1)
        
        self.encoder_group_combo = ttk.Combobox(mode_codec_subframe, textvariable=self.encoder_group_var, values=["Detecting..."], state="readonly")
        self.encoder_group_combo.grid(row=0, column=0, sticky="ew")
        self.encoder_group_combo.bind("<<ComboboxSelected>>", self._on_encoder_group_change)
        
        ttk.Label(mode_codec_subframe, text="Codec:").grid(row=0, column=1, padx=(10, 5), sticky="w")
        self.codec_var = tk.StringVar()
        self.codec_combo = ttk.Combobox(mode_codec_subframe, textvariable=self.codec_var, state="readonly")
        self.codec_combo.grid(row=0, column=2, sticky="ew")
        self.codec_combo.bind("<<ComboboxSelected>>", self._on_codec_change)

        # 프리셋 범위 선택 UI 구성
        row1_left = ttk.Frame(top_frame)
        row1_left.grid(row=1, column=0, sticky="ew", pady=1)
        row1_left.columnconfigure(1, weight=1)
        ttk.Label(row1_left, text="Preset Range:").grid(row=0, column=0, sticky="w")
        
        preset_control_frame = ttk.Frame(row1_left)
        preset_control_frame.grid(row=0, column=1, sticky="ew", padx=5)
        self.preset_start_var = tk.StringVar(value="fast")
        self.preset_end_var = tk.StringVar(value="veryslow")
        self.preset_start_combo = ttk.Combobox(preset_control_frame, textvariable=self.preset_start_var, values=[], state="readonly")
        self.preset_start_combo.pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Label(preset_control_frame, text=" to ").pack(side=tk.LEFT, padx=3)
        self.preset_end_combo = ttk.Combobox(preset_control_frame, textvariable=self.preset_end_var, values=[], state="readonly")
        self.preset_end_combo.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # 최적화 모드 선택 라디오 버튼 구성
        opt_mode_frame = ttk.Frame(top_frame)
        opt_mode_frame.grid(row=2, column=0, sticky="ew")
        opt_mode_frame.columnconfigure(1, weight=1)
        ttk.Label(opt_mode_frame, text="Optimization Mode:").grid(row=0, column=0, sticky="w")
        
        opt_mode_rb_frame = ttk.Frame(opt_mode_frame)
        opt_mode_rb_frame.grid(row=0, column=1, sticky="ew", padx=5)
        
        self.range_test_rb = ttk.Radiobutton(opt_mode_rb_frame, text="Range Test", variable=self.optimization_mode_var, value="Range Test")
        self.range_test_rb.pack(side=tk.LEFT, padx=(0, 10))
        ToolTip(self.range_test_rb, "Tests every combination of selected presets and quality (CRF) values.\nIdeal for a comprehensive analysis of the quality/size trade-off.")
        
        self.target_vmaf_rb = ttk.Radiobutton(opt_mode_rb_frame, text="Target VMAF", variable=self.optimization_mode_var, value="Target VMAF")
        self.target_vmaf_rb.pack(side=tk.LEFT)
        ToolTip(self.target_vmaf_rb, "Finds the most efficient setting (highest CRF) for each preset that meets the target VMAF score.")

        # "Range Test" 모드 선택 시 표시될 품질 범위 설정 UI
        self.quality_range_frame = ttk.Frame(top_frame)
        self.quality_range_frame.grid(row=3, column=0, sticky="ew", pady=1)
        self.quality_range_frame.columnconfigure(1, weight=1)
        
        self.quality_range_label = ttk.Label(self.quality_range_frame, text="CRF Range (0-51):")
        self.quality_range_label.grid(row=0, column=0, sticky="w")
        
        crf_control_frame = ttk.Frame(self.quality_range_frame)
        crf_control_frame.grid(row=0, column=1, sticky="ew", padx=5)
        self.crf_start_var = tk.StringVar(value="18")
        self.crf_end_var = tk.StringVar(value="28")
        self.crf_start_spinbox = ttk.Spinbox(crf_control_frame, from_=0, to=63, textvariable=self.crf_start_var, width=5)
        self.crf_start_spinbox.pack(side=tk.LEFT)
        ttk.Label(crf_control_frame, text=" to ").pack(side=tk.LEFT, padx=3)
        self.crf_end_spinbox = ttk.Spinbox(crf_control_frame, from_=0, to=63, textvariable=self.crf_end_var, width=5)
        self.crf_end_spinbox.pack(side=tk.LEFT)

        # "Target VMAF" 모드 선택 시 표시될 목표 VMAF 설정 UI
        self.target_vmaf_frame = ttk.Frame(top_frame)
        self.target_vmaf_frame.grid(row=3, column=0, sticky="ew", pady=1)
        self.target_vmaf_frame.columnconfigure(1, weight=1)
        
        ttk.Label(self.target_vmaf_frame, text="Target VMAF Score:").grid(row=0, column=0, sticky="w")
        self.target_vmaf_spinbox = ttk.Spinbox(self.target_vmaf_frame, from_=0, to=100, increment=0.1, textvariable=self.target_vmaf_var, width=8)
        self.target_vmaf_spinbox.grid(row=0, column=1, sticky="w", padx=5)

        # 오디오 처리 방식 선택 UI 구성
        row4_left = ttk.Frame(top_frame)
        row4_left.grid(row=4, column=0, sticky="ew", pady=1)
        row4_left.columnconfigure(1, weight=1)
        ttk.Label(row4_left, text="Audio:").grid(row=0, column=0, sticky="w")
        self.audio_var = tk.StringVar(value="Remove Audio")
        self.audio_combo = ttk.Combobox(row4_left, textvariable=self.audio_var, values=["Copy Audio", "Remove Audio"], state="readonly")
        self.audio_combo.grid(row=0, column=1, sticky="ew", padx=5)

        # 하단 컨트롤 영역(메트릭, 분석 방식, 병렬 작업 등)을 위한 컨테이너 프레임
        bottom_controls_container = ttk.Frame(top_frame)
        # columnspan=2를 사용하여 컨테이너가 top_frame의 두 열을 모두 차지하도록 설정
        bottom_controls_container.grid(row=5, column=0, columnspan=2, sticky="ew", pady=(5,0), rowspan=2)

        # 추가 메트릭 선택 체크박스 그룹
        metrics_frame = ttk.Frame(bottom_controls_container)
        metrics_frame.pack(side=tk.LEFT) # 컨테이너의 왼쪽에 배치
        ttk.Label(metrics_frame, text="Add Metrics:").pack(side=tk.LEFT)
        
        self.psnr_check = ttk.Checkbutton(metrics_frame, text="PSNR", variable=self.calc_psnr_var)
        self.psnr_check.pack(side=tk.LEFT, padx=(5,0))
        ToolTip(self.psnr_check, "Calculate Peak Signal-to-Noise Ratio. A classic metric, but less correlated with human perception than VMAF. Adds minor overhead.")
        
        self.ssim_check = ttk.Checkbutton(metrics_frame, text="SSIM", variable=self.calc_ssim_var)
        self.ssim_check.pack(side=tk.LEFT, padx=(5,0))
        ToolTip(self.ssim_check, "Calculate Structural Similarity Index. Better than PSNR, but still less perceptually accurate than VMAF. Adds minor overhead.")
        
        self.blockdetect_check = ttk.Checkbutton(metrics_frame, text="Block Score", variable=self.calc_blockdetect_var)
        self.blockdetect_check.pack(side=tk.LEFT, padx=(5,0))
        ToolTip(self.blockdetect_check, "Calculate a score for blocking artifacts (higher is worse). Adds minor overhead.")

        # 병렬 작업 및 고급 설정 버튼 그룹
        parallel_jobs_and_adv_frame = ttk.Frame(bottom_controls_container)
        parallel_jobs_and_adv_frame.pack(side=tk.RIGHT) # 컨테이너의 오른쪽에 배치
 
        self.advanced_button = ttk.Button(parallel_jobs_and_adv_frame, text="Advanced Settings...", command=self.open_advanced_settings)
        self.advanced_button.pack(side=tk.RIGHT) # 그룹 내에서 가장 오른쪽에 배치
        
        self.parallel_jobs_var = tk.IntVar(value=max(1, self.physical_cores - 1))
        self.parallel_jobs_spinbox = ttk.Spinbox(parallel_jobs_and_adv_frame, from_=1, to=self.physical_cores, textvariable=self.parallel_jobs_var, width=5)
        self.parallel_jobs_spinbox.pack(side=tk.RIGHT, padx=(0, 5))
        ttk.Label(parallel_jobs_and_adv_frame, text="Parallel Jobs: ").pack(side=tk.RIGHT)

        # 장면 분석 방식 선택 콤보박스 그룹
        analysis_method_frame = ttk.Frame(bottom_controls_container)
        analysis_method_frame.pack(side=tk.LEFT, padx=10) # 왼쪽 그룹과 오른쪽 그룹 사이의 공간에 배치
        ttk.Label(analysis_method_frame, text="Analysis Method:").pack(side=tk.LEFT)

        self.analysis_method_combo = ttk.Combobox(
            analysis_method_frame,
            textvariable=self.analysis_method_var,
            values=[self.ANALYSIS_METHOD_SINGLE, self.ANALYSIS_METHOD_WINDOW],
            state="readonly",
            width=25
        )
        self.analysis_method_combo.pack(side=tk.LEFT, padx=5)
        ToolTip(
            self.analysis_method_combo,
            f"{self.ANALYSIS_METHOD_WINDOW}: Finds the most representative 'section' (e.g., a full 10s). More reliable.\n"
            f"{self.ANALYSIS_METHOD_SINGLE}: Finds the single most complex 'point' (e.g., 0.1s) and centers the sample. Faster but can be less representative."
        )

        # --- 우측 열: 샘플 선택 설정 ---
        sample_frame = ttk.LabelFrame(top_frame, text="Sample Selection")
        sample_frame.grid(row=0, column=1, rowspan=5, sticky="new", padx=(10,0))
        
        # 'Auto' 샘플링 모드 UI 구성
        auto_row_frame = ttk.Frame(sample_frame)
        auto_row_frame.pack(fill=tk.X, padx=5, pady=(5, 1))
        self.auto_rb = ttk.Radiobutton(auto_row_frame, text="Auto:", variable=self.sample_mode_var, value="Auto", command=self.toggle_sample_mode_ui)
        self.auto_rb.pack(side=tk.LEFT)
        
        self.auto_mode_type_combo = ttk.Combobox(auto_row_frame, textvariable=self.auto_mode_type_var, values=["Complex Scene", "Simple Scene"], state="readonly", width=15)
        self.auto_mode_type_combo.pack(side=tk.LEFT, padx=5)
        ToolTip(self.auto_mode_type_combo, "Complex Scene: Finds high motion/detail.\nSimple Scene: Finds areas prone to blocking (e.g., flat areas).")

        self.sample_duration_var = tk.IntVar(value=10)
        self.sample_duration_spinbox = ttk.Spinbox(auto_row_frame, from_=1, to=300, textvariable=self.sample_duration_var, width=5)
        self.sample_duration_spinbox.pack(side=tk.RIGHT)
        ttk.Label(auto_row_frame, text="Duration (s):").pack(side=tk.RIGHT, padx=(5,2))
        
        # 'Manual' 샘플링 모드 UI 구성
        manual_grid_frame = ttk.Frame(sample_frame)
        manual_grid_frame.pack(fill=tk.X, padx=5, pady=5)
        manual_grid_frame.columnconfigure(1, weight=1)

        self.manual_rb = ttk.Radiobutton(manual_grid_frame, text="Manual:", variable=self.sample_mode_var, value="Manual", command=self.toggle_sample_mode_ui)
        self.manual_rb.grid(row=0, column=0, sticky="w", pady=(0, 2))

        self.manual_time_entry = ttk.Entry(manual_grid_frame, textvariable=self.manual_time_display_var, state='readonly')
        self.manual_time_entry.grid(row=0, column=1, sticky="ew")
        ToolTip(self.manual_time_entry, "Manually select the start and end time for the sample.")

        self.manual_time_button = ttk.Button(manual_grid_frame, text="Set Range...", command=self.open_manual_time_selector)
        self.manual_time_button.grid(row=1, column=1, sticky="ew", pady=(1, 0))
        
        # 샘플 미리보기 버튼 구성
        self.sample_preview_button = ttk.Button(sample_frame, text="Sample Preview", state=tk.DISABLED, command=self.preview_sample)
        self.sample_preview_button.pack(fill=tk.X, padx=5, pady=(0, 5))

        # --- VMAF 모델 선택 UI ---
        vmaf_frame = ttk.Frame(frame)
        vmaf_frame.pack(fill=tk.X, expand=True, pady=(5, 0))
        vmaf_frame.columnconfigure(1, weight=1)
        
        vmaf_label = ttk.Label(vmaf_frame, text="VMAF Model:")
        vmaf_label.grid(row=0, column=0, padx=(0, 5), sticky='w')
        ToolTip(vmaf_label, "Select a VMAF model. Leave as default or choose a downloaded model.")
        
        self.vmaf_model_entry = ttk.Entry(vmaf_frame, textvariable=self.vmaf_model_path_var, state="readonly")
        self.vmaf_model_entry.grid(row=0, column=1, sticky='ew', padx=5)
        ToolTip(self.vmaf_model_entry, "Displays the currently selected VMAF model. 'Default' uses the standard model built into FFmpeg.\nUse the 'Browse...' button to select a specific model after downloading them.")
        
        self.vmaf_model_browse_button = ttk.Button(vmaf_frame, text="Browse...", command=self.open_vmaf_model_selector)
        self.vmaf_model_browse_button.grid(row=0, column=2, padx=(0,5))
        
        self.vmaf_model_update_button = ttk.Button(vmaf_frame, text="Download/Update Models", command=self.update_vmaf_models)
        self.vmaf_model_update_button.grid(row=0, column=3, padx=0)
        
        # 작업 중 비활성화할 컨트롤 목록을 정의
        self.controls_to_disable.extend([
            self.encoder_group_combo, self.codec_combo, self.audio_combo, self.preset_start_combo, self.preset_end_combo,
            self.crf_start_spinbox, self.crf_end_spinbox, self.parallel_jobs_spinbox,
            self.sample_duration_spinbox, self.advanced_button, self.psnr_check, self.ssim_check, self.blockdetect_check,
            self.vmaf_model_entry, self.vmaf_model_browse_button, self.vmaf_model_update_button,
            self.auto_rb, self.manual_rb, self.manual_time_button, self.sample_preview_button, self.auto_mode_type_combo,
            self.range_test_rb, self.target_vmaf_rb, self.target_vmaf_spinbox, self.analysis_method_combo
        ])
        
        # 초기 UI 상태를 설정하기 위해 관련 메서드들을 호출
        self.toggle_sample_mode_ui()
        self.range_test_rb.config(command=self._toggle_optimization_mode_ui)
        self.target_vmaf_rb.config(command=self._toggle_optimization_mode_ui)
        self._toggle_optimization_mode_ui()

    def _setup_action_frame(self, parent):
        """
        시작/취소 버튼 및 진행률 표시줄 UI 부분을 생성.

        인코딩 최적화 작업을 시작하고 취소할 수 있는 버튼들과 작업 진행 상황을 표시하는 진행률 표시줄을 생성함.
        작업 중에는 시작 버튼이 비활성화되고 취소 버튼이 활성화됨.

        Args:
            parent: 부모 위젯 (메인 프레임)
        """
        # 시작/취소 버튼을 담을 프레임
        action_frame = ttk.Frame(parent)
        action_frame.pack(fill=tk.X, pady=5)
        
        self.start_button = ttk.Button(action_frame, text="Start Optimization", command=self.start_optimization)
        self.start_button.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 5))
        
        self.cancel_button = ttk.Button(action_frame, text="Cancel", command=self.cancel_optimization, state=tk.DISABLED)
        self.cancel_button.pack(side=tk.LEFT, expand=True, fill=tk.X)
        
        # 진행 상황 표시를 위한 프레임
        progress_frame = ttk.LabelFrame(parent, text="Progress", padding=5)
        progress_frame.pack(fill=tk.X, pady=5)
        
        self.status_label_var = tk.StringVar(value="Ready.")
        ttk.Label(progress_frame, textvariable=self.status_label_var).pack(fill=tk.X)
        
        self.progress_bar = ttk.Progressbar(progress_frame, orient="horizontal", mode="determinate")
        self.progress_bar.pack(fill=tk.X, pady=5)

    def _setup_results_frame(self, parent):
        """
        결과 표시 및 관련 기능 버튼 UI 부분을 생성.

        인코딩 최적화 결과를 표시하는 테이블과 결과를 분석하고 내보낼 수 있는 다양한 기능 버튼들을 생성함.
        결과는 트리뷰 형태로 표시되며, 필터링과 정렬 기능을 제공함.

        Args:
            parent: 부모 위젯 (메인 프레임)
        """
        # 결과 섹션 전체를 감싸는 LabelFrame을 생성
        result_frame = ttk.LabelFrame(parent, text="Results", padding=5)
        result_frame.pack(fill=tk.BOTH, expand=True)
        
        # 결과 프레임 내부에 뷰 옵션과 결과 트리를 생성하는 헬퍼 메서드를 호출
        self._setup_view_options(result_frame)
        self._setup_results_tree(result_frame)

    def _setup_view_options(self, parent):
        """
        결과 필터링 및 내보내기 등 결과 관련 옵션 UI를 생성.

        결과를 다양한 방식으로 보기 위한 옵션들과 결과를 내보내거나 분석할 수 있는 기능 버튼들을 생성함.
        뷰 모드 선택, VMAF 임계값 설정, 결과 내보내기, 그래프 보기, A/B 비교 등의 기능을 제공함.

        Args:
            parent: 부모 위젯 (결과 프레임)
        """
        # 뷰 옵션과 액션 버튼들을 담을 상단 프레임
        top_frame = ttk.Frame(parent)
        top_frame.pack(fill=tk.X, pady=(0, 5))
        
        # 왼쪽: 뷰 필터링 옵션
        view_options_frame = ttk.Frame(top_frame)
        view_options_frame.pack(side=tk.LEFT)

        ttk.Label(view_options_frame, text="View:").pack(side=tk.LEFT, padx=(0, 5))
        self.view_mode_combo = ttk.Combobox(view_options_frame, textvariable=self.view_mode_display_var, values=list(self.view_mode_map.keys()), state="readonly", width=12)
        self.view_mode_combo.pack(side=tk.LEFT)
        self.view_mode_combo.bind("<<ComboboxSelected>>", lambda e: self.apply_view_filter())

        self.vmaf_threshold_label = ttk.Label(view_options_frame, text=" VMAF >=")
        self.vmaf_threshold_label.pack(side=tk.LEFT, padx=(10, 0))
        self.vmaf_threshold_spinbox = ttk.Spinbox(view_options_frame, from_=0, to=100, increment=0.1, textvariable=self.vmaf_threshold_var, width=6, command=self.apply_view_filter)
        self.vmaf_threshold_spinbox.pack(side=tk.LEFT)
        self.vmaf_threshold_spinbox.bind("<KeyRelease>", lambda e: self.root.after(100, self.apply_view_filter))

        # 오른쪽: 액션 버튼들
        action_buttons_frame = ttk.Frame(top_frame)
        action_buttons_frame.pack(side=tk.RIGHT)

        self.export_results_button = ttk.Button(action_buttons_frame, text="Export Results", command=self.export_results, state=tk.DISABLED)
        self.export_results_button.pack(side=tk.RIGHT, padx=2)

        self.gen_cmd_button = ttk.Button(action_buttons_frame, text="View Command", command=self.generate_final_command, state=tk.DISABLED)
        self.gen_cmd_button.pack(side=tk.RIGHT, padx=2)
        
        self.log_button = ttk.Button(action_buttons_frame, text="View Log", command=self.show_selected_log, state=tk.DISABLED)
        self.log_button.pack(side=tk.RIGHT, padx=2)

        self.ab_compare_button = ttk.Button(action_buttons_frame, text="A/B Compare", command=self.create_ab_samples, state=tk.DISABLED)
        self.ab_compare_button.pack(side=tk.RIGHT, padx=2)
        
        self.graph_button = ttk.Button(action_buttons_frame, text="View Graph", command=self.show_graph, state=tk.DISABLED)
        self.graph_button.pack(side=tk.RIGHT, padx=2)
        
        # 생성된 버튼들을 작업 중 비활성화할 목록에 추가
        self.controls_to_disable.extend([self.export_results_button, self.graph_button, self.ab_compare_button, 
                                         self.gen_cmd_button])

    def _setup_results_tree(self, parent):
        """
        결과를 표 형태로 보여주는 Treeview 위젯을 생성.

        인코딩 최적화 결과를 테이블 형태로 표시하는 Treeview 위젯을 생성함.
        각 결과는 프리셋, CRF, VMAF, PSNR, SSIM, 블록 점수, 파일 크기, 효율성 등의 컬럼으로 구성되며, 정렬과 필터링 기능을 제공함.

        Args:
            parent: 부모 위젯 (결과 프레임)
        """
        # Treeview와 스크롤바를 담을 프레임
        tree_frame = ttk.Frame(parent)
        tree_frame.pack(fill=tk.BOTH, expand=True)
        
        # Treeview의 컬럼 정의
        columns_tuple = ("preset", "crf", "vmaf", "vmaf_1_low", "psnr", "ssim", "block_score", "size_mb", "efficiency")
        self.tree = ttk.Treeview(tree_frame, columns=columns_tuple, show="headings")
        
        # 각 컬럼의 속성(너비, 제목 등)을 설정
        columns = {
            "preset": {"w": 80, "t": "Preset"}, "crf": {"w": 40, "t": "CRF"},
            "vmaf": {"w": 70, "t": "VMAF"}, "vmaf_1_low": {"w": 80, "t": "VMAF 1% Low"},
            "psnr": {"w": 70, "t": "PSNR"}, "ssim": {"w": 70, "t": "SSIM"},
            "block_score": {"w": 80, "t": "Block Score"},
            "size_mb": {"w": 80, "t": "Size (MB)"},
            "efficiency": {"w": 90, "t": "VMAF/MB"}
        }
        for col, p in columns.items():
            self.tree.column(col, width=p["w"], anchor="center")
            self.tree.heading(col, text=p["t"], command=lambda c=col: self.sort_treeview_column(c, False))

        # Treeview에 연결될 스크롤바를 생성하고 배치
        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # 결과 항목을 시각적으로 구분하기 위한 태그(스타일)를 설정
        self.tree.tag_configure('sweet_spot', background='yellow', foreground='black')
        self.tree.tag_configure('pareto', background='pale green', foreground='black')
        self.tree.tag_configure('worst_quality', background='purple', foreground='white')
        self.tree.tag_configure('worst_efficiency', background='red', foreground='white')

        # Treeview의 선택 이벤트를 메서드에 바인딩
        self.tree.bind("<<TreeviewSelect>>", self._on_tree_select)
        
        # 초기 뷰 필터를 적용하여 테이블을 그림
        self.apply_view_filter()



    # ==============================================================================
    # 6B. UI 이벤트 핸들러 및 사용자 상호작용 (UI Event Handlers & User Interaction)
    # ==============================================================================

    def _show_about_dialog(self):
        """
        'About' 정보 메시지 박스 표시.
        """
        info = APP_CONFIG['about_info']  # 프로그램 정보 가져오기
        
        # 표시할 메시지 문자열을 구성
        message = (
            f"{info['program']}\n"
            f"Version: {info['version']} (Last updated: {info['updated']})\n\n"
            f"Developer: {info['developer']}\n"
            f"Website: {info['website']}\n\n"
            f"License: {info['license']}"
        )
        
        messagebox.showinfo(f"About", message, parent=self.root)  # 정보 메시지 박스를 화면에 표시

    def select_file(self):
        """
        파일 열기 대화상자를 통해 비디오 파일을 선택.

        사용자가 비디오 파일을 선택할 때 호출되며, 파일 선택 대화상자를 열어 비디오 파일을 선택할 수 있게 함.
        파일이 선택되면 경로를 저장하고 샘플 미리보기 버튼을 활성화함.
        """
        # 사용자에게 비디오 파일을 선택할 수 있는 대화상자를 표시
        filepath = filedialog.askopenfilename(title="Select a video file", filetypes=self.video_file_types)
        
        # 사용자가 파일을 선택한 경우 (취소하지 않은 경우)
        if filepath:
            self.filepath_var.set(filepath) # 선택된 파일 경로를 tkinter 변수에 저장
            self.sample_preview_button.config(state=tk.NORMAL) # 파일이 선택되었으므로 샘플 미리보기 버튼을 활성화
            
            # 파일 선택 로깅
            try:
                file_size_mb = os.path.getsize(filepath) / (1024 * 1024)
                logging.info(LOG_MESSAGES['file_selected'].format(filepath, file_size_mb))
            except Exception as e:
                logging.warning(f"Failed to get file size for logging: {e}")
                logging.info(f"Video file selected: {filepath}")

    def _on_encoder_group_change(self, event=None):
        """
        인코더 그룹(Software, NVENC 등)이 변경될 때마다 해당 그룹의 코덱 목록을 업데이트.

        사용자가 인코더 그룹을 선택했을 때 호출되며, 해당 그룹에 속하는 사용 가능한 코덱들의 목록을 동적으로 업데이트함.
        시스템에서 실제로 사용 가능한 코덱만 목록에 포함시켜 사용자 경험을 향상시킴.

        Args:
            event: 콤보박스 선택 이벤트 객체 (사용되지 않음)
        """
        selected_group = self.encoder_group_var.get() # 선택된 인코더 그룹 가져오기

        # 인코더 그룹 변경 로깅
        logging.info(f"Encoder group changed to: {selected_group}")

        # 선택된 그룹에 속하면서, 시스템에서 사용 가능한 것으로 감지된 코덱들만 필터링
        available_codecs = [
            codec_name
            for codec_name, config in self.CODEC_CONFIG.items()
            if config.get("group") == selected_group and codec_name in self.available_encoders
        ]

        # 코덱 콤보박스의 목록을 필터링된 코덱들로 업데이트
        self.codec_combo["values"] = available_codecs
        if available_codecs:
            self.codec_var.set(available_codecs[0]) # 목록이 있으면 첫 번째 코덱을 기본으로 선택
        else:
            self.codec_var.set("") # 목록이 없으면 선택을 비움
        
        # 코덱 선택이 변경되었으므로, 관련 UI를 업데이트하기 위해 _on_codec_change 호출
        self._on_codec_change()

    def _on_codec_change(self, event=None):
        """
        코덱 선택이 변경될 때마다 프리셋 목록과 품질 범위 UI를 업데이트.

        사용자가 코덱을 선택했을 때 호출되며, 선택된 코덱에 맞는 프리셋 목록, 품질 범위, 고급 설정 등을 동적으로 업데이트함.
        코덱별로 다른 설정 옵션을 제공하여 사용자가 올바른 설정을 할 수 있도록 함.

        Args:
            event: 콤보박스 선택 이벤트 객체 (사용되지 않음)
        """
        codec = self.codec_var.get() # 현재 선택된 코덱 가져오기
        if not codec: # 선택된 코덱이 없으면 함수 종료
            return

        # 코덱 변경 로깅
        logging.info(f"Codec changed to: {codec}")

        config = self.CODEC_CONFIG.get(codec, {}) # 코덱 설정 스키마를 가져옴

        # 선택된 코덱에 맞는 프리셋 목록으로 콤보박스 업데이트
        presets = config.get("preset_values", [])
        self.preset_start_combo["values"] = presets
        self.preset_end_combo["values"] = presets

        # 현재 선택된 프리셋이 새 목록에 없으면, 목록의 첫 번째와 마지막 값으로 재설정
        if presets:
            if self.preset_start_var.get() not in presets:
                self.preset_start_var.set(presets[0])
            if self.preset_end_var.get() not in presets:
                self.preset_end_var.set(presets[-1])

        # 선택된 코덱의 고급 설정을 위한 tkinter 변수들을 동적으로 (재)생성
        self.adv_settings_vars.clear() # 이전 코덱의 변수들을 모두 제거
        adv_options = config.get("adv_options", {})
        for key, option_data in adv_options.items():
            default_value = option_data.get("default", "")
            if option_data.get("widget") == "checkbutton":
                self.adv_settings_vars[key] = tk.BooleanVar(value=bool(default_value))
            else:
                self.adv_settings_vars[key] = tk.StringVar(value=str(default_value))

        # 품질 제어 파라미터(CRF, CQ 등)의 라벨과 범위를 코덱에 맞게 업데이트
        rate_control_param = config.get("rate_control", "-crf").replace('-', '').upper()
        min_q, max_q = config.get("quality_range", (0, 51))
        
        self.quality_range_label.config(text=f"{rate_control_param} Range ({min_q}-{max_q}):")
        self.crf_start_spinbox.config(from_=min_q, to=max_q)
        self.crf_end_spinbox.config(from_=min_q, to=max_q)

    def _toggle_optimization_mode_ui(self):
        """
        최적화 모드(Range Test vs Target VMAF)에 따라 UI를 전환하는 함수.

        사용자가 최적화 모드를 변경했을 때 호출되며, 선택된 모드에 따라 관련 UI 프레임들을 표시하거나 숨김.
        Range Test 모드일 때는 품질 범위 설정을, Target VMAF 모드일 때는 목표 VMAF 설정을 표시함.
        """
        mode = self.optimization_mode_var.get() # 현재 선택된 최적화 모드 값을 가져옴
        
        # 최적화 모드 변경 로깅
        logging.info(f"Optimization mode changed to: {mode}")
        
        # 선택된 모드에 따라 적절한 UI 프레임을 보여주거나 숨김
        if mode == "Range Test":
            self.quality_range_frame.grid() # 품질 범위 설정 프레임을 화면에 표시
            self.target_vmaf_frame.grid_remove() # 목표 VMAF 설정 프레임을 화면에서 제거
        else: # "Target VMAF" 모드인 경우
            self.quality_range_frame.grid_remove() # 품질 범위 설정 프레임을 화면에서 제거
            self.target_vmaf_frame.grid() # 목표 VMAF 설정 프레임을 화면에 표시

        # 모드 전환 시 병렬 작업 스핀박스는 항상 활성화 상태로 유지
        self.parallel_jobs_spinbox.config(state=tk.NORMAL)

    def toggle_sample_mode_ui(self):
        """
        샘플 선택 모드(자동/수동)에 따라 관련 UI 위젯의 활성화 상태를 전환.

        사용자가 샘플링 모드를 변경했을 때 호출되며, 선택된 모드에 따라 관련 UI 위젯들의 활성화/비활성화 상태를 적절히 조정함.
        자동 모드일 때는 분석 옵션들을, 수동 모드일 때는 시간 입력 옵션들을 활성화함.
        """
        mode = self.sample_mode_var.get() # 현재 선택된 샘플 모드 값을 가져옴
        is_manual = (mode == "Manual")
        is_auto = (mode == "Auto")

        # Analysis Method 콤보박스 상태 제어 코드 추가
        self.analysis_method_combo.config(state="readonly" if is_auto else tk.DISABLED)
        
        # 'Auto' 모드 관련 위젯들의 활성화 상태를 설정
        self.auto_mode_type_combo.config(state="readonly" if is_auto else tk.DISABLED)
        self.sample_duration_spinbox.config(state=tk.NORMAL if is_auto else tk.DISABLED)
        
        # 'Manual' 모드 관련 위젯들의 활성화 상태를 설정
        self.manual_time_entry.config(state='readonly') # 이 위젯은 항상 읽기 전용
        self.manual_time_button.config(state=tk.NORMAL if is_manual else tk.DISABLED)

    def open_manual_time_selector(self):
        """
        수동 시간 선택 창을 열기.

        사용자가 수동 시간 선택을 원할 때 호출되며, ManualTimeSelectorWindow를 생성하여 사용자가 직접 샘플 구간의 시작과 끝 시간을 설정할 수 있도록 함.
        파일 유효성 검사를 통해 안전한 사용을 보장함.
        """
        filepath = self.filepath_var.get()
        if not filepath or not os.path.exists(filepath): # 비디오 파일이 선택되었는지 먼저 확인
            messagebox.showwarning("File Not Found", "Please select a valid video file first.", parent=self.root)
            return

        duration = self.get_video_duration(filepath) # 비디오의 전체 길이를 가져옴
        if duration is None: # 길이를 가져오지 못하면 오류 메시지 표시
            messagebox.showerror("Error", "Could not determine the duration of the selected video.", parent=self.root)
            return
            
        # 수동 시간 선택 창(Toplevel)을 생성하여 사용자에게 보여줌
        ManualTimeSelectorWindow(
            self.root,
            self.set_manual_time,
            duration,
            self.manual_start_time_s.get(),
            self.manual_end_time_s.get()
        )

    def set_manual_time(self, start_s, end_s):
        """
        수동 시간 선택 창에서 전달받은 시간 값으로 상태를 업데이트.

        ManualTimeSelectorWindow에서 사용자가 설정한 시작 시간과 종료 시간을 받아서
        애플리케이션의 상태 변수에 저장하고, UI에 포맷된 시간 문자열을 표시함.

        Args:
            start_s: 시작 시간 (초)
            end_s: 종료 시간 (초)
        """
        # 전달받은 시작/종료 시간(초)을 tkinter 변수에 저장
        self.manual_start_time_s.set(start_s)
        self.manual_end_time_s.set(end_s)

        def format_time(seconds): # 시간을 HH:MM:SS.ms 형식으로 포맷하는 내부 헬퍼 함수
            h = int(seconds // 3600)
            m = int((seconds % 3600) // 60)
            s = int(seconds % 60)
            ms = int((seconds - int(seconds)) * 1000)
            return f"{h:02}:{m:02}:{s:02}.{ms:03}"

        # 포맷된 시간 문자열과 계산된 지속 시간을 UI에 표시
        start_str = format_time(start_s)
        end_str = format_time(end_s)
        duration = end_s - start_s
        self.manual_time_display_var.set(f"{start_str} to {end_str} (Duration: {duration:.3f}s)")

    def preview_sample(self):
        """
        'Sample Preview' 버튼 클릭 시 실행되는 진입점 메서드.

        사용자가 샘플 미리보기를 요청할 때 호출되며, 선택된 샘플 모드에 따라 다르게 동작함.
        Auto 모드의 경우 장면 분석을 백그라운드에서 실행하고, Manual 모드의 경우 즉시 미리보기를 시작함.
        """
        # 현재 선택된 파일 경로를 가져와 유효성을 검사
        filepath = self.filepath_var.get()
        if not filepath or not os.path.exists(filepath):
            messagebox.showwarning("No Video", "Please select a video file first.", parent=self.root)
            return

        # ffplay 실행 파일이 존재하는지 확인
        if not os.path.exists(self.ffplay_path):
            messagebox.showerror("FFplay Not Found", f"ffplay.exe was not found at:\n{self.ffplay_path}", parent=self.root)
            return

        # 'Auto' 모드는 분석에 시간이 걸리므로, UI 멈춤을 방지하기 위해 비동기적으로 처리
        if self.sample_mode_var.get() == "Auto":
            self.is_previewing = True  # Preview 작업 시작 플래그 설정
            self.sample_preview_button.config(state=tk.DISABLED) # 미리보기 버튼 비활성화
            self.start_button.config(state=tk.DISABLED)  # 최적화 시작 버튼도 비활성화
            self.cancel_button.config(state=tk.NORMAL)  # 취소 버튼 활성화
            self.status_label_var.set("Analyzing for preview...") # 상태 메시지 업데이트
            logging.info("Preview analysis started")
            threading.Thread(target=self._run_preview_analysis, daemon=True).start() # 분석 작업을 별도 스레드에서 시작
        
        # 'Manual' 모드는 시간 값이 이미 정해져 있으므로 즉시 실행
        else:
            try:
                ss, sd = self._get_sample_timestamps() # 설정된 수동 시간 값을 가져옴
                if ss is None or sd <= 0: # 시간 값이 유효하지 않으면 오류 메시지 표시
                    messagebox.showerror("Error", "Invalid manual time range selected.", parent=self.root)
                    return
                self._launch_ffplay(ss, sd) # ffplay로 미리보기 실행
            except Exception as e:
                messagebox.showerror("Preview Error", f"An error occurred: {e}", parent=self.root)
                # 오류 발생 시, 다른 작업이 진행 중이 아니라면 'Start' 버튼을 다시 활성화
                if not self.is_busy:
                    self.start_button.config(state=tk.NORMAL)

    def open_advanced_settings(self):
        """
        현재 선택된 코덱에 맞는 고급 설정 창을 열기.

        사용자가 코덱을 선택한 후 고급 설정을 변경하려고 할 때 호출되며, 선택된 코덱에 맞는 설정 옵션들을 포함한 AdvancedSettingsWindow를 생성함.
        코덱이 선택되지 않은 경우 경고 메시지를 표시함.
        """
        codec_name = self.codec_var.get() # 현재 선택된 코덱의 이름을 가져옴
        if not codec_name: # 코덱이 선택되지 않았으면 경고 메시지를 표시하고 함수를 종료
            messagebox.showwarning("Codec Not Selected", "Please select a codec first.", parent=self.root)
            return

        # 해당 코덱의 설정 스키마를 가져옴
        codec_config = self.CODEC_CONFIG.get(codec_name, {})

        # 고급 설정 창을 생성하여 사용자에게 표시
        AdvancedSettingsWindow(self.root, self.adv_settings_vars, codec_config, codec_name)

    def open_vmaf_model_selector(self):
        """
        VMAF 모델 선택 창을 열기.

        사용자가 VMAF 모델을 선택하려고 할 때 호출되며, VMAF 모델 디렉토리의 존재 여부를 확인한 후 VMAFModelSelectorWindow를 생성함.
        모델이 없는 경우 사용자에게 다운로드를 안내함.
        """
        # VMAF 모델 디렉토리가 존재하지 않거나 비어있는지 확인
        if not os.path.exists(self.vmaf_model_dir) or not os.listdir(self.vmaf_model_dir):
            messagebox.showinfo("No Models Found", "VMAF models directory is empty.\n\nPlease use the 'Download/Update Models' button first.", parent=self.root)
            return
        
        # 모델 선택 창(Toplevel)을 생성하여 사용자에게 보여줌
        VMAFModelSelectorWindow(self.root, self.vmaf_model_dir, self.set_vmaf_model_path)

    def set_vmaf_model_path(self, path):
        """
        VMAF 모델 선택 창에서 선택된 모델 경로를 UI에 반영.

        사용자가 VMAF 모델을 선택한 후 해당 모델의 경로를 애플리케이션에 설정하고, UI를 업데이트함.
        경로가 None인 경우 기본값으로 설정하여 사용자가 모델을 선택하지 않은 상태를 명확히 표시함.

        Args:
            path: 선택된 VMAF 모델의 파일 경로 또는 None (기본값 설정 시)
        """
        if path: # 사용자가 특정 모델 파일을 선택한 경우
            relative_path = os.path.relpath(path, self.vmaf_model_dir) # 전체 경로를 상대 경로로 변환하여 UI에 표시
            self.vmaf_model_path_var.set(relative_path)
        else: # 사용자가 'Reset to Default'를 선택한 경우 (path가 None)
            self.vmaf_model_path_var.set("[Default] vmaf_v0.6.1.json (FFmpeg built-in)")

    def _on_tree_select(self, event):
        """
        결과 테이블에서 항목이 선택될 때마다 관련 버튼의 활성화 상태를 업데이트.

        사용자가 결과 테이블에서 항목을 선택할 때마다 호출되며, 선택된 항목의 수에 따라
        관련 기능 버튼들의 활성화/비활성화 상태를 적절히 조정함.
        작업 중일 때는 버튼 상태 변경을 방지하여 안전성을 보장함.

        Args:
            event: 트리뷰 선택 이벤트 객체
        """
        if self.is_busy: # 다른 작업이 진행 중일 때는 UI 상태를 변경하지 않음
            return

        selection = self.tree.selection() # 현재 선택된 항목들의 ID 리스트
        num_selected = len(selection) # 선택된 항목의 개수

        # 선택된 항목의 개수에 따라 버튼의 활성화/비활성화 상태를 결정
        self.log_button.config(state=tk.NORMAL if num_selected == 1 else tk.DISABLED)
        self.gen_cmd_button.config(state=tk.NORMAL if num_selected == 1 else tk.DISABLED)
        
        # A/B 비교 작업이 실행 중이 아닐 때만 A/B 비교 버튼의 상태를 업데이트
        if not self.is_ab_comparing:
            self.ab_compare_button.config(state=tk.NORMAL if num_selected == 2 else tk.DISABLED)

    def show_selected_log(self):
        """
        결과 테이블에서 선택된 항목의 상세 FFmpeg 로그를 보여줌.

        사용자가 결과 테이블에서 항목을 선택했을 때 해당 항목의 FFmpeg 실행 로그를 LogViewerWindow를 통해 표시함.
        로그 데이터가 없는 경우 사용자에게 정보 메시지를 표시함.
        """
        selected_items = self.tree.selection() # 결과 테이블에서 선택된 항목들의 ID를 가져옴
        if not selected_items: # 선택된 항목이 없으면 함수를 종료
            return
        
        # 첫 번째 선택 항목의 ID를 사용하여 결과 데이터를 가져옴
        result_data = self.tree_item_to_result.get(selected_items[0])
        
        # 로그 데이터의 존재 여부에 따라 로그 뷰어를 열거나 안내 메시지를 표시
        if result_data and "log" in result_data:
            LogViewerWindow(self.root, result_data["log"]) # 로그 뷰어 창을 생성
        else:
            messagebox.showinfo("Info", "No log data available for this entry.") # 로그가 없음을 알림

    def generate_final_command(self):
        """
        선택된 결과 항목을 기반으로 전체 비디오에 적용할 FFmpeg 명령어를 생성하여 보여줌.

        사용자가 결과 테이블에서 선택한 최적화 결과를 기반으로 전체 비디오에 적용할 수 있는 FFmpeg 명령어를 생성함.
        2패스 인코딩의 경우 1패스와 2패스 명령어를 모두 생성하여 사용자가 쉽게 복사하여 사용할 수 있도록 함.
        """
        selected_items = self.tree.selection() # 결과 테이블에서 선택된 항목을 가져옴
        if not selected_items:
            messagebox.showwarning("Warning", "Please select a result from the table first.", parent=self.root)
            return

        # 선택된 첫 번째 항목의 결과 데이터를 가져옴
        result_data = self.tree_item_to_result[selected_items[0]]

        # 명령어 생성을 위해 선택된 결과 데이터로 임시 EncodingTask 객체를 생성
        temp_task = EncodingTask(
            ffmpeg_path=self.ffmpeg_path,
            sample_path="", temp_dir="",
            codec=self.codec_var.get(),
            preset=result_data['preset'],
            crf=result_data['crf'],
            audio_option=self.audio_var.get(),
            adv_opts=result_data['adv_opts_snapshot']
        )

        # FFmpeg 명령어 빌더를 사용하여 최종 명령어를 생성
        builder = FFmpegCommandBuilder(temp_task, full_video_path=self.filepath_var.get())

        # 2패스 인코딩 여부에 따라 명령어를 다르게 구성
        if temp_task.adv_opts.get('is_2pass'):
            cmd1 = builder.build_encode_command(pass_num=1)
            cmd2 = builder.build_encode_command(pass_num=2)
            full_command = f"# Pass 1\n{' '.join(shlex.quote(c) for c in cmd1)}\n\n# Pass 2\n{' '.join(shlex.quote(c) for c in cmd2)}"
        else: # 단일 패스인 경우
            cmd = builder.build_encode_command(pass_num=0)
            full_command = ' '.join(shlex.quote(c) for c in cmd)
            
        # 생성된 명령어를 보여주는 팝업 창을 띄움
        CommandGeneratorWindow(self.root, full_command)

    def create_ab_samples(self):
        """
        결과 테이블에서 선택된 두 항목을 A/B 비교할 수 있도록 샘플 비디오를 생성.

        사용자가 결과 테이블에서 두 개의 최적화 결과를 선택했을 때 A/B 비교를 위한 샘플 비디오를 생성함.
        선택된 항목이 2개가 아닌 경우 아무 작업도 수행하지 않으며, 작업 시작 시 관련 버튼들을 비활성화하여 중복 실행을 방지함.
        """
        selected_items = self.tree.selection()
        if len(selected_items) != 2: # 정확히 2개의 항목이 선택되었는지 확인
            return

        # A/B 비교 작업이 진행 중임을 나타내는 상태 플래그를 설정하고 관련 UI를 비활성화
        self.is_ab_comparing = True
        self.start_button.config(state=tk.DISABLED)
        self.ab_compare_button.config(state=tk.DISABLED)

        # 선택된 두 항목의 결과 데이터를 가져옴
        res_a = self.tree_item_to_result[selected_items[0]]
        res_b = self.tree_item_to_result[selected_items[1]]

        # 프로그래스바의 최대값과 현재 값을 명확하게 초기화
        self.progress_bar.config(mode='determinate', maximum=5, value=0)

        # UI 멈춤을 방지하기 위해 A/B 샘플 생성 작업을 별도의 스레드에서 실행
        threading.Thread(target=self._run_ab_encoding, args=(res_a, res_b), daemon=True).start()

        # 사용자에게 작업이 시작되었음을 알림
        messagebox.showinfo(
            "A/B Comparison Creation",
            "Two sample videos and their difference videos will now be generated.\n\n"
            "This may take a moment. You will be notified upon completion.",
            parent=self.root,
        )

    def show_graph(self):
        """
        결과 그래프 창을 열기.

        최적화 결과 데이터를 시각화하는 그래프 창을 생성함.
        결과 데이터가 없는 경우 사용자에게 정보 메시지를 표시하고 창을 열지 않음.
        """
        if not self.all_results: # 그래프를 그릴 데이터가 없으면 사용자에게 알리고 종료
            messagebox.showinfo("Info", "No data available to plot.", parent=self.root)
            return
        
        # 결과 데이터와 함께 GraphWindow를 생성하여 화면에 표시
        GraphWindow(self.root, self.all_results, APP_CONFIG["metric_formats"])

    def export_results(self):
        """
        파일 저장 대화상자를 열어 사용자에게 내보낼 형식을 선택하게 하고 해당 함수를 호출.

        사용자가 최적화 결과를 외부 파일로 내보낼 수 있도록 파일 저장 대화상자를 열고,
        선택된 형식에 따라 적절한 내보내기 함수를 호출함.
        HTML과 CSV 형식을 지원하며, 파일 확장자에 따라 자동으로 형식을 결정함.
        """
        if not self.all_results: # 내보낼 데이터가 없으면 사용자에게 알리고 종료
            messagebox.showinfo("Info", "There is no data to export.")
            return

        # 파일 저장 대화상자에 표시할 파일 형식 필터
        file_types = [
            ("HTML Report", "*.html"),
            ("CSV Data File", "*.csv"),
        ]

        # 사용자에게 파일 저장 경로와 형식을 입력받음
        filepath = filedialog.asksaveasfilename(
            title="Export Results",
            filetypes=file_types,
            defaultextension=".html"
        )

        if not filepath: # 사용자가 대화상자를 취소한 경우 함수 종료
            return

        # 파일 확장자에 따라 적절한 내보내기 함수를 호출
        try:
            # 내보내기 시작 로깅
            file_format = "CSV" if filepath.lower().endswith(".csv") else "HTML"
            logging.info(LOG_MESSAGES['export_started'].format(file_format, filepath))
            
            if filepath.lower().endswith(".csv"):
                self.export_to_csv(filepath)
            elif filepath.lower().endswith(".html"):
                self.export_to_html(filepath)
            else:
                messagebox.showwarning("Unknown Format", "Could not determine file format from the filename. Please use a .csv or .html extension.")
                return
            
            # 내보내기 완료 로깅
            try:
                file_size_mb = os.path.getsize(filepath) / (1024 * 1024)
                logging.info(LOG_MESSAGES['export_completed'].format(filepath, file_size_mb))
            except Exception as e:
                logging.warning(f"Failed to get export file size: {e}")
                logging.info(f"Export completed: {filepath}")
                
        except Exception as e:
            logging.error(f"Export failed: {e}")
            messagebox.showerror("Export Error", f"Failed to export results.\nError: {e}")



    # ==============================================================================
    # 6C. 핵심 최적화 로직 (Core Optimization Logic)
    # ==============================================================================

    def start_optimization(self):
        """
        'Start Optimization' 버튼 클릭 시 실행되는 메인 진입점.

        사용자가 최적화 작업을 시작하려고 할 때 호출되며, 설정 유효성 검사, NVENC 제한 경고, UI 상태 초기화 등을 수행한 후 별도 스레드에서 최적화 작업을 시작함.
        """
        # --- 1. 사전 조건 검사 ---
        # 다른 작업(미리보기, 이전 최적화)이 실행 중인지 확인
        if self.is_previewing:
            messagebox.showwarning("Preview in Progress", "Please wait for the sample preview analysis to complete or cancel it first.", parent=self.root)
            return
        if self.is_busy:
            messagebox.showwarning("Operation in Progress", "Please wait for the current operation to complete or cancel it first.", parent=self.root)
            return

        # 사용자가 입력한 모든 설정 값이 유효한지 검사
        if not self.validate_settings():
            return

        # NVENC 코덱 사용 시 병렬 작업 수 제한에 대한 경고 표시
        if self._should_warn_nvenc_parallel_limit():
            title = "NVIDIA Encoder Limit Warning"
            message = (
                f"You have selected an NVIDIA (NVENC) encoder with more than {APP_CONFIG['max_parallel_jobs']} parallel jobs.\n\n"
                f"Most consumer NVIDIA GPUs are limited to {APP_CONFIG['max_parallel_jobs']} concurrent encoding sessions.\n\n"
                "Exceeding this limit may cause errors or failed encodes.\n\n"
                f"• Yes: Limit jobs to {APP_CONFIG['max_parallel_jobs']} and continue.\n"
                "• No: Continue with the current setting (at your own risk).\n"
                "• Cancel: Stop the optimization process."
            )
            
            response = messagebox.askyesnocancel(title, message, parent=self.root)

            if response is None: # 사용자가 '취소'를 누르거나 창을 닫은 경우
                return # 최적화 시작을 중단
            elif response: # 사용자가 '예'를 누른 경우
                self.parallel_jobs_var.set(APP_CONFIG['max_parallel_jobs']) # 병렬 작업 수를 제한값으로 설정
            # '아니요'를 누른 경우, 아무 작업 없이 그대로 진행

        # --- 2. 작업 시작을 위한 상태 초기화 ---
        # 이전 결과 및 상태 초기화
        self.progress_bar["value"] = 0
        self.all_results.clear()
        self.apply_view_filter()
        self.is_busy = True # 전체 작업 중 플래그 설정
        self.is_cancelling = False # 취소 플래그 초기화
        self.run_start_time = time.time() # ETA 계산을 위한 시작 시간 기록
        self.completed_tasks = 0 # 완료된 작업 카운터 초기화
        
        # 최적화 시작 로깅
        try:
            codec = self.codec_var.get()
            mode = self.optimization_mode_var.get()
            quality = f"{self.crf_start_var.get()}-{self.crf_end_var.get()}"
            jobs = self.parallel_jobs_var.get()
            duration = self.sample_duration_var.get()
            
            logging.info(LOG_MESSAGES['optimization_started'].format(
                mode, jobs, duration
            ))
        except Exception as e:
            logging.warning(f"Failed to log optimization start details: {e}")
        
        # UI 컨트롤 상태 변경
        self.start_button.config(state=tk.DISABLED)
        self.cancel_button.config(state=tk.NORMAL)
        self._toggle_controls_state(tk.DISABLED) # 모든 설정 컨트롤 비활성화
        self.log_button.config(state=tk.DISABLED)
        self.gen_cmd_button.config(state=tk.DISABLED)
        self.ab_compare_button.config(state=tk.DISABLED)

        # --- 3. 최적화 작업 실행 ---
        # UI 멈춤을 방지하기 위해 최적화 작업을 별도의 스레드에서 실행
        self.optimization_thread = threading.Thread(
            target=self._run_optimization_task,
            args=(self.filepath_var.get(),),
            daemon=True
        )
        self.optimization_thread.start()

    def cancel_optimization(self):
        """
        'Cancel' 버튼 클릭 시 실행되는 작업 중단 메서드.

        현재 진행 중인 모든 종류의 백그라운드 작업(최적화, 미리보기, A/B 비교 등)을
        안전하게 중단시킴. FFmpeg 자식 프로세스들을 종료하고 멀티프로세싱 풀을 정리하여 리소스 누수를 방지함.
        """
        # 취소 버튼의 중복 클릭을 방지하기 위해 즉시 비활성화
        self.cancel_button.config(state=tk.DISABLED)
        # 모든 백그라운드 스레드가 참조할 취소 플래그를 설정
        self.is_cancelling = True
        
        # 'Sample Preview' 분석 중에 취소한 경우
        if self.is_previewing:
            self.status_label_var.set("Cancelling preview analysis...")
            # 미리보기 분석은 FFmpeg 프로세스를 직접 종료하는 것만으로 충분함
            self._terminate_child_ffmpeg_processes()
            return

        # A/B 비교 생성 중에 취소한 경우
        if self.is_ab_comparing and self.ab_compare_thread and self.ab_compare_thread.is_alive():
            self.status_label_var.set("Cancelling A/B comparison...")
            # A/B 비교 작업에서 실행되는 FFmpeg 프로세스들을 종료
            self._terminate_child_ffmpeg_processes()
            return

        # 메인 최적화 작업 중에 취소한 경우
        if self.is_busy and self.optimization_thread and self.optimization_thread.is_alive():
            self.status_label_var.set("Cancelling optimization...")

            # 파일 잠금을 해제하고 리소스를 즉시 정리하기 위해 자식 프로세스들을 먼저 종료
            self._terminate_child_ffmpeg_processes()
            if self.pool:
                try:
                    self.pool.terminate() # 멀티프로세싱 워커 풀을 강제 종료
                    self.pool.join()      # 풀이 완전히 정리될 때까지 대기
                except Exception as e:
                    logging.warning(f"Error terminating multiprocessing pool: {e}")

    def _run_optimization_task(self, filepath):
        """
        최적화 작업 전체를 관리하는 내부 메서드.

        별도 스레드에서 실행되며, 전체 최적화 워크플로우를 관리함.
        임시 디렉토리 생성, 작업 큐 구성, 멀티프로세싱 풀 생성, 결과 수집 및 UI 업데이트 등을 순차적으로 수행함.

        Args:
            filepath: 최적화할 비디오 파일의 경로
        """
        # 작업 시작 전, 취소 요청이 있었는지 확인
        if self.is_cancelling:
            self.root.after(0, self.status_label_var.set, "Operation cancelled by user.")
            return

        # UI 초기화 (결과 테이블 비우기)
        self.root.after(0, self.all_results.clear)
        self.root.after(0, self.apply_view_filter)
        self.root.after(0, lambda: self.status_label_var.set(f"Initializing for: {os.path.basename(filepath)}"))

        # 인코딩 및 분석을 위한 임시 디렉토리 생성
        base_dir = os.path.dirname(os.path.abspath(__file__))
        resource_dir = os.path.join(base_dir, APP_CONFIG["data_folder_name"])
        sanitized = sanitize_for_path(os.path.basename(filepath))
        temp_dir = os.path.join(resource_dir, f"temp_{sanitized}_{os.getpid()}")
        if os.path.exists(temp_dir): 
            shutil.rmtree(temp_dir)
            logging.info(LOG_MESSAGES['temp_dir_cleaned'].format(temp_dir))
        os.makedirs(temp_dir)
        logging.info(LOG_MESSAGES['temp_dir_created'].format(temp_dir))

        try:
            # 진행률 표시줄을 2단계(샘플 분석, 샘플 추출)로 설정
            self.root.after(0, lambda: self.progress_bar.config(mode='determinate', maximum=2, value=0))

            # 1단계: 샘플 구간 분석
            self.root.after(0, lambda: self.status_label_var.set("Step 1/2: Determining sample timestamps..."))
            ss, sd = self._get_sample_timestamps()

            if self.is_cancelling: # 분석 중 취소된 경우
                return # finally 블록으로 이동하여 정리 작업 수행

            if ss is None or sd <= 0: # 유효한 샘플 구간을 찾지 못한 경우
                self.root.after(0, lambda: messagebox.showerror("Error", "Could not determine a valid sample time range. Check settings and logs."))
                return

            self.root.after(0, self.progress_bar.step) # 진행률 1/2

            # 2단계: 샘플 영상 추출
            self.root.after(0, lambda: self.status_label_var.set("Step 2/2: Extracting reference sample..."))
            sample_path_abs = self._execute_sample_extraction(filepath, temp_dir, ss, sd)
            
            if not sample_path_abs: # 샘플 추출에 실패한 경우
                self.root.after(0, lambda: messagebox.showerror("Error", "Could not extract a video sample. Check logs."))
                return

            self.root.after(0, self.progress_bar.step) # 진행률 2/2
            
            # --- 3단계: 실제 인코딩 및 분석 작업 ---
            # 원본 영상의 색상 정보를 미리 가져와 인코딩 시 사용
            color_info = self.get_color_info(filepath)
            
            # 현재 실행의 모든 설정값을 저장 (HTML 리포트 생성 시 사용)
            self.last_run_context = {
                'source_path': filepath, 'ss': ss, 'sd': sd,
                'encoder_group': self.encoder_group_var.get(),
                'codec': self.codec_var.get(),
                'preset_start': self.preset_start_var.get(), 'preset_end': self.preset_end_var.get(),
                'optimization_mode': self.optimization_mode_var.get(),
                'target_vmaf': self.target_vmaf_var.get() if self.optimization_mode_var.get() == "Target VMAF" else None,
                'quality_start': self.crf_start_var.get(), 'quality_end': self.crf_end_var.get(),
                'sample_mode': self.sample_mode_var.get(), 'auto_mode_type': self.auto_mode_type_var.get(),
                'analysis_method': self.analysis_method_var.get(),
                'vmaf_model': self.vmaf_model_path_var.get(),
                'audio_option': self.audio_var.get(),
                'parallel_jobs': self.parallel_jobs_var.get(),
                'adv_opts': {k: v.get() for k, v in self.adv_settings_vars.items()},
                'metrics': {'psnr': self.calc_psnr_var.get(), 'ssim': self.calc_ssim_var.get(), 'blockdetect': self.calc_blockdetect_var.get()}
            }

            # 선택된 최적화 모드에 따라 해당 함수를 실행
            mode = self.optimization_mode_var.get()
            if mode == "Range Test":
                self.run_range_test_optimization(sample_path_abs, temp_dir, color_info)
            else:  # Target VMAF
                self.run_target_vmaf_optimization(sample_path_abs, temp_dir, color_info)

        except Exception as e:
            # 작업 중 예외 발생 시 로깅 및 사용자에게 오류 알림
            logging.error(f"Optimization task failed for {filepath}: {e}", exc_info=True)
            self.root.after(0, lambda: self.status_label_var.set(f"Error: {str(e)[:50]}..."))
            self.root.after(0, lambda err=e: messagebox.showerror("Error", f"An error occurred while processing {filepath}:\n{err}"))
        
        finally:
            # --- 4단계: 마무리 및 정리 ---
            self.pool = None # 멀티프로세싱 풀 참조 해제
            if os.path.exists(temp_dir):
                self.root.after(0, lambda: self.status_label_var.set("Cleaning up temporary files..."))
                self._cleanup_temp_dir(temp_dir)
            
            # UI 상태를 최종적으로 정리하는 메서드 호출
            self.root.after(0, self.finalize_run)

    def run_range_test_optimization(self, sample_path_abs, temp_dir, color_info: Dict[str, str]):
        """
        'Range Test' 모드에 대한 최적화 프로세스를 실행.
        (사용자가 지정한 프리셋과 CRF 범위 내의 모든 조합을 테스트)
        """
        # 사용자 설정값들을 기반으로 테스트할 모든 인코딩 작업 목록을 생성
        presets_list = self.preset_start_combo['values']
        ps, pe = presets_list.index(self.preset_start_var.get()), presets_list.index(self.preset_end_var.get())
        presets = presets_list[ps:pe + 1]
        cs, ce = int(self.crf_start_var.get()), int(self.crf_end_var.get())
        adv_opts = {k: v.get() for k, v in self.adv_settings_vars.items()}
        vmaf_model_path = self.get_selected_vmaf_model_path()

        tasks = [
            EncodingTask(
                ffmpeg_path=self.ffmpeg_path, sample_path=sample_path_abs, temp_dir=temp_dir,
                codec=self.codec_var.get(), preset=p, crf=c, audio_option=self.audio_var.get(),
                adv_opts=adv_opts,
                metrics={'psnr': self.calc_psnr_var.get(), 'ssim': self.calc_ssim_var.get(), 'blockdetect': self.calc_blockdetect_var.get()},
                vmaf_model_path=vmaf_model_path,
                color_info=color_info
            ) for p in presets for c in range(cs, ce + 1)
        ]

        # UI 업데이트: 진행률 표시줄의 최대값을 전체 작업 수로 설정하고 상태 메시지 업데이트
        self.root.after(0, lambda: self.progress_bar.config(mode='determinate', maximum=len(tasks), value=0))
        self.root.after(0, lambda: self.status_label_var.set(f"Starting {len(tasks)} encoding tasks..."))
        
        # 멀티프로세싱 풀을 생성하여 작업들을 병렬로 실행
        self.pool = multiprocessing.Pool(processes=self.parallel_jobs_var.get())
        for task in tasks:
            if self.is_cancelling: # 취소 요청이 있으면 더 이상 작업을 추가하지 않음
                break
            # 각 작업을 비동기적으로 풀에 추가. 완료되면 process_worker_result 콜백 함수가 호출됨
            self.pool.apply_async(perform_one_test, args=(task,), callback=self.process_worker_result)
        
        self.pool.close() # 모든 작업이 추가되었으므로 풀을 닫음
        self.pool.join() # 모든 작업이 완료될 때까지 대기

    def run_target_vmaf_optimization(self, sample_path_abs, temp_dir, color_info: Dict[str, str]):
        """
        'Target VMAF' 모드에 대한 최적화 프로세스를 실행.
        각 프리셋에 대한 탐색 작업을 병렬로 처리하여 성능을 극대화.
        """
        # 테스트할 프리셋 목록을 생성
        presets_list = self.preset_start_combo['values']
        ps, pe = presets_list.index(self.preset_start_var.get()), presets_list.index(self.preset_end_var.get())
        presets_to_test = presets_list[ps:pe + 1]
        
        # 현재 코덱의 설정 정보를 가져옴
        codec_config = self.CODEC_CONFIG.get(self.codec_var.get(), {})

        # 모든 병렬 작업에 공통적으로 전달될 기본 인자 딕셔너리를 생성
        base_task_args = {
            'ffmpeg_path': self.ffmpeg_path, 'sample_path': sample_path_abs, 'temp_dir': temp_dir,
            'codec': self.codec_var.get(), 'audio_option': self.audio_var.get(),
            'adv_opts': {k: v.get() for k, v in self.adv_settings_vars.items()},
            'metrics': {'psnr': self.calc_psnr_var.get(), 'ssim': self.calc_ssim_var.get(), 'blockdetect': self.calc_blockdetect_var.get()},
            'vmaf_model_path': self.get_selected_vmaf_model_path(),
            'color_info': color_info,
            'target_vmaf': self.target_vmaf_var.get()
        }

        # UI 업데이트: 진행률 표시줄의 최대값을 프리셋 수로 설정하고 상태 메시지 업데이트
        total_presets = len(presets_to_test)
        self.root.after(0, lambda: self.progress_bar.config(mode='determinate', maximum=total_presets, value=0))
        self.root.after(0, lambda: self.status_label_var.set(f"Starting search for {total_presets} presets..."))

        # 멀티프로세싱 풀을 사용하여 각 프리셋에 대한 탐색을 병렬로 실행
        self.pool = multiprocessing.Pool(processes=self.parallel_jobs_var.get())
        
        for preset in presets_to_test:
            if self.is_cancelling: # 취소 요청이 있으면 더 이상 작업을 추가하지 않음
                break
            
            # 클로저를 사용하여 콜백 함수에 현재 프리셋 이름과 전체 프리셋 수를 전달
            callback = lambda result, p=preset: self.process_target_vmaf_result(result, p, total_presets)
            
            # 각 프리셋에 대한 CRF 탐색 작업을 비동기적으로 풀에 추가
            self.pool.apply_async(find_best_crf_for_preset, args=(preset, codec_config, base_task_args), callback=callback)

        self.pool.close() # 모든 작업이 추가되었으므로 풀을 닫음
        self.pool.join() # 모든 작업이 완료될 때까지 대기

    def finalize_run(self):
        """최적화 작업이 (성공, 실패, 취소에 관계없이) 완료된 후 UI를 최종 상태로 정리."""
        # 기본 버튼 상태 복원
        self.start_button.config(state=tk.NORMAL)
        self.cancel_button.config(state=tk.DISABLED)
        
        # 읽기 전용 필드 상태 복원
        self.filepath_entry.config(state="readonly")
        self.vmaf_model_entry.config(state="readonly")
        self.manual_time_entry.config(state="readonly")
        self.view_mode_combo.config(state="readonly")
        
        # 모든 설정 컨트롤의 상태를 원래대로 복원
        self._toggle_controls_state(tk.NORMAL)
        
        # 프로그래스바 초기화
        self.progress_bar.config(mode='determinate', value=0)
        
        # 작업이 취소되지 않고 정상 종료된 경우
        if not self.is_cancelling:
            self.status_label_var.set("All jobs completed.")
            self.highlight_best_result() # 결과 테이블에서 최적 항목을 강조 표시
            
            # 최적화 완료 로깅
            try:
                total_tests = len(self.all_results)
                duration = time.time() - self.run_start_time
                best_result = "N/A"
                
                if self.all_results:
                    # 최고 효율성 결과 찾기
                    best_efficiency = max(self.all_results, key=lambda x: x.get('efficiency', 0))
                    best_result = f"VMAF: {best_efficiency.get('vmaf', 0):.2f}, Efficiency: {best_efficiency.get('efficiency', 0):.2f}"
                
                logging.info(LOG_MESSAGES['optimization_completed'].format(
                    total_tests, duration, best_result
                ))
                
                # 성능 요약 로깅
                if self.all_results:
                    avg_vmaf = sum(r.get('vmaf', 0) for r in self.all_results) / len(self.all_results)
                    best_efficiency = max(r.get('efficiency', 0) for r in self.all_results)
                    logging.info(LOG_MESSAGES['performance_summary'].format(
                        duration / total_tests, avg_vmaf, best_efficiency
                    ))
                    
            except Exception as e:
                logging.warning(f"Failed to log optimization completion details: {e}")
        else: # 작업이 취소된 경우
            self.status_label_var.set("Operation cancelled.")
            
            # 최적화 취소 로깅
            try:
                completed_tests = len(self.all_results)
                logging.info(LOG_MESSAGES['optimization_cancelled'].format(completed_tests))
            except Exception as e:
                logging.warning(f"Failed to log optimization cancellation: {e}")

        # 결과 데이터가 있는 경우, 관련 버튼들을 활성화
        if self.all_results:
            self.graph_button.config(state=tk.NORMAL)
            self.export_results_button.config(state=tk.NORMAL)
        
        # 현재 선택 상태에 맞게 버튼들(A/B 비교 등)의 상태를 최종 갱신
        self._on_tree_select(None)
    
        self.is_busy = False  # 전체 작업 중 플래그 해제



    # ==============================================================================
    # 6D. 결과 처리 및 분석 (Result Processing & Analysis)
    # ==============================================================================

    def process_worker_result(self, result):
        """
        워커 프로세스에서 반환된 결과를 메인 스레드에서 처리하도록 전달.

        멀티프로세싱 워커에서 반환된 결과를 메인 스레드의 GUI 업데이트 큐에 안전하게 전달함.
        Tkinter의 after 메서드를 사용하여 스레드 안전성을 보장함.

        Args:
            result: 워커 프로세스에서 반환된 결과 딕셔너리
        """
        # 워커 프로세스(별도 프로세스)에서 직접 GUI를 업데이트하는 것은 위험하므로,
        # self.root.after를 사용하여 GUI 업데이트 작업을 메인 스레드의 이벤트 큐에 등록
        self.root.after(0, self.update_gui_with_result, result)

    def update_gui_with_result(self, result):
        """
        워커 프로세스로부터 받은 결과로 UI(진행률, 결과 테이블 등)를 업데이트.

        Range Test 모드의 워커 프로세스에서 반환된 결과를 받아서 진행률, 결과 테이블, 상태 메시지 등을 업데이트함.
        ETA 계산과 결과 필터링을 포함하여 사용자에게 실시간 피드백을 제공함.

        Args:
            result: 워커 프로세스에서 반환된 결과 딕셔너리
        """
        if self.is_cancelling or not result: # 작업이 취소되었거나 유효하지 않은 결과인 경우 중단
            return
        
        # 'Range Test' 모드일 때만 ETA 계산 및 진행률 업데이트
        if self.optimization_mode_var.get() == "Range Test":
            self.completed_tasks += 1
            total_tasks = self.progress_bar['maximum']
            eta_str = ""
            if self.completed_tasks > 0 and self.run_start_time:
                elapsed = time.time() - self.run_start_time
                avg_time = elapsed / self.completed_tasks
                eta_seconds = (total_tasks - self.completed_tasks) * avg_time
                if eta_seconds > 0:
                    eta_str = f" (ETA: {str(timedelta(seconds=int(eta_seconds)))})"

            # 상태 메시지와 진행률 표시줄 업데이트
            self.status_label_var.set(f"Encoding and analyzing... ({self.completed_tasks}/{total_tasks}){eta_str}")
            self.progress_bar['value'] = self.completed_tasks

        # 워커의 결과 상태에 따라 처리
        if result.get("status") == "success": # 성공한 경우
            self.all_results.append(result) # 결과 리스트에 추가
            self.apply_view_filter() # 결과 테이블 갱신
        elif result.get("status") == "error": # 실패한 경우
            # result 딕셔셔너리에서 message와 log_content를 먼저 가져옴
            message = result.get("message", "An unknown worker error occurred.")
            log_content = result.get("log", "No log was captured from worker.")
            
            # 워커의 실패 내용을 메인 로그 파일에 상세히 기록
            logging.error("="*80)
            logging.error("--- Worker Process Failed ---")
            logging.error(f"Error Summary: {message}")
            logging.error(f"Full Worker Log:\n{log_content}")
            logging.error("--- End of Worker Failure Report ---")
            logging.error("="*80)
            
            messagebox.showerror("Worker Process Error", message) # 사용자에게 오류 메시지 표시
            LogViewerWindow(self.root, log_content) # 상세 로그 뷰어 창을 띄움

    def process_target_vmaf_result(self, result, preset_name, total_presets):
        """
        Target VMAF 워커로부터 받은 결과를 처리하고 GUI를 업데이트.

        Target VMAF 모드의 워커 프로세스에서 반환된 결과를 메인 스레드의 GUI 업데이트 큐에 전달함.
        진행률과 상태 메시지를 업데이트하여 사용자에게 작업 진행 상황을 실시간으로 표시함.

        Args:
            result: 워커 프로세스에서 반환된 결과
            preset_name: 현재 처리 중인 프리셋 이름
            total_presets: 전체 프리셋 수
        """
        # 스레드 안전성을 위해 GUI 업데이트 로직을 메인 스레드에서 실행하도록 예약
        self.root.after(0, self.update_gui_for_target_vmaf, result, preset_name, total_presets)

    def update_gui_for_target_vmaf(self, result, preset_name, total_presets):
        """
        메인 스레드에서 Target VMAF 결과로 GUI를 업데이트.

        Target VMAF 모드의 결과를 받아서 진행률, 상태 메시지, 결과 목록 등을 업데이트함.
        ETA(예상 완료 시간)를 계산하여 사용자에게 작업 진행 상황을 상세하게 표시함.

        Args:
            result: 워커 프로세스에서 반환된 결과
            preset_name: 현재 처리 중인 프리셋 이름
            total_presets: 전체 프리셋 수
        """
        if self.is_cancelling: # 작업이 취소된 경우 UI 업데이트를 중단
            return

        # 완료된 작업 수를 증가시키고 ETA를 계산
        self.completed_tasks += 1
        eta_str = ""
        if self.completed_tasks > 0 and self.run_start_time:
            elapsed = time.time() - self.run_start_time # 총 경과 시간
            avg_time = elapsed / self.completed_tasks # 작업당 평균 시간
            eta_seconds = (total_presets - self.completed_tasks) * avg_time # 남은 예상 시간
            if eta_seconds > 0:
                eta_str = f" (ETA: {str(timedelta(seconds=int(eta_seconds)))})"

        # 워커의 결과 상태에 따라 상태 메시지를 업데이트하고 결과 테이블을 갱신
        if result and result.get("status") == "success": # 성공적으로 최적 CRF를 찾은 경우
            self.status_label_var.set(f"Finished preset '{preset_name}'. ({self.completed_tasks}/{total_presets}){eta_str}")
            self.all_results.append(result) # 결과 리스트에 추가
            self.apply_view_filter() # 결과 테이블 갱신
        else: # 최적 CRF를 찾지 못했거나 실패한 경우
            self.status_label_var.set(f"No suitable CRF for preset '{preset_name}'. ({self.completed_tasks}/{total_presets}){eta_str}")

        # 진행률 표시줄 업데이트
        self.progress_bar['value'] = self.completed_tasks

    def apply_view_filter(self):
        """
        결과 테이블에 표시될 내용을 현재 선택된 보기 모드와 VMAF 임계값에 따라 필터링하고 갱신.
        또한, 각 항목에 'sweet_spot', 'pareto' 등의 태그를 부여하여 시각적으로 강조.
        """
        # --- 1. UI 초기화 ---
        self.tree.delete(*self.tree.get_children()) # 기존에 표시된 모든 결과 항목을 삭제
        self.tree_item_to_result.clear() # Treeview 아이템 ID와 결과 데이터 매핑을 초기화

        if not self.all_results: # 표시할 결과 데이터가 없으면 함수 종료
            return

        # --- 2. 필터링 및 정렬을 위한 데이터 준비 ---
        display_mode = self.view_mode_display_var.get()
        mode = self.view_mode_map.get(display_mode, "sweet_spot")
        self.vmaf_threshold_spinbox.config(state=tk.NORMAL) # VMAF 임계값 스핀박스 활성화
        self.vmaf_threshold_label.config(state=tk.NORMAL) # VMAF 임계값 라벨 활성화

        # 현재 활성화된 메트릭 정보를 딕셔너리로 구성
        metrics_to_consider = {'psnr': self.calc_psnr_var.get(), 'ssim': self.calc_ssim_var.get(), 'blockdetect': self.calc_blockdetect_var.get()}
        
        # --- 3. 특별한 결과 항목들(파레토, 스위트 스팟 등) 계산 ---
        current_codec = self.codec_var.get()
        codec_config = self.CODEC_CONFIG.get(current_codec, {})
        pareto_ids = self._calculate_pareto_front(self.all_results, metrics_to_consider, codec_config) # 파레토 프론트 계산
        pareto_results = [r for r in self.all_results if (r['preset'], r['crf']) in pareto_ids]
        sweet_spot_id = self._find_sweet_spot(pareto_results) # 스위트 스팟 계산

        # 시각적 강조를 위해 가장 낮은 품질과 효율성을 가진 항목도 찾아둠
        lowest_vmaf_item = min(self.all_results, key=lambda r: r.get('vmaf', float('inf')))
        lowest_vmaf_id = (lowest_vmaf_item['preset'], lowest_vmaf_item['crf'])
        lowest_efficiency_item = min(self.all_results, key=lambda r: r.get('efficiency', float('inf')))
        lowest_efficiency_id = (lowest_efficiency_item['preset'], lowest_efficiency_item['crf'])

        # --- 4. 최종 표시할 데이터 필터링 및 정렬 ---
        try:
            threshold = self.vmaf_threshold_var.get()
        except tk.TclError: # 사용자가 유효하지 않은 값을 입력한 경우
            threshold = 0.0
        filtered_results = [r for r in self.all_results if r.get('vmaf', 0) >= threshold] # VMAF 임계값 필터 적용

        # 선택된 뷰 모드에 따라 최종 데이터를 정렬
        if mode == 'max_quality':
            display_data = sorted(filtered_results, key=lambda r: r.get('vmaf', 0), reverse=True)
        else: # 'efficiency' 모드가 기본값
            display_data = sorted(filtered_results, key=lambda r: r.get('efficiency', 0), reverse=True)
        
        # --- 5. Treeview에 데이터 삽입 ---
        for result in display_data:
            # 각 결과에 해당하는 시각적 태그를 결정
            tags = []
            result_id = (result['preset'], result['crf'])
            if result_id == sweet_spot_id:
                tags.append('sweet_spot')
            elif result_id == lowest_vmaf_id:
                tags.append('worst_quality')
            elif result_id == lowest_efficiency_id:
                tags.append('worst_efficiency')
            elif result_id in pareto_ids:
                tags.append('pareto')

            # 포맷팅된 값들로 Treeview에 한 행을 삽입
            item_id = self.tree.insert("", "end", values=(
                result.get("preset", ""), result.get("crf", 0),
                f'{result.get("vmaf", 0):{APP_CONFIG["metric_formats"]["vmaf"]}}',
                f'{result.get("vmaf_1_low", 0):{APP_CONFIG["metric_formats"]["vmaf_1_low"]}}',
                f'{result.get("psnr", 0):{APP_CONFIG["metric_formats"]["psnr"]}}',
                f'{result.get("ssim", 0):{APP_CONFIG["metric_formats"]["ssim"]}}',
                f'{result.get("block_score", 0):{APP_CONFIG["metric_formats"]["block_score"]}}',
                f'{result.get("size_mb", 0):{APP_CONFIG["metric_formats"]["size_mb"]}}',
                f'{result.get("efficiency", 0):{APP_CONFIG["metric_formats"]["efficiency"]}}'
            ), tags=tags)
            self.tree_item_to_result[item_id] = result # 나중에 쉽게 접근할 수 있도록 아이템 ID와 원본 데이터를 매핑

    def highlight_best_result(self):
        """
        모든 작업이 완료된 후, 가장 추천하는 결과를 결과 테이블에서 자동으로 선택하고 강조 표시.

        최적화 작업 완료 후 가장 추천할 만한 결과를 자동으로 찾아서 UI에서 강조 표시함.
        스위트 스팟이 있으면 해당 결과를, 없으면 현재 정렬 기준에서 최상위 항목을 추천 결과로 제시함.
        """
        # --- 1. 사전 조건 검사 ---
        if not self.all_results: # 성공한 결과가 하나도 없는 경우
            self.status_label_var.set("Done. No successful encodes were generated.")
            return

        children = self.tree.get_children() # 현재 결과 테이블에 표시된 항목들을 가져옴
        if not children: # 필터링 후 표시된 항목이 없는 경우
            try:
                threshold = self.vmaf_threshold_var.get()
                message = f"Done. No results meet the VMAF >= {threshold:.1f} filter. Try lowering it to see results."
                self.status_label_var.set(message)
            except tk.TclError:
                self.status_label_var.set("Done. No results are visible with the current filter settings.")
            return

        # --- 2. 최적 결과 탐색 ---
        # 스위트 스팟을 다시 계산하여 가장 균형 잡힌 결과를 찾음
        metrics_to_consider = {'psnr': self.calc_psnr_var.get(), 'ssim': self.calc_ssim_var.get(), 'blockdetect': self.calc_blockdetect_var.get()}
        current_codec = self.codec_var.get()
        codec_config = self.CODEC_CONFIG.get(current_codec, {})
        pareto_ids = self._calculate_pareto_front(self.all_results, metrics_to_consider, codec_config)
        pareto_results = [r for r in self.all_results if (r['preset'], r['crf']) in pareto_ids]
        sweet_spot_id = self._find_sweet_spot(pareto_results)

        best_item_id = None
        recommended_preset = ""
        recommended_crf = ""

        # 스위트 스팟이 있으면 해당 항목을 최적 결과로 선택
        if sweet_spot_id:
            for item_id, result_data in self.tree_item_to_result.items():
                if (result_data.get('preset'), result_data.get('crf')) == sweet_spot_id:
                    best_item_id = item_id
                    recommended_preset = sweet_spot_id[0]
                    recommended_crf = sweet_spot_id[1]
                    break

        # 스위트 스팟이 없으면, 현재 정렬된 목록의 첫 번째 항목을 최적 결과로 간주 (대체 로직)
        if not best_item_id:
            best_item_id = children[0]
            values = self.tree.item(best_item_id, "values")
            recommended_preset = values[0]
            recommended_crf = values[1]

        # --- 3. UI 업데이트 ---
        # 찾은 최적 항목을 결과 테이블에서 선택하고, 해당 위치로 스크롤
        if best_item_id:
            self.tree.selection_set(best_item_id) # 항목 선택
            self.tree.focus(best_item_id) # 항목에 포커스
            self.tree.see(best_item_id) # 항목이 보이도록 스크롤
            self.status_label_var.set(f"Done. Recommended -> Preset: {recommended_preset}, CRF: {recommended_crf}") # 상태 메시지에 추천 항목 표시

    def _calculate_pareto_front(self, results: List[Dict], metrics_to_consider: Dict[str, bool], codec_config: Dict) -> set:
        """
        결과 목록으로부터 다차원 파레토 프론트(Pareto front) 계산.

        파레ト 프론트는 어떤 결과를 다른 어떤 결과와 비교했을 때, 모든 측정 항목에서 동시에 뒤처지지 않는 효율적인 결과들의 집합을 의미함.
        만약 모든 수치 지표가 동일하다면, 더 빠른 프리셋을 더 우수한 것으로 간주하는 타이 브레이커를 적용함.

        Args:
            results: 분석할 결과들의 리스트
            metrics_to_consider: 고려할 메트릭들의 활성화 여부
            codec_config: 코덱별 설정 정보

        Returns:
            set: 파레토 프론트에 속하는 결과들의 (preset, crf) 튜플 집합
        """
        if not results: # 분석할 결과가 없으면 빈 집합을 반환
            return set()

        # 사용자가 활성화한 메트릭에 따라 비교할 항목들을 동적으로 구성
        HIGHER_IS_BETTER_METRICS = ['vmaf', 'vmaf_1_low']
        if metrics_to_consider.get('psnr'):
            HIGHER_IS_BETTER_METRICS.append('psnr')
        if metrics_to_consider.get('ssim'):
            HIGHER_IS_BETTER_METRICS.append('ssim')

        active_lower_metrics = ['size_mb']
        if metrics_to_consider.get('blockdetect'):
            active_lower_metrics.append('block_score')

        pareto_front_ids = set() # 파레토 프론트에 속하는 결과의 ID를 저장할 집합

        # 모든 결과를 순회하며 각 결과(candidate)가 파레토 프론트에 속하는지 검사
        for candidate in results:
            is_dominated = False # 현재 candidate가 다른 결과에 의해 '지배'당하는지 여부
            for competitor in results:
                if candidate is competitor: # 자기 자신과는 비교하지 않음
                    continue

                # competitor가 candidate보다 모든 면에서 같거나 우월한지 확인하기 위한 플래그
                is_at_least_as_good_in_all = True
                is_strictly_better_in_one = False

                # 값이 높을수록 좋은 메트릭들을 비교
                for metric in HIGHER_IS_BETTER_METRICS:
                    if competitor.get(metric, 0) < candidate.get(metric, 0): # 하나라도 열등하면
                        is_at_least_as_good_in_all = False
                        break
                    if competitor.get(metric, 0) > candidate.get(metric, 0): # 하나라도 우월하면
                        is_strictly_better_in_one = True
                if not is_at_least_as_good_in_all: # 이미 열등한 점이 발견되면 더 이상 비교할 필요 없음
                    continue

                # 값이 낮을수록 좋은 메트릭들을 비교
                for metric in active_lower_metrics:
                    if competitor.get(metric, float('inf')) > candidate.get(metric, float('inf')): # 하나라도 열등하면
                        is_at_least_as_good_in_all = False
                        break
                    if competitor.get(metric, float('inf')) < candidate.get(metric, float('inf')): # 하나라도 우월하면
                        is_strictly_better_in_one = True
                if not is_at_least_as_good_in_all:
                    continue
                
                # 모든 수치 메트릭이 동일한 경우, 프리셋 속도로 순위를 결정 (tie-breaker)
                if is_at_least_as_good_in_all and not is_strictly_better_in_one:
                    preset_order = codec_config.get("preset_values", [])
                    if preset_order:
                        try:
                            candidate_preset_idx = preset_order.index(candidate['preset'])
                            competitor_preset_idx = preset_order.index(competitor['preset'])
                            if competitor_preset_idx < candidate_preset_idx: # 더 빠른 프리셋(인덱스가 낮음)이 우월함
                                is_strictly_better_in_one = True
                        except (ValueError, IndexError):
                            pass # 프리셋 목록에 없는 경우 무시

                # competitor가 모든 면에서 같거나 우월하고, 한 가지 면 이상에서 명백히 우월하다면 candidate는 지배당함
                if is_at_least_as_good_in_all and is_strictly_better_in_one:
                    is_dominated = True
                    break

            # 어떤 다른 결과에게도 지배당하지 않았다면, 이 candidate는 파레토 프론트에 속함
            if not is_dominated:
                pareto_front_ids.add((candidate['preset'], candidate['crf']))

        return pareto_front_ids

    def _find_sweet_spot(self, pareto_results: List[Dict]) -> Tuple[str, int]:
        """
        파레토 프론트 결과들 중에서 가장 균형 잡힌 지점인 '스위트 스팟(Sweet Spot)' 탐색.

        파레토 프론트에 속하는 결과들 중에서 품질과 파일 크기의 균형이 가장 좋은 지점을 찾음.
        그래프의 시작점과 끝점을 잇는 가상의 직선에서 가장 멀리 떨어진 점을 스위트 스팟으로 결정함.

        Args:
            pareto_results: 파레토 프론트에 속하는 결과들의 리스트

        Returns:
            Tuple[str, int]: 스위트 스팟의 (preset, crf) 튜플 또는 None (찾지 못한 경우)
        """
        if len(pareto_results) < 3: # 점이 3개 미만이면 의미 있는 스위트 스팟을 찾기 어려움
            return None

        # 파일 크기를 기준으로 파레토 프론트 점들을 정렬
        points = sorted(pareto_results, key=lambda r: r.get('size_mb', 0))

        # 정렬된 점들의 양 끝점을 잇는 직선의 시작점(p1)과 끝점(p2)을 정의
        p1 = (points[0]['size_mb'], points[0]['vmaf'])
        p2 = (points[-1]['size_mb'], points[-1]['vmaf'])

        # 직선에서 가장 멀리 떨어진 점을 찾기 위한 변수 초기화
        max_distance = -1.0
        sweet_spot_result = None

        # 양 끝점을 제외한 모든 중간 점들에 대해 직선과의 거리를 계산
        for i in range(1, len(points) - 1):
            point = points[i]
            px = (point['size_mb'], point['vmaf'])

            # 점(px)과 두 점(p1, p2)을 지나는 직선 사이의 거리 계산 공식
            distance = abs((p2[1] - p1[1]) * px[0] - (p2[0] - p1[0]) * px[1] + p2[0] * p1[1] - p2[1] * p1[0])

            # 현재까지의 최대 거리보다 더 먼 점을 찾으면 업데이트
            if distance > max_distance:
                max_distance = distance
                sweet_spot_result = point

        if sweet_spot_result:
            return (sweet_spot_result['preset'], sweet_spot_result['crf'])
        
        return None

    def export_to_csv(self, filepath):
        """
        현재까지의 모든 결과를 CSV 파일로 저장.

        최적화 결과 데이터를 CSV 형식으로 내보내며, 프리셋과 CRF 값을 기준으로 정렬하여 저장함.
        결과 테이블의 모든 컬럼을 포함하며, UTF-8 인코딩을 사용하여 한글 등의 특수 문자를 올바르게 처리함.

        Args:
            filepath: 저장할 CSV 파일의 경로
        """
        try:
            # CSV 내보내기 시작 로깅
            logging.info(f"CSV export started - File: {filepath}, Results: {len(self.all_results)}")
            
            # 정렬 기준을 위해 현재 코덱의 프리셋 순서를 가져옴
            current_codec = self.codec_var.get()
            codec_config = self.CODEC_CONFIG.get(current_codec, {})
            presets_for_sorting = codec_config.get("preset_values", [])

            def get_sort_key(r): # 프리셋 순서와 CRF를 기준으로 결과를 정렬하기 위한 키 함수
                preset = r['preset']
                crf = r['crf']
                if presets_for_sorting and preset in presets_for_sorting:
                    return (presets_for_sorting.index(preset), crf)
                return (preset, crf) # 프리셋 순서를 모를 경우 문자열 순으로 정렬

            # CSV 파일 쓰기 시작
            with open(filepath, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                
                # 헤더(머리글) 작성
                headers = [self.tree.heading(c)['text'] for c in self.tree['columns']]
                writer.writerow(headers)

                # 정렬된 결과 데이터를 한 줄씩 파일에 씀
                for result in sorted(self.all_results, key=get_sort_key):
                    writer.writerow([
                        result["preset"], result.get("crf", 0), result.get("vmaf", 0),
                        result.get("vmaf_1_low", 0), result.get("psnr", 0), result.get("ssim", 0),
                        result.get("block_score", 0), result.get("size_mb", 0),
                        result.get("efficiency", 0)
                    ])
            
            # CSV 내보내기 완료 로깅
            logging.info(f"CSV export completed successfully - File: {filepath}")
            
            # 작업 완료 후 사용자에게 성공 메시지 표시
            messagebox.showinfo("Success", f"All {len(self.all_results)} results exported to\n{filepath}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export file.\nError: {e}")

    def export_to_html(self, filepath):
        """
        모든 데이터를 수집하여 상세 HTML 리포트를 생성.

        최적화 결과 데이터를 수집하여 상세한 HTML 리포트를 생성함.
        Pareto front, Sweet Spot, 최고 품질, 최고 효율성 등의 주요 결과를 포함하며, 인터랙티브한 그래프와 정렬된 데이터 테이블을 제공함.

        Args:
            filepath: 저장할 HTML 파일의 경로
        """
        try:
            # HTML 리포트 생성 시작 로깅
            logging.info(f"HTML report generation started - File: {filepath}")
            
            # --- 1. 리포트 생성에 필요한 데이터 수집 및 계산 ---
            view_mode = self.view_mode_display_var.get()

            # 그래프 생성을 위한 옵션 정의 (GraphWindow와 동일한 구조)
            plot_options = {
                "CRF": ("crf", False), "VMAF Score": ("vmaf", True),
                "VMAF 1% Low": ("vmaf_1_low", True), "Block Score": ("block_score", False),
                "File Size (MB)": ("size_mb", False), "Efficiency (VMAF/MB)": ("efficiency", True),
                "PSNR": ("psnr", True), "SSIM": ("ssim", True),
            }

            # 강조 표시를 위한 추천 항목 및 특별 결과 ID 찾기
            metrics_to_consider = self.last_run_context['metrics']
            codec_config = self.CODEC_CONFIG.get(self.last_run_context['codec'], {})
            
            pareto_ids = self._calculate_pareto_front(self.all_results, metrics_to_consider, codec_config)
            pareto_results = [r for r in self.all_results if (r['preset'], r['crf']) in pareto_ids]
            sweet_spot_id = self._find_sweet_spot(pareto_results)
            
            # 주요 추천 항목들에 대한 전체 결과 데이터를 찾음
            sweet_spot = next((r for r in self.all_results if (r['preset'], r['crf']) == sweet_spot_id), None)
            best_quality = max(self.all_results, key=lambda r: r.get('vmaf', 0))
            most_efficient = max(self.all_results, key=lambda r: r.get('efficiency', 0))
            
            # 테이블 하이라이팅을 위한 최저 성능 항목 ID를 찾음
            lowest_vmaf_item = min(self.all_results, key=lambda r: r.get('vmaf', float('inf')))
            lowest_vmaf_id = (lowest_vmaf_item['preset'], lowest_vmaf_item['crf'])
            lowest_efficiency_item = min(self.all_results, key=lambda r: r.get('efficiency', float('inf')))
            lowest_efficiency_id = (lowest_efficiency_item['preset'], lowest_efficiency_item['crf'])
            
            # --- 2. HTML 콘텐츠 생성 및 파일 저장 ---
            # 모든 데이터를 전달하여 전체 HTML 리포트 콘텐츠를 생성
            html_content = self.generate_html_report(
                self.last_run_context, self.all_results, pareto_ids, sweet_spot,
                best_quality, most_efficient, sweet_spot_id, lowest_vmaf_id,
                lowest_efficiency_id, view_mode, plot_options
            )

            # 생성된 HTML 콘텐츠를 파일에 씀
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            # HTML 리포트 생성 완료 로깅
            logging.info(f"HTML report generated successfully - File: {filepath}")
            
            # 사용자에게 성공 메시지 표시
            messagebox.showinfo("Success", f"Report successfully saved to:\n{filepath}")

        except Exception as e:
            # 오류 발생 시 로깅 및 사용자에게 알림
            logging.error(f"Failed to generate HTML report: {e}", exc_info=True)
            messagebox.showerror("Error", f"Failed to generate report.\nError: {e}")

    def generate_html_report(self, context, results, pareto_ids, sweet_spot, best_quality, most_efficient, sweet_spot_id, lowest_vmaf_id, lowest_efficiency_id, view_mode, plot_options):
        """
        상호작용형 그래프와 일관된 정렬/색상 규칙을 포함하여 리포트의 전체 HTML 콘텐츠를 생성.

        HTML 리포트의 전체 콘텐츠를 생성하며, 인터랙티브한 그래프, 정렬된 데이터 테이블, 추천 항목 등을 포함함.
        Chart.js를 사용하여 동적 그래프를 생성하고, 일관된 스타일링을 적용함.

        (함수 인자는 docstring에 이미 상세히 기술되어 있음)

        Returns:
            str: 생성된 HTML 콘텐츠
        """
        report_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        def format_time(seconds):
            """초 단위 시간을 HH:MM:SS.ms 형식의 문자열로 변환하는 헬퍼 함수."""
            return str(timedelta(seconds=seconds)).split('.')[0] + f".{int((seconds % 1) * 1000):03d}"

        def get_command(result):
            """주어진 결과 딕셔너리를 기반으로 전체 비디오용 FFmpeg 명령어를 생성하는 헬퍼 함수."""
            if not result:
                return "N/A"
            
            task = EncodingTask(
                ffmpeg_path="ffmpeg", sample_path="", temp_dir="",
                codec=context['codec'], preset=result['preset'], crf=result['crf'],
                audio_option=self.audio_var.get(), adv_opts=result['adv_opts_snapshot']
            )
            builder = FFmpegCommandBuilder(task, full_video_path=f'"{context["source_path"]}"')
            cmd_list = builder.build_encode_command()
            cmd_list[-1] = f'"output_{result["preset"]}_{result["crf"]}.mkv"'
            
            return ' '.join(cmd_list)

        def build_rec_row(title, result):
            """추천 항목 테이블의 단일 행(row) HTML을 생성하는 헬퍼 함수."""
            if not result:
                return ""

            # HTML 셀에 들어갈 내용을 미리 변수에 할당하여 가독성 향상
            quality_param_name = self.quality_range_label.cget('text').split(' ')[0]
            setting_str = f"{result.get('preset', 'N/A')}, {quality_param_name}: {result.get('crf', 'N/A')}"
            vmaf_avg_str = f"{result.get('vmaf', 0):{APP_CONFIG['metric_formats']['vmaf']}}"
            vmaf_1_low_str = f"{result.get('vmaf_1_low', 0):{APP_CONFIG['metric_formats']['vmaf_1_low']}}"
            vmaf_combined_str = f"{vmaf_avg_str} / {vmaf_1_low_str}" # 템플릿에서 사용되지 않으므로 참고용
            size_mb_str = f"{result.get('size_mb', 0):{APP_CONFIG['metric_formats']['size_mb']}} MB"
            
            sample_duration = self.last_run_context.get('sd', 1)
            bitrate_kbps = (result.get('size_mb', 0) * 1024 * 8) / sample_duration if sample_duration > 0 else 0
            bitrate_str = f"{bitrate_kbps:,.0f} kbps"
            
            efficiency_str = f"{result.get('efficiency', 0):{APP_CONFIG['metric_formats']['efficiency']}}"

            # 준비된 변수들을 사용하여 f-string으로 HTML 구조를 생성
            return f"""
            <tr>
                <td><b>{title}</b></td>
                <td>{setting_str}</td>
                <td>{vmaf_avg_str}</td>
                <td>{size_mb_str}</td>
                <td>{bitrate_str}</td>
                <td>{efficiency_str}</td>
            </tr>
            """

        # --- 데이터 준비 및 HTML 생성 ---
        # 메인 UI의 보기 모드에 따라 상세 결과 테이블의 데이터를 정렬
        if view_mode == 'Max Quality':
            sorted_results = sorted(results, key=lambda r: r.get('vmaf', 0), reverse=True)
        else:
            sorted_results = sorted(results, key=lambda r: r.get('efficiency', 0), reverse=True)

        # 상세 결과 테이블의 모든 행(row) HTML을 생성
        table_rows = ""
        for r in sorted_results:
            result_id = (r['preset'], r['crf'])
            row_class = ""
            if result_id == sweet_spot_id: row_class = "class='sweet-spot'"
            elif result_id == lowest_vmaf_id: row_class = "class='worst-quality'"
            elif result_id == lowest_efficiency_id: row_class = "class='worst-efficiency'"
            elif result_id in pareto_ids: row_class = "class='pareto'"
            
            bitrate_kbps = (r['size_mb'] * 1024 * 8) / context.get('sd', 1) if context.get('sd', 0) > 0 else 0
            is_pareto_text = "Yes" if result_id in pareto_ids else ""
            
            table_rows += f"""
            <tr {row_class}>
                <td>{r['preset']}</td>
                <td>{r['crf']}</td>
                <td>{r.get('vmaf', 0):{APP_CONFIG['metric_formats']['vmaf']}}</td>
                <td>{r.get('vmaf_1_low', 0):{APP_CONFIG['metric_formats']['vmaf_1_low']}}</td>
                <td>{r.get('psnr', 0):{APP_CONFIG['metric_formats']['psnr']}}</td>
                <td>{r.get('ssim', 0):{APP_CONFIG['metric_formats']['ssim']}}</td>
                <td>{r.get('block_score', 0):{APP_CONFIG['metric_formats']['block_score']}}</td>
                <td>{r.get('size_mb', 0):{APP_CONFIG['metric_formats']['size_mb']}}</td>
                <td>{bitrate_kbps:,.0f}</td>
                <td>{r.get('efficiency', 0):{APP_CONFIG['metric_formats']['efficiency']}}</td>
                <td>{is_pareto_text}</td>
            </tr>
            """

        # 사용된 고급 옵션들을 표시하기 위한 문자열 생성
        adv_opts_str = '<br>'.join([f"&nbsp;&nbsp;&nbsp;&nbsp;{k}: {v}" for k, v in context['adv_opts'].items() if v and str(v) not in ['0', 'False']])
        if not adv_opts_str: adv_opts_str = "Defaults"

        # JavaScript에서 사용할 데이터를 JSON 형식으로 직렬화
        all_data_json = json.dumps(results)
        plot_options_map = {name: key for name, (key, _) in plot_options.items()}
        plot_options_json = json.dumps(plot_options_map)
        metric_formats_json = json.dumps(APP_CONFIG["metric_formats"])
        
        # 프로그램 정보를 변수로 저장
        prog_info = APP_CONFIG['about_info']

        # --- 최종 HTML 문서 템플릿 ---
        # f-string을 사용하여 모든 동적 데이터를 포함한 HTML 문자열을 반환
        html_template = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <title>Video Encoding Optimization Report</title>
            <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
            <script src="https://cdn.jsdelivr.net/npm/chartjs-plugin-zoom@2.0.1/dist/chartjs-plugin-zoom.min.js"></script>
            <style>
                /* 기본 레이아웃 및 타이포그래피 */
                body {{
                    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
                    margin: 0 auto;
                    max-width: 80%;
                    padding: 20px;
                    color: #333;
                }}
                h1, h2, h3 {{
                    color: #111;
                    border-bottom: 1px solid #ddd;
                    padding-bottom: 10px;
                }}
                code {{
                    background-color: #eee;
                    padding: 2px 5px;
                    border-radius: 3px;
                    font-family: "Consolas", "Courier New", monospace;
                }}

                /* 컴포넌트 스타일 */
                .summary-box {{
                    background-color: #f6f6f6;
                    border: 1px solid #ddd;
                    border-left: 5px solid #4CAF50;
                    padding: 15px;
                    margin-bottom: 20px;
                }}
                .summary-box p {{
                    margin: 5px 0;
                }}
                .command-box {{
                    background-color: #2d2d2d;
                    color: #ccc;
                    padding: 15px;
                    border-radius: 5px;
                    font-family: "Consolas", "Courier New", monospace;
                    white-space: pre-wrap;
                    word-break: break-all;
                    margin-bottom: 10px;
                }}

                /* 테이블 스타일 */
                table {{
                    width: 100%;
                    border-collapse: collapse;
                    margin-bottom: 20px;
                }}
                th, td {{
                    border: 1px solid #ddd;
                    padding: 8px;
                    text-align: left;
                }}
                th {{
                    background-color: #f2f2f2;
                }}

                /* 결과 하이라이팅 (테이블 행) */
                tr.sweet-spot {{ background-color: yellow !important; color: black !important; }}
                tr.pareto {{ background-color: palegreen !important; color: black !important; }}
                tr.worst-quality {{ background-color: purple !important; color: white !important; }}
                tr.worst-efficiency {{ background-color: red !important; color: white !important; }}

                /* 그래프 및 컨트롤 */
                .graph-container {{
                    text-align: center;
                    margin: 20px 0;
                }}
                .graph-controls {{
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    gap: 20px;
                    margin-bottom: 15px;
                }}
                .graph-controls label {{
                    font-weight: bold;
                }}
                .graph-controls select {{
                    padding: 5px;
                    border-radius: 4px;
                    border: 1px solid #ccc;
                }}

                /* 범례 (Legend) 스타일 */
                .legend {{
                    display: flex;
                    flex-wrap: wrap;
                    justify-content: center;
                    gap: 20px;
                    margin-bottom: 15px;
                    font-size: 0.9em;
                }}
                .legend span {{
                    display: inline-flex;
                    align-items: center;
                }}
                .legend-color {{
                    display: inline-block;
                    width: 12px;
                    height: 12px;
                    margin-right: 6px;
                    border: 1px solid #ccc;
                }}
                .sweet-spot-bg {{ background-color: yellow; }}
                .pareto-bg {{ background-color: palegreen; }}
                .worst-quality-bg {{ background-color: purple; }}
                .worst-efficiency-bg {{ background-color: red; }}

                /* 푸터 (Footer) 스타일 */
                .footer {{
                    text-align: center;
                    margin-top: 40px;
                    font-size: 0.8em;
                    color: #777;
                    border-top: 1px solid #eee;
                    padding-top: 20px;
                }}
            </style>
        </head>
        <body>
            <h1>Video Encoding Optimization Report</h1>
            
            <!-- 요약 (Summary) 섹션 -->
            <h2>Summary</h2>
            <div class="summary-box">
                <p><b>Source File:</b> <code>{os.path.basename(context['source_path'])}</code></p>
                <p><b>Report Date:</b> {report_date}</p>
                <p>
                    <b>Analysis Overview:</b> Performed {len(results)} encodes using the <code>{context['codec']}</code> codec, 
                    with presets from <code>{context['preset_start']}</code> to <code>{context['preset_end']}</code> 
                    and a quality range of <code>{context['quality_start']}</code>-<code>{context['quality_end']}</code>.
                </p>
                <hr style="border: 0; border-top: 1px solid #ddd; margin: 10px 0;">
                <p><b>Generated by:</b> {prog_info['program']} v{prog_info['version']} ({prog_info['updated']})</p>
                <p><b>Developer:</b> <a href="{prog_info['website']}" target="_blank">{prog_info['developer']}</a></p>
            </div>
            <br>

            <!-- 추천 항목 (Top Recommendations) 섹션 -->
            <h2>Top Recommendations</h2>
            <table>
                <thead>
                    <tr>
                        <th>Recommendation Type</th>
                        <th>Setting (Preset, Quality)</th>
                        <th>VMAF (Avg)</th>
                        <th>File Size (Compression)</th>
                        <th>Bitrate</th>
                        <th>Efficiency (VMAF/MB)</th>
                    </tr>
                </thead>
                <tbody>
                    {build_rec_row("Sweet Spot (Balanced)", sweet_spot)}
                    {build_rec_row("Best Quality", best_quality)}
                    {build_rec_row("Most Efficient", most_efficient)}
                </tbody>
            </table>
            <br>

            <!-- 분석 파라미터 (Analysis Parameters) 섹션 -->
            <h2>Analysis Parameters</h2>
            <table>
                <!-- ================== 1. Core Encoding Settings ================== -->
                <tr>
                    <td>Encoder Group</td>
                    <td>{context.get('encoder_group', 'N/A')}</td>
                </tr>
                <tr>
                    <td>Optimization Mode</td>
                    <td>
                        {context.get('optimization_mode', 'N/A')}
                        {f" (Target: {context.get('target_vmaf')} VMAF)" if context.get('optimization_mode') == 'Target VMAF' else ''}
                    </td>
                </tr>
                <tr>
                    <td>Parallel Jobs</td>
                    <td>{context.get('parallel_jobs', 'N/A')}</td>
                </tr>
                <tr>
                    <td>Audio</td>
                    <td>{context.get('audio_option', 'N/A')}</td>
                </tr>
                <!-- ================== 2. Source & Sampling Settings ================== -->
                <tr>
                    <td>Analysis Sample</td>
                    <td>{context['sd']:.2f} second segment starting at {format_time(context['ss'])}</td>
                </tr>
                <tr>
                    <td>Sample Method</td>
                    <td>{context['sample_mode']} {'(' + context['auto_mode_type'] + ')' if context['sample_mode'] == 'Auto' else ''}</td>
                </tr>
                <tr>
                    <td>Scene Analysis Method</td>
                    <td>{context.get('analysis_method', 'N/A')}</td>
                </tr>
                <!-- ================== 3. Advanced & Technical Settings ================== -->
                <tr>
                    <td>VMAF Model</td>
                    <td>{context['vmaf_model']}</td>
                </tr>
                <tr>
                    <td>Applied Advanced Options</td>
                    <td>{adv_opts_str}</td>
                </tr>
            </table>
            <br>

            <!-- 시각화 (Visualizations) 섹션 - 그래프 영역 -->
            <h2>Visualizations</h2>
            <div class="graph-container">
                <div class="graph-controls">
                    <label for="xAxisSelect">X-Axis:</label>
                    <select id="xAxisSelect" onchange="updateChart()"></select>
                    <label for="yAxisSelect">Y-Axis:</label>
                    <select id="yAxisSelect" onchange="updateChart()"></select>
                    <button id="resetZoomBtn" onclick="myChart.resetZoom()" style="padding: 5px 10px;">Reset Zoom</button>
                </div>
                <canvas id="resultsChart"></canvas>
            </div>
            <br>

            <!-- 상세 결과 (Detailed Results) 섹션 - 테이블 및 범례 -->
            <h2>Detailed Results</h2>
            <div class="legend">
                <span><span class="legend-color sweet-spot-bg"></span>Sweet Spot (Balanced)</span>
                <span><span class="legend-color pareto-bg"></span>Pareto Optimal</span>
                <span><span class="legend-color worst-quality-bg"></span>Lowest VMAF</span>
                <span><span class="legend-color worst-efficiency-bg"></span>Least Efficient</span>
            </div>
            <table>
                <thead>
                    <tr>
                        <th>Preset</th>
                        <th>Quality</th>
                        <th>VMAF</th>
                        <th>VMAF 1% Low</th>
                        <th>PSNR</th>
                        <th>SSIM</th>
                        <th>Block Score</th>
                        <th>Size (MB)</th>
                        <th>Bitrate (kbps)</th>
                        <th>Efficiency</th>
                        <th>Pareto Optimal</th>
                    </tr>
                </thead>
                <tbody>{table_rows}</tbody>
            </table>
            <br>

            <!-- 실행 가능 명령어 (Actionable Commands) 섹션 -->
            <h2>Actionable Commands</h2>
            <h3>Command for Sweet Spot</h3>
            <div class="command-box">{get_command(sweet_spot)}</div>
            <h3>Command for Best Quality</h3>
            <div class="command-box">{get_command(best_quality)}</div>
            <h3>Command for Most Efficient</h3>
            <div class="command-box">{get_command(most_efficient)}</div>
            
            <!-- 자바스크립트 (JavaScript) 섹션 - 차트 로직 -->
            <script>
                // # 파이썬에서 주입되는 핵심 데이터
                const allData = {all_data_json};
                const plotOptions = {plot_options_json};
                const metricFormats = {metric_formats_json};
                
                // # 차트를 그릴 캔버스 컨텍스트
                const ctx = document.getElementById('resultsChart').getContext('2d');
                let myChart; // 차트 객체를 저장할 변수

                // # 점 색상을 위한 VMAF 점수 범위 계산
                const vmafScores = allData.map(d => d.vmaf || 0);
                const minVmaf = Math.min(...vmafScores);
                const maxVmaf = Math.max(...vmafScores);

                // # VMAF 값에 따라 Viridis 스타일의 색상을 반환하는 함수
                function getColorForValue(value, vmin, vmax) {{
                    if (vmin === vmax) return 'rgba(68, 1, 84, 0.8)'; // 데이터가 하나일 경우 대비
                    const color_low = [253, 231, 37];   // 노란색 (낮은 VMAF)
                    const color_high = [68, 1, 84];     // 보라색 (높은 VMAF)
                    const t = Math.max(0, Math.min(1, (value - vmin) / (vmax - vmin)));
                    const r = Math.round(color_low[0] + t * (color_high[0] - color_low[0]));
                    const g = Math.round(color_low[1] + t * (color_high[1] - color_low[1]));
                    const b = Math.round(color_low[2] + t * (color_high[2] - color_low[2]));
                    return `rgba(${{r}}, ${{g}}, ${{b}}, 0.8)`;
                }}

                // # X축, Y축 선택 드롭다운 메뉴를 채우는 함수
                function populateSelectors() {{
                    const xSelect = document.getElementById('xAxisSelect');
                    const ySelect = document.getElementById('yAxisSelect');
                    for (const displayName in plotOptions) {{
                        xSelect.add(new Option(displayName, displayName));
                        ySelect.add(new Option(displayName, displayName));
                    }}
                    xSelect.value = "File Size (MB)";
                    ySelect.value = "VMAF Score";
                }}

                // # 사용자가 축을 변경할 때마다 차트를 다시 그리는 함수
                function updateChart() {{
                    const xName = document.getElementById('xAxisSelect').value;
                    const yName = document.getElementById('yAxisSelect').value;
                    
                    if (xName === yName) {{ // 동일한 축 선택 방지
                        alert("X and Y axes cannot be the same.");
                        document.getElementById('xAxisSelect').value = myChart.options.scales.x.title.text;
                        return;
                    }}
                    
                    const xKey = plotOptions[xName];
                    const yKey = plotOptions[yName];

                    // # 현재 선택된 축에 맞게 데이터 포맷팅
                    const chartData = allData.map(d => ({{
                        x: d[xKey] || 0,
                        y: d[yKey] || 0,
                        fullData: d, // 툴팁에 전체 데이터를 보여주기 위해 원본 저장
                        color: getColorForValue(d.vmaf || 0, minVmaf, maxVmaf)
                    }}));
                    
                    myChart.data.datasets[0].data = chartData;
                    myChart.options.scales.x.title.text = xName;
                    myChart.options.scales.y.title.text = yName;
                    myChart.update();
                }}
                
                // # HTML 문서가 모두 로드되면 차트를 생성하고 초기화
                document.addEventListener("DOMContentLoaded", function() {{
                    myChart = new Chart(ctx, {{
                        type: 'scatter', // 산점도 그래프
                        data: {{
                            datasets: [{{
                                label: 'All Encodes',
                                data: [], // updateChart() 함수에서 채워짐
                                pointRadius: 5,
                                pointHoverRadius: 8,
                                backgroundColor: (context) => {{
                                    const point = context.dataset.data[context.dataIndex];
                                    return point ? point.color : 'rgba(128, 128, 128, 0.5)';
                                }},
                                borderColor: (context) => {{
                                    const point = context.dataset.data[context.dataIndex];
                                    return point && point.color ? point.color.replace('0.8', '1') : 'rgba(128, 128, 128, 1)';
                                }},
                                borderWidth: 1,
                            }}]
                        }},
                        options: {{
                            plugins: {{
                                // # 마우스 호버 시 상세 정보를 보여주는 툴팁 설정
                                tooltip: {{
                                    callbacks: {{
                                        label: function(context) {{
                                            const pointData = context.dataset.data[context.dataIndex].fullData;
                                            function formatMetric(key, value) {{
                                                const formatSpec = metricFormats[key];
                                                if (!formatSpec || typeof value !== 'number') return String(value);
                                                const digits = parseInt(formatSpec.match(/\\d+/)[0]);
                                                return value.toFixed(digits);
                                            }}
                                            let label = [];
                                            label.push(`Preset: ${{pointData.preset}}`);
                                            label.push(`CRF: ${{pointData.crf}}`);
                                            label.push(`VMAF: ${{formatMetric('vmaf', pointData.vmaf)}} (1% Low: ${{formatMetric('vmaf_1_low', pointData.vmaf_1_low)}})`);
                                            label.push(`PSNR: ${{formatMetric('psnr', pointData.psnr)}}`);
                                            label.push(`SSIM: ${{formatMetric('ssim', pointData.ssim)}}`);
                                            label.push(`Block Score: ${{formatMetric('block_score', pointData.block_score)}}`);
                                            label.push(`Size: ${{formatMetric('size_mb', pointData.size_mb)}} MB`);
                                            label.push(`Efficiency: ${{formatMetric('efficiency', pointData.efficiency)}}`);
                                            return label;
                                        }}
                                    }}
                                }},
                                // # 마우스 휠/드래그로 줌/패닝 기능 활성화
                                zoom: {{
                                    pan: {{ enabled: true, mode: 'xy' }},
                                    zoom: {{
                                        wheel: {{ enabled: true }},
                                        pinch: {{ enabled: true }},
                                        drag: {{ enabled: true }},
                                        mode: 'xy',
                                    }}
                                }}
                            }},
                            // # X축과 Y축 설정
                            scales: {{
                                x: {{ 
                                    type: 'linear', 
                                    position: 'bottom', 
                                    title: {{ display: true, text: '' }} 
                                }},
                                y: {{ 
                                    title: {{ display: true, text: '' }} 
                                }}
                            }}
                        }}
                    }});

                    // # 초기 차트 로드
                    populateSelectors();
                    updateChart(); 
                }});
            </script>
            <div class="footer">
                Report generated by {prog_info['program']} v{prog_info['version']}
            </div>
        </body>
        </html>
        """
        return html_template



    # ==============================================================================
    # 6E. 시스템 연동 및 유틸리티 (System Integration & Utilities)
    # ==============================================================================

    # --- 설정 및 준비 (Setup & Preparation) ---
    def setup_ffmpeg(self):
        """
        FFmpeg 실행 파일의 경로를 설정하고, 파일이 없으면 다운로드를 시작.

        애플리케이션 시작 시 FFmpeg 도구들의 경로를 설정하고, 필요한 파일들이 존재하는지 확인함.
        파일이 없으면 자동으로 다운로드를 시작하고, 있으면 사용 가능한 인코더들을 감지함.
        """
        # 애플리케이션 리소스 디렉토리 및 FFmpeg 관련 실행 파일들의 전체 경로를 설정
        base_dir = os.path.dirname(os.path.abspath(__file__))
        resource_dir = os.path.join(base_dir, APP_CONFIG["data_folder_name"])
        self.ffmpeg_path = os.path.join(resource_dir, "ffmpeg.exe")
        self.ffprobe_path = os.path.join(resource_dir, "ffprobe.exe")
        self.ffplay_path = os.path.join(resource_dir, "ffplay.exe")

        # FFmpeg 실행 파일이 존재하는지 확인
        if not os.path.exists(self.ffmpeg_path) or not os.path.exists(self.ffplay_path):
            # 파일이 없으면 다운로드를 시작하고 사용자에게 상태를 알림
            self.status_label_var.set("FFmpeg not found. Downloading...")
            self.start_button.config(state=tk.DISABLED) # 다운로드 중에는 작업 시작 버튼 비활성화
            # UI 멈춤을 방지하기 위해 다운로드 작업을 별도 스레드에서 실행
            threading.Thread(target=self.download_ffmpeg, args=(resource_dir,), daemon=True).start()
        else:
            # 파일이 이미 존재하면 인코더 감지를 시작하고 사용자에게 상태를 알림
            self.status_label_var.set("FFmpeg is ready. Detecting available encoders...")
            self.populate_ffmpeg_filetypes() # FFmpeg이 지원하는 파일 형식을 가져와 파일 열기 대화상자에 반영
            # UI 멈춤을 방지하기 위해 인코더 감지 작업을 별도 스레드에서 실행
            threading.Thread(target=self._detect_available_encoders, daemon=True).start()

    def setup_vmaf_models(self):
        """
        VMAF 모델 디렉토리를 설정하고, 비어있으면 다운로드를 시작.

        VMAF 품질 분석에 필요한 모델 파일들의 경로를 설정하고, 모델 디렉토리가
        비어있거나 존재하지 않으면 자동으로 Netflix의 공식 VMAF 모델들을 다운로드함.
        """
        # VMAF 모델이 저장될 디렉토리의 전체 경로를 설정
        base_dir = os.path.dirname(os.path.abspath(__file__))
        resource_dir = os.path.join(base_dir, APP_CONFIG["data_folder_name"])
        self.vmaf_model_dir = os.path.join(resource_dir, "vmaf_models")

    def download_ffmpeg(self, resource_dir):
        """
        FFmpeg 빌드를 다운로드하고 압축을 푼 후, 필요한 실행 파일들을 Resource 폴더로 이동.
        """
        ffmpeg_temp_dir = os.path.join(resource_dir, "ffmpeg_temp")
        try:
            # 다운로드 및 압축 해제를 위한 임시 디렉토리 생성
            os.makedirs(resource_dir, exist_ok=True)
            os.makedirs(ffmpeg_temp_dir, exist_ok=True)

            archive_path = os.path.join(ffmpeg_temp_dir, os.path.basename(APP_CONFIG["ffmpeg_download_url"]))

            # --- 1. FFmpeg 다운로드 ---
            logging.info("FFmpeg download started")
            self.root.after(0, lambda: self.status_label_var.set("Downloading FFmpeg..."))
            with requests.get(APP_CONFIG["ffmpeg_download_url"], stream=True) as r:
                r.raise_for_status() # HTTP 오류가 있으면 예외 발생
                total_size = int(r.headers.get('content-length', 0)) # 전체 파일 크기를 가져옴
                self.root.after(0, lambda: self.progress_bar.config(mode='determinate', maximum=total_size, value=0))

                downloaded_size = 0
                with open(archive_path, 'wb') as f:
                    # 파일을 청크 단위로 다운로드하며 진행률 표시줄 업데이트
                    for chunk in r.iter_content(chunk_size=8192):
                        if not chunk:
                            continue
                        f.write(chunk)
                        downloaded_size += len(chunk)
                        self.root.after(0, lambda size=downloaded_size: self.progress_bar.config(value=size))

            # --- 2. 압축 해제 ---
            self.root.after(0, lambda: self.status_label_var.set("Extracting..."))
            with zipfile.ZipFile(archive_path, 'r') as z:
                z.extractall(path=ffmpeg_temp_dir)

            # --- 3. 파일 이동 ---
            # 압축 해제 후 생성된 폴더(예: ffmpeg-master-....)의 경로를 찾음
            extracted_root_dir = os.path.join(ffmpeg_temp_dir, [d for d in os.listdir(ffmpeg_temp_dir) if os.path.isdir(os.path.join(ffmpeg_temp_dir, d)) and d.startswith('ffmpeg-')][0])
            bin_dir = os.path.join(extracted_root_dir, "bin") # 실행 파일이 있는 'bin' 폴더 경로

            # 'bin' 폴더 안의 모든 파일(ffmpeg.exe, ffprobe.exe 등)을 최종 리소스 폴더로 이동
            for item in os.listdir(bin_dir):
                shutil.move(os.path.join(bin_dir, item), resource_dir)

            # --- 4. 설치 완료 및 후속 작업 ---
            logging.info("FFmpeg download and setup completed successfully")
            self.root.after(0, lambda: self.status_label_var.set("FFmpeg setup complete. Detecting encoders..."))
            self.root.after(0, lambda: self.start_button.config(state=tk.NORMAL)) # 시작 버튼 활성화
            self.root.after(0, lambda: self.progress_bar.config(mode='determinate', value=0)) # 진행률 표시줄 초기화
            self.root.after(0, self.populate_ffmpeg_filetypes) # 파일 형식 목록 업데이트
            
            # 다운로드 완료 후, 인코더 감지를 별도 스레드에서 시작
            threading.Thread(target=self._detect_available_encoders, daemon=True).start()

        except Exception as e:
            # 다운로드 중 예외 발생 시 로깅 및 사용자에게 오류 알림
            error_message = f"FFmpeg download error: {str(e)[:40]}..."
            logging.error(LOG_MESSAGES['ffmpeg_download_failed'].format(e), exc_info=True)
            self.root.after(0, lambda: self.status_label_var.set(error_message))
            self.root.after(0, lambda: messagebox.showerror("Error", f"Failed to setup FFmpeg.\nError: {e}"))
        
        finally:
            # 성공/실패 여부와 관계없이 임시 다운로드 폴더를 정리
            if os.path.exists(ffmpeg_temp_dir):
                shutil.rmtree(ffmpeg_temp_dir)

    def update_vmaf_models(self):
        """
        사용자에게 확인을 받은 후 VMAF 모델 다운로드를 시작.

        사용자에게 VMAF 모델 다운로드에 대한 확인을 받고, 승인 시 백그라운드에서
        Netflix의 공식 VMAF 모델들을 병렬로 다운로드함. 다운로드 중에는 버튼이 비활성화됨.
        """
        # 사용자에게 다운로드 여부를 묻는 확인 대화상자를 표시
        if messagebox.askyesno("Download VMAF Models", "This will download all official VMAF models from the Netflix GitHub repository (~5.52MB).\n\nThis may take a few moments. Continue?"):
            # 사용자가 '예'를 선택하면, 다운로드 버튼을 비활성화하고 별도 스레드에서 다운로드 시작
            self.vmaf_model_update_button.config(state=tk.DISABLED)
            threading.Thread(target=self._download_all_vmaf_models, daemon=True).start()

    def _download_all_vmaf_models(self):
        """
        VMAF 모델 파일 목록을 가져온 후, 스레드 풀을 사용하여 병렬로 다운로드.

        Netflix의 VMAF 모델 저장소에서 모든 모델 파일의 목록을 가져온 후,
        ThreadPoolExecutor를 사용하여 여러 파일을 동시에 다운로드함. 진행률 표시줄로 다운로드 상태를 표시함.
        """
        # 기존 모델 디렉토리를 삭제하고 새로 생성
        target_dir = self.vmaf_model_dir
        if os.path.exists(target_dir):
            shutil.rmtree(target_dir)
        os.makedirs(target_dir, exist_ok=True)

        files_to_download = []
        try:
            # VMAF 모델 다운로드 시작 로깅
            logging.info("VMAF model download started")
            
            # 1. 다운로드할 파일 목록을 재귀적으로 탐색
            self.root.after(0, lambda: self.status_label_var.set("Discovering VMAF model files..."))
            self._discover_vmaf_files(APP_CONFIG["vmaf_repo_api_url"], target_dir, files_to_download)

            if self.is_cancelling:
                self.root.after(0, lambda: self.status_label_var.set("VMAF model download cancelled."))
                return

            # 2. 병렬 다운로드 준비
            total_files = len(files_to_download)
            self.root.after(0, lambda: self.progress_bar.config(mode='determinate', maximum=total_files, value=0))

            # 3. 스레드 풀을 사용하여 파일들을 병렬로 다운로드
            with ThreadPoolExecutor(max_workers=APP_CONFIG["max_download_workers"]) as executor:
                # 각 다운로드 작업을 스레드 풀에 제출
                futures = {executor.submit(self._download_one_file, url, path): path for url, path in files_to_download}

                completed_count = 0
                for future in as_completed(futures): # 작업이 완료되는 순서대로 처리
                    if self.is_cancelling:
                        executor.shutdown(wait=False, cancel_futures=True) # 남은 작업들을 취소하고 즉시 종료
                        break

                    try:
                        future.result() # 작업 결과를 확인 (예외가 발생했는지 체크)
                        completed_count += 1
                        status_msg = f"Downloading models... ({completed_count}/{total_files})"
                        # UI 업데이트를 메인 스레드에서 안전하게 실행
                        self.root.after(0, lambda v=completed_count, s=status_msg: (self.status_label_var.set(s), self.progress_bar.config(value=v)))
                    except Exception as e:
                        path = futures[future]
                        logging.error(f"Failed to download {os.path.basename(path)}: {e}")

            # 4. 다운로드 완료 후 상태 메시지 업데이트
            if self.is_cancelling:
                logging.info("VMAF model download cancelled by user")
                self.root.after(0, lambda: self.status_label_var.set("VMAF model download cancelled."))
            else:
                logging.info(f"VMAF model download completed successfully - Downloaded {len(files_to_download)} files")
                self.root.after(0, lambda: self.status_label_var.set("VMAF models updated successfully."))

        except Exception as e:
            # 전체 다운로드 과정에서 예외 발생 시 처리
            logging.error(f"Failed to download VMAF models: {e}")
            self.root.after(0, lambda: self.status_label_var.set(f"Model download error: {str(e)[:40]}..."))
        
        finally:
            # 성공, 실패, 취소 여부와 관계없이 UI 상태를 원래대로 복원
            self.root.after(0, lambda: self.vmaf_model_update_button.config(state=tk.NORMAL))
            self.root.after(0, lambda: self.progress_bar.config(mode='determinate', value=0))

    def _discover_vmaf_files(self, url, target_dir, file_list):
        """
        GitHub API를 재귀적으로 호출하여 다운로드할 모든 VMAF 모델 파일의 목록을 만듦.

        Netflix의 VMAF 모델 저장소를 재귀적으로 탐색하여 다운로드할 모든 파일들의 URL과 경로를 수집함.
        디렉토리 구조를 그대로 유지하면서 파일 목록을 구성함.

        Args:
            url: GitHub API URL
            target_dir: 대상 디렉토리 경로
            file_list: 다운로드할 파일들의 (URL, 경로) 튜플 리스트
        """
        if self.is_cancelling: # 취소 요청이 있으면 재귀 호출 중단
            return

        try:
            # GitHub API에 GET 요청을 보내 폴더 내용을 가져옴
            response = requests.get(url)
            response.raise_for_status() # HTTP 오류가 있으면 예외 발생
            contents = response.json()

            # 폴더 내의 각 항목(파일 또는 하위 폴더)을 처리
            for item in contents:
                if self.is_cancelling: # 각 항목 처리 전에도 취소 확인
                    break
                path = os.path.join(target_dir, item['name'])
                if item['type'] == 'file': # 항목이 파일이면 다운로드 목록에 추가
                    file_list.append((item['download_url'], path))
                elif item['type'] == 'dir': # 항목이 폴더이면 로컬에 해당 폴더를 만들고 재귀적으로 함수 호출
                    os.makedirs(path, exist_ok=True)
                    self._discover_vmaf_files(item['url'], path, file_list)
        except requests.RequestException as e:
            # API 요청 실패 시 로깅 및 사용자에게 오류 알림
            logging.error(f"Failed to fetch VMAF model list from {url}: {e}")
            self.root.after(0, lambda: messagebox.showerror("Download Error", f"Failed to fetch model list.\nURL: {url}\nError: {e}"))
            raise # 예외를 다시 발생시켜 상위 호출자에게 실패를 알림

    def _download_one_file(self, url, path):
        """
        단일 파일을 지정된 경로에 다운로드.

        주어진 URL에서 파일을 스트리밍 방식으로 다운로드하여 지정된 경로에 저장함.
        청크 단위로 다운로드하여 메모리 사용량을 최적화하고, 취소 요청 시 즉시 중단함.

        Args:
            url: 다운로드할 파일의 URL
            path: 파일을 저장할 로컬 경로
        """
        if self.is_cancelling: # 다운로드 시작 전 취소 확인
            return
        
        # 스트리밍 모드로 파일을 다운로드
        with requests.get(url, stream=True) as r:
            r.raise_for_status()
            total_size = int(r.headers.get('content-length', 0))
            downloaded_size = 0
            
            with open(path, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192): # 8KB 청크 단위로 파일 쓰기
                    if self.is_cancelling:
                        return
                    f.write(chunk)
                    downloaded_size += len(chunk)
                    
                    # 개별 파일 다운로드 진행률 로깅 (너무 자주 하지 않도록)
                    if downloaded_size % (1024 * 1024) == 0:  # 1MB마다
                        logging.debug(f"Downloading {os.path.basename(path)}: {downloaded_size}/{total_size} bytes")

    def populate_ffmpeg_filetypes(self):
        """
        `ffmpeg -demuxers` 명령을 실행하여 지원하는 파일 형식을 동적으로 가져와 파일 열기 대화상자에 반영.
        """
        if not os.path.exists(self.ffmpeg_path): # FFmpeg가 없으면 실행 불가
            return
            
        try:
            # FFmpeg에 내장된 디먹서(demuxer) 목록을 조회하는 명령어를 실행
            cmd = [self.ffmpeg_path, '-hide_banner', '-demuxers']
            result = subprocess.run(cmd, capture_output=True, text=True, check=True, encoding='utf-8', errors='ignore', startupinfo=_get_subprocess_startupinfo())
            
            # 명령어 출력 결과를 파싱하여 파일 확장자들을 추출
            exts = {
                f"*.{ext}"
                for line in result.stdout.splitlines()
                if line.strip().startswith(' D') # 디먹서 목록 라인만 필터링
                for ext in line.strip().split()[1].split(',') # 확장자 부분만 추출 (쉼표로 구분된 경우 포함)
                if ext.isalnum() and len(ext) > 1 # 유효한 확장자만 필터링
            }
            
            # 추출된 확장자가 있으면 파일 열기 대화상자의 필터 목록을 업데이트
            if exts:
                self.video_file_types = [
                    ("Supported Media Files", " ".join(sorted(list(exts)))),
                    ("All files", "*.*"),
                ]
        except subprocess.CalledProcessError as e:
            logging.warning(f"FFmpeg process failed getting file formats: {e}")
        except OSError as e:
            logging.warning(f"System error getting file formats from FFmpeg: {e}")
        except Exception as e:
            logging.warning(f"Unexpected error getting file formats from FFmpeg: {e}")

    def _detect_available_encoders(self):
        """
        `ffmpeg -encoders`를 실행하여 사용 가능한 모든 비디오 인코더를 감지하고 분류.

        FFmpeg의 -encoders 옵션을 사용하여 시스템에서 사용 가능한 모든 비디오 인코더를 자동으로 감지함.
        감지된 인코더들을 CODEC_CONFIG에 정의된 그룹별로 분류하여 사용자에게 적절한 선택 옵션을 제공함.
        """
        if not os.path.exists(self.ffmpeg_path): # FFmpeg가 없으면 실행 불가
            self.root.after(0, lambda: self.status_label_var.set(LOG_MESSAGES['ffmpeg_not_found']))
            return

        try:
            # FFmpeg에 내장된 모든 인코더 목록을 조회하는 명령어를 실행
            cmd = [self.ffmpeg_path, '-hide_banner', '-encoders']
            result = subprocess.run(cmd, capture_output=True, text=True, check=True, encoding='utf-8', errors='ignore', startupinfo=_get_subprocess_startupinfo())
            
            # 이 애플리케이션에서 지원하는 모든 코덱의 목록을 가져옴
            all_known_codecs = self.CODEC_CONFIG.keys()
            available = set() # 실제 사용 가능한 코덱을 저장할 집합

            # FFmpeg 출력 결과를 한 줄씩 파싱
            for line in result.stdout.splitlines():
                if "encoders:" in line: # 헤더 라인은 건너뜀
                    continue
                # 정규 표현식을 사용하여 비디오 인코더(V.....) 라인에서 인코더 이름을 추출
                match = re.search(r'V.....\s+([a-zA-Z0-9_-]+)', line)
                if match:
                    encoder_name = match.group(1)
                    if encoder_name in all_known_codecs: # 추출된 인코더가 지원 목록에 있으면
                        available.add(encoder_name) # 사용 가능한 인코더 집합에 추가

            self.available_encoders = available # 감지된 인코더 목록을 인스턴스 변수에 저장

            # 인코더 감지 완료 로깅
            logging.info(f"Encoder detection completed - Found {len(self.available_encoders)} available encoders")
            
            # UI를 업데이트하여 감지된 인코더 그룹을 표시하도록 메인 스레드에 요청
            self.root.after(0, self._update_encoder_group_ui)

        except subprocess.CalledProcessError as e:
            # 인코더 감지 실패 시, 모든 코덱을 사용 가능하다고 가정하고 경고를 로깅 (폴백)
            logging.error(LOG_MESSAGES['ffmpeg_encoder_detection_failed'].format(e), exc_info=True)
            self.root.after(0, lambda: self.status_label_var.set(LOG_MESSAGES['encoder_detection_error']))
            self.available_encoders = set(self.CODEC_CONFIG.keys())
            self.root.after(0, self._update_encoder_group_ui)
        except OSError as e:
            logging.error(LOG_MESSAGES['system_error_encoder_detection'].format(e), exc_info=True)
            self.root.after(0, lambda: self.status_label_var.set(LOG_MESSAGES['encoder_detection_error']))
            self.available_encoders = set(self.CODEC_CONFIG.keys())
            self.root.after(0, self._update_encoder_group_ui)
        except Exception as e:
            logging.error(LOG_MESSAGES['unexpected_error_encoder_detection'].format(e), exc_info=True)
            self.root.after(0, lambda: self.status_label_var.set(LOG_MESSAGES['encoder_detection_error']))
            self.available_encoders = set(self.CODEC_CONFIG.keys())
            self.root.after(0, self._update_encoder_group_ui)

    def _update_encoder_group_ui(self):
        """감지된 인코더 목록을 기반으로 인코더 그룹 콤보박스를 업데이트."""
        # 사용 가능한 모든 인코더로부터 고유한 그룹 이름을 추출
        groups = set()
        for codec_name in self.available_encoders:
            group = self.CODEC_CONFIG.get(codec_name, {}).get("group")
            if group:
                groups.add(group)

        # 그룹 목록을 사용자 친화적인 순서로 정렬 (주요 그룹 우선)
        custom_order = ["Software", "AMD AMF", "Intel QSV", "NVIDIA NVENC"]
        ordered_part = [group for group in custom_order if group in groups] # 정의된 순서에 맞는 그룹
        remaining_groups = sorted([group for group in groups if group not in custom_order]) # 그 외 그룹 (알파벳순)
        sorted_groups = ordered_part + remaining_groups

        # 정렬된 그룹 목록으로 콤보박스를 업데이트하고 첫 번째 항목을 기본값으로 선택
        self.encoder_group_combo["values"] = sorted_groups
        if sorted_groups:
            self.encoder_group_var.set(sorted_groups[0])
            self._on_encoder_group_change() # 그룹 변경에 따른 코덱 목록 업데이트 호출

        self.status_label_var.set("Ready.") # 모든 준비가 끝났음을 상태 표시줄에 알림



    # --- 유효성 검사 (Validation) ---
    def validate_settings(self):
        """
        최적화 시작 전, 사용자가 입력한 설정 값들의 유효성을 검사.

        최적화 작업을 시작하기 전에 모든 필수 설정이 올바르게 입력되었는지 확인함.
        파일 경로, 샘플 시간, 코덱, 품질 범위, 프리셋 순서 등을 검증하여 오류를 사전에 방지함.

        Returns:
            bool: 모든 설정이 유효하면 True, 그렇지 않으면 False
        """
        # 실행할 모든 유효성 검사 함수들을 리스트로 정의
        validators = [
            self._validate_file_path,
            self._validate_sample_time,
            self._validate_codec_selection,
            self._validate_quality_settings,
            self._validate_preset_order,
        ]

        # 모든 검사 함수를 순차적으로 실행
        for validator in validators:
            if not validator(): # 하나라도 실패하면 즉시 False를 반환
                return False

        # 모든 검사를 통과하면 True를 반환
        return True

    def _validate_file_path(self):
        """
        비디오 파일 경로의 유효성을 검사하는 헬퍼 메서드.

        Returns:
            bool: 파일 경로가 유효하면 True, 그렇지 않으면 False
        """
        if not self.filepath_var.get() or not os.path.exists(self.filepath_var.get()):
            messagebox.showwarning(APP_CONFIG['message_titles']['input_error'], APP_CONFIG['message_texts']['file_not_found'])
            return False
        return True

    def _validate_sample_time(self):
        """
        샘플 시간 설정의 유효성을 검사하는 헬퍼 메서드.

        Returns:
            bool: 샘플 시간이 유효하면 True, 그렇지 않으면 False
        """
        # 'Manual' 모드일 때만 종료 시간이 시작 시간보다 늦는지 확인
        if (self.sample_mode_var.get() == "Manual" and 
            self.manual_end_time_s.get() <= self.manual_start_time_s.get()):
            messagebox.showwarning(APP_CONFIG['message_titles']['input_error'],
                                 APP_CONFIG['message_texts']['invalid_time_range'], 
                                 parent=self.root)
            return False
        return True

    def _validate_codec_selection(self):
        """
        코덱 선택의 유효성을 검사하는 헬퍼 메서드.

        Returns:
            bool: 코덱이 선택되었으면 True, 그렇지 않으면 False
        """
        if not self.codec_var.get():
            messagebox.showwarning(APP_CONFIG['message_titles']['input_error'], APP_CONFIG['message_texts']['codec_not_selected'])
            return False
        return True

    def _validate_quality_settings(self):
        """
        품질 설정 값들의 유효성을 검사하는 헬퍼 메서드.

        Returns:
            bool: 품질 설정이 유효하면 True, 그렇지 않으면 False
        """
        # 현재 선택된 코덱의 설정 정보를 가져옴
        codec = self.codec_var.get()
        config = self.CODEC_CONFIG.get(codec, {})
        min_q, max_q = config.get("quality_range", (0, 51))
        rate_control_param = config.get("rate_control", "-crf").replace('-', '').upper()

        try:
            # 현재 최적화 모드에 따라 유효성 검사를 분기
            if self.optimization_mode_var.get() == "Range Test":
                # Range Test 모드일 경우, 품질 시작값과 종료값을 정수로 변환하여 유효성 검사
                cs, ce = int(self.crf_start_var.get()), int(self.crf_end_var.get())
                if not self._is_valid_quality_range(cs, ce, min_q, max_q):
                    raise ValueError(f"{rate_control_param} range is invalid.")
            else:  # Target VMAF 모드일 경우
                # 목표 VMAF 값이 0과 100 사이인지 확인
                target_vmaf = self.target_vmaf_var.get()
                if not (0 < target_vmaf <= 100):
                    raise ValueError("Target VMAF must be between 0 and 100.")

            # 일부 고급 설정 값들이 유효한 숫자인지 검증 (VBV 관련)
            if "vbv_maxrate" in self.adv_settings_vars:
                if self.adv_settings_vars["vbv_maxrate"].get():
                    int(self.adv_settings_vars["vbv_maxrate"].get()) # 정수 변환이 실패하면 ValueError 발생
            if "vbv_bufsize" in self.adv_settings_vars:
                if self.adv_settings_vars["vbv_bufsize"].get():
                    int(self.adv_settings_vars["vbv_bufsize"].get()) # 정수 변환이 실패하면 ValueError 발생
        
        except (ValueError, tk.TclError) as e:
            # 유효성 검사 중 숫자 변환 오류나 tkinter 변수 오류 발생 시 사용자에게 알림
            messagebox.showwarning(APP_CONFIG['message_titles']['input_error'], APP_CONFIG['message_texts']['invalid_setting_value'].format(e))
            return False

        return True

    def _is_valid_quality_range(self, start_val: int, end_val: int, min_q: int, max_q: int) -> bool:
        """
        품질 범위가 유효한지 확인하는 헬퍼 메서드.

        Args:
            start_val: 시작 값
            end_val: 끝 값
            min_q: 해당 코덱의 최소 품질 값
            max_q: 해당 코덱의 최대 품질 값

        Returns:
            bool: 품질 범위가 유효하면 True, 그렇지 않으면 False
        """
        # 시작값과 종료값이 모두 유효 범위 내에 있고, 시작값이 종료값보다 크지 않은지 확인
        return (min_q <= start_val <= max_q and 
                min_q <= end_val <= max_q and 
                start_val <= end_val)

    def _validate_preset_order(self):
        """
        프리셋 순서의 유효성을 검사하는 헬퍼 메서드.

        Returns:
            bool: 프리셋 순서가 유효하면 True, 그렇지 않으면 False
        """
        presets_list = self.preset_start_combo["values"] # 현재 코덱의 프리셋 목록을 가져옴
        
        # 프리셋 목록이 있고, 선택된 시작/종료 프리셋이 모두 목록에 존재하는 경우에만 검사
        if (presets_list and 
            self.preset_start_var.get() in presets_list and 
            self.preset_end_var.get() in presets_list):
            
            # 시작 프리셋의 인덱스가 종료 프리셋의 인덱스보다 크면(더 느리면) 오류
            if presets_list.index(self.preset_start_var.get()) > presets_list.index(self.preset_end_var.get()):
                messagebox.showwarning(APP_CONFIG['message_titles']['input_error'], APP_CONFIG['message_texts']['invalid_preset_order'])
                return False
                
        return True

    def _should_warn_nvenc_parallel_limit(self) -> bool:
        """
        NVENC 코덱 사용 시 병렬 작업 수 제한 경고가 필요한지 확인하는 헬퍼 메서드.

        Returns:
            bool: 경고가 필요하면 True, 그렇지 않으면 False
        """
        # 'Range Test' 모드이고, 'nvenc' 코덱을 사용하며, 설정된 병렬 작업 수가 최대치를 초과하는지 확인
        return (self.optimization_mode_var.get() == "Range Test" and 
                "_nvenc" in self.codec_var.get() and 
                self.parallel_jobs_var.get() > APP_CONFIG['max_parallel_jobs'])



    # --- 장면 분석 (Scene Analysis) ---
    def _get_sample_timestamps(self) -> Tuple[float, float]:
        """
        UI에서 선택된 샘플 모드에 따라 샘플의 시작 시간(ss)과 지속 시간(sd)을 결정하여 반환.

        사용자가 선택한 샘플링 모드(Auto/Manual)에 따라 분석할 비디오 구간의 시작 시간과 지속 시간을 계산함.
        Auto 모드의 경우 장면 분석을 통해 최적의 구간을 자동으로 선택하고, Manual 모드의 경우 사용자가 직접 설정한 시간을 사용함.

        Returns:
            Tuple[float, float]: (시작 시간, 지속 시간) 또는 (None, None) (취소된 경우)
        """
        mode = self.sample_mode_var.get()
        if mode == "Auto": # 'Auto' 모드인 경우
            ss, sd = self._analyze_for_sample_time(self.filepath_var.get())
            if self.is_cancelling: # 분석 중 취소된 경우
                return None, None
            return ss, sd
        else:  # 'Manual' 모드인 경우
            ss = self.manual_start_time_s.get()
            sd = self.manual_end_time_s.get() - ss
            return ss, sd

    def _analyze_for_sample_time(self, input_file: str) -> Tuple[float, int]:
        """
        UI 설정에 따라 적절한 장면 분석 함수를 호출하여 샘플 시작 시간과 길이를 결정.

        사용자가 선택한 자동 모드 타입(Complex Scene/Simple Scene)에 따라
        적절한 장면 분석 알고리즘을 실행함. 분석이 실패할 경우 대체 로직을 사용하여
        안전하게 샘플 구간을 결정함.

        Args:
            input_file: 분석할 비디오 파일 경로

        Returns:
            Tuple[float, int]: (시작 시간, 지속 시간) 또는 (None, None) (취소된 경우)
        """
        sample_duration = self.sample_duration_var.get()
        start_time = None

        # 사용자가 선택한 분석 모드에 따라 프레임 크기 기반 분석을 직접 호출
        mode = self.auto_mode_type_var.get()
        if mode == "Complex Scene":
            # 가장 데이터량이 많은(복잡한) 구간을 찾음
            start_time = self._find_scene_by_frame_size_wrapper(input_file, sample_duration, find_largest=True)
        elif mode == "Simple Scene":
            # 가장 데이터량이 적은(단순한) 구간을 찾음
            start_time = self._find_scene_by_frame_size_wrapper(input_file, sample_duration, find_largest=False)

        if self.is_cancelling: # 분석 중 취소된 경우
            return None, None

        # 자동 분석에 실패한 경우, 안전한 대체(fallback) 로직을 사용
        if start_time is None:
            self.root.after(0, lambda: self.status_label_var.set("Scene analysis failed. Using fallback."))
            total_duration = self.get_video_duration(input_file)
            if total_duration is None:
                return None, None
            # 비디오의 1/3 지점을 시작점으로 사용
            ss = total_duration / 3
            sd = min(sample_duration, total_duration / 3)
        else:
            # 분석에 성공한 경우 해당 결과값을 사용
            ss = start_time
            sd = sample_duration
            
        return ss, sd

    def _find_scene_by_frame_size_wrapper(self, filepath: str, sample_duration: int, find_largest: bool = True) -> float:
        """
        사용자에게 병렬 처리 여부를 묻고, 선택에 따라 적절한 분석 함수를 호출하는 래퍼 함수.

        사용자에게 병렬 분석과 순차 분석 중 선택할 수 있는 옵션을 제공함.
        병렬 분석은 빠른 저장장치에서 성능을 크게 향상시키지만, 느린 저장장치에서는 디스크 경합으로 인해 오히려 성능이 저하될 수 있음.

        Args:
            filepath: 분석할 비디오 파일 경로
            sample_duration: 샘플 지속 시간 (초)
            find_largest: True면 가장 복잡한 장면, False면 가장 단순한 장면을 찾음

        Returns:
            float: 찾은 장면의 시작 시간 (초) 또는 None (취소 또는 실패 시)
        """
        title = "Parallel Analysis Option"
        message = (
            "Enable parallel analysis to speed up scene detection on large files?\n\n"
            "• Yes: Greatly improves speed on fast storage (EX. SSD).\n"
            "• No: May be faster on slow storage (EX. HDD) by avoiding disk contention.\n"
            "• Cancel: Abort the analysis."
        )
        # 사용자에게 병렬/순차/취소 중 하나를 선택하도록 대화상자를 표시
        response = messagebox.askyesnocancel(title, message, parent=self.root)

        if response is None:  # 사용자가 'Cancel'을 선택한 경우
            self.is_cancelling = True
            return None
        elif response:  # 사용자가 'Yes'(병렬)를 선택한 경우
            self.root.after(0, lambda: self.status_label_var.set("Analyzing in parallel using indexed keyframes..."))
            return self._find_scene_by_frame_size_indexed_parallel(filepath, sample_duration, find_largest)
        else:  # 사용자가 'No'(순차)를 선택한 경우
            self.root.after(0, lambda: self.status_label_var.set("Analyzing sequentially using I-frames..."))
            return self._find_scene_by_frame_size_sequential(filepath, sample_duration, find_largest)

    def _find_scene_by_frame_size_indexed_parallel(self, filepath: str, sample_duration: int, find_largest: bool = True) -> float:
        """
        안정적인 병렬 분석을 위해 'Two-Pass 하이브리드 접근법' 사용.

        영상의 장면 복잡도를 병렬로 분석하기 위해 두 단계 접근법을 사용함.
        1단계에서는 키프레임 인덱싱을 통해 병렬 작업을 효율적으로 분할하고, 2단계에서는 각 구간을 병렬로 분석하여 성능을 극대화함.

        Args:
            filepath: 분석할 비디오 파일 경로
            sample_duration: 샘플 지속 시간 (초)
            find_largest: True면 가장 복잡한 장면, False면 가장 단순한 장면을 찾음

        Returns:
            float: 찾은 장면의 시작 시간 (초) 또는 None (실패 시)
        """
        OVERLAP_KEYFRAMES = APP_CONFIG['overlap_keyframes'] # 병렬 분석 시 키프레임 중첩 수

        # 프로그래스바를 2단계로 설정
        self.root.after(0, lambda: self.progress_bar.config(mode='determinate', maximum=2, value=0))

        # --- 1단계: Keyframe 인덱싱 ---
        # 병렬 작업을 효율적으로 분할하기 위한 기준점(키프레임 시간)을 미리 스캔.
        self.root.after(0, lambda: self.status_label_var.set("Analyzing... (Step 1/2: Indexing keyframes)"))

        if self.is_cancelling: # 취소 요청 확인
            return None

        try:
            # -skip_frame nokey: 키프레임이 아닌 프레임을 모두 무시하여 스캔 속도를 극대화. 비디오 디코딩 없이 패킷 정보만 읽으므로 매우 빠름.
            cmd_index = [
                self.ffprobe_path, "-v", "error", "-select_streams", "v:0",
                "-show_entries", "frame=pts_time", "-skip_frame", "nokey",
                "-of", "json", filepath
            ]
            result = subprocess.run(cmd_index, capture_output=True, text=True, check=True, startupinfo=_get_subprocess_startupinfo())
            keyframe_data = json.loads(result.stdout).get("frames", [])

            if self.is_cancelling: # 취소 요청 확인
                return None

            # 키프레임을 찾지 못하면 병렬 처리의 이점이 없으므로, 안정적인 순차 분석으로 전환.
            if not keyframe_data:
                logging.warning(f"No keyframes found during indexing for {filepath}. Falling back to sequential.")
                return self._find_scene_by_frame_size_sequential(filepath, sample_duration, find_largest)

            # 모든 키프레임의 타임스탬프를 리스트로 추출하고 정렬
            keyframe_timestamps = sorted([float(frame['pts_time']) for frame in keyframe_data])

            # 1단계 완료 - 프로그래스바 진행
            self.root.after(0, self.progress_bar.step)

        except Exception as e:
            # 키프레임 인덱싱 실패 시, 순차 분석으로 대체
            logging.error(f"Keyframe indexing (Pass 1) failed for {filepath}: {e}. Falling back to sequential.")
            return self._find_scene_by_frame_size_sequential(filepath, sample_duration, find_largest)

        # --- 2단계: 병렬 프레임 분석 ---
        # 인덱싱된 키프레임을 기준으로, 누락과 중복이 없는 연속적인 병렬 분석 구간을 생성하고 실행.
        self.root.after(0, lambda: self.status_label_var.set("Analyzing... (Step 2/2: Parallel frame analysis)"))

        if self.is_cancelling: # 취소 요청 확인
            return None
        
        # GUI 응답성 및 시스템 안정성을 위해 전체 코어에서 하나를 제외한 수를 사용 (최소 1개 보장).
        num_cores = max(1, multiprocessing.cpu_count() - 1)

        # 키프레임 수가 충분하지 않으면 병렬화 오버헤드가 더 클 수 있으므로 순차 처리로 전환.
        if len(keyframe_timestamps) < num_cores * 2:
            logging.warning("Not enough keyframes for efficient parallel processing. Falling back to sequential.")
            return self._find_scene_by_frame_size_sequential(filepath, sample_duration, find_largest)

        # 각 코어(워커)가 처리할 키프레임 구간을 계산
        chunk_size = math.ceil(len(keyframe_timestamps) / num_cores)
        tasks_args = [] # 각 워커에 전달할 시간 간격 인자 리스트

        for i in range(num_cores):
            start_index = i * chunk_size
            if start_index >= len(keyframe_timestamps): # 처리할 키프레임이 더 이상 없으면 중단
                continue

            end_index = start_index + chunk_size

            # ffprobe의 -read_intervals 옵션에 사용할 시작/종료 시간 문자열을 결정
            start_time_str = ""
            if i > 0: # 첫 번째 워커가 아닐 경우에만 시작 시간을 지정
                start_time_str = str(keyframe_timestamps[start_index])

            end_time_str = ""
            is_last_worker = (i == num_cores - 1) or (end_index >= len(keyframe_timestamps))
            if not is_last_worker: # 마지막 워커가 아닐 경우에만 종료 시간을 지정 (경계 누락 방지를 위해 중첩 포함)
                overlapped_end_index = min(end_index + OVERLAP_KEYFRAMES, len(keyframe_timestamps) - 1)
                end_time_str = str(keyframe_timestamps[overlapped_end_index])

            # 최종 -read_intervals 문자열 조합 (예: "10.5%25.2")
            interval_str = f"{start_time_str}%{end_time_str}"
            tasks_args.append(interval_str)

        def _run_indexed_ffprobe_worker(interval_str: str): # 각 스레드에서 독립적으로 실행될 병렬 작업 워커 함수
            if self.is_cancelling:
                return []

            try:
                # 지정된 시간 간격 내의 프레임 정보만 분석하도록 ffprobe 실행
                cmd_analyze = [
                    self.ffprobe_path, "-v", "quiet", "-print_format", "json",
                    "-show_entries", "frame=pts_time,pkt_size,pict_type",
                    "-select_streams", "v:0", "-read_intervals", interval_str,
                    filepath
                ]
                result = subprocess.run(cmd_analyze, capture_output=True, text=True, check=True, startupinfo=_get_subprocess_startupinfo())
                return json.loads(result.stdout).get("frames", [])
            except Exception as e:
                logging.warning(LOG_MESSAGES['indexed_ffprobe_worker_failed'].format(interval_str, e))
                return []

        # 스레드 풀을 사용하여 각 시간 구간에 대해 워커 함수를 병렬로 실행하고 결과들을 스트리밍 처리
        seconds_map = {}
        seen_timestamps = set() # 중첩 구간으로 인한 중복 프레임 처리를 방지하기 위한 집합

        if hasattr(psutil, "Process"): # 메모리 사용량 모니터링 (디버깅용)
            try:
                process = psutil.Process()
                initial_memory = process.memory_info().rss / 1024 / 1024  # MB
                logging.info(LOG_MESSAGES['memory_usage_info'].format(initial_memory))
            except Exception:
                pass

        with ThreadPoolExecutor(max_workers=num_cores) as executor:
            # 각 워커의 결과를 즉시 처리하여 메모리 사용량 최소화
            for i, frames_data in enumerate(executor.map(_run_indexed_ffprobe_worker, tasks_args)):
                if self.is_cancelling:
                    return None

                # 프레임 데이터를 즉시 처리하여 메모리에 누적하지 않음
                for frame in frames_data:
                    ts = float(frame.get('pts_time', 0))
                    if ts not in seen_timestamps:
                        seen_timestamps.add(ts)
                        # 1초 단위로 그룹화
                        sec = int(ts)
                        if sec not in seconds_map:
                            seconds_map[sec] = 0
                        seconds_map[sec] += int(frame.get('pkt_size', 0))

                if i % max(1, len(tasks_args) // APP_CONFIG['progress_update_interval']) == 0: # 설정된 간격마다 취소 요청 확인
                    if self.is_cancelling:
                        return None

        if self.is_cancelling:
            return None

        # 병렬 분석에서 유효한 프레임을 전혀 찾지 못한 경우, 순차 분석으로 다시 시도
        if not seconds_map:
            logging.warning(LOG_MESSAGES['no_frames_found_parallel'].format(filepath))
            return self._find_scene_by_frame_size_sequential(filepath, sample_duration, find_largest)

        # --- 3단계: 최종 분석 ---
        # 병렬 처리로 취합된 전체 프레임 데이터를 기반으로 최종 분석을 수행.
        seconds_map = self._normalize_seconds_map(seconds_map) # 시간 오프셋이 있는 비디오를 처리하기 위해 타임스탬프 정규화
        seconds_map = {sec: size for sec, size in seconds_map.items() if size > 0} # 데이터가 없는 초(second)를 제거

        if not seconds_map: # 필터링 후 유효한 데이터가 없으면 순차 분석으로 전환
            logging.warning(LOG_MESSAGES['parallel_frame_analysis_no_data'].format(os.path.basename(filepath)))
            self.root.after(0, lambda: self.status_label_var.set(LOG_MESSAGES['parallel_analysis_fallback']))
            return self._find_scene_by_frame_size_sequential(filepath, sample_duration, find_largest)

        if hasattr(psutil, "Process"): # 최종 메모리 사용량 확인 (디버깅용)
            try:
                process = psutil.Process()
                final_memory = process.memory_info().rss / 1024 / 1024  # MB
                memory_diff = final_memory - initial_memory
                logging.info(LOG_MESSAGES['memory_usage_final'].format(final_memory, memory_diff))
            except Exception:
                pass

        # IQR 처리 정보를 수집하기 위한 딕셔너리 초기화
        iqr_info = {
            "applied": False,
            "original_data_points": len(seconds_map),
            "final_data_points": len(seconds_map),
            "removed_data_points": 0,
            "q1": None,
            "q3": None,
            "iqr": None,
            "lower_bound": None,
            "upper_bound": None,
            "reason": "Not enough data points for IQR processing"
        }

        # IQR(사분위수 범위)을 이용한 통계적 아웃라이어(극단값) 제거
        if len(seconds_map) > APP_CONFIG['min_data_points_for_iqr']:
            values = sorted(list(seconds_map.values())) # 모든 값을 리스트로 추출하고 정렬

            # Q1, Q3 계산
            q1_index = int(len(values) * APP_CONFIG['q1_percentile'])
            q3_index = int(len(values) * APP_CONFIG['q3_percentile'])
            q1 = values[q1_index]
            q3 = values[q3_index]

            iqr = q3 - q1 # 사분위수 범위 계산
            if iqr > 0: # IQR이 0이면 모든 값이 거의 같으므로 아웃라이어 제거를 건너뜀
                # 정상 범위(경계) 계산
                lower_bound = q1 - (APP_CONFIG['iqr_multiplier'] * iqr)
                upper_bound = q3 + (APP_CONFIG['iqr_multiplier'] * iqr)

                # IQR 처리 시작 로그
                logging.info(LOG_MESSAGES['iqr_processing_start'].format(
                    len(seconds_map), q1, q3, iqr, lower_bound, upper_bound
                ))

                # 아웃라이어 식별 및 상세 정보 수집
                outliers_seconds = []
                outliers_values = []
                seconds_map_filtered = {}
                
                for sec, size in seconds_map.items():
                    if lower_bound <= size <= upper_bound:
                        seconds_map_filtered[sec] = size
                    else:
                        outliers_seconds.append(sec)
                        outliers_values.append(size)

                # IQR 정보 업데이트
                iqr_info.update({
                    "applied": True,
                    "q1": q1,
                    "q3": q3,
                    "iqr": iqr,
                    "lower_bound": lower_bound,
                    "upper_bound": upper_bound,
                    "reason": "IQR processing completed successfully"
                })

                # 필터링 후 데이터가 남아있는지 확인하고 적용
                if seconds_map_filtered:
                    num_removed = len(outliers_seconds)
                    iqr_info.update({
                        "final_data_points": len(seconds_map_filtered),
                        "removed_data_points": num_removed
                    })
                    
                    # IQR 처리 완료 로그
                    logging.info(LOG_MESSAGES['iqr_processing_complete'].format(
                        len(seconds_map_filtered), num_removed, "Outliers successfully removed"
                    ))
                    
                    if num_removed > 0:
                        logging.info(LOG_MESSAGES['iqr_outlier_removed'].format(num_removed))
                        
                        # 아웃라이어 상세 정보 로깅
                        if len(outliers_seconds) <= 10:  # 10개 이하면 모든 정보 표시
                            outliers_info = ", ".join([f"{sec}s({val})" for sec, val in zip(outliers_seconds, outliers_values)])
                        else:  # 10개 초과면 요약 표시
                            outliers_info = f"{len(outliers_seconds)} outliers (first 5: {', '.join([f'{sec}s({val})' for sec, val in zip(outliers_seconds[:5], outliers_values[:5])])}...)"
                        
                        logging.info(LOG_MESSAGES['iqr_outlier_details'].format(
                            outliers_seconds, outliers_values, lower_bound, upper_bound
                        ))
                        
                    seconds_map = seconds_map_filtered
                else:
                    iqr_info.update({
                        "final_data_points": 0,
                        "removed_data_points": len(seconds_map),
                        "reason": "All data points removed by IQR filtering, using original data"
                    })
                    
                    # 모든 데이터가 제거된 경우 로그
                    logging.warning(LOG_MESSAGES['iqr_processing_complete'].format(
                        0, len(seconds_map), "All data points removed, using original data"
                    ))
                    logging.warning(LOG_MESSAGES['iqr_empty_data'])
            else:
                # IQR이 0인 경우 로그
                logging.info(LOG_MESSAGES['iqr_zero_detected'].format(q1, q3))
                
                iqr_info.update({
                    "applied": True,
                    "q1": q1,
                    "q3": q3,
                    "iqr": iqr,
                    "reason": "IQR is 0, all values are similar, no outlier removal applied"
                })
        else:
            # 데이터 포인트가 부족한 경우 로그
            reason = f"Not enough data points for IQR processing (minimum required: {APP_CONFIG['min_data_points_for_iqr']})"
            logging.info(LOG_MESSAGES['iqr_processing_skipped'].format(reason))
            iqr_info["reason"] = reason

        self._save_debug_analysis_json(seconds_map, find_largest, "parallel", iqr_info) # 디버깅용 JSON 파일 저장

        # 2단계 완료 - 프로그래스바 진행
        self.root.after(0, self.progress_bar.step)

        # 콤보박스 선택 값에 따라 분석 방식을 분기
        if self.analysis_method_var.get() == self.ANALYSIS_METHOD_WINDOW:
            # 슬라이딩 윈도우 방식: 구간(window)의 평균 복잡도를 계산하여 최적 구간의 중심점을 찾음
            target_second = self._find_best_window_from_map(seconds_map, sample_duration, find_largest)
            if target_second is None:
                return None
        else:
            # 단일 지점 방식: 가장 복잡도가 높은/낮은 단일 1초 지점을 찾음
            target_key = max(seconds_map, key=seconds_map.get) if find_largest else min(seconds_map, key=seconds_map.get)
            target_second = float(target_key)

        # 찾은 목표 시간(target_second)을 기준으로 최종 샘플 시작 시간을 계산하여 반환
        return self._calculate_start_time(filepath, target_second, sample_duration)

    def _find_scene_by_frame_size_sequential(self, filepath, sample_duration, find_largest=True):
        """
        ffprobe를 사용하여 영상의 모든 프레임 크기를 분석하고,
        초당 전체 프레임 데이터의 합이 가장 크거나 작은 구간을 찾아 반환 (순차 처리 버전).
        """
        try:
            # 변수 초기화
            chunk_size = APP_CONFIG['chunk_size'] # 메모리 효율성을 위해 한 번에 처리할 프레임 수
            seconds_map = {}
            total_frames_processed = 0

            # 비디오의 모든 프레임에 대한 정보(시간, 패킷 크기 등)를 JSON 형식으로 요청
            cmd = [
                self.ffprobe_path, "-v", "quiet",
                "-analyzeduration", "20M", "-probesize", "20M",
                "-print_format", "json", "-show_entries", "frame=pts_time,pkt_size,pict_type", 
                "-select_streams", "v:0", filepath
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, check=True, startupinfo=_get_subprocess_startupinfo())
            frames_data = json.loads(result.stdout).get("frames", [])

            if not frames_data: # 프레임 정보가 없으면 None 반환
                return None
            
            # 프로그래스바를 프레임 처리 진행률로 설정
            self.root.after(0, lambda: self.progress_bar.config(mode='determinate', maximum=len(frames_data), value=0))

            # 청크 단위로 프레임 데이터 처리하여 메모리 사용량 최소화
            for i in range(0, len(frames_data), chunk_size):
                if self.is_cancelling: # 각 청크 처리 전 취소 요청 확인
                    return None
                    
                chunk = frames_data[i:i + chunk_size]
                
                for frame in chunk:
                    if 'pts_time' in frame:
                        # 1초 단위로 그룹화
                        pts_time = float(frame['pts_time'])
                        sec = int(pts_time)
                        if sec not in seconds_map:
                            seconds_map[sec] = 0
                        seconds_map[sec] += int(frame.get('pkt_size', 0))
                
                total_frames_processed += len(chunk)
                
                # 프로그래스바 업데이트
                self.root.after(0, lambda: self.progress_bar.config(value=total_frames_processed))
                
                # 주기적으로 메모리 사용량 모니터링 및 취소 요청 확인
                if hasattr(psutil, 'Process') and i % (chunk_size * APP_CONFIG['memory_check_interval']) == 0:
                    try:
                        process = psutil.Process()
                        current_memory = process.memory_info().rss / 1024 / 1024  # MB
                        logging.info(f"Sequential analysis progress: {total_frames_processed}/{len(frames_data)} frames, Memory: {current_memory:.2f} MB")
                    except Exception:
                        pass
                
                if i % (chunk_size * 2) == 0: # 더 자주 취소 요청 확인
                    if self.is_cancelling:
                        return None

            # 후처리: 타임스탬프 정규화 및 유효하지 않은 데이터 제거
            seconds_map = self._normalize_seconds_map(seconds_map)
            seconds_map = {sec: size for sec, size in seconds_map.items() if size > 0}

            if not seconds_map: # 유효한 데이터가 없으면 None 반환
                logging.warning(f"No valid frames with size > 0 found during analysis for {filepath}.")
                return None

            # IQR 처리 정보를 수집하기 위한 딕셔너리 초기화
            iqr_info = {
                "applied": False,
                "original_data_points": len(seconds_map),
                "final_data_points": len(seconds_map),
                "removed_data_points": 0,
                "q1": None,
                "q3": None,
                "iqr": None,
                "lower_bound": None,
                "upper_bound": None,
                "reason": "Not enough data points for IQR processing"
            }
            
            # IQR(사분위수 범위)을 이용한 통계적 아웃라이어(극단값) 제거
            if len(seconds_map) > APP_CONFIG['min_data_points_for_iqr']:
                values = sorted(list(seconds_map.values())) # 모든 값을 리스트로 추출하고 정렬

                # Q1, Q3 계산
                q1_index = int(len(values) * APP_CONFIG['q1_percentile'])
                q3_index = int(len(values) * APP_CONFIG['q3_percentile'])
                q1 = values[q1_index]
                q3 = values[q3_index]

                iqr = q3 - q1 # 사분위수 범위 계산
                if iqr > 0: # IQR이 0이면 모든 값이 거의 같으므로 아웃라이어 제거를 건너뜀
                    # 정상 범위(경계) 계산
                    lower_bound = q1 - (APP_CONFIG['iqr_multiplier'] * iqr)
                    upper_bound = q3 + (APP_CONFIG['iqr_multiplier'] * iqr)

                    # IQR 처리 시작 로그
                    logging.info(LOG_MESSAGES['iqr_processing_start'].format(
                        len(seconds_map), q1, q3, iqr, lower_bound, upper_bound
                    ))

                    # 아웃라이어 식별 및 상세 정보 수집
                    outliers_seconds = []
                    outliers_values = []
                    seconds_map_filtered = {}
                    
                    for sec, size in seconds_map.items():
                        if lower_bound <= size <= upper_bound:
                            seconds_map_filtered[sec] = size
                        else:
                            outliers_seconds.append(sec)
                            outliers_values.append(size)

                    # IQR 정보 업데이트
                    iqr_info.update({
                        "applied": True,
                        "q1": q1,
                        "q3": q3,
                        "iqr": iqr,
                        "lower_bound": lower_bound,
                        "upper_bound": upper_bound,
                        "reason": "IQR processing completed successfully"
                    })

                    # 필터링 후 데이터가 남아있는지 확인하고 적용
                    if seconds_map_filtered:
                        num_removed = len(outliers_seconds)
                        iqr_info.update({
                            "final_data_points": len(seconds_map_filtered),
                            "removed_data_points": num_removed
                        })
                        
                        # IQR 처리 완료 로그
                        logging.info(LOG_MESSAGES['iqr_processing_complete'].format(
                            len(seconds_map_filtered), num_removed, "Outliers successfully removed"
                        ))
                        
                        if num_removed > 0:
                            # LOG_MESSAGES 상수를 사용하여 로그 메시지의 일관성을 유지
                            logging.info(LOG_MESSAGES['iqr_outlier_removed'].format(num_removed))
                            
                            # 아웃라이어 상세 정보 로깅
                            if len(outliers_seconds) <= 10:  # 10개 이하면 모든 정보 표시
                                outliers_info = ", ".join([f"{sec}s({val})" for sec, val in zip(outliers_seconds, outliers_values)])
                            else:  # 10개 초과면 요약 표시
                                outliers_info = f"{len(outliers_seconds)} outliers (first 5: {', '.join([f'{sec}s({val})' for sec, val in zip(outliers_seconds[:5], outliers_values[:5])])}...)"
                            
                            logging.info(LOG_MESSAGES['iqr_outlier_details'].format(
                                outliers_seconds, outliers_values, lower_bound, upper_bound
                            ))
                            
                        seconds_map = seconds_map_filtered
                    else:
                        iqr_info.update({
                            "final_data_points": 0,
                            "removed_data_points": len(seconds_map),
                            "reason": "All data points removed by IQR filtering, using original data"
                        })
                        
                        # 모든 데이터가 제거된 경우 로그
                        logging.warning(LOG_MESSAGES['iqr_processing_complete'].format(
                            0, len(seconds_map), "All data points removed, using original data"
                        ))
                        # 모든 데이터가 제거된 경우, 원본 데이터를 사용하고 경고를 로깅
                        logging.warning(LOG_MESSAGES['iqr_empty_data'])
                else:
                    # IQR이 0인 경우 로그
                    logging.info(LOG_MESSAGES['iqr_zero_detected'].format(q1, q3))
                    
                    iqr_info.update({
                        "applied": True,
                        "q1": q1,
                        "q3": q3,
                        "iqr": iqr,
                        "reason": "IQR is 0, all values are similar, no outlier removal applied"
                    })
            else:
                # 데이터 포인트가 부족한 경우 로그
                reason = f"Not enough data points for IQR processing (minimum required: {APP_CONFIG['min_data_points_for_iqr']})"
                logging.info(LOG_MESSAGES['iqr_processing_skipped'].format(reason))
                iqr_info["reason"] = reason

            self._save_debug_analysis_json(seconds_map, find_largest, "sequential", iqr_info) # 디버깅용 JSON 파일 저장
        
            # 콤보박스 선택 값에 따라 분석 방식을 분기
            if self.analysis_method_var.get() == self.ANALYSIS_METHOD_WINDOW:
                # 슬라이딩 윈도우 방식: 구간(window)의 평균 복잡도를 계산하여 최적 구간의 중심점을 찾음
                target_second = self._find_best_window_from_map(seconds_map, sample_duration, find_largest)
                if target_second is None:
                    return None
            else:
                # 단일 지점 방식: 가장 복잡도가 높은/낮은 단일 1초 지점을 찾음
                target_key = max(seconds_map, key=seconds_map.get) if find_largest else min(seconds_map, key=seconds_map.get)
                target_second = float(target_key)

                # 디버깅을 위해 선택 과정을 명시적으로 로깅
                chosen_function_name = "max()" if find_largest else "min()"
                logging.info(f"FINAL_EXECUTION_TRACE (Single-Point Method): find_largest is '{find_largest}'. Executing branch: '{chosen_function_name}'. Resulting target_second: '{target_second}'.")

            # 찾은 목표 시간(target_second)을 기준으로 최종 샘플 시작 시간을 계산하여 반환
            return self._calculate_start_time(filepath, target_second, sample_duration)
            
        except Exception as e:
            # 프레임 분석 과정에서 발생할 수 있는 모든 예외를 로깅
            logging.error(f"Error during sequential frame size analysis: {e}")
            return None



    # --- 저수준 헬퍼 (Low-level Helpers) ---
    def get_selected_vmaf_model_path(self):
        """
        현재 UI에 표시된 VMAF 모델의 절대 경로를 반환.

        현재 UI에 설정된 VMAF 모델 경로를 가져와서 절대 경로로 변환하여 반환함.
        기본값이 설정된 경우 빈 문자열을 반환하여 FFmpeg의 내장 모델을 사용하도록 함.

        Returns:
            str: VMAF 모델의 절대 경로 또는 빈 문자열 (기본값 사용 시)
        """
        path_str = self.vmaf_model_path_var.get() # UI에서 현재 모델 경로 문자열을 가져옴
        
        # 기본 모델이 선택된 경우, FFmpeg가 내장 모델을 사용하도록 빈 문자열을 반환
        if path_str == "[Default] vmaf_v0.6.1.json (FFmpeg built-in)" or not path_str:
            return ""
            
        # 사용자가 지정한 모델인 경우, 절대 경로를 구성하여 반환
        return os.path.join(self.vmaf_model_dir, path_str)

    def get_video_duration(self, filepath):
        """
        ffprobe를 사용하여 비디오의 전체 길이를 초 단위로 반환.

        ffprobe를 사용하여 비디오 파일의 메타데이터에서 전체 재생 시간을 추출함.
        샘플 구간 계산이나 진행률 표시 등에 사용되며, 오류 발생 시 None을 반환하여 안전하게 처리함.

        Args:
            filepath: 분석할 비디오 파일 경로

        Returns:
            float: 비디오의 전체 길이 (초) 또는 None (실패 시)
        """
        # ffprobe 명령어를 구성하여 비디오의 'duration' 정보만 요청
        cmd = [self.ffprobe_path, "-v", "error", 
               "-analyzeduration", "20M", "-probesize", "20M",
               "-show_entries", "format=duration", 
               "-of", "default=noprint_wrappers=1:nokey=1", filepath]
        
        try:
            # 명령어를 실행하고 표준 출력을 가져옴
            result = subprocess.run(cmd, capture_output=True, text=True, check=True, startupinfo=_get_subprocess_startupinfo())
            
            # 출력된 문자열을 부동소수점 숫자로 변환하여 반환
            return float(result.stdout)
            
        except subprocess.CalledProcessError as e:
            # ffprobe가 실행되었으나 0이 아닌 종료 코드를 반환하며 실패한 경우, 중앙 로깅 헬퍼로 상세히 기록
            self._log_subprocess_error(f"Get Video Duration for '{os.path.basename(filepath)}'", e)
            return None
        except ValueError as e:
            # ffprobe는 성공했으나, 그 출력이 숫자가 아니어서(예: "N/A") float() 변환에 실패한 경우의 오류 로깅
            logging.error(f"Invalid duration value for {filepath}: {e}")
            return None
        except OSError as e:
            # ffprobe.exe 파일을 찾지 못하거나 실행 권한이 없는 등, 프로세스 시작 자체를 실패한 경우의 오류 로깅
            import shlex
            cmd_str = shlex.join(cmd)
            logging.error(f"System error trying to execute ffprobe for {filepath}. Check paths and permissions.")
            logging.error(f"Failed Command: {cmd_str}")
            logging.error(f"OS Error Details: {e}", exc_info=True)
            return None
        except Exception as e:
            # 그 외 예상치 못한 모든 예외를 처리하기 위한 최종 오류 로깅 (디버깅용 상세 정보 포함)
            logging.error(f"Unexpected error getting video duration for {filepath}: {e}", exc_info=True)
            return None

    def get_color_info(self, filepath: str) -> Dict[str, str]:
        """
        ffprobe를 사용하여 원본 비디오의 색상 관련 메타데이터를 추출.

        ffprobe를 사용하여 비디오 파일의 색상 공간, 색상 범위, 색상 기본값, 색상 전송 특성 등의 메타데이터를 추출함.
        이 정보는 인코딩 시 색상 왜곡을 방지하기 위해 FFmpeg 명령어에 자동으로 포함됨.

        Args:
            filepath: 분석할 비디오 파일의 경로

        Returns:
            Dict[str, str]: 색상 관련 메타데이터를 담은 딕셔너리
        """
        color_keys = ["color_range", "colorspace", "color_primaries", "color_trc"]
        info = {}
        try:
            # ffprobe를 사용하여 비디오 스트림의 상세 정보를 JSON 형식으로 요청
            cmd = [
                self.ffprobe_path, "-v", "quiet",
                "-analyzeduration", "20M", "-probesize", "20M",
                "-print_format", "json", "-show_streams", "-select_streams", "v:0",
                filepath
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, check=True, startupinfo=_get_subprocess_startupinfo())
            stream_data = json.loads(result.stdout).get("streams", [{}])[0]

            # 필요한 색상 관련 키가 있는지 확인하고 딕셔너리에 추가
            for key in color_keys:
                if key in stream_data:
                    info[key] = stream_data[key]

            logging.info(LOG_MESSAGES['color_info_probed'].format(os.path.basename(filepath), info))
            return info
            
        except subprocess.CalledProcessError as e:
            logging.warning(LOG_MESSAGES['color_info_ffmpeg_failed'].format(filepath, e))
            return {} # 오류 발생 시 빈 딕셔너리 반환
        except OSError as e:
            logging.warning(LOG_MESSAGES['color_info_system_error'].format(filepath, e))
            return {}
        except Exception as e:
            logging.warning(f"Unexpected error probing color info for {filepath}. Defaults will be used. Error: {e}")
            return {}

    def check_section_interlace(self, filepath, start_time, duration):
        """
        비디오의 특정 구간이 인터레이스 방식인지 확인.

        FFmpeg의 showinfo 필터를 사용하여 지정된 시간 구간의 비디오가 인터레이스 방식인지 확인함.
        인터레이스 감지 시 디인터레이싱 필터 적용 여부를 결정하는 데 사용됨.

        Args:
            filepath: 분석할 비디오 파일 경로
            start_time: 분석 시작 시간 (초)
            duration: 분석 지속 시간 (초)

        Returns:
            bool: 인터레이스 방식이면 True, 프로그레시브 방식이면 False
        """
        try:
            # 지정된 시간 구간에 showinfo 필터를 적용하여 프레임 메타데이터를 추출하는 명령어
            cmd = [
                self.ffmpeg_path, "-hide_banner",
                "-analyzeduration", "20M", "-probesize", "20M",
                "-ss", str(start_time), "-t", str(duration), 
                "-i", filepath, "-vf", "showinfo", "-f", "null", "-"
            ]
            
            # 명령어를 실행하고 결과를 가져옴
            result = subprocess.run(cmd, capture_output=True, text=True, startupinfo=_get_subprocess_startupinfo(), encoding='utf-8', errors='ignore')
            
            # FFmpeg 로그에서 인터레이스 관련 플래그(' i:T ' for Top-Field-First, ' i:B ' for Bottom-Field-First)를 찾음
            return " i:T " in result.stderr or " i:B " in result.stderr
            
        except subprocess.CalledProcessError as e:
            # 오류 발생 시, 안전하게 프로그레시브로 간주하고 경고를 로깅
            logging.warning(f"FFmpeg process failed during interlace analysis: {e}. Assuming progressive.")
            return False
        except OSError as e:
            logging.warning(f"System error during interlace analysis: {e}. Assuming progressive.")
            return False
        except Exception as e:
            logging.warning(f"Unexpected error during interlace analysis: {e}. Assuming progressive.")
            return False

    def _execute_sample_extraction(self, input_file: str, temp_dir: str, ss: float, sd: int) -> str:
        """
        주어진 시간 정보로 원본 비디오에서 샘플 구간을 추출하여 무손실로 인코딩한 후 파일 경로를 반환.

        원본 비디오에서 지정된 시간 구간을 추출하여 무손실 압축으로 샘플 파일을 생성함.
        인터레이스 영상인 경우 자동으로 디인터레이싱 필터를 적용하여 품질을 향상시킴.

        Args:
            input_file: 원본 비디오 파일 경로
            temp_dir: 임시 디렉토리 경로
            ss: 시작 시간 (초)
            sd: 지속 시간 (초)

        Returns:
            str: 생성된 샘플 파일의 경로 또는 None (실패 시)
        """
        # 해당 구간이 인터레이스 방식인지 확인
        section_is_interlaced = self.check_section_interlace(input_file, ss, sd)
        sample_path_abs = os.path.join(temp_dir, "original_sample.mkv")
        
        # FFmpeg 명령어 구성
        cmd = [
            self.ffmpeg_path, "-y", "-hide_banner", "-loglevel", "error", 
            "-analyzeduration", "20M", "-probesize", "20M",
            "-ss", str(ss), "-t", str(sd), "-i", input_file
        ]
        
        vf_options = []
        if section_is_interlaced: # 인터레이스 영상이면 bwdif 디인터레이스 필터 추가
            vf_options.append("bwdif=mode=1")
        
        vf_options.append("setpts=PTS-STARTPTS") # 추출된 샘플의 타임스탬프를 0부터 시작하도록 리셋
        
        if vf_options:
            cmd.extend(["-vf", ",".join(vf_options)])
            
        # 추출된 샘플을 빠른 속도로 무손실(-qp 0) 압축하여 저장
        cmd.extend([
            "-vsync", "cfr",
            "-c:v", "libx264", "-preset", "ultrafast", "-qp", "0", 
            "-force_key_frames", "expr:eq(n,0)",
            "-an", sample_path_abs
        ])

        try:
            # 샘플 추출 시작 로깅
            logging.info(f"Sample extraction started - Duration: {sd}s, Interlaced: {section_is_interlaced}")
            
            # 명령어 실행
            subprocess.run(cmd, check=True, capture_output=True)
            
            # 샘플 추출 완료 로깅
            logging.info(f"Sample extraction completed successfully - Output: {sample_path_abs}")
            return sample_path_abs
        except subprocess.CalledProcessError as e:
            # 샘플 추출의 초기 실행이 실패한 경우, 상세한 오류 원인을 파악하여 로깅

            # 샘플 추출 작업이 실패했음을 알리는 로그 헤더를 기록
            logging.error(f"--- Subprocess Failed: Sample Extraction for '{os.path.basename(input_file)}' ---")

            # 초기 명령어 실행이 실패했음과 FFmpeg로부터 받은 반환 코드를 로깅
            logging.error(f"Initial sample extraction command failed with return code {e.returncode}.")

            # 오류의 상세 원인을 파악하기 위해, 출력을 캡처하는 모드로 명령어를 재실행함을 알림
            logging.error("Rerunning with output capture to get error details...")
            
            # 실패 원인을 파악하기 위해, 이번에는 출력을 캡처해서 다시 실행
            result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='ignore')
            
            # 재실행 결과에서 표준 오류(stderr) 출력을 가져와 앞뒤 공백을 제거
            stderr_output = result.stderr.strip()

            # 오류 출력이 존재하는 경우, 해당 내용을 로그 파일에 기록
            if stderr_output:
                logging.error(f"Error Output (stderr) on retry:\n{stderr_output}")
            else:
                # 오류 출력이 캡처되지 않은 경우, 그 사실을 로그에 기록
                logging.error("No error output (stderr) was captured on retry.")
            
            # 샘플 추출 실패 보고서의 끝을 알리는 로그 푸터를 기록
            logging.error("--- End of Sample Extraction Failure Report ---")
            return None
        except OSError as e:
            logging.error(f"System error during sample extraction: {e}")
            return None
        except Exception as e:
            logging.error(f"Unexpected error during sample extraction: {e}")
            return None

    def _run_ab_encoding(self, res_a, res_b):
        """
        A/B 비교 샘플 생성의 실제 로직을 처리하는 내부 메서드.

        A/B 비교를 위한 샘플 비디오들을 생성하는 핵심 로직을 처리함.
        5단계로 구성된 작업을 순차적으로 실행하며, 각 단계마다 취소 요청을 확인하고 진행 상황을 UI에 표시함.

        Args:
            res_a: 첫 번째 선택된 결과 데이터
            res_b: 두 번째 선택된 결과 데이터
        """
        temp_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ab_compare")

        # A/B 비교 작업의 총 단계 수를 상수로 정의하여 유지보수성을 향상
        TOTAL_STEPS = 5
        # 진행률을 명시적으로 추적하기 위한 카운터 변수
        progress_count = 0

        def update_progress(step, message):
            """지정된 단계와 메시지로 상태 표시줄과 프로그레스바를 업데이트하는 헬퍼 함수."""
            # UI 업데이트는 메인 스레드에서 안전하게 실행되도록 self.root.after를 사용
            self.root.after(0, lambda: self.status_label_var.set(message))
            # 프로그레스바의 maximum과 value를 함께 설정하여 다른 작업의 상태로부터 완전히 독립되도록 보장
            self.root.after(0, lambda: self.progress_bar.config(maximum=TOTAL_STEPS, value=step))

        try:
            # 이전 작업의 임시 디렉토리가 남아있으면 삭제하고 새로 생성
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)
            os.makedirs(temp_dir)

            # --- 1단계: 원본 샘플 추출 ---
            progress_count = 1
            update_progress(progress_count, f"Step {progress_count}/{TOTAL_STEPS}: Creating reference sample...")
            if self.is_cancelling: return # 각 단계 시작 전 취소 확인

            ss, sd = self._get_sample_timestamps()
            if ss is None or sd <= 0:
                self.root.after(0, lambda: messagebox.showerror("Error", "Invalid time range for A/B comparison."))
                return

            sample_path_abs = self._execute_sample_extraction(self.filepath_var.get(), temp_dir, ss, sd)
            if not sample_path_abs or self.is_cancelling:
                if not self.is_cancelling: # 사용자가 취소한 것이 아닐 때만 오류 메시지 표시
                    self.root.after(0, lambda: messagebox.showerror("Error", "Failed to extract reference sample for A/B comparison."))
                return
            
            def encode_one(result, label):
                """하나의 결과 설정으로 샘플 비디오를 인코딩하는 내부 헬퍼 함수."""
                task = EncodingTask(
                    ffmpeg_path=self.ffmpeg_path, sample_path=sample_path_abs, temp_dir=temp_dir,
                    codec=self.codec_var.get(), preset=result['preset'], crf=result['crf'],
                    audio_option='Remove Audio', adv_opts=result['adv_opts_snapshot']
                )
                builder = FFmpegCommandBuilder(task)
                cmd = builder.build_encode_command()
                encoded_filename = f"compare_{label}_{task.preset}_{task.crf}.mkv"
                cmd[-1] = encoded_filename # 명령어의 마지막 요소인 출력 파일명을 덮어씀
                subprocess.run(cmd, check=True, capture_output=True, startupinfo=_get_subprocess_startupinfo(), cwd=temp_dir)
                return os.path.join(temp_dir, encoded_filename)

            def diff_one(original_sample_path, encoded_sample_path, output_diff_filename):
                """원본과 인코딩된 샘플 간의 차이 비디오를 생성하는 내부 헬퍼 함수."""
                filter_complex = "[0:v]setpts=PTS-STARTPTS[dist];[1:v]setpts=PTS-STARTPTS[ref];[dist][ref]blend=all_mode=difference"
                cmd = [
                    self.ffmpeg_path, '-y', '-hide_banner', '-loglevel', 'info',
                    '-i', os.path.basename(encoded_sample_path),
                    '-i', os.path.basename(original_sample_path),
                    '-filter_complex', filter_complex,
                    '-c:v', 'libx264', '-crf', '16', '-an',
                    output_diff_filename
                ]
                subprocess.run(cmd, check=True, capture_output=True, startupinfo=_get_subprocess_startupinfo(), cwd=temp_dir)

            # --- 2단계: 샘플 A 인코딩 ---
            progress_count += 1
            update_progress(progress_count, f"Step {progress_count}/{TOTAL_STEPS}: Encoding sample A...")
            if self.is_cancelling: return
            encoded_path_a = encode_one(res_a, 'A')

            # --- 3단계: 샘플 A 차이 비디오 생성 ---
            progress_count += 1
            update_progress(progress_count, f"Step {progress_count}/{TOTAL_STEPS}: Generating difference video for A...")
            if self.is_cancelling: return
            diff_filename_a = f"diff_A_{res_a['preset']}_{res_a['crf']}_vs_Original.mkv"
            diff_one(sample_path_abs, encoded_path_a, diff_filename_a)

            # --- 4단계: 샘플 B 인코딩 ---
            progress_count += 1
            update_progress(progress_count, f"Step {progress_count}/{TOTAL_STEPS}: Encoding sample B...")
            if self.is_cancelling: return
            encoded_path_b = encode_one(res_b, 'B')
            
            # --- 5단계: 샘플 B 차이 비디오 생성 ---
            progress_count += 1
            update_progress(progress_count, f"Step {progress_count}/{TOTAL_STEPS}: Generating difference video for B...")
            if self.is_cancelling: return
            diff_filename_b = f"diff_B_{res_b['preset']}_{res_b['crf']}_vs_Original.mkv"
            diff_one(sample_path_abs, encoded_path_b, diff_filename_b)

            # 모든 작업이 완료되었고 취소되지 않은 경우에만 결과 폴더를 열고 성공 메시지를 표시
            if not self.is_cancelling:
                if os.name == 'nt':
                    os.startfile(temp_dir) # Windows의 경우
                else:
                    subprocess.Popen(['xdg-open', temp_dir]) # Linux/Mac의 경우

                # A/B 비교 완료 로깅
                logging.info(f"A/B comparison completed successfully - Output directory: {temp_dir}")
                self.root.after(0, lambda: self.status_label_var.set("A/B comparison samples created."))
                self.root.after(0, lambda: messagebox.showinfo("Success", f"Comparison samples and difference videos created in:\n{temp_dir}", parent=self.root))

        except Exception as e:
            # 사용자가 취소한 것이 아니라, 실제 예외가 발생한 경우에만 오류를 로깅하고 사용자에게 알림.
            if not self.is_cancelling:
                logging.error(f"A/B sample creation failed: {e}", exc_info=True)
                self.root.after(0, lambda: self.status_label_var.set(f"Error creating A/B samples."))
                self.root.after(0, lambda err=e: messagebox.showerror("Error", f"Failed to create A/B samples.\nError: {err}"))
            
        finally:
            # 작업의 성공, 실패, 취소 여부와 관계없이 항상 실행되는 최종 정리 블록.
            self.is_ab_comparing = False # A/B 비교 작업 상태 플래그를 해제.
            self.ab_compare_thread = None # 스레드에 대한 참조를 정리.

            # 작업이 취소된 경우, 취소 플래그를 리셋하고 상태 메시지를 명확하게 업데이트.
            if self.is_cancelling:
                self.is_cancelling = False
                logging.info("A/B comparison cancelled by user")
                self.root.after(0, lambda: self.status_label_var.set("A/B comparison cancelled."))
            
            # 다른 주요 작업(최적화, 미리보기 분석)이 진행 중이 아닐 때만 UI 컨트롤 상태를 복원.
            if not self.is_busy and not self.is_previewing:
                self.root.after(0, lambda: self.start_button.config(state=tk.NORMAL))
                self.root.after(0, lambda: self.cancel_button.config(state=tk.DISABLED))
                # _on_tree_select를 호출하여 현재 선택 상태에 맞게 A/B 버튼 등의 상태를 올바르게 갱신.
                self.root.after(0, self._on_tree_select, None)

            # 진행률 표시줄을 초기화.
            self.root.after(0, lambda: self.progress_bar.config(mode='determinate', value=0))

    def _launch_ffplay(self, ss: float, sd: float):
        """
        계산이 완료된 시작 시간(ss)과 지속 시간(sd)을 사용하여 ffplay 프로세스를 실행.

        분석이 완료된 샘플 구간 정보를 사용하여 ffplay를 실행하여 비디오 미리보기를 시작함.
        Windows에서는 분리된 프로세스로 실행하여 메인 애플리케이션과 독립적으로 동작함.

        Args:
            ss: 샘플 시작 시간 (초)
            sd: 샘플 지속 시간 (초)
        """
        filepath = self.filepath_var.get()
        self.status_label_var.set(f"Starting preview from {ss:.2f}s for {sd:.2f}s...")

        # ffplay 실행을 위한 명령어 리스트를 구성
        cmd = [
            self.ffplay_path, "-hide_banner", "-loglevel", "error",
            "-window_title", f"Sample Preview: {os.path.basename(filepath)}",
            "-x", str(APP_CONFIG['preview_window_size'][0]), "-y", str(APP_CONFIG['preview_window_size'][1]),
            "-analyzeduration", "20M", "-probesize", "20M",
            "-ss", str(ss), "-t", str(sd), "-i", filepath
        ]

        # Windows 환경에서는 프로세스를 분리하여 실행 (메인 앱과 독립적으로 동작)
        creation_flags = 0
        if os.name == 'nt':
            creation_flags = subprocess.DETACHED_PROCESS

        try:
            # ffplay 서브프로세스를 시작
            subprocess.Popen(cmd, creationflags=creation_flags)
        except Exception as e:
            logging.error(LOG_MESSAGES['ffplay_launch_failed'].format(e), exc_info=True)
            messagebox.showerror("Preview Error", f"An error occurred while launching ffplay:\n{e}", parent=self.root)
            # ffplay 실행 실패 시, 다른 작업이 없다면 'Start' 버튼을 다시 활성화
            if not self.is_busy:
                self.start_button.config(state=tk.NORMAL)

    def _run_preview_analysis(self):
        """
        'Auto' 모드일 때 비디오를 분석하여 샘플 구간을 찾는 핵심 로직을 수행.

        Auto 모드에서 비디오의 장면을 분석하여 최적의 샘플 구간을 찾는 백그라운드 작업을 수행함.
        분석이 완료되면 ffplay를 실행하여 미리보기를 시작하고, 작업 중 취소 요청이 있으면 적절히 처리함.
        """
        try:
            # 작업 시작 직후, 그리고 각 주요 단계 이후에 취소 플래그를 확인
            if self.is_cancelling:
                self.root.after(0, lambda: self.status_label_var.set(LOG_MESSAGES["preview_analysis_cancelled"]))
                self.root.after(0, self._finalize_preview_ui)
                return

            self.root.after(0, lambda: self.status_label_var.set("Starting scene analysis..."))

            # 실제 장면 분석 로직을 호출하여 최적의 시작 시간(ss)과 지속 시간(sd)을 찾음
            ss, sd = self._get_sample_timestamps()

            if self.is_cancelling:
                self.root.after(0, lambda: self.status_label_var.set(LOG_MESSAGES["preview_analysis_cancelled"]))
                self.root.after(0, self._finalize_preview_ui)
                return

            # 분석 결과가 유효하지 않은 경우 처리
            if ss is None or sd <= 0:
                if not self.is_cancelling: # 사용자가 취소한 것이 아니라 분석이 실패한 경우에만 오류 메시지 표시
                    self.root.after(0, lambda: messagebox.showerror("Error", "Could not automatically determine a valid sample time range.", parent=self.root))
                self.root.after(0, self._finalize_preview_ui)
                return

            # 분석이 성공적으로 완료되면, ffplay 실행을 메인 스레드에서 처리하도록 예약
            self.root.after(0, self._launch_ffplay, ss, sd)

        except Exception as e:
            # 분석 중 예외 발생 시 로깅 및 사용자에게 오류 알림
            logging.error(LOG_MESSAGES["preview_analysis_failed"].format(e), exc_info=True)
            self.root.after(0, lambda: self.status_label_var.set(f"Analysis error: {str(e)[:40]}..."))
            self.root.after(0, lambda err=e: messagebox.showerror("Preview Analysis Error", f"An error occurred during analysis:\n{err}", parent=self.root))
        
        finally:
            # 성공, 실패, 취소 여부와 관계없이 항상 UI 상태를 최종 정리
            self.root.after(0, self._finalize_preview_ui)

    def _finalize_preview_ui(self):
        """
        미리보기 분석 작업(성공 또는 실패)이 완료된 후 관련 UI 컨트롤들을 원래 상태로 복원.

        미리보기 분석 작업이 완료된 후 UI 상태를 정리하고 원래 상태로 복원함.
        취소된 경우와 정상 완료된 경우를 구분하여 적절한 상태 메시지를 표시함.
        """
        self.is_previewing = False # Preview 작업 완료 플래그 해제

        # 프로그래스바 초기화
        self.progress_bar.config(mode='determinate', value=0)

        # 작업이 취소되었는지 여부에 따라 상태 메시지를 다르게 설정
        if self.is_cancelling:
            self.is_cancelling = False # 취소 플래그 해제
            logging.info("Preview analysis cancelled by user")
            self.status_label_var.set("Preview analysis cancelled.")
        elif not self.is_busy: # 다른 전체 작업이 실행 중이 아닐 때만 'Ready'로 변경
            logging.info("Preview analysis completed successfully")
            self.status_label_var.set("Ready.")

        # 전체 최적화 작업이 실행 중이 아닐 때만 관련 버튼들을 다시 활성화
        if not self.is_busy:
            self.sample_preview_button.config(state=tk.NORMAL)
            self.start_button.config(state=tk.NORMAL)
            self.cancel_button.config(state=tk.DISABLED)

    def _run_cancellable_subprocess(self, cmd: List[str], line_callback=None) -> Tuple[str, str]:
        """
        취소가 가능한 방식으로 서브프로세스를 실행하고, stdout과 stderr를 반환.

        `subprocess.Popen`을 사용하여 서브프로세스를 비동기적으로 실행하고, 실행 중 주기적으로 취소 요청을 확인함.
        특히, 이 함수는 `proc.communicate()`를 사용하지 않고 `stderr`를 실시간으로 스트리밍하여 한 줄씩
        읽어 들임으로써, 대용량 로그(예: FFmpeg의 'showinfo' 필터 출력)로 인한 메모리 고갈 문제를
        근본적으로 해결함. `line_callback`을 통해 각 stderr 라인을 실시간으로 처리할 수 있음.

        Args:
            cmd: 실행할 명령어 리스트
            line_callback: 각 stderr 라인을 인자로 받는 콜백 함수. 이 함수가 False를 반환하면 프로세스를 즉시 중단.

        Returns:
            Tuple[str, str]: (stdout, stderr) 또는 (None, str) (취소되거나 오류 발생 시)
        """
        proc = None # 프로세스 객체를 저장할 변수 초기화. finally 블록에서 접근하기 위함.
        try:
            # Popen을 사용하여 서브프로세스를 비동기적으로 시작.
            # stdout/stderr를 PIPE로 연결하여 출력을 실시간으로 스트리밍할 수 있도록 설정.
            proc = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding='utf-8',
                errors='ignore',
                startupinfo=_get_subprocess_startupinfo()
            )

            # 스트리밍된 stderr 출력을 한 줄씩 저장할 리스트. 전체 출력을 메모리에 한 번에 올리지 않기 위함.
            stderr_lines = []
            
            # with 문을 사용하여 작업 종료 또는 예외 발생 시 파이프 리소스가 자동으로 정리되도록 보장.
            # iter(callable, sentinel) 패턴을 사용하여 스트림이 끝날 때까지 (빈 문자열이 반환될 때까지) 한 줄씩 효율적으로 읽음.
            with proc.stderr as pipe:
                for line in iter(pipe.readline, ''):
                    # 각 라인을 읽은 직후, 메인 스레드에서 설정된 취소 플래그를 확인하여 빠른 응답성을 보장.
                    if self.is_cancelling:
                        proc.terminate() # 프로세스에 정상 종료 신호(SIGTERM)를 보냄.
                        try:
                            # 정상적으로 종료될 시간을 주고, 지정된 시간 내에 종료되지 않으면 TimeoutExpired 예외를 발생시킴.
                            proc.wait(timeout=APP_CONFIG['subprocess_timeout'])
                        except subprocess.TimeoutExpired:
                            # 정상 종료에 실패한 경우, 프로세스를 강제 종료(SIGKILL)하여 좀비 프로세스를 방지.
                            proc.kill()
                        return None, None # 작업이 취소되었음을 명확히 알리기 위해 None을 반환.

                    # 콜백 함수가 제공되었으면 실행
                    if line_callback:
                        # 콜백이 False를 반환하면, 프로세스를 중단하고 실패 신호를 보냄.
                        if line_callback(line) is False:
                            logging.info("Subprocess terminated early by callback signal.")
                            proc.terminate()
                            try:
                                proc.wait(timeout=APP_CONFIG['subprocess_timeout'])
                            except subprocess.TimeoutExpired:
                                proc.kill()
                            # 부분적인 로그라도 반환할 수 있도록 처리
                            return None, "".join(stderr_lines)

                    stderr_lines.append(line)

            # stderr 스트림 처리가 끝난 후, 남아있는 모든 stdout 출력을 읽어들임.
            stdout_output = proc.stdout.read()
            # 프로세스가 완전히 종료되었는지 확인하고, 관련된 모든 시스템 리소스를 정리.
            proc.wait()

            # 프로세스의 종료 코드를 확인하여 작업 성공 여부를 판단. 0이 아닌 경우 오류로 간주.
            stderr_output = "".join(stderr_lines) # 오류 분석을 위해 stderr는 항상 결합
            if proc.returncode != 0:
                # 오류 로깅을 위해 지금까지 수집된 stderr 라인들을 하나의 문자열로 결합.
                logging.error(LOG_MESSAGES['ffmpeg_process_failed'].format(proc.returncode, ' '.join(cmd), stderr_output))
                return None, stderr_output # 오류가 발생했음을 알리기 위해 None과 함께 로그를 반환.

            # 성공 시, 수집된 모든 stderr 라인들을 최종적으로 하나의 문자열로 합쳐서 반환.
            return stdout_output, stderr_output

        except Exception as e:
            # 예외 발생 시에도 서브프로세스가 여전히 실행 중인지 확인.
            if proc and proc.poll() is None:
                # 예기치 않은 오류로 인해 제어 루프를 빠져나왔을 경우, 남이있을 수 있는 자식 프로세스를 확실히 정리.
                proc.kill()
            logging.error(LOG_MESSAGES['subprocess_exception'].format(e), exc_info=True)
            return None, None

    def _terminate_child_ffmpeg_processes(self):
        """
        현재 실행 중인 애플리케이션의 모든 자식 ffmpeg.exe 프로세스를 찾아 강제 종료.

        애플리케이션이 종료되거나 취소될 때 남아있는 FFmpeg 프로세스들을 안전하게 정리함.
        파일 잠금 문제를 해결하여 임시 폴더 정리를 원활하게 하고 리소스 누수를 방지함.
        """
        try:
            parent = psutil.Process(os.getpid()) # 현재 실행 중인 파이썬 애플리케이션의 프로세스 객체를 가져옴
            children = parent.children(recursive=True) # 이 프로세스의 모든 자식 프로세스들을 재귀적으로 찾음

            # 찾은 모든 자식 프로세스들을 순회
            for process in children:
                # 자식 프로세스의 이름이 'ffmpeg.exe'인 경우에만 종료 대상으로 지정
                if process.name().lower() == 'ffmpeg.exe':
                    try:
                        logging.info(f"Terminating leftover ffmpeg process with PID {process.pid}...")
                        process.kill() # 해당 프로세스를 강제 종료
                    except psutil.NoSuchProcess:
                        # 프로세스를 종료하려는 순간 이미 자발적으로 종료되었을 수 있으므로, 이 오류는 무시
                        pass
                    except Exception as e:
                        logging.warning(f"Could not terminate ffmpeg process {process.pid}: {e}")
        except psutil.NoSuchProcess:
            # 메인 애플리케이션 프로세스를 찾는 도중 이미 종료된 경우, 이 오류는 무시
            pass
        except Exception as e:
            logging.error(f"Error while trying to terminate child ffmpeg processes: {e}")

    def _log_subprocess_error(self, context: str, e: subprocess.CalledProcessError):
        """
        subprocess.CalledProcessError 예외가 발생했을 때 상세 정보를 로깅하는 중앙 헬퍼 함수.
        """        
        logging.error(f"--- Subprocess Failed: {context} ---")
        try:
            # 실행하려 했던 명령어를 사람이 읽기 좋은 문자열로 변환
            cmd_str = shlex.join(e.cmd)
            logging.error(f"Command: {cmd_str}")
        except Exception:
            logging.error(f"Command (raw list): {e.cmd}")
        
        logging.error(f"Return Code: {e.returncode}")
        
        # FFmpeg/FFprobe가 출력한 실제 오류 메시지(stderr)를 로깅
        stderr_output = e.stderr
        if isinstance(stderr_output, bytes):
            stderr_output = stderr_output.decode('utf-8', errors='ignore')
        
        if stderr_output:
            # multi-line 로그를 위해 앞에 들여쓰기 없이 출력
            logging.error(f"Error Output (stderr):\n{stderr_output.strip()}")
        else:
            logging.error("No error output (stderr) was captured from the subprocess.")
        
        logging.error("--- End of Subprocess Failure Report ---")

    def _cleanup_temp_dir(self, temp_dir):
        """
        임시 디렉토리를 정리. (파일이 사용 중일 수 있으므로 여러 번 재시도.)

        작업 완료 후 임시 디렉토리를 안전하게 정리함.
        남아있는 FFmpeg 프로세스들을 먼저 종료하고, 파일 시스템의 I/O 지연을 고려하여 여러 번 재시도하여 안정성을 보장함.

        Args:
            temp_dir: 정리할 임시 디렉토리 경로
        """
        # 임시 폴더를 삭제하기 전, 폴더 내 파일을 사용 중일 수 있는 모든 자식 ffmpeg 프로세스를 먼저 종료
        self._terminate_child_ffmpeg_processes()

        # 파일 시스템의 I/O 지연이나 파일 잠금 문제에 대응하기 위해 최대 10번까지 삭제를 재시도
        for i in range(10):
            try:
                shutil.rmtree(temp_dir) # 디렉토리와 그 안의 모든 내용을 재귀적으로 삭제
                logging.info(LOG_MESSAGES['temp_dir_cleaned'].format(temp_dir))
                return # 삭제에 성공하면 함수를 즉시 종료
            except (PermissionError, OSError) as e:
                # 삭제 실패 시 경고를 로깅하고 1초 대기 후 재시도
                logging.warning(f"Attempt {i+1} to remove '{temp_dir}' failed: {e}. Retrying...")
                time.sleep(1)

        # 모든 재시도 후에도 삭제에 실패한 경우, 사용자에게 수동 삭제를 요청하는 메시지를 표시
        error_msg = f"Failed to clean up temporary folder: {temp_dir}.\n\nPlease remove it manually."
        logging.error(error_msg)
        self.root.after(0, lambda: messagebox.showwarning("Cleanup Failed", error_msg))

    def _normalize_seconds_map(self, seconds_map: Dict[int, Any]) -> Dict[int, Any]:
        """
        타임스탬프 기반 딕셔너리의 키(초)가 0부터 시작하도록 정규화.

        M2TS/TS와 같은 방송용 스트림은 파일의 시작 타임스탬프가 0이 아닌 큰 값을 가질 수 있음 (PTS 오프셋).
        이 오프셋을 처리하지 않으면 샘플 추출 시 영상 길이를 벗어나는 잘못된 시간으로 접근하여 오류가 발생할 수 있음.

        Args:
            seconds_map: 정규화할 초 단위 딕셔너리

        Returns:
            Dict[int, Any]: 정규화된 딕셔너리 (키가 0부터 시작)
        """
        if not seconds_map: # 비어있는 딕셔너리는 그대로 반환
            return {}

        try:
            int_keys = [int(k) for k in seconds_map.keys()] # 모든 키를 정수로 변환
            min_time_offset = min(int_keys) # 가장 작은 타임스탬프(오프셋)를 찾음

            # 1초를 초과하는 큰 오프셋이 있을 때만 정규화를 수행
            if min_time_offset > 1:
                logging.info(LOG_MESSAGES['time_offset_detected'].format(min_time_offset))
                # 모든 키에서 오프셋을 빼서 0부터 시작하도록 조정
                normalized_map = {int(k) - min_time_offset: v for k, v in seconds_map.items()}
                return normalized_map
            else:
                # 큰 오프셋이 없는 경우, 키 타입만 정수로 변환하여 반환
                return {int(k): v for k, v in seconds_map.items()}

        except (ValueError, TypeError) as e:
            logging.error(LOG_MESSAGES['seconds_map_normalization_error'].format(e))
            return seconds_map # 예외 발생 시 원본 딕셔너리를 안전하게 반환

    def _find_best_window_from_map(self, time_interval_map: Dict[int, int], sample_duration: int, find_largest: bool) -> float:
        """
        1초 단위 데이터 맵에 슬라이딩 윈도우를 적용하여 최적 구간의 '중심 시간'을 계산.

        Args:
            time_interval_map: 키가 초 단위 인덱스인 데이터 맵.
            sample_duration: 샘플의 지속 시간 (초).
            find_largest: True이면 데이터 합이 가장 큰 구간을, False이면 가장 작은 구간을 찾음.

        Returns:
            float: 최적 구간의 중심 시간 (초) 또는 None.
        """
        if not time_interval_map:
            return None

        # 샘플 지속 시간을 초 단위 윈도우 크기로 변환
        window_size = int(sample_duration)
        
        # 시간 순서대로 키(초 인덱스)를 정렬
        sorted_keys = sorted(time_interval_map.keys())

        # 데이터 포인트 수가 윈도우 크기보다 작으면 분석을 수행하지 않음
        if len(sorted_keys) < window_size:
            logging.warning("Not enough data points to form a full sliding window.")
            return None

        # 초기 윈도우의 합을 계산
        initial_window_keys = sorted_keys[:window_size]
        current_sum = sum(time_interval_map.get(k, 0) for k in initial_window_keys)
        
        best_sum = current_sum
        best_start_key = sorted_keys[0]

        # 윈도우를 한 칸씩 이동하며 합을 효율적으로 갱신
        for i in range(1, len(sorted_keys) - window_size + 1):
            # 이전 윈도우의 첫 요소를 빼고, 새 윈도우의 마지막 요소를 더함
            key_to_remove = sorted_keys[i - 1]
            key_to_add = sorted_keys[i + window_size - 1]
            
            current_sum = current_sum - time_interval_map.get(key_to_remove, 0) + time_interval_map.get(key_to_add, 0)

            # 최적의 합(최대 또는 최소)을 찾음
            if find_largest:
                if current_sum > best_sum:
                    best_sum = current_sum
                    best_start_key = sorted_keys[i]
            else: # find smallest
                if current_sum < best_sum:
                    best_sum = current_sum
                    best_start_key = sorted_keys[i]
        
        # 찾은 최적 구간의 시작점을 기준으로 '중심 시간'을 계산하여 반환
        start_time_sec = float(best_start_key)
        center_time_sec = start_time_sec + (sample_duration / 2.0)
        return center_time_sec

    def _calculate_start_time(self, filepath, target_second, sample_duration):
        """
        분석을 통해 찾은 목표 시간(target_second)을 중심으로 샘플의 시작 시간을 계산.

        장면 분석을 통해 찾은 목표 시간을 중심으로 샘플 구간의 시작 시간을 계산함.
        샘플 구간이 비디오의 시작이나 끝을 벗어나지 않도록 경계를 조정하여 유효한 샘플 구간을 보장함.

        Args:
            filepath: 비디오 파일 경로
            target_second: 분석을 통해 찾은 목표 시간 (초)
            sample_duration: 샘플 지속 시간 (초)

        Returns:
            float: 조정된 샘플 시작 시간 (초)
        """
        # 목표 시간을 중심으로 샘플이 위치하도록 시작 시간을 계산
        start_time = max(0, target_second - (sample_duration / 2))
        
        # 계산된 샘플 구간이 비디오의 끝을 넘어가지 않도록 조정
        total_duration = self.get_video_duration(filepath)
        if total_duration is not None and start_time + sample_duration > total_duration:
            start_time = max(0, total_duration - sample_duration)
            
        return start_time

    def _save_debug_analysis_json(self, seconds_map: Dict[int, int], find_largest: bool, mode_prefix: str, iqr_info: Dict = None):
        """
        [테스트 전용] 분석 결과를 사람이 읽기 좋은 디버깅용 JSON 파일로 저장.

        장면 분석 결과를 디버깅 목적으로 JSON 파일로 저장함.
        enable_debug_logging 플래그가 True일 때만 동작하며, 분석 알고리즘의 동작을 검증하고 개선하는 데 사용됨.

        Args:
            seconds_map: 초 단위 장면 복잡도 맵
            find_largest: 최대값을 찾는 모드 여부
            mode_prefix: 파일명에 사용할 모드 접두사
            iqr_info: IQR 처리 정보 딕셔너리 (선택사항)
        """
        if not APP_CONFIG['enable_debug_logging']: # 디버그 로깅이 비활성화되어 있으면 즉시 종료
            return

        if not seconds_map: # 저장할 데이터가 없으면 종료
            return

        filename = f"debug_{mode_prefix}_analysis_report.json"
        try:
            # --- 데이터 가공 시작 ---
            # 1. 통계 정보 계산
            all_sizes = list(seconds_map.values())
            average_size = sum(all_sizes) / len(all_sizes) if all_sizes else 0
            max_size = max(all_sizes) if all_sizes else 0
            min_size = min(all_sizes) if all_sizes else 0

            # 2. 사람이 읽기 좋은 형태로 데이터 변환
            readable_data = []
            sorted_keys = sorted(seconds_map.keys())

            for key in sorted_keys:
                size_bytes = seconds_map[key]
                
                # 시간 포맷팅 (HH:MM:SS)
                total_seconds = float(key)
                hours = int(total_seconds // 3600)
                minutes = int((total_seconds % 3600) // 60)
                seconds = int(total_seconds % 60)
                timestamp = f"{hours:02}:{minutes:02}:{seconds:02}"

                # 크기 포맷팅 (KB 또는 MB)
                if size_bytes > 1024 * 1024:
                    size_formatted = f"{size_bytes / (1024*1024):.2f} MB"
                else:
                    size_formatted = f"{size_bytes / 1024:.2f} KB"
                
                # 상대적 복잡도 계산
                complexity_vs_avg = ((size_bytes / average_size) - 1) * 100 if average_size > 0 else 0

                readable_data.append({
                    "timestamp": timestamp,
                    "interval_start_sec": total_seconds,
                    "size_bytes": size_bytes,
                    "size_formatted": size_formatted,
                    "complexity_vs_avg_percent": f"{complexity_vs_avg:+.2f}%"
                })
            
            # --- JSON 구조 생성 ---
            debug_data = {
                "analysis_summary": {
                    "mode": mode_prefix,
                    "target": "Most Complex (Largest Size)" if find_largest else "Least Complex (Smallest Size)",
                    "total_intervals_analyzed": len(seconds_map),
                    "analysis_timestamp": datetime.now().isoformat(),
                    "statistics": {
                        "average_interval_size": f"{average_size / 1024:.2f} KB",
                        "max_interval_size": f"{max_size / 1024:.2f} KB",
                        "min_interval_size": f"{min_size / 1024:.2f} KB"
                    }
                },
                "iqr_processing": iqr_info if iqr_info else {"applied": False, "reason": "Not performed"},
                "detailed_analysis_data": readable_data
            }
            
            # --- 파일 저장 ---
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(debug_data, f, indent=4, ensure_ascii=False)
            logging.info(f"Saved readable analysis debug report to {filename}")

        except Exception as e:
            logging.error(f"Failed to save readable debug JSON to {filename}: {e}")

    def _toggle_controls_state(self, new_state):
        """
        최적화 작업 중/후에 UI 컨트롤들의 상태를 일괄적으로 변경.

        최적화 작업의 시작과 종료 시 UI 컨트롤들의 활성화/비활성화 상태를 일괄적으로 관리함.
        비활성화 시에는 원래 상태를 저장하고, 복원 시에는 저장된 상태로 되돌림.

        Args:
            new_state: 설정할 새로운 상태 (tk.DISABLED 또는 tk.NORMAL)
        """
        if new_state == tk.DISABLED: # UI 컨트롤을 비활성화할 경우
            self.original_widget_states.clear() # 이전에 저장된 위젯 상태를 모두 지움
            
            # 비활성화할 모든 컨트롤을 순회
            for widget in self.controls_to_disable:
                try:
                    # 비활성화 전 원래 상태를 저장
                    self.original_widget_states[widget] = widget.cget('state')
                    widget.config(state=tk.DISABLED) # 위젯을 비활성화 상태로 변경
                except tk.TclError:
                    pass # 위젯이 이미 파괴된 경우 등 예외 상황을 무시
        else: # UI 컨트롤을 원래 상태로 복원할 경우
            # 저장된 원래 상태로 복원하기 위해 모든 컨트롤을 순회
            for widget in self.controls_to_disable:
                try:
                    original_state = self.original_widget_states.get(widget) # 저장된 상태를 딕셔너리에서 가져옴
                    if original_state:
                        # 저장해둔 원래 상태로 복원
                        widget.config(state=original_state)
                except tk.TclError:
                    pass
            
            # 전체 컨트롤 상태 복원 후, 특정 UI 모드에 맞게 다시 조정
            self.toggle_sample_mode_ui()  # 샘플 모드에 따라 UI를 다시 조정
            self._toggle_optimization_mode_ui()  # 최적화 모드에 따라 UI 다시 조정

            # 미리보기 작업 중이 아닐 때만 'Start' 버튼을 최종적으로 활성화
            if not self.is_previewing:
                self.start_button.config(state=tk.NORMAL)

    def _on_closing(self):
        """
        프로그램 종료 시 호출되는 메서드.
        
        사용자가 윈도우의 X 버튼을 클릭하거나 프로그램을 종료할 때 호출되며,
        세션 정보를 로깅하고 안전하게 프로그램을 종료함.
        """
        try:
            # 세션 지속 시간 계산
            session_duration = time.time() - self.start_time
            
            # 프로그램 종료 로깅
            logging.info(LOG_MESSAGES['program_shutdown'].format(session_duration))
            logging.info(LOG_MESSAGES['program_exit'])
            
            # 진행 중인 작업이 있다면 정리
            if hasattr(self, 'pool') and self.pool:
                try:
                    logging.info("Terminating worker pool...")
                    self.pool.terminate()
                    self.pool.join()
                    logging.info("Worker pool terminated successfully")
                except Exception as e:
                    logging.warning(f"Error terminating worker pool: {e}")
            
            # 임시 파일 정리 로깅
            logging.info("Cleaning up temporary resources...")
            
        except Exception as e:
            logging.error(f"Error during program shutdown: {e}")
        finally:
            # 윈도우 종료
            self.root.destroy()



# ==============================================================================
# 7. 애플리케이션 실행
# ==============================================================================
# 애플리케이션 실행 진입점
if __name__ == "__main__":
    # Windows에서 PyInstaller 등으로 실행 파일을 만들었을 때,
    # 멀티프로세싱이 올바르게 동작하기 위해 필요한 호출
    multiprocessing.freeze_support()

    # Tkinter GUI의 가장 기본이 되는 메인 윈도우(루트)를 생성
    root = tk.Tk()
    # VideoOptimizerApp 클래스의 인스턴스를 생성하고, 루트 윈도우를 전달하여 앱을 구성 및 초기화
    app = VideoOptimizerApp(root)

    # GUI 이벤트 루프를 시작하여 창을 화면에 표시하고, 사용자의 상호작용(클릭, 키보드 입력 등)을 기다림
    root.mainloop()
