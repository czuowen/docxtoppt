import sys
import os
from src.parser import QuizParser
from src.renderer import QuizRenderer

def main():
    if len(sys.argv) < 2:
        print("Usage: python main.py <input_docx_file>")
        # Default fallback for testing if file exists
        if os.path.exists('20251211.docx'):
            input_file = '20251211.docx'
            print(f"No argument provided. Using default: {input_file}")
        else:
            return
    else:
        input_file = sys.argv[1]

    if not os.path.exists(input_file):
        print(f"Error: File '{input_file}' not found.")
        return

    print(f"Analyzing {input_file}...")
    
    # 1. Parse
    parser = QuizParser()
    questions = parser.parse(input_file)
    print(f"Successfully extracted {len(questions)} questions.")
    
    if not questions:
        print("No questions found. Please check the document format.")
        return

    # 2. Render
    output_filename = f"PPT_{os.path.basename(input_file).replace('.docx', '.pptx')}"
    print(f"Generating presentation: {output_filename}...")
    
    renderer = QuizRenderer(output_filename)
    renderer.create_title_slide()
    renderer.add_question_slides(questions)
    
    try:
        renderer.save()
        print(f"Done! Saved to {output_filename}")
    except PermissionError:
        print(f"Warning: '{output_filename}' is open or locked.")
        # Try new name
        import time
        new_filename = output_filename.replace('.pptx', f'_{int(time.time())}.pptx')
        renderer.output_file = new_filename
        renderer.save()
        print(f"Done! Basic file was locked, saved to new file: {new_filename}")

if __name__ == "__main__":
    main()
