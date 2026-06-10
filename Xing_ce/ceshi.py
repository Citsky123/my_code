import requests
import pandas as pd
import csv
import time

def fetch_user_data():
    """获取用户数据"""
    print("正在获取用户数据...")
    
    # API 端点
    users_url = "https://jsonplaceholder.typicode.com/users"
    
    try:
        # 发送 GET 请求
        response = requests.get(users_url)
        
        # 检查请求是否成功
        if response.status_code == 200:
            print("成功获取用户数据!")
            return response.json()  # 解析 JSON 响应
        else:
            print(f"请求失败，状态码: {response.status_code}")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"网络请求错误: {e}")
        return None

def fetch_user_posts(user_id):
    """获取指定用户的帖子"""
    posts_url = f"https://jsonplaceholder.typicode.com/posts?userId={user_id}"
    
    try:
        response = requests.get(posts_url)
        if response.status_code == 200:
            return response.json()
        else:
            print(f"获取用户 {user_id} 的帖子失败")
            return []
    except requests.exceptions.RequestException as e:
        print(f"获取帖子时出错: {e}")
        return []

def process_user_data(users_data):
    """处理用户数据并获取每个人的帖子"""
    processed_data = []
    
    for user in users_data:
        print(f"处理用户: {user['name']}")
        
        # 获取用户的帖子
        posts = fetch_user_posts(user['id'])
        
        # 提取需要的信息
        user_info = {
            "id": user["id"],
            "name": user["name"],
            "username": user["username"],
            "email": user["email"],
            "city": user["address"]["city"],
            "company": user["company"]["name"],
            "post_count": len(posts),
            "post_titles": [post["title"] for post in posts[:3]]  # 只取前3个帖子标题
        }
        
        processed_data.append(user_info)
        
        # 添加延迟，避免请求过快
        time.sleep(0.5)
    
    return processed_data

def save_to_csv(data, filename="user_data.csv"):
    """将数据保存到CSV文件"""
    if not data:
        print("没有数据可保存")
        return
    
    # 创建DataFrame
    df = pd.DataFrame(data)
    
    # 保存到CSV
    df.to_csv(filename, index=False, encoding='utf-8')
    print(f"数据已保存到 {filename}")

def main():
    """主函数"""
    print("开始API调用练习...")
    
    # 1. 获取用户数据
    users_data = fetch_user_data()
    
    if users_data:
        # 2. 处理数据并获取帖子信息
        processed_data = process_user_data(users_data)
        
        # 3. 保存到CSV
        save_to_csv(processed_data)
        
        # 4. 显示前几条数据
        print("\n前5条数据预览:")
        df = pd.DataFrame(processed_data)
        print(df.head())
    else:
        print("无法获取用户数据，程序结束")

if __name__ == "__main__":
    main()