# Helper function to convert rich text runs to plain text
def rich_text_to_plain(rich_text_runs):
    """Converts rich text format to plain text string."""
    if isinstance(rich_text_runs, str):
        return rich_text_runs
    if isinstance(rich_text_runs, list):
        return ''.join([run['text'] for run in rich_text_runs])
    return ""

# Helper function to create rich text from plain string  
def plain_to_rich(text):
    """Converts plain text string to rich text format."""
    if not text:
        return []
    return [{'text': text, 'format': {'bold': False, 'italic': False, 'underline': False, 'emphasis': None}}]
