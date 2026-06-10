import requests
from bs4 import BeautifulSoup
import time
import csv
#pip install requests beautifulsoup4 (安装库)

def simple_crawler(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    try:
        # 1. 发送请求
        response = requests.get(url, headers=headers)

        # 手动指定编码
        # 查看网页的 meta 标签来确定其实际编码，（例如 <meta charset="UTF-8"> 表示网页使用 UTF - 8 编码）
        response.encoding = 'utf-8'  # 根据实际情况修改编码

        response.raise_for_status()  # 检查请求是否成功

        time.sleep(3)  # 等待 3 秒

        # 2. 解析网页内容
        soup = BeautifulSoup(response.text, 'html.parser')

        # 3. 提取试题答案
        # 这里需要根据实际网页结构修改选择器
        # 假设答案在 class 为 'cell' 的元素中
        answer_elements = soup.find_all(class_='leftBottomEachDiagram1')   #只需要更改括号里的标签
        answers = [element.text.strip() for element in answer_elements]

        print("试题答案:")
        for i, answer in enumerate(answers, start=1):
            print(f"答案 {i}: {answer}")

        # 4. 将结果写入 CSV
        with open("answers.csv", "w", newline="", encoding="utf-8") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["答案内容"])
            for answer in answers:
                writer.writerow([answer])

    except requests.exceptions.RequestException as e:
        print(f"请求失败: {e}")
    except Exception as e:
        print(f"其他错误: {e}")

# 示例网址
if __name__ == "__main__":
    # 替换为你想爬取的网页地址
    url = "http://hpte.simplo.com.cn/index.php?r=wsr%2Fcomprehensive-information"
    simple_crawler(url)