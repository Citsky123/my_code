import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy import stats
import seaborn as sns
import tkinter as tk
from tkinter import simpledialog, filedialog
import os

# 配置中文显示
plt.rcParams["font.family"] = ["SimHei", "Microsoft YaHei", "Arial Unicode MS"]
plt.rcParams["axes.unicode_minus"] = False  # 解决负号显示问题


class CPKAnalyzer:
    """CPK过程能力分析器"""
    def __init__(self, data, usl, lsl):
        self.data = np.array(data)
        self.usl = usl  # 上规格限
        self.lsl = lsl  # 下规格限
        self.mu = np.mean(data)  # 过程均值
        self.sigma = np.std(data, ddof=1)  # 样本标准差
        self.cpk = self._calculate_cpk()
        self.target = (usl + lsl) / 2  # 规格中心

    def _calculate_cpk(self):
        """计算CPK值"""
        if self.sigma == 0:
            return float('inf')
        
        cpu = (self.usl - self.mu) / (3 * self.sigma)  # 上侧能力指数
        cpl = (self.mu - self.lsl) / (3 * self.sigma)  # 下侧能力指数
        return min(cpu, cpl)

    def normality_test(self, alpha=0.05):
        """正态性检验（Shapiro-Wilk方法）"""
        stat, p = stats.shapiro(self.data)
        is_normal = p > alpha
        return {
            "统计量": round(stat, 4),
            "p值": round(p, 4),
            "结论": "符合正态分布" if is_normal else "不符合正态分布"
        }

    def plot_histogram(self):
        """绘制直方图与正态分布曲线"""
        plt.figure(figsize=(10, 6))
        
        # 直方图
        sns.histplot(self.data, kde=False, bins=15, 
                   color='skyblue', edgecolor='black', label='数据分布')
        
        # 正态分布曲线
        x_range = np.linspace(min(self.data), max(self.data), 100)
        normal_curve = stats.norm.pdf(x_range, self.mu, self.sigma)
        plt.plot(x_range, normal_curve * len(self.data) * 0.8, 
                 'r-', label='拟合正态分布')
        
        # 标注规格限和均值
        plt.axvline(self.lsl, color='green', linestyle='--', label=f'LSL={self.lsl}')
        plt.axvline(self.usl, color='red', linestyle='--', label=f'USL={self.usl}')
        plt.axvline(self.mu, color='purple', linestyle='-', label=f'均值μ={self.mu:.4f}')
        
        plt.title('数据分布与正态拟合')
        plt.xlabel('测量值')
        plt.ylabel('频数')
        plt.legend()
        plt.grid(alpha=0.3)
        plt.tight_layout()
        plt.show()

    def plot_control_chart(self, subgroup_size=5):
        """绘制均值-极差控制图"""
        n = len(self.data) // subgroup_size * subgroup_size
        if n < 2 * subgroup_size:
            print("⚠️ 数据量不足，无法生成控制图（至少需要10个子组）")
            return

        subgroups = self.data[:n].reshape(-1, subgroup_size)
        x_bar = np.mean(subgroups, axis=1)  # 组均值
        r = np.ptp(subgroups, axis=1)       # 组极差

        x_bar_bar = np.mean(x_bar)  # 总均值
        r_bar = np.mean(r)          # 平均极差

        # 控制限系数（子组大小2-6）
        coeff = {2: (1.88, 0, 3.27), 3: (1.02, 0, 2.58),
                 4: (0.73, 0, 2.28), 5: (0.58, 0, 2.11), 6: (0.48, 0, 2.00)}
        a2, d3, d4 = coeff.get(subgroup_size, (0.58, 0, 2.11))

        # 计算控制限
        x_ucl, x_lcl = x_bar_bar + a2*r_bar, x_bar_bar - a2*r_bar
        r_ucl, r_lcl = d4*r_bar, d3*r_bar

        # 绘图
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10), sharex=True)
        
        # 均值图
        ax1.plot(x_bar, 'bo-', markersize=5, label='组均值')
        ax1.axhline(x_bar_bar, color='black', label='中心线')
        ax1.axhline(x_ucl, color='red', linestyle='--', label=f'UCL={x_ucl:.4f}')
        ax1.axhline(x_lcl, color='red', linestyle='--', label=f'LCL={x_lcl:.4f}')
        ax1.set_title(f'均值控制图（子组大小={subgroup_size}）')
        ax1.set_ylabel('均值')
        ax1.legend()
        ax1.grid(alpha=0.3)
        
        # 极差图
        ax2.plot(r, 'ro-', markersize=5, label='组极差')
        ax2.axhline(r_bar, color='black', label='中心线')
        ax2.axhline(r_ucl, color='red', linestyle='--', label=f'UCL={r_ucl:.4f}')
        ax2.axhline(r_lcl, color='red', linestyle='--', label=f'LCL={r_lcl:.4f}')
        ax2.set_title(f'极差控制图（子组大小={subgroup_size}）')
        ax2.set_xlabel('组号')
        ax2.set_ylabel('极差')
        ax2.legend()
        ax2.grid(alpha=0.3)
        
        plt.tight_layout()
        plt.show()

    def plot_cpk_analysis(self):
        """绘制CPK分析图"""
        plt.figure(figsize=(12, 6))
        
        # 绘制规格限和过程范围
        plt.axvline(self.lsl, color='green', linewidth=2, label=f'LSL={self.lsl}')
        plt.axvline(self.usl, color='red', linewidth=2, label=f'USL={self.usl}')
        plt.axvline(self.target, color='gray', linestyle='-.', label=f'规格中心')
        
        # 过程均值和波动范围
        plt.axvline(self.mu, color='purple', linewidth=2, label=f'均值μ={self.mu:.4f}')
        plt.axvline(self.mu-3*self.sigma, color='blue', linestyle='--', label=f'μ-3σ')
        plt.axvline(self.mu+3*self.sigma, color='blue', linestyle='--', label=f'μ+3σ')
        
        # 标注CPK值
        plt.text(0.05, 0.95, f'CPK={self.cpk:.4f}', 
                 transform=plt.gca().transAxes,
                 bbox=dict(facecolor='yellow', alpha=0.5))
        
        # 数据点分布
        plt.scatter(self.data, np.zeros_like(self.data), alpha=0.5, color='gray')
        
        plt.title('CPK过程能力分析')
        plt.xlabel('测量值')
        plt.yticks([])
        plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))
        plt.grid(alpha=0.3, axis='x')
        plt.tight_layout()
        plt.show()

    def print_report(self):
        """打印分析报告"""
        print("\n" + "="*50)
        print("          CPK过程能力分析报告          ")
        print("="*50)
        print(f"数据量: {len(self.data)} 个")
        print(f"过程均值: {self.mu:.4f}")
        print(f"标准差: {self.sigma:.4f}")
        print(f"上规格限(USL): {self.usl}")
        print(f"下规格限(LSL): {self.lsl}")
        print(f"CPK值: {self.cpk:.4f}")
        
        # 正态性检验结果
        norm_result = self.normality_test()
        print("\n正态性检验:")
        print(f"  统计量: {norm_result['统计量']}")
        print(f"  p值: {norm_result['p值']}")
        print(f"  {norm_result['结论']}")
        
        # CPK评级
        if self.cpk >= 1.33:
            rating = "充足 (过程能力良好)"
        elif self.cpk >= 1.0:
            rating = "尚可 (需加强监控)"
        elif self.cpk >= 0.67:
            rating = "不足 (需立即改进)"
        else:
            rating = "严重不足 (过程失控)"
        print(f"\n评级: {rating}")
        print("="*50 + "\n")


def import_data():
    """从Excel导入数据"""
    root = tk.Tk()
    root.withdraw()  # 隐藏窗口
    
    # 选择文件
    file_path = filedialog.askopenfilename(
        title="选择Excel文件",
        filetypes=[("Excel文件", "*.xlsx;*.xls")]
    )
    if not file_path:
        print("未选择文件，程序退出")
        exit()
    
    # 读取数据
    try:
        df = pd.read_excel(file_path)
        print(f"已导入: {os.path.basename(file_path)}")
        print(f"数据规模: {df.shape[0]}行, {df.shape[1]}列")
        
        # 选择数据列
        print("\n数据列信息:")
        for i, col in enumerate(df.columns):
            print(f"  索引 {i}: {col}")
        
        while True:
            col_input = input("请输入数据所在列的索引或名称: ").strip()
            try:
                # 按索引读取
                data = df.iloc[:, int(col_input)].dropna().values
                break
            except ValueError:
                # 按名称读取
                if col_input in df.columns:
                    data = df[col_input].dropna().values
                    break
                else:
                    print(f"错误: 未找到列 '{col_input}'")
        
        return data
    except Exception as e:
        print(f"导入失败: {str(e)}")
        exit()


def get_spec_limits():
    """获取规格上下限"""
    root = tk.Tk()
    root.withdraw()
    
    while True:
        try:
            usl = simpledialog.askfloat("输入", "请输入上规格限(USL):")
            lsl = simpledialog.askfloat("输入", "请输入下规格限(LSL):")
            
            if usl is None or lsl is None:
                print("未输入规格限，程序退出")
                exit()
            if usl <= lsl:
                print("错误: 上规格限必须大于下规格限")
                continue
            return usl, lsl
        except Exception as e:
            print(f"输入错误: {str(e)}")


if __name__ == "__main__":
    print("="*50)
    print("        CPK分析工具 (支持Excel数据导入)        ")
    print("="*50)
    
    # 1. 导入数据
    data = import_data()
    
    # 2. 输入规格限
    usl, lsl = get_spec_limits()
    
    # 3. 分析数据
    analyzer = CPKAnalyzer(data, usl, lsl)
    analyzer.print_report()
    
    # 4. 生成图表
    analyzer.plot_histogram()
    
    # 控制图选项
    while True:
        ans = input("是否生成控制图? (y/n): ").lower()
        if ans in ['y', 'yes']:
            while True:
                try:
                    sub_size = int(input("请输入子组大小(2-6): "))
                    if 2 <= sub_size <=6:
                        analyzer.plot_control_chart(sub_size)
                        break
                    else:
                        print("子组大小必须在2-6之间")
                except ValueError:
                    print("请输入整数")
            break
        elif ans in ['n', 'no']:
            break
        else:
            print("请输入y或n")
    
    analyzer.plot_cpk_analysis()
    print("分析完成!")
