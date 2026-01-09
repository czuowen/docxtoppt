import os
import time
import uuid
from flask import Flask, render_template, request, send_file, jsonify
from flask_cors import CORS
from src.parser import QuizParser
from src.renderer import QuizRenderer

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/convert', methods=['POST'])
def convert():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if not file.filename.endswith('.docx'):
        return jsonify({'error': 'Only .docx files are supported'}), 400

    # Generate unique ID for this session
    session_id = str(uuid.uuid4())
    input_filename = f"{session_id}.docx"
    output_filename = f"PPT_{session_id}.pptx"
    
    input_path = os.path.join(UPLOAD_FOLDER, input_filename)
    output_path = os.path.join(UPLOAD_FOLDER, output_filename)
    
    try:
        file.save(input_path)
        
        # 1. Parsing
        parser = QuizParser(input_path)
        questions = parser.parse()
        
        if not questions:
            return jsonify({'error': 'No questions found in the document'}), 400
        
        # 2. Rendering
        renderer = QuizRenderer(output_path)
        renderer.add_title_slide(os.path.basename(file.filename).replace('.docx', ''))
        renderer.add_question_slides(questions)
        renderer.save()
        
        # Returning path for the client to download
        return jsonify({
            'success': True,
            'download_url': f'/download/{output_filename}',
            'filename': f"{os.path.splitext(file.filename)[0]}.pptx"
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/download/<filename>')
def download(filename):
    path = os.path.join(UPLOAD_FOLDER, filename)
    if os.path.exists(path):
        return send_file(path, as_attachment=True)
    return "File not found", 404

if __name__ == '__main__':
    app.run(debug=True, port=5000)
