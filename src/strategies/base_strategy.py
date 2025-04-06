from abc import ABC, abstractmethod
import pandas as pd
import numpy as np
from typing import Dict, Any, List, ClassVar, Optional

class BaseStrategy(ABC):
    """트레이딩 전략의 기본 인터페이스"""
    
    # 전략 메타데이터 (각 서브클래스에서 덮어씀)
    STRATEGY_CODE: ClassVar[str] = ""
    STRATEGY_NAME: ClassVar[str] = ""
    STRATEGY_DESCRIPTION: ClassVar[str] = ""
    
    @classmethod
    def register_strategy_params(cls) -> List[Dict[str, Any]]:
        """
        전략 파라미터 등록 (자동 문서화 및 CLI에서 사용)
        기본적으로 빈 목록 반환
        """
        return []
    
    @abstractmethod
    def apply(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        전략 로직을 적용하고 신호를 생성
        
        Parameters:
            df (pd.DataFrame): OHLCV 데이터
            
        Returns:
            pd.DataFrame: 신호가 추가된 데이터프레임
        """
        pass
    
    def generate_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        백테스팅을 위한 거래 신호 생성
        
        Parameters:
            df (pd.DataFrame): 이미 apply() 메서드로 지표가 계산된 데이터프레임
            
        Returns:
            pd.DataFrame: 거래 신호가 있는 데이터프레임
        """
        # 신호가 포함된 행만 필터링
        # position 값은 signal의 변화를 나타냄: 1(매수 진입), -1(매도 진입), 0(유지)
        signal_df = df[df['position'] != 0].copy()
        
        # 결과 데이터프레임 준비
        result_df = pd.DataFrame(index=signal_df.index)
        
        # 매수/매도 신호 설정
        result_df['type'] = np.where(signal_df['position'] > 0, 'buy', 'sell')
        result_df['ratio'] = 1.0  # 100% 투자/청산
        
        return result_df
    
    def validate_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        데이터 유효성 검사 및 전처리
        
        Parameters:
            df (pd.DataFrame): 검증할 OHLCV 데이터
            
        Returns:
            pd.DataFrame: 검증된 데이터프레임
            
        Raises:
            ValueError: 데이터가 불충분한 경우
        """
        # 데이터 충분성 검사
        min_required_rows = self.get_min_required_rows()
        if len(df) < min_required_rows:
            # raise ValueError(f"전략 적용에 최소 {min_required_rows}개 행이 필요합니다. 현재: {len(df)}")
            print(f"\n⚠️ 경고: 전략 적용에 최소 {min_required_rows}개 행이 필요합니다. 현재: {len(df)}")
            print("다음 옵션을 시도해보세요:")
            print(f"  1. 더 긴 기간 사용: -p 3m 또는 -p 6m")
            print(f"  2. 더 짧은 시간 간격 사용: -v minute60 또는 -v minute30")
            print(f"  3. 더 많은 데이터가 필요한 전략이므로 다른 전략을 시도")
        return df
    
    def get_min_required_rows(self) -> int:
        """
        전략에 필요한 최소 데이터 행 수 반환
        
        Returns:
            int: 최소 필요 행 수
        """
        return 30  # 기본값, 하위 클래스에서 재정의 필요
    
    @property
    @abstractmethod
    def name(self) -> str:
        """전략 이름"""
        pass
    
    @property
    @abstractmethod
    def params(self) -> Dict[str, Any]:
        """전략 파라미터"""
        pass 