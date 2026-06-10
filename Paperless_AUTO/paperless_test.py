import requests
import re
import time

# 配置信息
API_BASE_URL = "http://192.168.98.54:99/api"
API_TOKEN = "dd31a074b7b32bcf282eeff46de19fde63b5ece1"  # 替换为你的实际令牌

# 设置请求头
headers = {
    "Authorization": f"Token {API_TOKEN}",
    "Content-Type": "application/json"
}

def fetch_all_tags():
    """获取系统中所有已有的标签"""
    try:
        response = requests.get(f"{API_BASE_URL}/tags/", headers=headers, timeout=10)
        response.raise_for_status()
        tags_data = response.json()
        return tags_data.get("results", [])
    except requests.exceptions.RequestException as e:
        print(f"获取标签列表失败: {e}")
        return []

def fetch_specific_document(document_id):
    """获取特定ID的文档"""
    try:
        response = requests.get(f"{API_BASE_URL}/documents/{document_id}/", headers=headers, timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"获取文档失败: {e}")
        return None

def find_matching_tags(document_title, all_tags):
    """根据文档标题查找匹配的标签"""
    matching_tags = []
    
    # 将标题转换为小写以便不区分大小写匹配
    title_lower = document_title.lower()
    
    for tag in all_tags:
        tag_name = tag.get("name", "").lower()
        tag_id = tag.get("id")
        
        # 如果标签名称出现在文档标题中，则认为是匹配的
        if tag_name and tag_name in title_lower:
            matching_tags.append({
                "id": tag_id,
                "name": tag.get("name")
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
        return True, all_tag_ids
    except requests.exceptions.RequestException as e:
        print(f"更新文档ID {document_id} 失败: {e}")
        return False, current_tag_ids

def get_tag_names_from_ids(tag_ids, all_tags):
    """根据标签ID列表获取标签名称列表"""
    tag_id_to_name = {tag["id"]: tag["name"] for tag in all_tags}
    return [tag_id_to_name.get(tag_id, f"未知标签({tag_id})") for tag_id in tag_ids]

def test_single_document(document_id, all_tags):
    """测试单个文档的标签匹配"""
    print(f"\n开始获取文档 ID={document_id}...")
    doc = fetch_specific_document(document_id)
    
    if not doc:
        print("❌ 无法获取文档，请检查文档ID是否正确")
        return False
    
    doc_title = doc.get("title", "无标题")
    current_tag_ids = doc.get("tags", [])  # 这里可能是标签ID列表
    
    # 获取当前标签的名称
    current_tag_names = get_tag_names_from_ids(current_tag_ids, all_tags)
    
    print(f"文档标题: '{doc_title}'")
    print(f"当前标签: {current_tag_names}")
    
    # 查找匹配的标签
    matching_tags = find_matching_tags(doc_title, all_tags)
    
    if matching_tags:
        matching_tag_ids = [tag["id"] for tag in matching_tags]
        matching_tag_names = [tag["name"] for tag in matching_tags]
        
        print(f"找到匹配的标签: {matching_tag_names}")
        
        # 检查是否需要添加新标签（排除已存在的标签）
        new_tag_ids = [tag_id for tag_id in matching_tag_ids if tag_id not in current_tag_ids]
        
        if new_tag_ids:
            new_tag_names = get_tag_names_from_ids(new_tag_ids, all_tags)
            print(f"将添加新标签: {new_tag_names}")
            
            # 询问用户是否确认添加
            user_input = input("是否确认添加这些标签? (y/n): ")
            if user_input.lower() == 'y':
                success, updated_tag_ids = update_document_tags(document_id, current_tag_ids, new_tag_ids)
                if success:
                    print("✅ 标签更新成功")
                    
                    # 获取更新后的文档信息以验证
                    updated_doc = fetch_specific_document(document_id)
                    if updated_doc:
                        updated_tag_ids = updated_doc.get("tags", [])
                        updated_tag_names = get_tag_names_from_ids(updated_tag_ids, all_tags)
                        print(f"更新后的标签: {updated_tag_names}")
                    return True
                else:
                    print("❌ 标签更新失败")
                    return False
            else:
                print("操作已取消")
                return False
        else:
            print("所有匹配标签已存在，无需更新")
            return True
    else:
        print("未找到匹配的标签")
        return True

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
        # 获取所有标签
        print("开始获取系统中所有标签...")
        all_tags = fetch_all_tags()
        print(f"系统中共有 {len(all_tags)} 个标签")
        
        # 获取用户输入的文档ID
        document_id = input("请输入要测试的文档ID: ")
        
        if document_id.isdigit():
            # 测试单个文档
            success = test_single_document(int(document_id), all_tags)
            
            if success:
                print("\n✅ 测试完成！")
                print("请在Paperless-ngx界面中验证结果是否正确。")
            else:
                print("\n❌ 测试失败！")
        else:
            print("❌ 文档ID必须是数字")
    else:
        print("请检查API地址和令牌是否正确，以及网络连接是否正常")