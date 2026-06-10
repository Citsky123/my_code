"""
OpenProject 工作包Markdown导出工具
功能：支持1.导出整个项目所有工作包 2.根据单个工作包URL导出独立任务
认证方式：使用 Basic Auth
"""

import requests
import os
import re
from datetime import datetime
from urllib.parse import urlparse
from requests.auth import HTTPBasicAuth

# ==============================
# 配置区 (请根据你的情况修改)
# ==============================
OPENPROJECT_BASE_URL = "http://192.168.98.54:8080"  # OpenProject实例基础地址
API_KEY = "6507df6843cdc448bef268b48ad56ec46143387cda3fb1915b4d4ba8c7dc21f6"  # 你的API令牌
OUTPUT_DIR = "./openproject_exports"  # 输出目录

# ==============================
# 全局设置
# ==============================
HEADERS = {"Content-Type": "application/json"}
AUTH = HTTPBasicAuth('apikey', API_KEY)  # Basic Auth认证

# ==============================
# 核心功能函数
# ==============================

def extract_url_info(input_url):
    """
    从用户输入的URL中提取信息
    返回: (url_type, project_identifier, work_package_id)
    url_type: 'project' 或 'work_package'
    """
    parsed_url = urlparse(input_url.rstrip('/'))
    path_parts = parsed_url.path.split('/')
    
    if 'work_packages' in path_parts:
        # 工作包URL: /projects/{标识符}/work_packages/{ID}
        # 或: /projects/{标识符}/work_packages/{ID}/activity
        wp_index = path_parts.index('work_packages')
        
        if wp_index + 1 < len(path_parts):
            wp_id_part = path_parts[wp_index + 1]
            
            # 检查wp_id_part是否为数字（工作包ID）
            if wp_id_part.isdigit():
                work_package_id = int(wp_id_part)
                
                # 查找项目标识符（应该在'projects'后面）
                if 'projects' in path_parts:
                    proj_index = path_parts.index('projects')
                    if proj_index + 1 < len(path_parts):
                        project_identifier = path_parts[proj_index + 1]
                        return 'work_package', project_identifier, work_package_id
    
    elif 'projects' in path_parts:
        # 项目URL: /projects/{标识符} 或 /projects/{标识符}/work_packages
        proj_index = path_parts.index('projects') + 1
        if proj_index < len(path_parts):
            identifier = path_parts[proj_index]
            
            # 如果标识符后面还有'work_packages'（列表页），则去掉
            if identifier == 'work_packages' and proj_index - 1 > 0:
                identifier = path_parts[proj_index - 1]
            
            return 'project', identifier, None
    
    raise ValueError(f"无法识别URL类型: '{input_url}'。请确保是有效的项目或工作包URL。")

def fetch_all_work_packages(project_identifier):
    """获取指定项目的所有工作包 (自动处理分页)"""
    all_work_packages = []
    page = 1
    page_size = 100
    
    print(f"开始获取项目 '{project_identifier}' 的工作包...")
    
    while True:
        api_url = f"{OPENPROJECT_BASE_URL}/api/v3/projects/{project_identifier}/work_packages"
        params = {'pageSize': page_size, 'offset': (page - 1) * page_size + 1}
        
        try:
            response = requests.get(api_url, headers=HEADERS, auth=AUTH, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            work_packages = data.get('_embedded', {}).get('elements', [])
            total = data.get('total', 0)
            
            if not work_packages:
                print(f"第 {page} 页没有数据，停止获取。")
                break
            
            all_work_packages.extend(work_packages)
            print(f"已获取第 {page} 页，共 {len(work_packages)} 个工作包 (累计: {len(all_work_packages)}/{total})")
            
            if len(all_work_packages) >= total:
                print(f"✓ 所有数据获取完成，共 {len(all_work_packages)} 个工作包。")
                break
            
            page += 1
            
        except requests.exceptions.RequestException as e:
            print(f"获取第 {page} 页数据时发生错误: {e}")
            if 'response' in locals():
                print(f"响应内容: {response.text[:200]}")
            break
    
    return all_work_packages

def fetch_work_package_details(work_package_id):
    """获取单个工作包的详细信息"""
    api_url = f"{OPENPROJECT_BASE_URL}/api/v3/work_packages/{work_package_id}"
    try:
        response = requests.get(api_url, headers=HEADERS, auth=AUTH, timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"获取工作包 {work_package_id} 详情失败: {e}")
        return None

def format_markdown_content(work_package):
    """将单个工作包格式化为Markdown内容"""
    wp = work_package
    content = f"""## {wp.get('subject', '无主题')} (ID: {wp['id']})

### 基本信息
| 属性 | 值 |
|------|-----|
"""
    
    # 基础信息
    content += f"| **类型** | {wp.get('_links', {}).get('type', {}).get('title', '未指定')} |\n"
    content += f"| **状态** | {wp.get('_links', {}).get('status', {}).get('title', '未指定')} |\n"
    content += f"| **优先级** | {wp.get('_links', {}).get('priority', {}).get('title', '未指定')} |\n"
    
    # 日期信息
    if wp.get('startDate'):
        content += f"| **开始日期** | {wp['startDate']} |\n"
    if wp.get('dueDate'):
        content += f"| **截止日期** | {wp['dueDate']} |\n"
    
    # 负责人
    if wp.get('_links', {}).get('assignee'):
        assignee = wp['_links']['assignee']
        content += f"| **负责人** | {assignee.get('title', assignee.get('name', '未指定'))} |\n"
    
    # 工时信息
    if wp.get('estimatedTime'):
        content += f"| **预计工时** | {wp['estimatedTime']} |\n"
    if wp.get('spentTime'):
        content += f"| **已花费工时** | {wp['spentTime']} |\n"
    
    content += "\n"
    
    # 详细描述 (保留原始Markdown格式)
    description = wp.get('description', {})
    if description and description.get('raw'):
        content += "### 详细描述\n"
        content += description['raw'] + "\n\n"
    else:
        content += "### 详细描述\n无\n\n"
    
    # 链接信息
    content += f"**在OpenProject中查看:** [{OPENPROJECT_BASE_URL}/work_packages/{wp['id']}]({OPENPROJECT_BASE_URL}/work_packages/{wp['id']})\n\n"
    
    return content

def generate_project_markdown_report(project_identifier, work_packages):
    """生成完整的项目Markdown格式报告"""
    if not work_packages:
        return f"""# OpenProject 项目工作包报告

**项目标识符**: {project_identifier}
**导出时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 结果
未找到任何工作包。
"""
    
    # 报告头部
    markdown_content = f"""# OpenProject 项目工作包详细报告

## 项目信息
- **项目标识符**: {project_identifier}
- **导出时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **工作包总数**: {len(work_packages)}

## 报告概述
本报告包含项目 **{project_identifier}** 中所有工作包的详细信息。报告由脚本自动生成，内容与OpenProject系统中的数据实时同步。

---
"""
    
    # 统计信息
    with_description = sum(1 for wp in work_packages if wp.get('description', {}).get('raw'))
    with_due_date = sum(1 for wp in work_packages if wp.get('dueDate'))
    
    # 生成每个工作包的详细内容
    for i, wp in enumerate(work_packages, 1):
        markdown_content += f"\n## 工作包 {i}/{len(work_packages)}\n\n"
        markdown_content += format_markdown_content(wp)
        markdown_content += "---\n"
    
    # 报告尾部
    markdown_content += f"""
## 报告统计
- **工作包总数**: {len(work_packages)}
- **包含详细描述的工作包**: {with_description}
- **设置了截止日期的工作包**: {with_due_date}

## 导出信息
- **导出工具**: OpenProject Markdown导出脚本
- **数据来源**: {OPENPROJECT_BASE_URL}
- **导出时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

> 提示：此报告为自动生成，内容仅供参考。
> 最新信息请以OpenProject系统为准。
"""
    
    return markdown_content

def generate_single_work_package_report(work_package):
    """生成单个工作包的Markdown报告"""
    wp = work_package
    
    markdown_content = f"""# OpenProject 工作包独立报告

## 工作包信息
- **工作包ID**: {wp['id']}
- **工作包标题**: {wp.get('subject', '无主题')}
- **所属项目**: {wp.get('_links', {}).get('project', {}).get('title', '未知项目')}
- **导出时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---
"""
    
    markdown_content += format_markdown_content(wp)
    
    # 报告尾部
    markdown_content += f"""
## 导出信息
- **导出工具**: OpenProject Markdown导出脚本
- **数据来源**: {OPENPROJECT_BASE_URL}
- **原始链接**: {OPENPROJECT_BASE_URL}/work_packages/{wp['id']}
- **导出时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

> 此报告为单个工作包的独立导出，内容与OpenProject系统实时同步。
"""
    
    return markdown_content

def save_markdown_file(filename_prefix, content):
    """保存Markdown报告到文件"""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_prefix = re.sub(r'[^\w\-]', '_', filename_prefix)
    filename = f"OpenProject_{safe_prefix}_Report_{timestamp}.md"
    filepath = os.path.join(OUTPUT_DIR, filename)
    
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return filepath
    except IOError as e:
        print(f"文件保存失败: {e}")
        return None

def export_single_work_package(work_package_id):
    """导出单个工作包"""
    print(f"开始获取工作包 #{work_package_id} 的详细信息...")
    
    wp_details = fetch_work_package_details(work_package_id)
    if not wp_details:
        print(f"❌ 无法获取工作包 #{work_package_id} 的详细信息。")
        return None
    
    print(f"✓ 成功获取工作包: {wp_details.get('subject', '无主题')}")
    
    # 生成报告
    markdown_content = generate_single_work_package_report(wp_details)
    
    # 保存文件
    filename_prefix = f"WorkPackage_{work_package_id}"
    saved_file = save_markdown_file(filename_prefix, markdown_content)
    
    return saved_file, wp_details

def export_entire_project(project_identifier):
    """导出整个项目的所有工作包"""
    work_packages = fetch_all_work_packages(project_identifier)
    
    if not work_packages:
        print(f"项目 '{project_identifier}' 中没有工作包，无需导出。")
        return None
    
    print(f"\n正在生成项目Markdown报告...")
    markdown_content = generate_project_markdown_report(project_identifier, work_packages)
    
    # 保存文件
    saved_file = save_markdown_file(f"Project_{project_identifier}", markdown_content)
    
    return saved_file, work_packages

def main():
    """主函数：控制整个导出流程"""
    print("=" * 60)
    print("OpenProject Markdown导出工具 (增强版)")
    print("=" * 60)
    print(f"OpenProject实例: {OPENPROJECT_BASE_URL}")
    print(f"输出目录: {OUTPUT_DIR}")
    print("-" * 60)
    
    # 获取用户输入
    print("\n请输入OpenProject的URL (支持以下格式):")
    print("1. 项目概览页: http://192.168.98.54:8080/projects/she-bei-bao-yang-xi-tong")
    print("2. 项目工作包列表: http://192.168.98.54:8080/projects/she-bei-bao-yang-xi-tong/work_packages")
    print("3. 单个工作包页: http://192.168.98.54:8080/projects/she-bei-bao-yang-xi-tong/work_packages/73")
    print("4. 工作包活动页: http://192.168.98.54:8080/projects/she-bei-bao-yang-xi-tong/work_packages/73/activity")
    print("5. 输入 'q' 退出程序")
    print("-" * 60)
    
    while True:
        user_input = input("\n请输入URL: ").strip()
        
        if user_input.lower() == 'q':
            print("程序退出。")
            return
        
        if not user_input.startswith('http'):
            print("错误：请输入完整的URL（以http://开头）。")
            continue
        
        try:
            # 提取URL信息
            url_type, project_id, wp_id = extract_url_info(user_input)
            print(f"✓ 识别为: {url_type} 类型")
            if project_id:
                print(f"✓ 项目标识符: '{project_id}'")
            if wp_id:
                print(f"✓ 工作包ID: {wp_id}")
            break
        except ValueError as e:
            print(f"错误: {e}")
            print("请检查URL格式并重新输入。")
    
    # 根据URL类型执行不同的导出逻辑
    if url_type == 'work_package':
        # 导出单个工作包
        result = export_single_work_package(wp_id)
        if result:
            saved_file, wp_details = result
            print(f"\n" + "=" * 60)
            print("✅ 单个工作包导出成功！")
            print("=" * 60)
            print(f"工作包标题: {wp_details.get('subject', '无主题')}")
            print(f"工作包ID: {wp_details['id']}")
            print(f"报告文件: {saved_file}")
    
    elif url_type == 'project':
        # 导出整个项目
        result = export_entire_project(project_id)
        if result:
            saved_file, work_packages = result
            print(f"\n" + "=" * 60)
            print("✅ 项目导出成功！")
            print("=" * 60)
            print(f"项目: {project_id}")
            print(f"工作包数量: {len(work_packages)}")
            print(f"报告文件: {saved_file}")
    
    print("\n📝 提示:")
    print("1. 你可以用Typora、VS Code或任何Markdown编辑器打开此文件")
    print("2. 文件保存在: " + OUTPUT_DIR)
    print("=" * 60)

# ==============================
# 脚本入口
# ==============================
if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n用户中断，程序退出。")
    except Exception as e:
        print(f"\n程序运行出错: {e}")
        print("请检查配置和网络连接。")