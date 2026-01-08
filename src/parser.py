import re
import zipfile
import xml.etree.ElementTree as ET
import os

class QuizParser:
    def __init__(self):
        self.questions = []

    def get_docx_text(self, path):
        """Extracts text from a docx file using zipfile/xml approach."""
        if not os.path.exists(path):
            return ""

        try:
            document = zipfile.ZipFile(path)
            xml_content = document.read('word/document.xml')
            document.close()
        except Exception:
            return ""
        
        try:
            tree = ET.fromstring(xml_content)
        except Exception:
            return ""
        
        ns = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
        text_content = []
        
        for p in tree.findall('.//w:p', ns):
            texts = [node.text for node in p.findall('.//w:t', ns) if node.text]
            if texts:
                text_content.append(''.join(texts))
            else:
                text_content.append('')
                
        return '\n'.join(text_content)

    def parse(self, file_path):
        """Parses the docx file and returns a list of question dictionaries."""
        content = self.get_docx_text(file_path)
        lines = content.split('\n')
        
        self.questions = []
        current_q = {}
        
        # Regex Patterns
        q_start = re.compile(r'^(\d+)\.\s*(.*)')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # 1. Detect start of a Question
            q_match = q_start.match(line)
            if q_match:
                if current_q:
                    self.questions.append(current_q)
                
                q_num = q_match.group(1)
                q_text = line
                
                # Check for inline answer in previous format (e.g. ".... ( B )")
                # We want to extract "B" and normalize the brackets to "（   ）"
                # Regex for inline answer: "（\s*([A-D])\s*）" or parens
                inline_ans_match = re.search(r'[（\(]\s*([A-D])\s*[）\)]', q_text)
                
                inline_answer = None
                if inline_ans_match:
                    inline_answer = inline_ans_match.group(1)
                    # Normalize to empty brackets for the "Question" slide
                    q_text = re.sub(r'[（\(]\s*[A-D]\s*[）\)]', '（   ）', q_text)
                else:
                    # Normalize empty brackets or placeholders
                    # 1. Replace Underscores at end of line (______ -> （   ）)
                    # Use regex to find underscores at the end, allowing for punctuation like period/question mark?
                    # Usually fill-in-blanks are straight underscores.
                    if '_' in q_text:
                        # Replace sequence of 2 or more underscores with brackets
                        q_text = re.sub(r'_{2,}', '（   ）', q_text)
                    
                    # 2. Normalize existing brackets
                    q_text = re.sub(r'（\s*）', '（   ）', q_text)
                    
                    # 3. Fallback: if no brackets and no underscores (and it's a choice question), append brackets?
                    # The prompt implies "If it ends with underscore, force convert".
                    # Let's check if it still has no brackets.
                    if '（' not in q_text and '(' not in q_text:
                         q_text += '（   ）'

                current_q = {
                    'number': q_num,
                    'question': q_text,
                    'real_answer': inline_answer,
                    'options': [],
                    'explanation': ''
                }
                continue
            
            # 2. Detect Options
            # Pattern: Starts with A. or contains A. B. C. D.
            # Fix: Must also detect lines starting with B., C., D. if split across lines
            if re.search(r'(?:^|\s)[A-D]\.', line) and current_q:
                # STRATEGY: Find all [A-D]. markers and split.
                # Simplified Regex: Just look for Letter + Dot.
                # We assume that in a "Options" line, A. B. C. D. are markers.
                # Risk: "This is A. grade" might trigger.
                # Mitigation: We expect A, B, C, D to be present roughly in order or count.
                
                pattern = re.compile(r'([A-D])\.')
                matches = list(pattern.finditer(line))
                
                # Filter matches?
                # If we found matches, check if they are likely options.
                # E.g. we expect A. to be first? 
                # For now let's just trust them.
                
                if matches:
                    # Logic to slice string
                    for i, match in enumerate(matches):
                        # Start of this option content is:
                        # match start + 2 (len of "X.")
                        # BUT we want to include the label "A." in the option string for the renderer to show?
                        # The renderer typically shows what we give it.
                        # Previous logic included "A.".
                        
                        start = match.start(0) # Start of "A."
                        
                        # End is start of next match
                        if i + 1 < len(matches):
                            end = matches[i+1].start(0)
                        else:
                            end = len(line)
                            
                        opt = line[start:end].strip()
                        opt = re.sub(r'\s+', ' ', opt).strip()
                        current_q['options'].append(opt)
                continue
                
            # 3. Detect Explicit Answer Line
            # Supports: 【答案】B, 答案：B, Answer: B
            if (line.startswith('【答案】') or line.startswith('答案：') or line.startswith('Answer:')) and current_q:
                # Remove label
                ans_text = re.sub(r'^(【答案】|答案：|Answer:)\s*', '', line).strip()
                # Extract just the letter A-D
                ans_char_match = re.search(r'[A-D]', ans_text)
                if ans_char_match:
                     current_q['real_answer'] = ans_char_match.group(0)
                continue
                
            # 4. Detect Explanation Line
            # Supports: 【解析】..., 解析：..., Explanation:...
            if (line.startswith('解析') or line.startswith('【解析】') or line.startswith('Explanation')) and current_q:
                # Remove label
                raw_expl = re.sub(r'^(【解析】|解析：|解析:|Explanation:?)\s*', '', line).strip()
                
                # Tag Cleaning 
                # Remove 【...】 tags inside explanation (e.g. 【分析】)
                cleaned_expl = re.sub(r'【[^】]*】', '', raw_expl)
                
                # Append to identification
                if current_q['explanation']:
                    current_q['explanation'] += "\n" + cleaned_expl.strip()
                else:
                     current_q['explanation'] = cleaned_expl.strip()
                continue
            
            # 5. Fallback: Append generic text to explanation if we are in explanation mode? 
            # Or maybe just append to question if it's multiline?
            # For now, let's assume single line questions/options/answers for simplicity
            # unless we detect we are "inside" explanation.
            if current_q and current_q.get('explanation'):
                 # If we already started explanation, assume following lines are part of it
                 # until next question starts (handled by line 50)
                 current_q['explanation'] += "\n" + line.strip()

        if current_q:
            self.questions.append(current_q)
            
        return self.questions
