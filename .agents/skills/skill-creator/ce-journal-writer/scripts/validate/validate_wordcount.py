#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
论文字数统计脚本

统计论文总字数（含正文、摘要、关键词、参考文献）
检查是否符合期刊要求：一般不超过6000字

使用方法：
1. 统计文本字数：python validate_wordcount.py <文本内容>
2. 统计文件字数：python validate_wordcount.py --file <文件路径>
"""

import re
import sys
import os
from typing import Dict, List, Tuple


def count_text_words(text: str, include_chars: List[str] = None) -> Dict:
    """
    统计文本字数

    Args:
        text: 要统计的文本
        include_chars: 需要包含的特殊字符列表（如"123"、"abc"等）

    Returns:
        包含各种统计信息的字典
    """
    if include_chars is None:
        include_chars = ["123", "abc"]

    # 去除空白字符
    text = text.strip()

    # 统计总字符数（包含所有字符）
    total_chars = len(text)

    # 统计中文字数（Unicode范围）
    chinese_pattern = re.compile(r'[\u4e00-\u9fff\u3400-\u4dbf\U00020000-\U0002a6df\U0002a700-\U0002b73f\U0002b740-\U0002b81f\U0002b820-\U0002ceaf]')
    chinese_count = len(chinese_pattern.findall(text))

    # 统计英文单词数
    english_words = re.findall(r'\b[a-zA-Z]+\b', text)
    english_word_count = len(english_words)

    # 统计数字个数
    digit_count = len(re.findall(r'\d', text))

    # 统计标点符号
    punctuation_count = len(re.findall(r'[，。！？；：""''（）、【】\[\]\{\}\-…—]', text))

    # 统计纯文本字数（不含图表、公式等）
    plain_text_chars = total_chars

    return {
        'total_chars': total_chars,
        'chinese_count': chinese_count,
        'english_word_count': english_word_count,
        'digit_count': digit_count,
        'punctuation_count': punctuation_count,
        'plain_text_chars': plain_text_chars,
        'estimated_word_count': int(plain_text_chars / 2.5)  # 估算字数（英文算1字，中文算1字）
    }


def check_word_limit(count_result: Dict, limit: int = 6000) -> Tuple[bool, Dict, str]:
    """
    检查字数限制

    Args:
        count_result: count_text_words的返回结果
        limit: 字数限制，默认6000字

    Returns:
        (是否合格, 详细统计, 消息)
    """
    estimated_word_count = count_result['estimated_word_count']

    if estimated_word_count <= limit:
        return True, {
            'word_count': estimated_word_count,
            'limit': limit,
            'percentage': round(estimated_word_count / limit * 100, 1)
        }, f"字数符合要求：{estimated_word_count}字（限制{limit}字）"
    else:
        return False, {
            'word_count': estimated_word_count,
            'limit': limit,
            'excess': estimated_word_count - limit,
            'percentage': round(estimated_word_count / limit * 100, 1)
        }, f"字数超限：{estimated_word_count}字（限制{limit}字，超{estimated_word_count - limit}字）"


def analyze_content_parts(text: str) -> Dict:
    """
    分析论文各部分内容
    """
    # 按章节分割（简单实现）
    parts = {
        '题目': '',
        '摘要': '',
        '关键词': '',
        '正文': '',
        '参考文献': ''
    }

    # 尝试识别各部分
    lines = text.split('\n')
    current_part = '正文'

    for line in lines:
        line = line.strip()
        if not line:
            continue

        # 检测题目（通常在第一行）
        if current_part == '正文' and len(parts['题目']) == 0:
            if len(line) < 30 and '研究' not in line and not line.startswith('第'):
                parts['题目'] = line
                continue

        # 检测摘要
        if '摘要' in line and len(line) > 10:
            current_part = '摘要'
            parts['摘要'] = line
            continue

        # 检测关键词
        if '关键词' in line or '关键词' in line:
            current_part = '关键词'
            parts['关键词'] = line
            continue

        # 检测参考文献
        if '参考文献' in line or '参考' in line:
            current_part = '参考文献'
            parts['参考文献'] = line
            continue

        # 添加到当前部分
        if current_part in parts:
            parts[current_part] += line + '\n'

    return parts


def validate_paper(text: str, limit: int = 6000) -> Dict:
    """
    完整验证论文字数
    """
    # 统计总字数
    count_result = count_text_words(text)

    # 检查字数限制
    word_check, word_detail, word_msg = check_word_limit(count_result, limit)

    # 分析各部分
    parts_result = analyze_content_parts(text)
    parts_count = {}
    for part_name, part_text in parts_result.items():
        if part_text.strip():
            part_count = count_text_words(part_text)['estimated_word_count']
            parts_count[part_name] = part_count

    result = {
        'valid': word_check,
        'total': {
            'word_count': count_result['estimated_word_count'],
            'message': word_msg
        },
        'parts': parts_count,
        'suggestions': [],
        'statistics': count_result
    }

    # 生成建议
    if not word_check:
        result['suggestions'].append(f"字数超限，建议删除不必要的内容（可参考各部分字数分析）")

    # 分析各部分字数
    for part_name, count in parts_count.items():
        if part_name == '摘要' and (count < 150 or count > 350):
            result['suggestions'].append(f"{part_name}字数{count}字，建议控制在200-300字")
        elif part_name == '正文' and count > 4500:
            result['suggestions'].append(f"{part_name}字数过多，建议精简内容")
        elif part_name == '题目' and len(count_result['chinese_count']) > 20:
            result['suggestions'].append(f"{part_name}字数超限，题目不超过20字")

    return result


def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("使用方法:")
        print("  python validate_wordcount.py <文本内容>")
        print("  python validate_wordcount.py --file <文件路径>")
        sys.exit(1)

    if sys.argv[1] == '--file':
        if len(sys.argv) != 3:
            print("使用方法: python validate_wordcount.py --file <文件路径>")
            sys.exit(1)

        file_path = sys.argv[2]
        if not os.path.exists(file_path):
            print(f"文件不存在: {file_path}")
            sys.exit(1)

        with open(file_path, 'r', encoding='utf-8') as f:
            text = f.read()
    else:
        text = sys.argv[1]

    # 验证论文
    result = validate_paper(text)

    # 输出结果
    print("=== 论文字数验证结果 ===")
    print(result['total']['message'])
    print()

    print("=== 各部分字数统计 ===")
    for part_name, count in result['parts'].items():
        print(f"{part_name}: {count}字")

    print()
    print("=== 详细统计 ===")
    stats = result['statistics']
    print(f"总字符数: {stats['total_chars']}")
    print(f"中文字数: {stats['chinese_count']}")
    print(f"英文单词数: {stats['english_word_count']}")
    print(f"数字个数: {stats['digit_count']}")
    print(f"标点符号数: {stats['punctuation_count']}")

    if result['suggestions']:
        print("\n=== 修改建议 ===")
        for suggestion in result['suggestions']:
            print(f"  • {suggestion}")
    else:
        print("\n✓ 论文字数符合期刊要求")


if __name__ == "__main__":
    main()