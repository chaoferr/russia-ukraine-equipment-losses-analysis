import numpy as np
import scipy.stats as stats

def two_poisson_conditional_test(x_values, y_values):
    """
    两独立 Poisson 条件检验 (Two-independent Poisson Conditional Test)
    针对装备记录：假设 X(官方战报) ~ Poi(lambda_1), Y(影像记录) ~ Poi(lambda_2)
    检验 H0: lambda_1 = lambda_2 / H1: lambda_1 != lambda_2
    
    返回：P-value
    """
    if len(x_values) == 0 or len(y_values) == 0:
        return 1.0
        
    X_sum = int(np.sum(x_values))
    Y_sum = int(np.sum(y_values))
    k = X_sum + Y_sum
    
    if k == 0:
        return 1.0
        
    # 二项分布精确检验。在 H0 成立时，X_sum 给定 X+Y=k 服从 Binomial(k, 0.5)
    p_value = stats.binomtest(X_sum, n=k, p=0.5, alternative='two-sided').pvalue
    return p_value
