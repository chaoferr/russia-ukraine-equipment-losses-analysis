import numpy as np
import scipy.stats as stats

def poisson_mle(data):
    """计算单个时间序列下 Poisson 分布率参数的 MLE 点估计"""
    data = np.asarray(data)
    n = len(data)
    if n == 0: 
        return 0.0
    return np.mean(data)

def poisson_intervals(data, alpha=0.05):
    """
    提供泊松参数的估计的 Wald, Score 和 Exact 置信区间 (1-alpha CI)
    返回: wald_ci, score_ci, exact_ci
    """
    data = np.asarray(data)
    n = len(data)
    if n == 0:
        return (0,0), (0,0), (0,0)
        
    S = np.sum(data)
    lambda_hat = S / n
    z = stats.norm.ppf(1 - alpha/2)
    
    # 1. Wald Interval
    se_wald = np.sqrt(lambda_hat / n) if n > 0 else 0
    wald_ci = (lambda_hat - z * se_wald, lambda_hat + z * se_wald)
    
    # 2. Score Interval
    a = 1
    b = -(2 * lambda_hat + z**2 / n)
    c_term = lambda_hat**2
    delta = b**2 - 4 * a * c_term
    if delta >= 0:
        score_low = (-b - np.sqrt(delta)) / 2
        score_high = (-b + np.sqrt(delta)) / 2
    else:
        score_low, score_high = lambda_hat, lambda_hat
    score_ci = (score_low, score_high)
    
    # 3. Exact Interval (基于卡方分布)
    if S == 0:
        exact_low = 0
    else:
        exact_low = stats.chi2.ppf(alpha / 2, 2 * S) / (2 * n)
    exact_high = stats.chi2.ppf(1 - alpha / 2, 2 * (S + 1)) / (2 * n)
    exact_ci = (exact_low, exact_high)
    
    return wald_ci, score_ci, exact_ci
