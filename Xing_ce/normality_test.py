import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
from scipy.stats import shapiro, kstest, anderson

# 设置中文显示
plt.rcParams["font.family"] = ["SimHei", "WenQuanYi Micro Hei", "Heiti TC"]
plt.rcParams["axes.unicode_minus"] = False

def normality_test(data, alpha=0.05):
    """
    对数据进行多种正态性检验
    :param data: 待检验的数据（数组或列表）
    :param alpha: 显著性水平（默认0.05）
    :return: 检验结果字典
    """
    data = np.array(data)
    results = {}
    
    # 1. Shapiro-Wilk检验
    stat_shapiro, p_shapiro = shapiro(data)
    results["Shapiro-Wilk"] = {
        "统计量": round(stat_shapiro, 4),
        "p值": round(p_shapiro, 4),
        "结论": "符合正态分布" if p_shapiro > alpha else "不符合正态分布"
    }
    
    # 2. Kolmogorov-Smirnov检验（与标准正态分布对比）
    stat_ks, p_ks = kstest(data, 'norm', args=(np.mean(data), np.std(data)))
    results["Kolmogorov-Smirnov"] = {
        "统计量": round(stat_ks, 4),
        "p值": round(p_ks, 4),
        "结论": "符合正态分布" if p_ks > alpha else "不符合正态分布"
    }
    
    # 3. Anderson-Darling检验
    anderson_result = anderson(data, dist='norm')
    # 判断是否符合正态分布（比较统计量与临界值）
    ad_conclusion = "符合正态分布"
    for i in range(len(anderson_result.critical_values)):
        sig_level = 100 * (1 - anderson_result.significance_level[i] / 100)
        if anderson_result.statistic > anderson_result.critical_values[i]:
            ad_conclusion = f"在{sig_level}%置信水平下不符合正态分布"
            break
    results["Anderson-Darling"] = {
        "统计量": round(anderson_result.statistic, 4),
        "临界值": {f"{100 - sl}%": round(cv, 4) 
                  for sl, cv in zip(anderson_result.significance_level, anderson_result.critical_values)},
        "结论": ad_conclusion
    }
    
    return results

def visualize_normality(data):
    """可视化数据分布，辅助判断正态性"""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    
    # 1. 直方图+正态分布曲线
    sns.histplot(data, kde=True, ax=ax1, color='skyblue')
    ax1.set_title('数据直方图与核密度估计')
    ax1.set_xlabel('数值')
    ax1.set_ylabel('频数')
    
    # 2. Q-Q图（比较数据分位数与理论正态分布分位数）
    stats.probplot(data, plot=ax2)
    ax2.set_title('Q-Q图（正态性检验）')
    
    plt.tight_layout()
    plt.show()

# 示例：测试不同分布的数据
if __name__ == "__main__":
    # 生成测试数据
    np.random.seed(42)
    normal_data = np.random.normal(loc=0, scale=1, size=100)  # 正态分布数据
    uniform_data = np.random.uniform(low=-3, high=3, size=100)  # 均匀分布数据（非正态）
    
    # 测试正态分布数据
    print("="*50)
    print("正态分布数据检验结果：")
    normal_results = normality_test(normal_data)
    for test_name, result in normal_results.items():
        print(f"\n{test_name}检验：")
        for key, value in result.items():
            print(f"  {key}：{value}")
    visualize_normality(normal_data)
    
    # 测试非正态分布数据
    print("\n" + "="*50)
    print("均匀分布数据检验结果：")
    uniform_results = normality_test(uniform_data)
    for test_name, result in uniform_results.items():
        print(f"\n{test_name}检验：")
        for key, value in result.items():
            print(f"  {key}：{value}")
    visualize_normality(uniform_data)
    