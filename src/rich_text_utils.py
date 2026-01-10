"""
Rich Text Rendering Utilities for PPT Generation
"""

def apply_rich_text_formatting(paragraph, rich_text_runs, default_font_name="Microsoft YaHei", default_font_size=None, default_color=None):
    """
    Applies rich text formatting to a PPT paragraph.
    
    Args:
        paragraph: python-pptx paragraph object
        rich_text_runs: List of {'text': str, 'format': dict} from parser
        default_font_name: Default font name
        default_font_size: Default font size (Pt object or None)
        default_color: Default color (RGBColor or None)
    
    Returns:
        The paragraph with formatted runs added
    """
    if not rich_text_runs:
        return paragraph
    
    for run_data in rich_text_runs:
        text = run_data.get('text', '')
        fmt = run_data.get('format', {})
        
        run = paragraph.add_run()
        run.text = text
        
        # Apply font settings
        run.font.name = default_font_name
        if default_font_size:
            run.font.size = default_font_size
        if default_color:
            run.font.color.rgb = default_color
        
        # Apply formatting
        if fmt.get('bold'):
            run.font.bold = True
        if fmt.get('italic'):
            run.font.italic = True
        if fmt.get('underline'):
            run.font.underline = True
        
        # Apply emphasis marks (着重号) if present
        # Note: PPT doesn't have native emphasis dots like Word
        # We can simulate with spacing or leave as-is
        # For now, we'll just keep the text as-is
        
    return paragraph


def has_rich_text(rich_runs):
    """Check if rich text data exists and is not empty."""
    return rich_runs and isinstance(rich_runs, list) and len(rich_runs) > 0
