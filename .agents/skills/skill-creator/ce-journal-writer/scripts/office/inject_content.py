#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
内容注入脚本

将论文内容注入到Word模板的XML中，生成最终的Word文档

使用方法：
python inject_content.py --template <模板目录> --output <输出文件> --content <内容文件>
"""

import os
import sys
import re
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, List, Optional


class WordDocumentInjector:
    """Word文档内容注入器"""

    def __init__(self, template_dir: str):
        self.template_dir = template_dir
        self.namespace = {
            'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
        }

        # 检查模板目录
        if not os.path.exists(template_dir):
            raise Exception(f"模板目录不存在: {template_dir}")

        # 检查必需文件
        self.document_path = os.path.join(template_dir, 'word', 'document.xml')
        self.styles_path = os.path.join(template_dir, 'word', 'styles.xml')

        if not os.path.exists(self.document_path):
            raise Exception(f"document.xml 不存在: {self.document_path}")

    def load_document(self) -> ET.ElementTree:
        """加载文档XML"""
        try:
            tree = ET.parse(self.document_path)
            return tree
        except Exception as e:
            raise Exception(f"加载文档失败: {e}")

    def find_body(self, tree: ET.ElementTree) -> ET.Element:
        """查找body元素"""
        root = tree.getroot()
        body = root.find('w:body', self.namespace)
        if body is None:
            raise Exception("未找到body元素")
        return body

    def inject_title(self, body: ET.Element, title: str):
        """注入标题"""
        # 创建段落
        p = ET.Element('w:p')
        p.set(f"{{{self.namespace['w']}}}space", "preserve")

        # 创建文本运行
        r = ET.Element('w:r')
        rPr = ET.SubElement(r, 'w:rPr')

        # 设置标题样式
        rStyle = ET.SubElement(rPr, 'w:rStyle')
        rStyle.set(f"{{{self.namespace['w']}}}val", "Heading1")

        # 创建文本
        t = ET.SubElement(r, 'w:t')
        t.text = title

        p.append(r)
        body.insert(0, p)

    def inject_abstract(self, body: ET.Element, abstract: str):
        """注入摘要"""
        # 创建摘要标题
        p = ET.Element('w:p')
        p.set(f"{{{self.namespace['w']}}}space", "preserve")

        r = ET.SubElement(p, 'w:r')
        rPr = ET.SubElement(r, 'w:rPr')
        rStyle = ET.SubElement(rPr, 'w:rStyle')
        rStyle.set(f"{{{self.namespace['w']}}}val", "Subtitle")

        t = ET.SubElement(r, 'w:t')
        t.text = "摘要"

        # 创建摘要内容
        p2 = ET.Element('w:p')
        p2.set(f"{{{self.namespace['w']}}}space", "preserve")

        r2 = ET.SubElement(p2, 'w:r')
        t2 = ET.SubElement(r2, 'w:t')
        t2.text = abstract

        # 插入到body中
        body.append(p)
        body.append(p2)

    def inject_keywords(self, body: ET.Element, keywords: str):
        """注入关键词"""
        p = ET.Element('w:p')
        p.set(f"{{{self.namespace['w']}}}space", "preserve")

        r = ET.SubElement(p, 'w:r')
        rPr = ET.SubElement(r, 'w:rPr')
        rStyle = ET.SubElement(rPr, 'w:rStyle')
        rStyle.set(f"{{{self.namespace['w']}}}val", "Subtitle")

        t = ET.SubElement(r, 'w:t')
        t.text = "关键词"

        # 创建关键词内容
        p2 = ET.Element('w:p')
        p2.set(f"{{{self.namespace['w']}}}space", "preserve")

        r2 = ET.SubElement(p2, 'w:r')
        t2 = ET.SubElement(r2, 'w:t')
        t2.text = keywords

        body.append(p)
        body.append(p2)

    def inject_section(self, body: ET.Element, section_name: str, content: str):
        """注入章节"""
        # 创建章节标题
        p = ET.Element('w:p')
        p.set(f"{{{self.namespace['w']}}}space", "preserve")

        r = ET.SubElement(p, 'w:r')
        rPr = ET.SubElement(r, 'w:rPr')
        rStyle = ET.SubElement(rPr, 'w:rStyle')
        rStyle.set(f"{{{self.namespace['w']}}}val", "Heading2")

        t = ET.SubElement(r, 'w:t')
        t.text = section_name

        # 创建章节内容
        if content:
            # 按段落分割内容
            paragraphs = content.split('\n\n')
            for para_text in paragraphs:
                if para_text.strip():
                    p_content = ET.Element('w:p')
                    p_content.set(f"{{{self.namespace['w']}}}space", "preserve")

                    r_content = ET.SubElement(p_content, 'w:r')
                    t_content = ET.SubElement(r_content, 'w:t')
                    t_content.text = para_text.strip()

                    body.append(p_content)

        body.append(p)

    def inject_references(self, body: ET.Element, references: List[str]):
        """注入参考文献"""
        # 创建参考文献标题
        p = ET.Element('w:p')
        p.set(f"{{{self.namespace['w']}}}space", "preserve")

        r = ET.SubElement(p, 'w:r')
        rPr = ET.SubElement(r, 'w:rPr')
        rStyle = ET.SubElement(rPr, 'w:rStyle')
        rStyle.set(f"{{{self.namespace['w']}}}val", "Heading2")

        t = ET.SubElement(r, 'w:t')
        t.text = "参考文献"

        # 注入每条参考文献
        for i, ref in enumerate(references, 1):
            p_ref = ET.Element('w:p')
            p_ref.set(f"{{{self.namespace['w']}}}space", "preserve")

            r_ref = ET.SubElement(p_ref, 'w:r')
            t_ref = ET.SubElement(r_ref, 'w:t')
            t_ref.text = ref

            body.append(p_ref)

    def inject_content(self, content: Dict) -> ET.ElementTree:
        """注入所有内容"""
        # 加载文档
        tree = self.load_document()
        body = self.find_body(tree)

        # 清空现有内容（保留模板结构）
        # 这里可以根据需要调整保留的内容

        # 注入各部分内容
        if 'title' in content:
            self.inject_title(body, content['title'])

        if 'abstract' in content:
            self.inject_abstract(body, content['abstract'])

        if 'keywords' in content:
            self.inject_keywords(body, content['keywords'])

        # 注入正文章节
        if 'sections' in content:
            for section_name, section_content in content['sections'].items():
                self.inject_section(body, section_name, section_content)

        # 注入参考文献
        if 'references' in content:
            self.inject_references(body, content['references'])

        return tree

    def save_document(self, tree: ET.ElementTree, output_path: str):
        """保存文档"""
        try:
            # 确保输出目录存在
            output_dir = os.path.dirname(output_path)
            if output_dir and not os.path.exists(output_dir):
                os.makedirs(output_dir)

            # 保存XML
            tree.write(output_path, encoding='utf-8', xml_declaration=True)
            print(f"文档已保存到: {output_path}")
        except Exception as e:
            raise Exception(f"保存文档失败: {e}")

    def validate_injection(self, tree: ET.ElementTree) -> bool:
        """验证注入结果"""
        try:
            # 检查基本结构
            body = self.find_body(tree)
            if body is None:
                return False

            # 检查是否有内容
            paragraphs = body.findall('.//w:p', self.namespace)
            if len(paragraphs) < 2:  # 至少应该有标题
                print("警告：注入的内容可能过少")
                return False

            print(f"验证通过：文档包含 {len(paragraphs)} 个段落")
            return True

        except Exception as e:
            print(f"验证失败：{e}")
            return False


def load_content_from_file(file_path: str) -> Dict:
    """从文件加载内容"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # 简单解析内容（实际应用中可能需要更复杂的解析）
        lines = content.strip().split('\n')

        result = {}
        current_section = None

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # 检测特殊字段
            if line.startswith('题目：'):
                result['title'] = line[3:].strip()
            elif line.startswith('摘要：'):
                result['abstract'] = line[3:].strip()
            elif line.startswith('关键词：'):
                result['keywords'] = line[4:].strip()
            elif line.startswith('参考文献：'):
                # 这里简化处理，实际应该逐条解析
                result['references'] = [line]
            elif line.startswith('第') and '章' in line:
                current_section = line
                result['sections'] = result.get('sections', {})
                result['sections'][current_section] = ""
            elif current_section and line.startswith('第') and '章' in line:
                # 新章节开始
                result['sections'][current_section] = result['sections'].get(current_section, "")
                current_section = line
                result['sections'][current_section] = ""
            else:
                if current_section:
                    if current_section not in result['sections']:
                        result['sections'][current_section] = ""
                    result['sections'][current_section] += line + '\n'

        return result

    except Exception as e:
        raise Exception(f"加载内容文件失败：{e}")


def main():
    """主函数"""
    if len(sys.argv) < 7:
        print("使用方法:")
        print("  python inject_content.py --template <模板目录> --output <输出文件> --content <内容文件>")
        sys.exit(1)

    # 解析参数
    template_dir = None
    output_file = None
    content_file = None

    for i, arg in enumerate(sys.argv):
        if arg == '--template' and i + 1 < len(sys.argv):
            template_dir = sys.argv[i + 1]
        elif arg == '--output' and i + 1 < len(sys.argv):
            output_file = sys.argv[i + 1]
        elif arg == '--content' and i + 1 < len(sys.argv):
            content_file = sys.argv[i + 1]

    if not template_dir or not output_file or not content_file:
        print("参数错误：缺少必需的参数")
        sys.exit(1)

    try:
        # 创建注入器
        injector = WordDocumentInjector(template_dir)

        # 加载内容
        content = load_content_from_file(content_file)

        # 注入内容
        tree = injector.inject_content(content)

        # 保存文档
        injector.save_document(tree, output_file)

        # 验证结果
        if injector.validate_injection(tree):
            print("\n✓ 内容注入成功")
        else:
            print("\n⚠️  内容注入可能存在问题")

    except Exception as e:
        print(f"错误：{e}")
        sys.exit(1)


if __name__ == "__main__":
    main()