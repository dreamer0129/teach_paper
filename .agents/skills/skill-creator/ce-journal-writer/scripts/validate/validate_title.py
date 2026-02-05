#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
题目格式验证脚本

检查题目是否符合计算机教育期刊要求：
1. 中文题名不超过20个汉字
2. 简洁明了，准确反映研究内容
3. 避免使用"的研究"、"的探索"等冗余词

使用方法：
1. 验证题目：python validate_title.py <题目内容>
2. 验证文件：python validate_title.py --file <文件路径>
"""

import re
import sys
import os
from typing import Dict, List, Tuple


def count_chinese_chars(text: str) -> int:
    """统计中文字符数"""
    # Unicode中文范围
    chinese_pattern = re.compile(r'[\u4e00-\u9fff\u3400-\u4dbf\U00020000-\U0002a6df\U0002a700-\U0002b73f\U0002b740-\U0002b81f\U0002b820-\U0002ceaf]')
    return len(chinese_pattern.findall(text))


def check_title_length(title: str) -> Tuple[bool, int, str]:
    """检查题目长度"""
    chinese_count = count_chinese_chars(title)

    if chinese_count == 0:
        return False, chinese_count, "题目不含中文字符"

    if chinese_count <= 20:
        return True, chinese_count, f"题目长度合格：{chinese_count}个汉字"
    else:
        return False, chinese_count, f"题目过长：{chinese_count}个汉字，要求不超过20个汉字"


def check_title_content(title: str) -> Tuple[bool, List[str], str]:
    """检查题目内容质量"""
    problems = []

    # 检查冗余词
    redundant_patterns = [
        r"的研究",
        r"的探索",
        r"的实践",
        r"的思考",
        r"的探讨",
        r"的分析",
        r"的调查",
        r"的研究报告",
        r"的初步研究"
    ]

    for pattern in redundant_patterns:
        if re.search(pattern, title):
            problems.append(f"包含冗余词：{pattern}")

    # 检查标题长度（过短可能缺乏信息）
    chinese_count = count_chinese_chars(title)
    if chinese_count < 8:
        problems.append("题目过短，可能缺乏足够信息")

    # 检查是否包含"计算机教育"（可选，但推荐）
    if "计算机" not in title and "教育" not in title:
        problems.append("建议包含'计算机'或'教育'关键词")

    # 检查是否使用标点符号
    if re.search(r'[，。！？；：""''（）【】\[\]\{\}\-…—]', title):
        problems.append("题目中不应包含标点符号")

    # 检查格式是否规范
    if title.startswith("关于") or title.startswith("对"):
        problems.append("建议避免使用'关于'、'对'等开头词")

    if problems:
        return False, problems, "题目内容存在以下问题"
    else:
        return True, problems, "题目内容质量良好"


def generate_suggestions(title: str, problems: List[str]) -> List[str]:
    """生成修改建议"""
    suggestions = []

    # 基于问题生成建议
    for problem in problems:
        if "冗余词" in problem:
            suggestions.append("删除冗余词，使标题更简洁")
        if "过短" in problem:
            suggestions.append("补充研究内容，使标题更具体")
        if "建议包含" in problem:
            suggestions.append("添加'计算机'或'教育'关键词，突出期刊特色")
        if "标点符号" in problem:
            suggestions.append("移除所有标点符号")
        if "避免使用'关于'" in problem:
            suggestions.append("直接陈述研究主题，避免使用'关于'")

    # 生成示例
    examples = [
        "AI赋能微处理器设计课程改革",
        "大模型融入计算机公共基础教学",
        "计算机网络课程思政建设实践",
        "软件需求工程教学改革探索",
        "无人机仿真Python教学创新"
    ]

    suggestions.append(f"参考示例：{', '.join(examples)}")

    return suggestions


def validate_title(title: str) -> Dict:
    """完整验证题目"""
    result = {
        'valid': True,
        'length_check': {'valid': False, 'count': 0, 'message': ''},
        'content_check': {'valid': False, 'problems': [], 'message': ''},
        'suggestions': [],
        'summary': ''
    }

    # 检查长度
    lc_valid, lc_count, lc_msg = check_title_length(title)
    result['length_check'] = {
        'valid': lc_valid,
        'count': lc_count,
        'message': lc_msg,
        'problems': []
    }
    if not lc_valid:
        result['length_check']['problems'].append(lc_msg)
        result['valid'] = False

    # 检查内容
    cc_valid, cc_problems, cc_msg = check_title_content(title)
    result['content_check'] = {
        'valid': cc_valid,
        'problems': cc_problems,
        'message': cc_msg
    }
    if not cc_valid:
        result['valid'] = False

    # 生成建议
    if result['length_check']['problems'] or result['content_check']['problems']:
        all_problems = result['length_check'].get('problems', []) + result['content_check'].get('problems', [])
        result['suggestions'] = generate_suggestions(title, all_problems)

    # 生成总结
    if result['valid']:
        result['summary'] = "✓ 题目符合所有要求"
    else:
        result['summary'] = "✗ 题目需要修改"

    return result


def read_title_from_file(file_path: str) -> str:
    """从文件中读取题目"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        # 题目通常在文件开头几行
        for line in lines[:10]:
            line = line.strip()
            if line and not line.startswith('#') and not line.startswith('//'):
                # 可能是题目
                if len(line) < 100 and ('研究' in line or '教育' in line or '计算机' in line):
                    return line

        # 如果没有找到，返回第一行
        if lines:
            return lines[0].strip()

        return ""
    except Exception as e:
        return f"读取文件失败：{str(e)}"


def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("使用方法:")
        print("  python validate_title.py <题目内容>")
        print("  python validate_title.py --file <文件路径>")
        sys.exit(1)

    if sys.argv[1] == '--file':
        if len(sys.argv) != 3:
            print("使用方法: python validate_title.py --file <文件路径>")
            sys.exit(1)

        file_path = sys.argv[2]
        if not os.path.exists(file_path):
            print(f"文件不存在: {file_path}")
            sys.exit(1)

        title = read_title_from_file(file_path)
        if title.startswith("读取文件失败"):
            print(title)
            sys.exit(1)
    else:
        title = sys.argv[1]

    print(f"验证题目：{title}")
    print()

    # 验证题目
    result = validate_title(title)

    # 输出结果
    print("=== 题目验证结果 ===")
    print(result['length_check']['message'])
    print(result['content_check']['message'])

    if result['suggestions']:
        print("\n=== 修改建议 ===")
        for suggestion in result['suggestions']:
            print(f"  • {suggestion}")
    else:
        print()

    print(result['summary'])


if __name__ == "__main__":
    main()