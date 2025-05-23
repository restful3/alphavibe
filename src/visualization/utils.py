"""
시각화 유틸리티 모듈

차트 시각화에 사용되는 다양한 유틸리티 함수를 제공합니다.
"""
import os
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.figure import Figure
from datetime import datetime
import pandas as pd
from typing import Tuple, List, Optional, Dict, Any

from src.utils.file_utils import ensure_directory
from src.utils.config import CHART_SAVE_PATH

def setup_chart_dir(chart_dir: str = CHART_SAVE_PATH) -> str:
    """
    차트 저장 디렉토리 설정 및 생성
    
    Parameters:
        chart_dir (str): 차트 저장 경로 (기본값: CHART_SAVE_PATH)
        
    Returns:
        str: 생성된 차트 디렉토리 경로
    """
    # 디렉토리 생성 및 경로 반환
    return ensure_directory(chart_dir)

def format_date_axis(ax):
    """
    날짜 축 포맷 설정
    
    Parameters:
        ax: matplotlib 축 객체
    """
    # 날짜 포맷터 설정 - 연도 없이 월-일만 표시
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))
    
    # 날짜 라벨 간격 설정 - 데이터 수에 따라 적응적으로 조절
    x_ticks = ax.get_xticks()
    if len(x_ticks) > 10:
        # 데이터가 많으면 로케이터를 조정하여 라벨 수 줄이기
        ax.xaxis.set_major_locator(mdates.DayLocator(interval=max(1, len(x_ticks) // 6)))
    
    # 그리드 설정
    ax.grid(True, alpha=0.3)

def format_price_axis(ax):
    """
    가격 축 포맷 설정
    
    Parameters:
        ax: matplotlib 축 객체
    """
    # 천 단위 콤마 포맷터 설정
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, loc: "{:,}".format(int(x))))
    
    # 그리드 설정
    ax.grid(True, alpha=0.3)

def save_chart(fig, file_name, chart_dir=CHART_SAVE_PATH, dpi=300) -> str:
    """
    차트 저장
    
    Parameters:
        fig: matplotlib 그림 객체
        file_name: 파일명
        chart_dir: 차트 저장 디렉토리
        dpi: 해상도
        
    Returns:
        str: 저장된 파일의 전체 경로
    """
    # 디렉토리 확인 및 생성
    chart_path = ensure_directory(chart_dir)
    
    # 파일 전체 경로
    full_path = os.path.join(chart_path, file_name)
    
    # 그림 저장 - bbox_inches='tight' 제거하여 그래프 잘림 방지
    fig.savefig(full_path, dpi=dpi)
    plt.close(fig)
    
    return full_path

def generate_filename(ticker: str, interval: str = "day", period: str = "1m", suffix: str = "", strategy: str = "", initial_capital: float = None, **kwargs) -> str:
    """
    차트 파일명 생성
    
    Parameters:
        ticker: 티커 심볼
        interval: 간격 (day, hour, minute)
        period: 기간 (1d, 5d, 1m, 3m, 6m, 1y)
        suffix: 파일명 접미사
        strategy: 전략 이름 (백테스팅에만 사용)
        initial_capital: 초기 자본금 (백테스팅에만 사용)
        **kwargs: 추가 매개변수
        
    Returns:
        str: 생성된 파일명
    """
    # 현재 시간
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # 접미사가 있으면 언더스코어 추가
    suffix = f"_{suffix}" if suffix else ""
    
    # 전략 이름이 있으면 추가
    strategy_str = f"_{strategy}" if strategy else ""
    
    # 초기 자본금이 있으면 추가 (단위: 만원)
    capital_str = f"_{int(initial_capital/10000)}만원" if initial_capital else ""
    
    # 파일명 생성
    filename = f"{ticker}_{interval}_{period}{strategy_str}{capital_str}{suffix}_{timestamp}.png"
    
    return filename

def apply_mpl_styles():
    """기본 matplotlib 스타일 적용"""
    # Matplotlib 스타일 설정
    plt.style.use('seaborn-darkgrid')
    
    # 한글 폰트 문제 해결 (필요한 경우)
    plt.rcParams['axes.unicode_minus'] = False

def detect_chart_type(df: pd.DataFrame) -> str:
    """
    데이터프레임의 컬럼을 기반으로 차트 타입 감지
    
    Parameters:
        df: 데이터프레임
        
    Returns:
        str: 차트 타입 ('candlestick', 'ohlc', 'line')
    """
    required_cols = {
        'candlestick': ['Open', 'High', 'Low', 'Close'],
        'ohlc': ['Open', 'High', 'Low', 'Close'],
        'line': ['Close']
    }
    
    # 캔들스틱 또는 OHLC 차트 필요 컬럼 확인
    if all(col in df.columns for col in required_cols['candlestick']):
        # 가장 좋은 데이터가 있으면 캔들스틱 반환
        return 'candlestick'
    # 종가만 있으면 라인 차트
    elif 'Close' in df.columns:
        return 'line'
    # 기본값
    else:
        return 'line'
