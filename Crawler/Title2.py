import requests
from bs4 import BeautifulSoup
import time
import csv
import chardet  # 新增编码检测库

def simple_crawler(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept-Encoding": "gzip, deflate"  # 新增压缩支持
    }
    try:
        # 1. 发送请求
        response = requests.get(url, headers=headers)
        response.raise_for_status()

        # 2. 动态检测编码（比手动指定更可靠）
        encoding = chardet.detect(response.content)['encoding']
        response.encoding = encoding if encoding else 'utf-8'  # 默认使用utf-8
        print(f"检测到编码格式: {response.encoding}")

        time.sleep(3)

        # 3. 解析网页内容
        soup = BeautifulSoup(response.text, 'html.parser')

        # 4. 提取目标内容（需根据实际页面结构调整）
        # --------------------------------------------------
        # 重点调试部分：使用浏览器开发者工具确认选择器
        # 调试方法：先打印整个soup对象查看结构
        # print(soup.prettify())  # 调试时取消注释
        # --------------------------------------------------
        answer_elements = soup.select('.title')
        answers = [element.get_text(strip=True, separator=' ') for element in answer_elements]

        # 5. 终端显示结果
        print("\n提取到 {} 条答案:".format(len(answers)))
        for idx, answer in enumerate(answers, 1):
            print(f"[{idx}] {answer[:50]}...")  # 显示前50字符防止刷屏

        # 6. 写入文件（使用utf-8-sig解决Excel乱码问题）
        with open("answers.csv", "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.writer(f)
            writer.writerow(["序号", "答案内容"])
            for idx, answer in enumerate(answers, 1):
                writer.writerow([idx, answer])
        
        print("\n文件已保存为 answers.csv")

    except requests.exceptions.RequestException as e:
        print(f"网络请求失败: {str(e)}")
    except Exception as e:
        print(f"出现异常: {str(e)}")
        print("建议：检查CSS选择器是否正确，或尝试更新BeautifulSoup版本")

# 调试模式
if __name__ == "__main__":
    target_url = "https://www.mlearning365.com/uCenter.html#/user/staffExamList/detail/14105"
    
    # 首次运行建议先测试编码检测
    test_response = requests.get(target_url)
    detected_encoding = chardet.detect(test_response.content)['encoding']
    print("\n【调试信息】")
    print(f"建议使用的编码格式: {detected_encoding}")
    print(f"实际响应编码: {test_response.encoding}")
    
    # 正式运行
    simple_crawler(target_url)