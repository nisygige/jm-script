import os
import time
from pathlib import Path
from PIL import Image
import subprocess
import shutil

# 桌面路径
desktop = Path.home() / "Desktop"
pdf_collection_dir = desktop / "本子PDF合集"
pdf_collection_dir.mkdir(exist_ok=True)

# jmcomic 命令
JM_COMMAND = "jmcomic"

# 下载完成后等待时间（秒）
WAIT_TIME = 5

def run_jmcomic(code):
    """运行 jmcomic 下载本子"""
    print(f"📥 开始下载本子 {code} ...")
    subprocess.run(f"{JM_COMMAND} {code}", shell=True)
    print(f"✅ 下载完成：{code}")

def images_to_pdf(folder_path):
    """将文件夹内图片整合为 PDF"""
    pdf_path = pdf_collection_dir / f"{folder_path.name}.pdf"
    if pdf_path.exists():
        print(f"⚠️ PDF 已存在，跳过：{pdf_path}")
        return False

    images = []
    for ext in ("*.jpg", "*.jpeg", "*.png", "*.webp"):
        for img_path in sorted(folder_path.glob(ext)):
            try:
                images.append(Image.open(img_path).convert("RGB"))
            except Exception as e:
                print(f"⚠️ 无法打开图片 {img_path}: {e}")

    if not images:
        print(f"⚠️ 未找到图片：{folder_path}")
        return False

    images[0].save(pdf_path, save_all=True, append_images=images[1:])
    print(f"📕 PDF 生成完成：{pdf_path}")
    return True

def find_book_folder(code):
    """尝试找到桌面上与编号对应的文件夹，排除 PDF 总汇文件夹"""
    folders = [f for f in desktop.iterdir() if f.is_dir() and f != pdf_collection_dir]
    # 先找包含编号的文件夹
    for folder in sorted(folders, key=lambda x: x.stat().st_mtime, reverse=True):
        if code in folder.name:
            return folder
    # 找不到则取最近修改的文件夹（排除 PDF 总汇）
    return max(folders, key=lambda x: x.stat().st_mtime) if folders else None

def process_book(code):
    """处理单本子"""
    run_jmcomic(code)
    print(f"⌛ 等待 {code} 文件夹生成中...")
    time.sleep(WAIT_TIME)  # 给 jmcomic 一点时间生成文件夹

    folder = find_book_folder(code)
    if folder:
        success = images_to_pdf(folder)
        # 如果 PDF 生成成功，删除原本子图片文件夹
        if success:
            try:
                shutil.rmtree(folder)
                print(f"🗑 已删除原文件夹：{folder}")
            except Exception as e:
                print(f"⚠️ 删除文件夹失败：{folder}, {e}")
    else:
        print(f"❌ 未检测到 {code} 的文件夹，请确认下载成功。")

def main():
    user_input = input(
        "请输入要下载的本子编号（用空格或逗号分隔，例如 123,456 789）：\n> "
    )
    # 支持中文逗号、英文逗号、空格
    codes = [c.strip() for c in user_input.replace("，", " ").replace(",", " ").split() if c.strip()]

    if not codes:
        print("❌ 没有输入任何编号")
        return

    for code in codes:
        process_book(code)

    print(f"\n🎉 所有任务完成！PDF 已汇总到桌面文件夹：{pdf_collection_dir}")
    os.system("pause")

if __name__ == "__main__":
    main()
