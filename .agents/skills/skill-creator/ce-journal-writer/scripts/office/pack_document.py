#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文档打包脚本

将编辑后的XML文件重新打包成Word文档

使用方法：
python pack_document.py --source <源目录> --output <输出文件> --original <原始模板文件（可选）>
"""

import os
import sys
import zipfile
import shutil
from pathlib import Path


def validate_source_dir(source_dir: str) -> bool:
    """验证源目录"""
    if not os.path.exists(source_dir):
        raise Exception(f"源目录不存在: {source_dir}")

    word_dir = os.path.join(source_dir, 'word')
    if not os.path.exists(word_dir):
        raise Exception("缺少word目录")

    # 检查关键文件
    required_files = ['document.xml', 'styles.xml']
    for file in required_files:
        file_path = os.path.join(word_dir, file)
        if not os.path.exists(file_path):
            raise Exception(f"缺少必需文件: {file_path}")

    return True


def create_word_document(source_dir: str, output_path: str):
    """创建Word文档"""
    try:
        # 创建ZIP文件
        with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as docx:
            # 遍历源目录
            for root, dirs, files in os.walk(source_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    # 计算ZIP中的路径
                    arcname = os.path.relpath(file_path, source_dir)
                    docx.write(file_path, arcname)

        print(f"Word文档已创建: {output_path}")

    except Exception as e:
        raise Exception(f"创建Word文档失败: {e}")


def validate_output(output_path: str) -> bool:
    """验证输出文件"""
    try:
        # 检查文件存在
        if not os.path.exists(output_path):
            raise Exception(f"输出文件不存在: {output_path}")

        # 检查文件大小
        size = os.path.getsize(output_path)
        if size < 1024:  # 小于1KB可能有问题
            print(f"警告：文件过小 ({size} bytes)")

        # 验证ZIP结构
        try:
            with zipfile.ZipFile(output_path, 'r') as zip_ref:
                files = zip_ref.namelist()
                if 'word/document.xml' not in files:
                    raise Exception("无效的Word文档格式")
        except zipfile.BadZipFile:
            raise Exception("无效的ZIP文件")

        print(f"验证通过: {output_path}")
        return True

    except Exception as e:
        print(f"验证失败: {e}")
        return False


def create_backup_if_needed(original_path: str, output_path: str):
    """如果需要，创建备份"""
    if original_path and os.path.exists(original_path):
        backup_path = output_path + '.backup'
        try:
            shutil.copy2(original_path, backup_path)
            print(f"已创建备份: {backup_path}")
        except Exception as e:
            print(f"创建备份失败: {e}")


def main():
    """主函数"""
    if len(sys.argv) < 5:
        print("使用方法:")
        print("  python pack_document.py --source <源目录> --output <输出文件> --original <原始模板文件（可选）>")
        sys.exit(1)

    # 解析参数
    source_dir = None
    output_path = None
    original_path = None

    for i, arg in enumerate(sys.argv):
        if arg == '--source' and i + 1 < len(sys.argv):
            source_dir = sys.argv[i + 1]
        elif arg == '--output' and i + 1 < len(sys.argv):
            output_path = sys.argv[i + 1]
        elif arg == '--original' and i + 1 < len(sys.argv):
            original_path = sys.argv[i + 1]

    if not source_dir or not output_path:
        print("参数错误：缺少必需的参数")
        sys.exit(1)

    try:
        # 验证源目录
        print("验证源目录...")
        validate_source_dir(source_dir)

        # 创建备份（如果指定了原始文件）
        if original_path:
            create_backup_if_needed(original_path, output_path)

        # 创建Word文档
        print("正在创建Word文档...")
        create_word_document(source_dir, output_path)

        # 验证输出文件
        print("验证输出文件...")
        if validate_output(output_path):
            print("\n✓ Word文档创建成功")
            print(f"输出文件: {output_path}")
        else:
            print("\n⚠️  Word文档创建可能存在问题")

    except Exception as e:
        print(f"错误：{e}")
        sys.exit(1)


if __name__ == "__main__":
    main()