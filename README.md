# Docx to Quiz PPT Converter

A professional Python tool to convert DOCX quiz documents into high-fidelity, interactive PowerPoint presentations.

## Features

- **Automated Parsing**: Extracts questions, options, and explanations from Word documents.
- **High-Fidelity UI**: Modern slate/blue theme with professional card-style layouts.
- **Interactive Animations**: Click-based reveal logic for answers and explanations.
- **Custom Branding**: Supports circular wavy-edged logos and personalized signatures.
- **Standalone EXE**: Can be packaged into a single executable for easy distribution.

## Tech Stack

- **Python 3.13**
- **python-pptx**: For PowerPoint generation.
- **Pillow (PIL)**: For accurate text measurement and image processing.
- **Tkinter**: For the graphical user interface.

## Installation

```bash
git clone <repository-url>
cd gtht
pip install python-pptx Pillow
```

## Run the Web version (Streamlit):
```bash
streamlit run streamlit_app.py
```

## Cloud Deployment (Streamlit Cloud)

1. Push this repository to GitHub.
2. Sign in to [Streamlit Cloud](https://share.streamlit.io/).
3. Click "New app" and select your repository.
4. Set "Main file path" to `streamlit_app.py`.
5. Click "Deploy!".

## Project Structure

- `src/parser.py`: Logic for parsing DOCX files.
- `src/renderer.py`: Logic for rendering PPT slides.
- `gui.py`: Graphical user interface implementation.
- `main.py`: CLI entry point.
- `process_logo.py`: Artistic logo processing utility.

## Author

**山海寻梦**
- Website: [jxgqc.online](http://www.jxgqc.online)
- Platform: [江西教育云](https://xxyd.jxeduyun.com/index)
