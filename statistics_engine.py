"""statistics_engine.py - Statistical Analysis Engine"""
import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional, Union
from scipy import stats

class StatisticsEngine:
    """Statistik-Analyse-Engine"""
    
    def __init__(self):
        pass
    
    def descriptive_statistics(self, data: List[Union[int, float]]) -> Dict[str, float]:
        """Berechne deskriptive Statistiken"""
        arr = np.array(data)
        
        return {
            'count': len(arr),
            'mean': float(np.mean(arr)),
            'median': float(np.median(arr)),
            'std': float(np.std(arr)),
            'var': float(np.var(arr)),
            'min': float(np.min(arr)),
            'max': float(np.max(arr)),
            'q25': float(np.percentile(arr, 25)),
            'q75': float(np.percentile(arr, 75)),
            'iqr': float(np.percentile(arr, 75) - np.percentile(arr, 25)),
            'skewness': float(stats.skew(arr)),
            'kurtosis': float(stats.kurtosis(arr))
        }
    
    def correlation_analysis(self, x: List[float], y: List[float]) -> Dict[str, Any]:
        """Berechne Korrelation"""
        pearson_r, pearson_p = stats.pearsonr(x, y)
        spearman_r, spearman_p = stats.spearmanr(x, y)
        
        return {
            'pearson': {
                'coefficient': float(pearson_r),
                'p_value': float(pearson_p),
                'significant': pearson_p < 0.05
            },
            'spearman': {
                'coefficient': float(spearman_r),
                'p_value': float(spearman_p),
                'significant': spearman_p < 0.05
            }
        }
    
    def linear_regression(self, x: List[float], y: List[float]) -> Dict[str, Any]:
        """Führe lineare Regression durch"""
        slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
        
        # Vorhersagen
        predictions = [slope * xi + intercept for xi in x]
        residuals = [yi - pred for yi, pred in zip(y, predictions)]
        
        return {
            'slope': float(slope),
            'intercept': float(intercept),
            'r_squared': float(r_value ** 2),
            'p_value': float(p_value),
            'std_err': float(std_err),
            'equation': f"y = {slope:.4f}x + {intercept:.4f}",
            'predictions': predictions,
            'residuals': residuals
        }
    
    def moving_average(self, data: List[float], window: int = 3) -> List[float]:
        """Berechne gleitenden Durchschnitt"""
        return list(pd.Series(data).rolling(window=window).mean())
    
    def outlier_detection(self, data: List[float], method: str = 'iqr') -> Dict[str, Any]:
        """Erkenne Ausreißer"""
        arr = np.array(data)
        
        if method == 'iqr':
            q1 = np.percentile(arr, 25)
            q3 = np.percentile(arr, 75)
            iqr = q3 - q1
            lower_bound = q1 - 1.5 * iqr
            upper_bound = q3 + 1.5 * iqr
            
            outliers = arr[(arr < lower_bound) | (arr > upper_bound)]
            outlier_indices = np.where((arr < lower_bound) | (arr > upper_bound))[0]
        
        elif method == 'zscore':
            z_scores = np.abs(stats.zscore(arr))
            outliers = arr[z_scores > 3]
            outlier_indices = np.where(z_scores > 3)[0]
        
        return {
            'outliers': outliers.tolist(),
            'outlier_indices': outlier_indices.tolist(),
            'outlier_count': len(outliers),
            'outlier_percentage': (len(outliers) / len(arr)) * 100
        }
    
    def time_series_decomposition(self, data: List[float], period: int = 12) -> Dict[str, List[float]]:
        """Zerlege Zeitreihe (Trend, Saisonalität, Residuen)"""
        from statsmodels.tsa.seasonal import seasonal_decompose
        
        ts = pd.Series(data)
        result = seasonal_decompose(ts, model='additive', period=period)
        
        return {
            'trend': result.trend.tolist(),
            'seasonal': result.seasonal.tolist(),
            'residual': result.resid.tolist()
        }
    
    def hypothesis_test(self, sample1: List[float], sample2: List[float], 
                       test_type: str = 't-test') -> Dict[str, Any]:
        """Führe Hypothesentest durch"""
        if test_type == 't-test':
            statistic, p_value = stats.ttest_ind(sample1, sample2)
            test_name = "Independent t-test"
        elif test_type == 'mann-whitney':
            statistic, p_value = stats.mannwhitneyu(sample1, sample2)
            test_name = "Mann-Whitney U test"
        else:
            raise ValueError(f"Unknown test type: {test_type}")
        
        return {
            'test': test_name,
            'statistic': float(statistic),
            'p_value': float(p_value),
            'significant': p_value < 0.05,
            'alpha': 0.05
        }
