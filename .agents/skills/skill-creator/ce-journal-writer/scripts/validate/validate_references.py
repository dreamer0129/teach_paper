#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
参考文献格式验证脚本

检查参考文献格式是否符合计算机教育期刊要求：
1. 文献序号按顺序编排
2. 3人以上作者只列3人，加"等"字
3. 外文作者姓名按中文习惯（姓前名后）
4. 格式正确（期刊、专著、论文集等）

使用方法：
python validate_references.py --input <参考文献文本文件>
python validate_references.py --text "<参考文献内容>"
"""

import re
import sys
import os
from typing import Dict, List, Tuple, Optional


class Reference:
    """参考文献条目类"""
    def __init__(self, raw_text: str):
        self.raw_text = raw_text
        self.index = None
        self.authors = []
        self.title = ""
        self.source = ""
        self.year = None
        self.volume = None
        self.issue = None
        self.pages = ""
        self.type = ""  # J, M, C, D, S, Z, EB
        self.errors = []
        self.warnings = []

    def __str__(self):
        return self.raw_text


class ReferenceValidator:
    """参考文献验证器"""

    def __init__(self):
        # 各类文献的正则表达式模式
        self.patterns = {
            # 期刊论文 [序号] 作者. 题名[J]. 期刊名称, 出版年份, 卷号(期号): 起止页码.
            'journal': re.compile(
                r'^\[(\d+)\]\s+(.+?)\.\s*(.+?)\[\d+\]\.\s*([^,]+?),\s*(\d{4})\s*(?:,\s*([^,]+?)\(([^)]+)\))?\s*:\s*(.+?)\.$',
                re.MULTILINE
            ),

            # 专著 [序号] 作者. 书名[M]. 出版地: 出版者, 出版年. 起止页码.
            'monograph': re.compile(
                r'^\[(\d+)\]\s+(.+?)\.\s*(.+?)\s*[M]\.\s*([^:]+?):\s*([^,]+?),\s*(\d{4})\.\s*(.+?)\.$',
                re.MULTILINE
            ),

            # 论文集 [序号] 作者. 题名[C]//论文集主编者. 论文集名. 出版地: 出版者, 出版年: 起止页码.
            'conference': re.compile(
                r'^\[(\d+)\]\s+(.+?)\.\s*(.+?)\s*\[C\]//(.+?)\.\s*(.+?)\.\s*([^:]+?):\s*([^,]+?),\s*(\d{4})\s*:\s*(.+?)\.$',
                re.MULTILINE
            ),

            # 学位论文 [序号] 作者. 题名[D]. 保存地点: 保存单位, 年份.
            'dissertation': re.compile(
                r'^\[(\d+)\]\s+(.+?)\.\s*(.+?)\s*[D]\.\s*([^:]+?):\s*([^,]+?),\s*(\d{4})\.$',
                re.MULTILINE
            ),

            # 标准 [序号] 主要责任者. 标准编号—发布年, 标准名称[S]. 出版地: 出版者, 出版年: 页码.
            'standard': re.compile(
                r'^\[(\d+)\]\s+(.+?)\.\s*(.+?)—(\d{4}),\s*(.+?)\s*[S]\.\s*([^:]+?):\s*([^,]+?),\s*(\d{4})\.\s*(.+?)\.$',
                re.MULTILINE
            )
        }

    def parse_reference(self, raw_text: str) -> Optional[Reference]:
        """解析参考文献条目"""
        ref = Reference(raw_text)

        # 去除前后空白
        raw_text = raw_text.strip()

        # 提取序号
        index_match = re.match(r'^\[(\d+)\]', raw_text)
        if index_match:
            ref.index = int(index_match.group(1))

        # 尝试匹配各种文献类型
        for ref_type, pattern in self.patterns.items():
            match = pattern.match(raw_text)
            if match:
                ref.type = ref_type
                self._extract_fields(ref, match)
                break

        if not ref.type:
            ref.errors.append("无法识别文献类型")

        return ref

    def _extract_fields(self, ref: Reference, match):
        """提取字段"""
        if ref.type == 'journal':
            groups = match.groups()
            ref.authors = self._parse_authors(groups[1])
            ref.title = groups[2]
            ref.source = groups[3]
            ref.year = groups[4]
            ref.volume = groups[5] if groups[5] else None
            ref.issue = groups[6] if groups[6] else None
            ref.pages = groups[7] if groups[7] else ""

        elif ref.type == 'monograph':
            groups = match.groups()
            ref.authors = self._parse_authors(groups[1])
            ref.title = groups[2]
            ref.source = groups[3]  # 出版地
            self.publisher = groups[4]  # 出版者
            ref.year = groups[5]
            ref.pages = groups[6]

    def _parse_authors(self, authors_str: str) -> List[str]:
        """解析作者列表"""
        # 处理中文作者
        if re.search(r'[\u4e00-\u9fff]', authors_str):
            # 3人以上只列3人
            if ',' in authors_str:
                authors = authors_str.split(',')
                if len(authors) > 3:
                    return authors[:3] + ['等']
                return authors
            return [authors_str]

        # 处理外文作者（简单处理）
        return [authors_str]

    def validate_reference(self, ref: Reference) -> List[str]:
        """验证单个参考文献"""
        errors = []

        # 检查序号
        if ref.index is None:
            errors.append("缺少序号")
        elif ref.index != len(self.references) + 1:
            errors.append(f"序号不连续，应为{len(self.references) + 1}")

        # 检查作者
        if not ref.authors:
            errors.append("缺少作者")
        else:
            # 检查3人以上作者
            if len(ref.authors) > 3 and '等' not in ref.authors:
                errors.append("超过3人作者应加'等'字")

        # 检查标题
        if not ref.title:
            errors.append("缺少标题")
        elif len(ref.title) > 100:
            errors.append(f"标题过长：{len(ref.title)}字符")

        # 检查文献类型
        if not ref.type:
            errors.append("无法识别文献类型")
        else:
            type_names = {
                'journal': '期刊论文',
                'monograph': '专著',
                'conference': '会议论文',
                'dissertation': '学位论文',
                'standard': '标准'
            }
            print(f"  类型：{type_names.get(ref.type, ref.type)}")

        # 检查年份
        if not ref.year:
            errors.append("缺少出版年份")
        elif not re.match(r'\d{4}', ref.year):
            errors.append(f"年份格式错误：{ref.year}")

        return errors

    def validate_references(self, references_text: str) -> Dict:
        """验证所有参考文献"""
        self.references = []
        all_errors = []
        all_warnings = []

        # 分割参考文献条目
        ref_entries = re.split(r'\n+', references_text.strip())

        for entry in ref_entries:
            entry = entry.strip()
            if not entry:
                continue

            # 解析参考文献
            ref = self.parse_reference(entry)
            if ref:
                self.references.append(ref)

                # 验证
                errors = self.validate_reference(ref)
                if errors:
                    all_errors.extend([f"参考文献{ref.index}: {err}" for err in errors])

                # 检查常见问题
                warnings = self.check_common_problems(ref)
                if warnings:
                    all_warnings.extend([f"参考文献{ref.index}: {warn}" for warn in warnings])

        return {
            'valid': len(all_errors) == 0,
            'total_references': len(self.references),
            'errors': all_errors,
            'warnings': all_warnings,
            'references': self.references
        }

    def check_common_problems(self, ref: Reference) -> List[str]:
        """检查常见问题"""
        warnings = []

        # 检查期刊名称缩写
        if ref.type == 'journal' and ref.source:
            if len(ref.source) > 20:
                warnings.append("期刊名称建议使用缩写")

        # 检查页码格式
        if ref.pages and not re.match(r'\d+-?\d*', ref.pages):
            warnings.append("页码格式应为\"数字-数字\"或\"数字\"")

        # 检查外文文献
        if ref.authors and re.search(r'[a-zA-Z]', ' '.join(ref.authors)):
            warnings.append("外文作者姓名应姓前名后")

        return warnings

    def generate_format_examples(self) -> str:
        """生成格式示例"""
        examples = [
            # 期刊论文
            "期刊论文：[1] 张三. AI赋能教育的实践探索[J]. 计算机教育, 2023, 20(5): 12-18.",
            "期刊论文：[2] Smith J, Johnson M. AI in Education[J]. J. Educ. Tech., 2023, 15(2): 45-52.",

            # 专著
            "专著：[3] 李四. 人工智能与教学改革[M]. 北京: 高等教育出版社, 2022. 120-135.",
            "专著：[4] Wang L. AI in Modern Education[M]. New York: Springer, 2023. 88-102.",

            # 论文集
            "会议论文：[5] 王五. 大模型驱动的教学变革[C]//李明. 计算机教育创新文集. 北京: 清华大学出版社, 2023: 234-245.",
            "会议论文：[6] Chen X. AI Applications in Learning[C]//Zhang Y. Advances in Educational Technology. Singapore: World Scientific, 2023: 156-168.",

            # 学位论文
            "学位论文：[7] 赵六. AI赋能计算机课程思政建设研究[D]. 北京: 北京大学, 2023.",
            "学位论文：[8] Davis K. AI Ethics in Higher Education[D]. Stanford: Stanford University, 2023.",

            # 标准
            "标准：[9] 国家质量监督检验检疫总局. GB/T 7714—2015, 信息与文献 参考文献著录规则[S]. 北京: 中国标准出版社, 2015: 10-15.",
        ]

        return "=== 正确格式示例 ===\n" + "\n".join(examples)


def read_references_from_file(file_path: str) -> str:
    """从文件中读取参考文献"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        raise Exception(f"读取文件失败：{str(e)}")


def main():
    """主函数"""
    validator = ReferenceValidator()

    # 解析命令行参数
    if len(sys.argv) < 2:
        print("使用方法:")
        print("  python validate_references.py --input <参考文献文本文件>")
        print("  python validate_references.py --text \"<参考文献内容>\"")
        print("\n示例：")
        print("  python validate_references.py --text \"[1] 张三. AI教育研究[J]. 计算机教育, 2023, 20(5): 12-18.\"")
        sys.exit(1)

    if sys.argv[1] == '--input':
        if len(sys.argv) != 3:
            print("使用方法: python validate_references.py --input <参考文献文本文件>")
            sys.exit(1)

        file_path = sys.argv[2]
        if not os.path.exists(file_path):
            print(f"文件不存在: {file_path}")
            sys.exit(1)

        try:
            references_text = read_references_from_file(file_path)
        except Exception as e:
            print(e)
            sys.exit(1)

    elif sys.argv[1] == '--text':
        if len(sys.argv) != 3:
            print("使用方法: python validate_references.py --text \"<参考文献内容>\"")
            sys.exit(1)

        references_text = sys.argv[2]

    else:
        print("无效参数。使用 --input 或 --text")
        sys.exit(1)

    # 验证参考文献
    result = validator.validate_references(references_text)

    # 输出结果
    print(f"=== 参考文献验证结果 ===")
    print(f"总参考文献数: {result['total_references']}")
    print()

    if result['valid']:
        print("✓ 所有参考文献格式正确")
    else:
        print("✗ 存在格式错误")

    if result['errors']:
        print("\n=== 错误信息 ===")
        for error in result['errors']:
            print(f"  ❌ {error}")

    if result['warnings']:
        print("\n=== 警告信息 ===")
        for warning in result['warnings']:
            print(f"  ⚠️  {warning}")

    # 输出格式示例
    print("\n" + validator.generate_format_examples())


if __name__ == "__main__":
    main()