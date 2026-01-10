"""
测试脚本：验证 DOCX 格式提取功能

运行方法：
python test_rich_text.py <你的docx文件路径>

示例：
python test_rich_text.py 20251211.docx
"""

import sys
import os

# 添加 src 目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from parser import QuizParser

def test_rich_text_extraction(docx_path):
    if not os.path.exists(docx_path):
        print(f"❌ 文件不存在: {docx_path}")
        return
    
    print(f"📄 正在分析文件: {docx_path}\n")
    print("="*60)
    
    parser = QuizParser()
    
    # 提取带格式的文本
    rich_paragraphs = parser.get_docx_rich_text(docx_path)
    
    if not rich_paragraphs:
        print("❌ 未能提取到任何内容")
        return
    
    print(f"✅ 成功提取 {len(rich_paragraphs)} 个段落\n")
    
    # 显示前 10 个段落的格式信息
    for i, para in enumerate(rich_paragraphs[:10]):
        if not para:  # 空段落
            continue
            
        print(f"\n【段落 {i+1}】")
        print("-" * 60)
        
        for run in para:
            text = run['text']
            fmt = run['format']
            
            # 构建格式标记
            format_tags = []
            if fmt['bold']:
                format_tags.append("加粗")
            if fmt['italic']:
                format_tags.append("斜体")
            if fmt['underline']:
                format_tags.append("下划线")
            if fmt['emphasis']:
                format_tags.append(f"着重号({fmt['emphasis']})")
            
            if format_tags:
                print(f"  📌 [{', '.join(format_tags)}] {text}")
            else:
                print(f"  ➤ {text}")
    
    print("\n" + "="*60)
    print("测试完成！\n")
    
    # 统计格式使用情况
    total_runs = sum(len(p) for p in rich_paragraphs)
    bold_count = sum(1 for p in rich_paragraphs for r in p if r['format']['bold'])
    underline_count = sum(1 for p in rich_paragraphs for r in p if r['format']['underline'])
    emphasis_count = sum(1 for p in rich_paragraphs for r in p if r['format']['emphasis'])
    
    print(f"📊 格式统计：")
    print(f"   总文本片段: {total_runs}")
    print(f"   加粗文本: {bold_count}")
    print(f"   下划线文本: {underline_count}")
    print(f"   着重号文本: {emphasis_count}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python test_rich_text.py <docx文件路径>")
        print("\n示例:")
        print("  python test_rich_text.py 20251211.docx")
        print("  python test_rich_text.py C:\\path\\to\\your\\file.docx")
    else:
        test_rich_text_extraction(sys.argv[1])
