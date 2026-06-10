import os
import time
import requests
import sys
from pathlib import Path

# ---------- 配置 ----------
API_KEY = "sk-dffea99867634c53b16efabe11f6d0a6"
ENDPOINT_SUBMIT = "https://dashscope.aliyuncs.com/api/v1/services/aigc/image2image/image-synthesis/"
ENDPOINT_QUERY = "https://dashscope.aliyuncs.com/api/v1/tasks/{}"

# ---------- 辅助函数 ----------
def check_image(filepath, image_type="衣服"):
    """检查图片是否符合要求"""
    if not os.path.exists(filepath):
        print(f"❌ 错误：{image_type}图片文件不存在 -> {filepath}")
        return False
    file_size = os.path.getsize(filepath) / 1024
    if file_size < 5:
        print(f"⚠️ 警告：{image_type}图片大小 {file_size:.1f}KB 小于最小值 5KB")
    elif file_size > 5 * 1024:
        print(f"⚠️ 警告：{image_type}图片大小 {file_size/1024:.1f}MB 超过 5MB")
    return True

def upload_to_temporary_storage(filepath):
    """使用阿里云临时文件上传方案（无需OSS）"""
    print("📤 正在上传本地图片到临时存储...")
    
    upload_url = "https://dashscope.aliyuncs.com/api/v1/uploads"
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    body = {
        "file_name": os.path.basename(filepath),
        "content_type": "image/png"
    }
    
    resp = requests.post(upload_url, headers=headers, json=body)
    if resp.status_code != 200:
        print(f"❌ 获取上传凭证失败: {resp.text}")
        return None
    
    result = resp.json()
    upload_uri = result["data"]["upload_uri"]
    
    with open(filepath, "rb") as f:
        file_content = f.read()
    
    put_resp = requests.put(upload_uri, data=file_content, headers={"Content-Type": "image/png"})
    if put_resp.status_code != 200:
        print(f"❌ 上传图片到临时存储失败: {put_resp.text}")
        return None
    
    print("✅ 图片已上传到临时存储")
    return result["data"]["file_uri"]

# ---------- 主程序 ----------
def main():
    print("=" * 50)
    print("阿里云 OutfitAnyone Plus - 虚拟试衣测试")
    print("=" * 50)
    
    print("\n❗️重要提示：")
    print("1. 确保API Key是中国内地（北京）地域的")
    print("2. 图片必须符合以下要求：")
    print("   - 衣服图片：平铺图、背景干净、完整展示服装")
    print("   - 模特图片：正面、全身、双手可见、只含一人的照片")
    print("   - 大小：5KB-5MB，分辨率150px-4096px")
    print()
    
    # 获取图片路径
    garment_path = input("📷 请输入衣服图片的本地路径: ").strip().strip('"')
    if not check_image(garment_path, "衣服"):
        return
    
    model_path = input("👤 请输入模特图片的本地路径 (直接回车使用官方默认模特): ").strip().strip('"')
    if not model_path:
        print("ℹ️ 使用官方默认模特图片")
        model_url = "https://help-static-aliyun-doc.aliyuncs.com/file-manage-files/zh-CN/20250626/ubznva/model_person.png"
    else:
        if not check_image(model_path, "模特"):
            return
        print("📤 正在上传模特图片到临时存储...")
        model_uri = upload_to_temporary_storage(model_path)
        if not model_uri:
            return
        model_url = f"https://dashscope.aliyuncs.com/api/v1/uploads/{model_uri}"
    
    # 上传衣服图片
    print("📤 正在上传衣服图片到临时存储...")
    garment_uri = upload_to_temporary_storage(garment_path)
    if not garment_uri:
        return
    garment_url = f"https://dashscope.aliyuncs.com/api/v1/uploads/{garment_uri}"
    
    # 提交任务
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "aitryon-plus",
        "input": {
            "person_image_url": model_url,
            "top_garment_url": garment_url
        },
        "parameters": {
            "resolution": -1,
            "restore_face": True
        }
    }
    
    print("\n🚀 正在提交试衣任务...")
    submit_resp = requests.post(
        ENDPOINT_SUBMIT,
        headers=headers,
        json=payload,
        params={"X-DashScope-Async": "enable"}
    )
    
    if submit_resp.status_code != 200:
        print(f"❌ 提交失败 ({submit_resp.status_code}): {submit_resp.text}")
        return
    
    result = submit_resp.json()
    if "output" not in result or "task_id" not in result.get("output", {}):
        print(f"❌ 响应格式异常: {result}")
        return
    
    task_id = result["output"]["task_id"]
    print(f"✅ 任务已提交，task_id: {task_id}")
    
    # 轮询结果
    print("\n⏳ AI正在为你生成试穿图...")
    while True:
        query_resp = requests.get(
            ENDPOINT_QUERY.format(task_id),
            headers=headers
        )
        if query_resp.status_code != 200:
            print(f"⚠️ 查询失败 ({query_resp.status_code})，重试中...")
            time.sleep(3)
            continue
        
        data = query_resp.json()
        status = data.get("output", {}).get("task_status")
        print(f"🔄 当前状态: {status}")
        
        if status == "SUCCEEDED":
            result_url = data["output"].get("image_url")
            if result_url:
                print(f"\n🎉 生成成功！")
                print(f"📷 结果图片链接: {result_url}")
                save_path = Path(garment_path).parent / f"tryon_result_{int(time.time())}.png"
                img_data = requests.get(result_url).content
                with open(save_path, "wb") as f:
                    f.write(img_data)
                print(f"💾 已保存到: {save_path}")
                print("\n✨ 温馨提示：生成图链接有效期24小时，请及时保存。")
                break
            else:
                print("❌ 未找到结果图片链接")
                break
        elif status == "FAILED":
            error_msg = data.get("output", {}).get("message", "未知错误")
            print(f"❌ 生成失败: {error_msg}")
            break
        elif status in ["UNKNOWN", "CANCELED"]:
            print(f"❌ 任务状态异常: {status}")
            break
        else:
            time.sleep(3)
    
    print("\n测试结束！")
    print("🔐 提醒：测试完成后请登录阿里云控制台重置此API Key")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️ 用户中断了程序")
    except Exception as e:
        print(f"\n❌ 程序异常: {e}")
        print("\n💡 请检查：")
        print("1. 网络连接是否正常")
        print("2. API Key是否是中国内地（北京）地域的")
        print("3. 图片路径是否正确")