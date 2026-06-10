# pip install --default-timeout=1000 包名 (安装库，文件体积较大添加超时参数 --default-timeout=1000秒（默认15秒）)
# 安装依赖库 pip install pandas openpyxl

import pandas as pd

# 读取Excel文件
file_path = "D:\\桌面\\320.xlsx"  # 替换为实际路径
df = pd.read_excel(file_path, sheet_name="Worksheet", engine="openpyxl")  # 数据在工作表Worksheet中

# 1. 按"處理計時"列降序排序
df_sorted = df.sort_values(by="處理計時", ascending=False)

# 2. 筛选前20名
top20 = df_sorted.head(20)

# 3. 选择指定列（按Excel列字母定位）
# 定义列字母与索引的映射关系（A=0, B=1,..., Z=25, AA=26,...）
columns_needed = ["F", "G", "M", "N", "O", "P", "Q", "U", "V", "Z", "AD", "AG", "AJ", "AK", "AO", "AX"]

# 将列字母转换为数字索引（例如 F->5, G->6, AD->29, AG->32等）
def column_to_index(col_letter):
    index = 0
    for char in col_letter:
        index = index * 26 + (ord(char.upper()) - ord("A") )+ 1
    return index - 1  # 转换为0-based索引

# 获取所有目标列的索引
selected_columns = [column_to_index(col) for col in columns_needed]

# 通过iloc按位置选择列
result = top20.iloc[:, selected_columns]

# 5. 将结果写入原Excel文件的新工作表
with pd.ExcelWriter(file_path, mode="a", engine="openpyxl", if_sheet_exists="replace") as writer:
    result.to_excel(writer, sheet_name="出警时效", index=False)

print("处理完成！结果已写入原文件的【出警时效】工作表。")