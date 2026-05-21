import librosa
import soundfile as sf
import numpy as np
import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import threading

# =========================================
# CORE PROCESSING FUNCTION
# =========================================

def remove_silence(input_file, output_file, top_db, min_duration_ms):
    """
    Remove silence from audio file.
    
    Parameters:
    - input_file: path to input audio
    - output_file: path to save output
    - top_db: threshold in dB (higher = removes more)
    - min_duration_ms: minimum silence duration in milliseconds
    """
    try:
        print("Loading audio...")
        y, sr = librosa.load(input_file, sr=None)
        
        print(f"Sample Rate: {sr}")
        print(f"Audio Length: {len(y)/sr:.2f} seconds")
        
        print("Detecting speech/non-silent sections...")
        intervals = librosa.effects.split(y, top_db=top_db)
        
        # Filter out segments shorter than min_duration_ms
        min_samples = int(sr * min_duration_ms / 1000)
        intervals = [
            (start, end) for start, end in intervals 
            if (end - start) >= min_samples
        ]
        
        print(f"Found {len(intervals)} audio sections")
        
        print("Removing silence...")
        cleaned_audio = np.concatenate([
            y[start:end]
            for start, end in intervals
        ])
        
        sf.write(output_file, cleaned_audio, sr)
        
        print("\nDone.")
        print(f"Saved cleaned audio as: {output_file}")
        return True, "Successfully processed audio!"
        
    except Exception as e:
        return False, f"Error: {str(e)}"


# =========================================
# GUI APPLICATION
# =========================================

class SilenceRemoverGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Silence Remover")
        self.root.geometry("600x450")
        self.root.resizable(False, False)
        
        self.input_file = tk.StringVar()
        self.output_file = tk.StringVar(value="output.mp3")
        
        # Create main frame
        main_frame = ttk.Frame(root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Input File
        ttk.Label(main_frame, text="Input Audio File:", font=("Arial", 10, "bold")).grid(row=0, column=0, sticky=tk.W, pady=(10, 5))
        ttk.Entry(main_frame, textvariable=self.input_file, width=50).grid(row=1, column=0, sticky=(tk.W, tk.E), padx=(0, 5))
        ttk.Button(main_frame, text="Browse...", command=self.browse_input).grid(row=1, column=1, padx=5)
        
        # Output File
        ttk.Label(main_frame, text="Output Audio File:", font=("Arial", 10, "bold")).grid(row=2, column=0, sticky=tk.W, pady=(15, 5))
        ttk.Entry(main_frame, textvariable=self.output_file, width=50).grid(row=3, column=0, sticky=(tk.W, tk.E), padx=(0, 5))
        ttk.Button(main_frame, text="Browse...", command=self.browse_output).grid(row=3, column=1, padx=5)
        
        # Silence Threshold (Top DB)
        ttk.Label(main_frame, text="Silence Threshold (dB):", font=("Arial", 10, "bold")).grid(row=4, column=0, sticky=tk.W, pady=(15, 5))
        
        threshold_frame = ttk.Frame(main_frame)
        threshold_frame.grid(row=5, column=0, sticky=(tk.W, tk.E), pady=(0, 5))
        
        self.top_db_var = tk.IntVar(value=30)
        self.top_db_slider = ttk.Scale(threshold_frame, from_=10, to=60, orient=tk.HORIZONTAL, 
                                        variable=self.top_db_var, command=self.update_threshold_label)
        self.top_db_slider.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        self.threshold_label = ttk.Label(threshold_frame, text="30 dB", width=6)
        self.threshold_label.pack(side=tk.LEFT, padx=(10, 0))
        
        ttk.Label(main_frame, text="(Higher = removes more silence; Range: 10-60)", 
                 font=("Arial", 9, "italic")).grid(row=6, column=0, sticky=tk.W, pady=(0, 10))
        
        # Minimum Silence Duration
        ttk.Label(main_frame, text="Minimum Silence Duration (ms):", font=("Arial", 10, "bold")).grid(row=7, column=0, sticky=tk.W, pady=(10, 5))
        
        duration_frame = ttk.Frame(main_frame)
        duration_frame.grid(row=8, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        self.duration_var = tk.IntVar(value=100)
        self.duration_spinbox = ttk.Spinbox(duration_frame, from_=10, to=1000, textvariable=self.duration_var, width=10)
        self.duration_spinbox.pack(side=tk.LEFT)
        
        ttk.Label(duration_frame, text="ms (segments shorter than this will be removed)").pack(side=tk.LEFT, padx=(10, 0))
        
        # Process Button
        self.process_button = ttk.Button(main_frame, text="Process Audio", command=self.process_audio)
        self.process_button.grid(row=9, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(20, 10))
        
        # Status Label
        self.status_var = tk.StringVar(value="Ready")
        status_label = ttk.Label(main_frame, textvariable=self.status_var, foreground="blue", font=("Arial", 9))
        status_label.grid(row=10, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        # Configure grid
        main_frame.columnconfigure(0, weight=1)
        
    def update_threshold_label(self, value):
        self.threshold_label.config(text=f"{int(float(value))} dB")
    
    def browse_input(self):
        file = filedialog.askopenfilename(
            title="Select Audio File",
            filetypes=[("Audio Files", "*.mp3 "), ("All Files", "*.*")]
        )
        if file:
            self.input_file.set(file)
    
    def browse_output(self):
        file = filedialog.asksaveasfilename(
            title="Save Processed Audio As",
            defaultextension=".mp3",
            filetypes=[("MP3 Files", "*.mp3"),("All Files", "*.*")]
        )
        if file:
            self.output_file.set(file)
    
    def process_audio(self):
        input_file = self.input_file.get()
        output_file = self.output_file.get()
        
        if not input_file:
            messagebox.showerror("Error", "Please select an input audio file")
            return
        
        if not output_file:
            messagebox.showerror("Error", "Please specify an output file")
            return
        
        if not os.path.exists(input_file):
            messagebox.showerror("Error", f"Input file not found: {input_file}")
            return
        
        # Disable button and show processing status
        self.process_button.config(state=tk.DISABLED)
        self.status_var.set("Processing... Please wait")
        self.root.update()
        
        # Run processing in separate thread to avoid freezing UI
        thread = threading.Thread(
            target=self.run_processing,
            args=(input_file, output_file, self.top_db_var.get(), self.duration_var.get())
        )
        thread.start()
    
    def run_processing(self, input_file, output_file, top_db, min_duration_ms):
        success, message = remove_silence(input_file, output_file, top_db, min_duration_ms)
        
        # Update UI in main thread
        self.root.after(0, self.processing_complete, success, message)
    
    def processing_complete(self, success, message):
        self.process_button.config(state=tk.NORMAL)
        
        if success:
            self.status_var.set("✓ Completed successfully!")
            messagebox.showinfo("Success", message)
        else:
            self.status_var.set("✗ Processing failed")
            messagebox.showerror("Error", message)


# =========================================
# MAIN
# =========================================

if __name__ == "__main__":
    root = tk.Tk()
    app = SilenceRemoverGUI(root)
    root.mainloop()
