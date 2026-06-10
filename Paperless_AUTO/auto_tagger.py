import requests
import re
import time
from opencc import OpenCC  # 用于繁简转换

# 配置信息
API_BASE_URL = "http://192.168.98.54:99/api"
API_TOKEN = "e52f10c76750d024e6d52840b1e2ecbd2cf3df72"  # 替换为你的实际令牌

# 初始化繁简转换器
cc = OpenCC('t2s')  # 繁体转简体

# 设置请求头
headers = {
    "Authorization": f"Token {API_TOKEN}",
    "Content-Type": "application/json"
}

def fetch_all_tags():
    """获取系统中所有已有的标签（处理分页）"""
    all_tags = []
    page = 1
    has_next = True
    
    print("开始获取所有标签...")
    
    while has_next:
        try:
            params = {"page": page}
            response = requests.get(f"{API_BASE_URL}/tags/", headers=headers, params=params, timeout=10)
            response.raise_for_status()
            tags_data = response.json()
            
            # 添加当前页的标签
            all_tags.extend(tags_data.get("results", []))
            
            # 检查是否有下一页
            if tags_data.get("next"):
                page += 1
                print(f"获取第 {page} 页标签...")
            else:
                has_next = False
                
        except requests.exceptions.RequestException as e:
            print(f"获取标签列表失败: {e}")
            break
    
    print(f"共获取 {len(all_tags)} 个标签")
    return all_tags

def fetch_all_documents():
    """获取系统中所有文档（处理分页）"""
    all_documents = []
    page = 1
    has_next = True
    
    print("开始获取所有文档...")
    
    while has_next:
        try:
            params = {"page": page}
            response = requests.get(f"{API_BASE_URL}/documents/", headers=headers, params=params, timeout=30)
            response.raise_for_status()
            documents_data = response.json()
            
            # 添加当前页的文档
            all_documents.extend(documents_data.get("results", []))
            
            # 检查是否有下一页
            if documents_data.get("next"):
                page += 1
                print(f"获取第 {page} 页文档...")
            else:
                has_next = False
                
        except requests.exceptions.RequestException as e:
            print(f"获取文档列表失败: {e}")
            break
    
    print(f"共获取 {len(all_documents)} 个文档")
    return all_documents

def normalize_text(text):
    """规范化文本：转换为简体字并转为小写"""
    if not text:
        return ""
    
    # 先转换为简体字
    simplified_text = cc.convert(text)
    # 再转换为小写
    lower_text = simplified_text.lower()
    
    return lower_text

def find_matching_tags(document_title, all_tags):
    """根据文档标题查找匹配的标签"""
    matching_tags = []
    
    # 规范化文档标题（转换为简体并小写）
    normalized_title = normalize_text(document_title)
    
    for tag in all_tags:
        tag_name = tag.get("name", "")
        tag_id = tag.get("id")
        
        # 规范化标签名称（转换为简体并小写）
        normalized_tag = normalize_text(tag_name)
        
        # 检查规范化后的标签是否出现在规范化后的标题中
        if normalized_tag and normalized_tag in normalized_title:
            matching_tags.append({
                "id": tag_id,
                "name": tag_name
            })
    
    return matching_tags

def update_document_tags(document_id, current_tag_ids, new_tag_ids):
    """更新文档的标签"""
    # 合并现有标签和新标签，并去重
    all_tag_ids = list(set(current_tag_ids + new_tag_ids))
    
    update_data = {
        "tags": all_tag_ids
    }
    
    try:
        response = requests.patch(
            f"{API_BASE_URL}/documents/{document_id}/", 
            json=update_data, 
            headers=headers, 
            timeout=10
        )
        response.raise_for_status()
        return True
    except requests.exceptions.RequestException as e:
        print(f"更新文档ID {document_id} 失败: {e}")
        return False

def get_tag_names_from_ids(tag_ids, all_tags):
    """根据标签ID列表获取标签名称列表"""
    tag_id_to_name = {tag["id"]: tag["name"] for tag in all_tags}
    return [tag_id_to_name.get(tag_id, f"未知标签({tag_id})") for tag_id in tag_ids]

def process_all_documents():
    """处理所有文档，自动添加匹配的标签"""
    # 获取所有标签
    all_tags = fetch_all_tags()
    
    # 获取所有文档
    all_documents = fetch_all_documents()
    
    processed_count = 0
    updated_count = 0
    
    print(f"\n开始处理 {len(all_documents)} 个文档...")
    
    for doc in all_documents:
        processed_count += 1
        doc_id = doc.get("id")
        doc_title = doc.get("title", "无标题")
        current_tag_ids = doc.get("tags", [])
        
        # 获取当前标签的名称
        current_tag_names = get_tag_names_from_ids(current_tag_ids, all_tags)
        
        # 查找匹配的标签
        matching_tags = find_matching_tags(doc_title, all_tags)
        
        if matching_tags:
            matching_tag_ids = [tag["id"] for tag in matching_tags]
            matching_tag_names = [tag["name"] for tag in matching_tags]
            
            # 检查是否需要添加新标签（排除已存在的标签）
            new_tag_ids = [tag_id for tag_id in matching_tag_ids if tag_id not in current_tag_ids]
            
            if new_tag_ids:
                new_tag_names = get_tag_names_from_ids(new_tag_ids, all_tags)
                
                print(f"\n文档 {processed_count}/{len(all_documents)}: ID={doc_id}")
                print(f"标题: '{doc_title}'")
                print(f"当前标签: {current_tag_names}")
                print(f"匹配标签: {matching_tag_names}")
                print(f"添加标签: {new_tag_names}")
                
                success = update_document_tags(doc_id, current_tag_ids, new_tag_ids)
                if success:
                    updated_count += 1
                    print("✅ 标签更新成功")
                else:
                    print("❌ 标签更新失败")
            else:
                # 所有匹配标签已存在，无需更新
                pass
        
        # 显示进度
        if processed_count % 10 == 0:
            print(f"已处理 {processed_count}/{len(all_documents)} 个文档...")
        
        # 短暂休眠，避免对服务器请求过于频繁
        time.sleep(0.1)
    
    print(f"\n处理完成！")
    print(f"共处理 {processed_count} 个文档，成功更新 {updated_count} 个文档。")

def test_connection():
    """测试API连接"""
    try:
        response = requests.get(f"{API_BASE_URL}/tags/", headers=headers, timeout=10)
        if response.status_code == 200:
            print("✅ API连接测试成功")
            return True
        else:
            print(f"❌ API连接测试失败，状态码: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ API连接测试失败: {e}")
        return False

if __name__ == "__main__":
    # 测试连接
    if test_connection():
        # 处理所有文档
        process_all_documents()
    else:
        print("请检查API地址和令牌是否正确，以及网络连接是否正常")