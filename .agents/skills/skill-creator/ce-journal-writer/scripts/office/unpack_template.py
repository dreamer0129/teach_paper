#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
模板解包脚本

解包Word模板文件，为XML编辑做准备

使用方法：
python unpack_template.py --template <模板文件> --output <输出目录>
"""

import os
import sys
import shutil
import zipfile
from pathlib import Path


def unpack_template(template_path: str, output_dir: str):
    """解包Word模板"""
    # 检查模板文件
    if not os.path.exists(template_path):
        raise Exception(f"模板文件不存在: {template_path}")

    # 创建输出目录
    os.makedirs(output_dir, exist_ok=True)

    try:
        # 解压ZIP文件
        print(f"正在解包模板: {template_path}")
        print(f"解包目录: {output_dir}")

        with zipfile.ZipFile(template_path, 'r') as zip_ref:
            zip_ref.extractall(output_dir)

        # 验证解包结果
        word_dir = os.path.join(output_dir, 'word')
        if not os.path.exists(word_dir):
            raise Exception("解包失败：缺少word目录")

        # 检查关键文件
        required_files = [
            'document.xml',
            'styles.xml',
            'fontTable.xml',
            'settings.xml'
        ]

        for file in required_files:
            file_path = os.path.join(word_dir, file)
            if not os.path.exists(file_path):
                print(f"警告：缺少文件 {file}")

        # 生成解包报告
        print("\n=== 解包完成 ===")
        print(f"解包文件数: {len(os.listdir(output_dir))}")
        print(f"word目录文件: {len(os.listdir(word_dir))}")
        print("\n主要文件:")
        for file in sorted(os.listdir(word_dir)):
            file_path = os.path.join(word_dir, file)
            size = os.path.getsize(file_path)
            print(f"  {file} ({size} bytes)")

        print(f"\n解包完成，可在 {output_dir} 中编辑XML文件")

    except Exception as e:
        raise Exception(f"解包失败: {e}")


def validate_template(template_path: str) -> bool:
    """验证模板文件"""
    try:
        # 检查文件扩展名
        if not template_path.lower().endswith('.docx'):
            print(f"警告：文件扩展名不是.docx: {template_path}")
            return False

        # 尝试打开ZIP文件
        try:
            with zipfile.ZipFile(template_path, 'r') as zip_ref:
                # 检查是否为有效的Word文档
                if 'word/document.xml' not in zip_ref.namelist():
                    print("错误：不是有效的Word文档（缺少document.xml）")
                    return False
        except zipfile.BadZipFile:
            print("错误：文件不是有效的ZIP格式")
            return False

        print(f"模板验证通过: {template_path}")
        return True

    except Exception as e:
        print(f"模板验证失败: {e}")
        return False


def main():
    """主函数"""
    if len(sys.argv) < 5:
        print("使用方法:")
        print("  python unpack_template.py --template <模板文件> --output <输出目录>")
        sys.exit(1)

    # 解析参数
    template_path = None
    output_dir = None

    for i, arg in enumerate(sys.argv):
        if arg == '--template' and i + 1 < len(sys.argv):
            template_path = sys.argv[i + 1]
        elif arg == '--output' and i + 1 < len(sys.argv):
            output_dir = sys.argv[i + 1]

    if not template_path or not output_dir:
        print("参数错误：缺少必需的参数")
        sys.exit(1)

    try:
        # 验证模板
        if not validate_template(template_path):
            print("模板验证失败，退出")
            sys.exit(1)

        # 解包模板
        unpack_template(template_path, output_dir)

    except Exception as e:
        print(f"错误：{e}")
        sys.exit(1)


if __name__ == "__main__":
    main()