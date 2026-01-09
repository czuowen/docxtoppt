import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import sys
import os
import time

# Robust path handling
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

try:
    from src.parser import QuizParser
    from src.renderer import QuizRenderer
except ImportError as e:
    # If starting from inside src or other weirdness
    try:
        from parser import QuizParser
        from renderer import QuizRenderer
    except ImportError:
        print(f"Import Error: {e}")
        raise

class QuizApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Docx to Quiz PPT Converter")
        self.root.geometry("600x450")
        self.root.resizable(False, False)
        
        # Style
        style = ttk.Style()
        style.theme_use('clam') # Clean look
        
        # Header
        header_frame = ttk.Frame(root, padding="20 20 20 10")
        header_frame.pack(fill=tk.X)
        
        lbl_title = ttk.Label(header_frame, text="Docx to Quiz PPT", font=("Microsoft YaHei", 18, "bold"))
        lbl_title.pack(side=tk.LEFT)
        
        lbl_ver = ttk.Label(header_frame, text="v1.0", font=("Arial", 10), foreground="#888")
        lbl_ver.pack(side=tk.LEFT, padx=10, pady=(10, 0))

        # Main Content
        main_frame = ttk.Frame(root, padding="20 10 20 10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # File Selection
        file_frame = ttk.LabelFrame(main_frame, text="Input File", padding="10")
        file_frame.pack(fill=tk.X, pady=10)
        
        self.file_path_var = tk.StringVar()
        self.entry_file = ttk.Entry(file_frame, textvariable=self.file_path_var, width=50)
        self.entry_file.pack(side=tk.LEFT, padx=(0, 10), fill=tk.X, expand=True)
        
        btn_browse = ttk.Button(file_frame, text="Browse...", command=self.browse_file)
        btn_browse.pack(side=tk.RIGHT)
        
        # Actions
        action_frame = ttk.Frame(main_frame, padding="0 10")
        action_frame.pack(fill=tk.X)
        
        self.btn_convert = ttk.Button(action_frame, text="Start Conversion", command=self.start_conversion_thread)
        self.btn_convert.pack(fill=tk.X, ipady=5)
        
        # Log Area
        log_frame = ttk.LabelFrame(main_frame, text="Progress Log", padding="10")
        log_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        self.txt_log = tk.Text(log_frame, height=10, state='disabled', font=("Consolas", 9))
        self.txt_log.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)
        
        scroll = ttk.Scrollbar(log_frame, orient=tk.VERTICAL, command=self.txt_log.yview)
        scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.txt_log['yscrollcommand'] = scroll.set
        
        # Footer
        footer_frame = ttk.Frame(root, padding="10")
        footer_frame.pack(fill=tk.X, side=tk.BOTTOM)
        self.lbl_status = ttk.Label(footer_frame, text="Ready", font=("Microsoft YaHei", 9))
        self.lbl_status.pack(side=tk.LEFT)
        
    def log(self, message):
        self.txt_log.configure(state='normal')
        self.txt_log.insert(tk.END, message + "\n")
        self.txt_log.see(tk.END)
        self.txt_log.configure(state='disabled')
        # Force update (careful with performance, but okay for low freq logs)
        self.root.update_idletasks()
        
    def browse_file(self):
        filename = filedialog.askopenfilename(
            title="Select Quiz Docx",
            filetypes=(("Word Documents", "*.docx"), ("All Files", "*.*"))
        )
        if filename:
            self.file_path_var.set(filename)
            self.log(f"Selected: {filename}")
            
    def start_conversion_thread(self):
        input_file = self.file_path_var.get()
        if not input_file:
            messagebox.showwarning("Warning", "Please select a file first.")
            return
        
        if not os.path.exists(input_file):
            messagebox.showerror("Error", "File does not exist.")
            return

        self.btn_convert.configure(state='disabled')
        self.lbl_status.configure(text="Processing...", foreground="blue")
        self.log(f"-"*30)
        
        # Verify version
        try:
            with open(os.path.join(os.path.dirname(__file__), 'src', 'renderer.py'), 'r', encoding='utf-8') as f:
                ver_line = f.readline()
                self.log(f"Renderer {ver_line.strip()}")
        except:
            pass
            
        self.log(f"Starting conversion for: {os.path.basename(input_file)}")
        
        # Threading
        t = threading.Thread(target=self.run_conversion, args=(self.input_file,))
        t.start()
        
    def run_conversion(self, input_file): # input_file parameter is now redundant, but kept for compatibility
        try:
            # 1. Parsing
            self.lbl_status.config(text="正在分析文档并识别学科...", foreground="blue")
            self.log("Step 1/2: Parsing Document...")
            parser = QuizParser()
            questions = parser.parse(self.input_file)
            subject = parser.infer_subject()
            
            if not questions:
                self.log(f"错误: {os.path.basename(self.input_file)} 未发现试题")
                self.lbl_status.config(text="转换失败", foreground="red") # Using existing lbl_status
                self.finish_conversion(success=False)
                return

            self.log(f"成功识别学科: [{subject}]，提取共 {len(questions)} 道题目")

            # 2. Rendering
            self.lbl_status.config(text="正在生成幻灯片...", foreground="blue")
            self.log("Step 2/2: Generating PowerPoint...")
            
            doc_title = os.path.basename(self.input_file).replace('.docx', '')
            filename = os.path.basename(self.input_file).replace('.docx', '.pptx')
            self.output_file = os.path.join(os.path.dirname(self.input_file), f"PPT_{filename}")
            
            # Auto-rename if locked logic (reused from main.py)
            try:
                # Test write access roughly? No, just try to create Renderer
                # Renderer doesn't open file until save()
                pass
            except:
                pass
                
            renderer = QuizRenderer(self.output_file, subject)
            renderer.create_title_slide(subject)
            
            # Progress loop?
            # renderer.add_question_slides is atomic. 
            # If we want progress per slide, we'd need to modify renderer to accept a callback.
            # For now just run it.
            renderer.add_question_slides(questions)
            
            saved = False
            final_path = output_path
            
            try:
                renderer.save()
                saved = True
            except PermissionError:
                self.log(f"Warning: '{os.path.basename(output_path)}' is open. Trying new name...")
                import time
                final_path = output_path.replace('.pptx', f'_{int(time.time())}.pptx')
                renderer.output_file = final_path
                renderer.save()
                saved = True
                
            if saved:
                self.log(f"Success! Saved to:\n{final_path}")
                self.finish_conversion(success=True)
            else:
                self.log("Failed to save document.")
                self.finish_conversion(success=False)
                
        except Exception as e:
            import traceback
            err = traceback.format_exc()
            self.log(f"Critical Error:\n{err}")
            self.finish_conversion(success=False)
            
    def finish_conversion(self, success):
        self.root.after(0, lambda: self._post_conversion(success))
        
    def _post_conversion(self, success):
        self.btn_convert.configure(state='normal')
        if success:
            self.lbl_status.configure(text="Completed Successfully", foreground="green")
            messagebox.showinfo("Done", "Conversion Complete!")
        else:
            self.lbl_status.configure(text="Failed", foreground="red")
            messagebox.showerror("Error", "Conversion Failed. See log.")

if __name__ == "__main__":
    root = tk.Tk()
    app = QuizApp(root)
    root.mainloop()
