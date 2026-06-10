import tkinter as tk
from tkinter import ttk, messagebox
import random
import time
import math

class XingceHelper:
    def __init__(self, root):
        self.root = root
        self.root.title("XC小助手")
        self.root.geometry("800x600")
        self.root.configure(bg="#f0f0f0")
        
        # 全局变量
        self.start_time = 0
        self.question_count = 0
        self.correct_count = 0
        self.current_question = None
        
        # 创建主界面
        self.create_main_menu()
        
    def create_main_menu(self):
        """创建主菜单界面"""
        # 清空当前界面
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # 标题
        title_label = tk.Label(self.root, text="XC小助手", font=("SimHei", 30, "bold"), bg="#f0f0f0")
        title_label.pack(pady=50)
        
        # 功能按钮框架
        button_frame = tk.Frame(self.root, bg="#f0f0f0")
        button_frame.pack(expand=True)
        
        # 按钮样式
        button_style = {"font": ("SimHei", 14), "width": 20, "height": 2, 
                       "bg": "#4CAF50", "fg": "white", "relief": tk.RAISED,
                       "bd": 3, "cursor": "hand2"}
        
        # 基础计算练习按钮
        calc_btn = tk.Button(button_frame, text="基础计算练习", 
                           command=self.start_calculation, **button_style)
        calc_btn.grid(row=0, column=0, padx=20, pady=20)
        
        # 数字推理训练按钮
        number_btn = tk.Button(button_frame, text="SZTL训练", 
                             command=self.start_number_reasoning,** button_style)
        number_btn.grid(row=0, column=1, padx=20, pady=20)
        
        # 资料分析练习按钮
        data_btn = tk.Button(button_frame, text="ZLFX练习", 
                           command=self.start_data_analysis, **button_style)
        data_btn.grid(row=1, column=0, padx=20, pady=20)
        
        # 关于按钮
        about_btn = tk.Button(button_frame, text="关于", 
                            command=self.show_about,** button_style)
        about_btn.grid(row=1, column=1, padx=20, pady=20)
    
    def start_calculation(self):
        """开始基础计算练习"""
        # 清空当前界面
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # 返回按钮
        back_btn = tk.Button(self.root, text="返回主菜单", command=self.create_main_menu,
                           font=("SimHei", 10), bg="#f44336", fg="white")
        back_btn.pack(anchor=tk.NW, padx=10, pady=10)
        
        # 标题
        title_label = tk.Label(self.root, text=" 基础计算练习", font=("SimHei", 20), bg="#f0f0f0")
        title_label.pack(pady=20)
        
        # 设置区域
        settings_frame = tk.Frame(self.root, bg="#f0f0f0")
        settings_frame.pack(pady=10)
        
        tk.Label(settings_frame, text="题目数量:", font=("SimHei", 12), bg="#f0f0f0").grid(row=0, column=0, padx=5)
        self.question_num = tk.StringVar(value="10")
        question_entry = tk.Entry(settings_frame, textvariable=self.question_num, width=5, font=("SimHei", 12))
        question_entry.grid(row=0, column=1, padx=5)
        
        tk.Label(settings_frame, text="难度:", font=("SimHei", 12), bg="#f0f0f0").grid(row=0, column=2, padx=5)
        self.difficulty = tk.StringVar(value="中等")
        difficulty_menu = ttk.Combobox(settings_frame, textvariable=self.difficulty, 
                                      values=["简单", "中等", "困难"], width=8, font=("SimHei", 12))
        difficulty_menu.grid(row=0, column=3, padx=5)
        
        start_btn = tk.Button(settings_frame, text="开始练习", command=self.init_calculation,
                            font=("SimHei", 12), bg="#4CAF50", fg="white")
        start_btn.grid(row=0, column=4, padx=10)
        
        # 题目和结果显示区域
        self.calc_frame = tk.Frame(self.root, bg="#f0f0f0")
        self.calc_frame.pack(expand=True)
        
    def init_calculation(self):
        """初始化计算练习"""
        try:
            self.total_questions = int(self.question_num.get())
            if self.total_questions <= 0:
                messagebox.showerror("错误", "题目数量必须为正数")
                return
        except ValueError:
            messagebox.showerror("错误", "请输入有效的数字")
            return
            
        # 重置计数器
        self.question_count = 0
        self.correct_count = 0
        
        # 开始计时
        self.start_time = time.time()
        
        # 生成第一道题
        self.generate_calculation_question()
    
    def generate_calculation_question(self):
        """生成计算题目"""
        if self.question_count >= self.total_questions:
            self.show_calculation_result()
            return
            
        self.question_count += 1
        
        # 根据难度设置数字范围
        difficulty = self.difficulty.get()
        if difficulty == "简单":
            num1 = random.randint(1, 100)
            num2 = random.randint(1, 100)
        elif difficulty == "中等":
            num1 = random.randint(1, 1000)
            num2 = random.randint(1, 1000)
        else:  # 困难
            num1 = random.randint(1, 10000)
            num2 = random.randint(1, 10000)
        
        # 随机选择运算符
        operator = random.choice(["+", "-", "*", "//"])
        
        # 确保减法结果非负
        if operator == "-" and num1 < num2:
            num1, num2 = num2, num1
        
        # 确保除法能整除
        if operator == "//":
            num2 = random.randint(1, 100) if difficulty != "困难" else random.randint(1, 1000)
            num1 = num2 * random.randint(1, 10)
        
        # 计算正确答案
        if operator == "+":
            answer = num1 + num2
        elif operator == "-":
            answer = num1 - num2
        elif operator == "*":
            answer = num1 * num2
        else:  # //
            answer = num1 // num2
        
        self.current_question = {
            "question": f"{num1} {operator} {num2} = ?",
            "answer": answer
        }
        
        # 显示题目
        self.show_calculation_question()
    
    def show_calculation_question(self):
        """显示计算题目"""
        # 清空当前题目区域
        for widget in self.calc_frame.winfo_children():
            widget.destroy()
        
        # 显示进度
        progress_label = tk.Label(self.calc_frame, 
                                text=f"第 {self.question_count}/{self.total_questions} 题",
                                font=("SimHei", 12), bg="#f0f0f0")
        progress_label.pack(pady=10)
        
        # 显示题目
        question_label = tk.Label(self.calc_frame, 
                                text=self.current_question["question"],
                                font=("SimHei", 24), bg="#f0f0f0")
        question_label.pack(pady=30)
        
        # 答案输入
        ans_frame = tk.Frame(self.calc_frame, bg="#f0f0f0")
        ans_frame.pack(pady=20)
        
        tk.Label(ans_frame, text="你的答案:", font=("SimHei", 14), bg="#f0f0f0").pack(side=tk.LEFT, padx=10)
        self.answer_entry = tk.Entry(ans_frame, font=("SimHei", 14), width=10)
        self.answer_entry.pack(side=tk.LEFT, padx=10)
        self.answer_entry.focus()
        
        # 提交按钮
        submit_btn = tk.Button(self.calc_frame, text="提交", command=self.check_calculation,
                             font=("SimHei", 14), bg="#2196F3", fg="white")
        submit_btn.pack(pady=20)
        
        # 绑定回车键提交
        self.root.bind('<Return>', lambda event: self.check_calculation())
    
    def check_calculation(self):
        """检查计算答案，允许±3%的误差范围"""
        try:
            user_answer = int(self.answer_entry.get())
        except ValueError:
            messagebox.showerror("错误", "请输入有效的数字")
            return
        
        correct_answer = self.current_question["answer"]
        
        # 处理被除数为0的特殊情况
        if correct_answer == 0:
            if user_answer == 0:
                self.correct_count += 1
                messagebox.showinfo("结果", "正确！答案是: 0")
            else:
                messagebox.showinfo("结果", f"错误！正确答案是: {correct_answer}")
            self.generate_calculation_question()
            return
        
        # 计算误差百分比
        absolute_error = abs(user_answer - correct_answer)
        error_percentage = (absolute_error / abs(correct_answer)) * 100
        
        # 判断答案是否在允许的误差范围内
        if error_percentage <= 3:
            self.correct_count += 1
            messagebox.showinfo("结果", 
                              f"正确！\n正确答案是: {correct_answer}\n"
                              f"你的答案是: {user_answer}\n"
                              f"差值: {absolute_error} ({error_percentage:.2f}%)")
        else:
            messagebox.showinfo("结果", 
                              f"错误！\n正确答案是: {correct_answer}\n"
                              f"你的答案是: {user_answer}\n"
                              f"差值: {absolute_error} ({error_percentage:.2f}%)")
        
        # 生成下一题
        self.generate_calculation_question()
    
    def show_calculation_result(self):
        """显示计算练习结果"""
        # 清空当前题目区域
        for widget in self.calc_frame.winfo_children():
            widget.destroy()
        
        # 计算用时
        end_time = time.time()
        elapsed_time = round(end_time - self.start_time, 2)
        
        # 显示结果
        result_label = tk.Label(self.calc_frame, 
                              text=f"练习结束！\n总题数: {self.total_questions}\n"
                                   f"正确数: {self.correct_count}\n"
                                   f"正确率: {round(self.correct_count/self.total_questions*100, 1)}%\n"
                                   f"用时: {elapsed_time}秒",
                              font=("SimHei", 18), bg="#f0f0f0", justify=tk.CENTER)
        result_label.pack(pady=50)
        
        # 返回按钮
        back_btn = tk.Button(self.calc_frame, text="返回计算练习", 
                           command=self.start_calculation,
                           font=("SimHei", 14), bg="#4CAF50", fg="white")
        back_btn.pack(side=tk.LEFT, padx=20, pady=30)
        
        # 再做一次按钮
        again_btn = tk.Button(self.calc_frame, text="再做一次", 
                            command=self.init_calculation,
                            font=("SimHei", 14), bg="#2196F3", fg="white")
        again_btn.pack(side=tk.RIGHT, padx=20, pady=30)
    
    def start_number_reasoning(self):
        """开始数字推理训练"""
        # 清空当前界面
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # 返回按钮
        back_btn = tk.Button(self.root, text="返回主菜单", command=self.create_main_menu,
                           font=("SimHei", 10), bg="#f44336", fg="white")
        back_btn.pack(anchor=tk.NW, padx=10, pady=10)
        
        # 标题
        title_label = tk.Label(self.root, text="数字推理训练", font=("SimHei", 20), bg="#f0f0f0")
        title_label.pack(pady=20)
        
        # 生成数字推理题
        self.generate_number_sequence()
    
    def generate_number_sequence(self):
        """生成数字序列题目"""
        # 随机选择数列类型
        sequence_type = random.choice(["arithmetic", "geometric", "fibonacci", "square", "cube"])
        
        # 生成不同类型的数列
        if sequence_type == "arithmetic":  # 等差数列
            start = random.randint(1, 20)
            step = random.randint(2, 10)
            sequence = [start + i * step for i in range(5)]
            answer = start + 5 * step
        
        elif sequence_type == "geometric":  # 等比数列
            start = random.randint(1, 5)
            ratio = random.randint(2, 5)
            sequence = [start * (ratio **i) for i in range(5)]
            answer = start * (ratio** 5)
        
        elif sequence_type == "fibonacci":  # 斐波那契数列
            a, b = random.randint(1, 5), random.randint(1, 5)
            sequence = [a, b]
            for i in range(3):
                sequence.append(sequence[-1] + sequence[-2])
            answer = sequence[-1] + sequence[-2]
        
        elif sequence_type == "square":  # 平方数列
            start = random.randint(2, 7)
            sequence = [i **2 for i in range(start, start+5)]
            answer = (start + 5)** 2
        
        else:  # 立方数列
            start = random.randint(2, 5)
            sequence = [i **3 for i in range(start, start+5)]
            answer = (start + 5)** 3
        
        self.current_question = {
            "question": sequence,
            "answer": answer
        }
        
        # 显示数列题目
        self.show_number_sequence()
    
    def show_number_sequence(self):
        """显示数字序列题目"""
        # 创建题目框架
        seq_frame = tk.Frame(self.root, bg="#f0f0f0")
        seq_frame.pack(expand=True)
        
        # 显示题目
        question_text = "请找出数列的下一个数字: " + " ".join(map(str, self.current_question["question"])) + " ?"
        question_label = tk.Label(seq_frame, text=question_text, font=("SimHei", 16), bg="#f0f0f0", wraplength=600)
        question_label.pack(pady=30)
        
        # 答案输入
        ans_frame = tk.Frame(seq_frame, bg="#f0f0f0")
        ans_frame.pack(pady=20)
        
        tk.Label(ans_frame, text="你的答案:", font=("SimHei", 14), bg="#f0f0f0").pack(side=tk.LEFT, padx=10)
        self.seq_answer_entry = tk.Entry(ans_frame, font=("SimHei", 14), width=10)
        self.seq_answer_entry.pack(side=tk.LEFT, padx=10)
        self.seq_answer_entry.focus()
        
        # 按钮框架
        btn_frame = tk.Frame(seq_frame, bg="#f0f0f0")
        btn_frame.pack(pady=20)
        
        # 提交按钮
        submit_btn = tk.Button(btn_frame, text="提交", command=self.check_sequence,
                             font=("SimHei", 14), bg="#2196F3", fg="white")
        submit_btn.pack(side=tk.LEFT, padx=20)
        
        # 下一题按钮
        next_btn = tk.Button(btn_frame, text="下一题", command=self.start_number_reasoning,
                           font=("SimHei", 14), bg="#4CAF50", fg="white")
        next_btn.pack(side=tk.LEFT, padx=20)
        
        # 绑定回车键提交
        self.root.bind('<Return>', lambda event: self.check_sequence())
    
    def check_sequence(self):
        """检查数字序列答案"""
        try:
            user_answer = int(self.seq_answer_entry.get())
        except ValueError:
            messagebox.showerror("错误", "请输入有效的数字")
            return
        
        correct_answer = self.current_question["answer"]
        
        # 判断答案是否正确
        if user_answer == correct_answer:
            messagebox.showinfo("结果", "正确！")
        else:
            messagebox.showinfo("结果", f"错误！正确答案是: {correct_answer}")
    
    def start_data_analysis(self):
        """开始资料分析练习"""
        # 清空当前界面
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # 返回按钮
        back_btn = tk.Button(self.root, text="返回主菜单", command=self.create_main_menu,
                           font=("SimHei", 10), bg="#f44336", fg="white")
        back_btn.pack(anchor=tk.NW, padx=10, pady=10)
        
        # 标题
        title_label = tk.Label(self.root, text="ZLXF练习", font=("SimHei", 20), bg="#f0f0f0")
        title_label.pack(pady=20)
        
        # 生成资料分析题目
        self.generate_data_analysis_question()
    
    def generate_data_analysis_question(self):
        """生成资料分析题目"""
        # 随机生成一组数据
        year = random.randint(2018, 2022)
        current_value = random.randint(1000, 10000)
        growth_rate = round(random.uniform(0.05, 0.3), 2)  # 5% - 30%
        
        # 随机选择问题类型
        question_type = random.choice(["previous_year", "growth_amount", "future_value"])
        
        if question_type == "previous_year":  # 求上一年的值
            answer = round(current_value / (1 + growth_rate), 2)
            question = f"{year}年某指标为{current_value}，同比增长{growth_rate*100}%，则{year-1}年该指标为多少？"
        
        elif question_type == "growth_amount":  # 求增长量
            answer = round(current_value / (1 + growth_rate) * growth_rate, 2)
            question = f"{year}年某指标为{current_value}，同比增长{growth_rate*100}%，则较上年增长了多少？"
        
        else:  # 求下一年预测值
            next_year = year + 1
            answer = round(current_value * (1 + growth_rate), 2)
            question = f"{year}年某指标为{current_value}，若保持{growth_rate*100}%的增长率，则{next_year}年该指标预计为多少？"
        
        self.current_question = {
            "question": question,
            "answer": answer
        }
        
        # 显示资料分析题目
        self.show_data_analysis_question()
    
    def show_data_analysis_question(self):
        """显示资料分析题目"""
        # 创建题目框架
        data_frame = tk.Frame(self.root, bg="#f0f0f0")
        data_frame.pack(expand=True)
        
        # 显示题目
        question_label = tk.Label(data_frame, text=self.current_question["question"], 
                                font=("SimHei", 16), bg="#f0f0f0", wraplength=600, justify=tk.LEFT)
        question_label.pack(pady=30, padx=50)
        
        # 答案输入
        ans_frame = tk.Frame(data_frame, bg="#f0f0f0")
        ans_frame.pack(pady=20)
        
        tk.Label(ans_frame, text="你的答案:", font=("SimHei", 14), bg="#f0f0f0").pack(side=tk.LEFT, padx=10)
        self.data_answer_entry = tk.Entry(ans_frame, font=("SimHei", 14), width=15)
        self.data_answer_entry.pack(side=tk.LEFT, padx=10)
        self.data_answer_entry.focus()
        
        # 按钮框架
        btn_frame = tk.Frame(data_frame, bg="#f0f0f0")
        btn_frame.pack(pady=20)
        
        # 提交按钮
        submit_btn = tk.Button(btn_frame, text="提交", command=self.check_data_analysis,
                             font=("SimHei", 14), bg="#2196F3", fg="white")
        submit_btn.pack(side=tk.LEFT, padx=20)
        
        # 下一题按钮
        next_btn = tk.Button(btn_frame, text="下一题", command=self.start_data_analysis,
                           font=("SimHei", 14), bg="#4CAF50", fg="white")
        next_btn.pack(side=tk.LEFT, padx=20)
        
        # 绑定回车键提交
        self.root.bind('<Return>', lambda event: self.check_data_analysis())
    
    def check_data_analysis(self):
        """检查资料分析答案，允许±3%的误差范围"""
        try:
            user_answer = float(self.data_answer_entry.get())
        except ValueError:
            messagebox.showerror("错误", "请输入有效的数字")
            return
        
        correct_answer = self.current_question["answer"]
        
        # 处理被除数为0的特殊情况
        if correct_answer == 0:
            if user_answer == 0:
                self.correct_count += 1
                messagebox.showinfo("结果", "正确！答案是: 0")
            else:
                messagebox.showinfo("结果", f"错误！正确答案是: {correct_answer}")
            return
        
        # 计算误差百分比
        absolute_error = abs(user_answer - correct_answer)
        error_percentage = (absolute_error / abs(correct_answer)) * 100
        
        # 判断答案是否在允许的误差范围内
        if error_percentage <= 3:
            self.correct_count += 1
            messagebox.showinfo("结果", 
                              f"正确！\n正确答案是: {correct_answer}\n"
                              f"你的答案是: {user_answer}\n"
                              f"差值: {absolute_error:.2f} ({error_percentage:.2f}%)")
        else:
            messagebox.showinfo("结果", 
                              f"错误！\n正确答案是: {correct_answer}\n"
                              f"你的答案是: {user_answer}\n"
                              f"差值: {absolute_error:.2f} ({error_percentage:.2f}%)")
    
    def show_about(self):
        """显示关于信息"""
        messagebox.showinfo("关于", "行测小助手 v1.0\n\n一款行测联系工具，包含基础计算、数字推理和资料分析等功能。")

if __name__ == "__main__":
    root = tk.Tk()
    app = XingceHelper(root)
    root.mainloop()
