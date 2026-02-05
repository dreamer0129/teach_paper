#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
摘要格式验证脚本

检查摘要是否符合计算机教育期刊要求：
1. 字数：200-300字
2. 第三人称（不含"本文"、"作者"）
3. 内容包含：研究目的、方法、结果、结论

使用方法：python validate_abstract.py <摘要内容>
"""

import re
import sys
from typing import Dict, List, Tuple


def check_word_count(abstract: str) -> Tuple[bool, int, str]:
    """检查摘要字数"""
    # 去除空格和换行符
    content = abstract.strip()
    char_count = len(content)

    if char_count < 200:
        return False, char_count, f"摘要过短，只有{char_count}字，要求200-300字"
    elif char_count > 300:
        return False, char_count, f"摘要过长，有{char_count}字，要求200-300字"
    else:
        return True, char_count, f"摘要长度合格：{char_count}字"


def check_third_person(abstract: str) -> Tuple[bool, List[str], str]:
    """检查是否使用第三人称"""
    first_person_patterns = [
        r"本文",
        r"本论文",
        r"本研究",
        r"作者",
        r"我们",
        r"我",
        r"笔者",
        r"笔者认为",
        r"本文认为"
    ]

    violations = []
    for pattern in first_person_patterns:
        matches = re.findall(pattern, abstract)
        if matches:
            violations.extend(matches)

    if violations:
        return False, violations, f"发现第一人称表达：{', '.join(violations)}"
    else:
        return True, violations, "未发现第一人称表达"


def check_content_structure(abstract: str) -> Tuple[bool, Dict[str, bool], str]:
    """检查摘要内容结构"""
    structure_check = {
        'purpose': False,
        'method': False,
        'result': False,
        'conclusion': False
    }

    # 检查研究目的（为了...、针对...、根据...）
    purpose_patterns = [
        r"为了",
        r"针对",
        r"根据",
        r"针对",
        r"为解决"
    ]
    if any(re.search(pattern, abstract) for pattern in purpose_patterns):
        structure_check['purpose'] = True

    # 检查研究方法（通过...、采用...、使用...、基于...）
    method_patterns = [
        r"通过",
        r"采用",
        r"使用",
        r"基于",
        r"利用",
        r"运用",
        r"设计了",
        r"构建了"
    ]
    if any(re.search(pattern, abstract) for pattern in method_patterns):
        structure_check['method'] = True

    # 检查研究结果（结果表明、显示、发现、提出、建立）
    result_patterns = [
        r"结果表明",
        r"结果显示",
        r"研究发现",
        r"提出",
        r"建立",
        r"构建",
        r"实现了",
        r"达到"
    ]
    if any(re.search(pattern, abstract) for pattern in result_patterns):
        structure_check['result'] = True

    # 检查研究结论（表明、说明、证实、具有...意义、为...提供...）
    conclusion_patterns = [
        r"表明",
        r"说明",
        r"证实",
        r"具有",
        r"为",
        r"提供",
        r"奠定",
        r"奠定基础"
    ]
    if any(re.search(pattern, abstract) for pattern in conclusion_patterns):
        structure_check['conclusion'] = True

    missing_elements = [k for k, v in structure_check.items() if not v]

    if missing_elements:
        return False, structure_check, f"缺少必要要素：{', '.join(missing_elements)}"
    else:
        return True, structure_check, "摘要内容结构完整"


def validate_abstract(abstract: str) -> Dict:
    """完整验证摘要"""
    result = {
        'valid': True,
        'word_count': {'valid': False, 'count': 0, 'message': ''},
        'third_person': {'valid': False, 'violations': [], 'message': ''},
        'content_structure': {'valid': False, 'elements': {}, 'message': ''},
        'summary': '',
        'suggestions': []
    }

    # 检查字数
    wc_valid, wc_count, wc_msg = check_word_count(abstract)
    result['word_count'] = {
        'valid': wc_valid,
        'count': wc_count,
        'message': wc_msg
    }
    if not wc_valid:
        result['valid'] = False
        result['suggestions'].append(wc_msg)

    # 检查第三人称
    tp_valid, tp_violations, tp_msg = check_third_person(abstract)
    result['third_person'] = {
        'valid': tp_valid,
        'violations': tp_violations,
        'message': tp_msg
    }
    if not tp_valid:
        result['valid'] = False
        result['suggestions'].append(tp_msg)

    # 检查内容结构
    cs_valid, cs_elements, cs_msg = check_content_structure(abstract)
    result['content_structure'] = {
        'valid': cs_valid,
        'elements': cs_elements,
        'message': cs_msg
    }
    if not cs_valid:
        result['valid'] = False
        result['suggestions'].append(cs_msg)

    # 生成总结和建议
    if result['valid']:
        result['summary'] = "✓ 摘符合所有要求"
    else:
        result['summary'] = "✗ 摘要存在以下问题："

    return result


def main():
    """主函数"""
    if len(sys.argv) != 2:
        print("使用方法: python validate_abstract.py <摘要内容>")
        print("示例: python validate_abstract.py '为了解决XX问题，对XX进行了研究...'")
        sys.exit(1)

    abstract = sys.argv[1]
    result = validate_abstract(abstract)

    # 输出结果
    print("=== 摘要验证结果 ===")
    print(f"字数检查: {result['word_count']['message']}")
    print(f"人称检查: {result['third_person']['message']}")
    print(f"结构检查: {result['content_structure']['message']}")

    if not result['valid']:
        print("\n建议修改:")
        for suggestion in result['suggestions']:
            print(f"  - {suggestion}")
    else:
        print("\n" + result['summary'])


if __name__ == "__main__":
    main()