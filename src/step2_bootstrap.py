import numpy as np
import scipy.stats as stats

def moving_block_bootstrap(data, block_size, n_bootstraps=1000):
    """执行 Moving Block Bootstrap 针对存在时序自相关的装备损失序列"""
    n = len(data)
    boot_means = np.zeros(n_bootstraps)
    
    # 生成滑动区块
    blocks = [data[i:i + block_size] for i in range(n - block_size + 1)]
    num_blocks = len(blocks)
    
    if num_blocks == 0:
        blocks = [data]
        num_blocks = 1
        
    # 重抽样
    for i in range(n_bootstraps):
        idx = np.random.randint(0, num_blocks, size=int(np.ceil(n / block_size)))
        boot_sample = np.concatenate([blocks[j] for j in idx])[:n]
        boot_means[i] = np.mean(boot_sample)
        
    return boot_means

def bootstrap_bca_interval(data, alpha=0.05, block_size=7, n_bootstraps=1000):
    """
    计算基于 MBB 的 BCa 区间 (Bias-Corrected and Accelerated)
    处理时间序列偏误极其有效
    """
    data = np.asarray(data)
    if len(data) == 0:
        return (0, 0)
        
    stat_orig = np.mean(data)
    
    # 生成 MBB 分布
    boot_stats = moving_block_bootstrap(data, block_size, n_bootstraps)
    
    # bias-correction (z0)
    proportion_less = np.sum(boot_stats < stat_orig) / n_bootstraps
    proportion_less = np.clip(proportion_less, 1e-6, 1 - 1e-6)
    z0 = stats.norm.ppf(proportion_less)
    
    # acceleration (a) using jackknife
    n = len(data)
    if n <= 1:
        return (stat_orig, stat_orig)
        
    try:
        jackknife_stats = np.zeros(n)
        for i in range(n):
            jack_sample = np.delete(data, i)
            jackknife_stats[i] = np.mean(jack_sample)
        mean_jack = np.mean(jackknife_stats)
        
        num = np.sum((mean_jack - jackknife_stats)**3)
        den = 6.0 * (np.sum((mean_jack - jackknife_stats)**2))**1.5
        a = num / den if den != 0 else 0
    except:
        a = 0

    z_alpha_low = stats.norm.ppf(alpha / 2)
    z_alpha_high = stats.norm.ppf(1 - alpha / 2)
    
    # 计算 BCa 的分位数位置
    p_low = stats.norm.cdf(z0 + (z0 + z_alpha_low) / (1 - a * (z0 + z_alpha_low)))
    p_high = stats.norm.cdf(z0 + (z0 + z_alpha_high) / (1 - a * (z0 + z_alpha_high)))
    
    ci_low = np.percentile(boot_stats, p_low * 100)
    ci_high = np.percentile(boot_stats, p_high * 100)
    
    return (ci_low, ci_high)
