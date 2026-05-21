import customtkinter as ctk
from tkinter import filedialog
import threading

from processor import remove_silence


ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class App(ctk.CTk):

    def __init__(self):
        super().__init__()

        self.title("Silence Remover")
        self.geometry("700x600")

        self.input_path = ""
        self.output_path = ""

        self.build_ui()

    def build_ui(self):

        self.title_label = ctk.CTkLabel(
            self,
            text="Silence Remover",
            font=("Arial", 28, "bold")
        )
        self.title_label.pack(pady=20)

        # Input Audio Section
        self.input_label_title = ctk.CTkLabel(
            self,
            text="Input Audio:",
            font=("Arial", 12, "bold")
        )
        self.input_label_title.pack(pady=(20, 5))

        self.select_input_button = ctk.CTkButton(
            self,
            text="Browse Input Audio",
            command=self.select_input_file
        )
        self.select_input_button.pack(pady=5)

        self.input_file_label = ctk.CTkLabel(
            self,
            text="No file selected",
            wraplength=600
        )
        self.input_file_label.pack(pady=5)

        # Output Audio Section
        self.output_label_title = ctk.CTkLabel(
            self,
            text="Output Audio:",
            font=("Arial", 12, "bold")
        )
        self.output_label_title.pack(pady=(15, 5))

        self.select_output_button = ctk.CTkButton(
            self,
            text="Browse Output Location",
            command=self.select_output_file
        )
        self.select_output_button.pack(pady=5)

        self.output_file_label = ctk.CTkLabel(
            self,
            text="No output path selected",
            wraplength=600
        )
        self.output_file_label.pack(pady=5)

        self.slider_label = ctk.CTkLabel(
            self,
            text="Silence Threshold: 30"
        )
        self.slider_label.pack(pady=(20, 5))

        self.threshold_slider = ctk.CTkSlider(
            self,
            from_=10,
            to=60,
            number_of_steps=50,
            command=self.slider_changed
        )

        self.threshold_slider.set(30)
        self.threshold_slider.pack(fill="x", padx=40)

        self.process_button = ctk.CTkButton(
            self,
            text="Process Audio",
            height=40,
            command=self.start_processing
        )
        self.process_button.pack(pady=20)

        self.status_label = ctk.CTkLabel(
            self,
            text="Ready"
        )
        self.status_label.pack()

    def slider_changed(self, value):
        self.slider_label.configure(
            text=f"Silence Threshold: {int(value)}"
        )

    def select_input_file(self):

        file = filedialog.askopenfilename(
            filetypes=[
                ("Audio Files", "*.mp3 *.wav"),
                ("All Files", "*.*")
            ]
        )

        if file:
            self.input_path = file
            # Auto-generate output path if not manually set
            if self.output_path == "" or self.output_path.endswith("_cleaned.mp3") or self.output_path.endswith("_cleaned.wav"):
                self.output_path = file.replace(".", "_cleaned.")
                self.output_file_label.configure(
                    text=self.output_path
                )

            self.input_file_label.configure(
                text=file
            )

    def select_output_file(self):

        file = filedialog.asksaveasfilename(
            filetypes=[
                ("MP3 Files", "*.mp3"),
                ("WAV Files", "*.wav"),
                ("All Files", "*.*")
            ],
            defaultextension=".mp3"
        )

        if file:
            self.output_path = file
            self.output_file_label.configure(
                text=file
            )

    def start_processing(self):

        if not self.input_path:
            self.status_label.configure(
                text="Select a file first"
            )
            return

        self.process_button.configure(
            state="disabled"
        )

        self.status_label.configure(
            text="Processing..."
        )

        thread = threading.Thread(
            target=self.process_audio
        )

        thread.start()

    def process_audio(self):

        try:

            remove_silence(
                self.input_path,
                self.output_path,
                int(self.threshold_slider.get()),
                100
            )

            self.after(
                0,
                lambda: self.status_label.configure(
                    text=f"Done: {self.output_path}"
                )
            )

        except Exception as e:

            self.after(
                0,
                lambda: self.status_label.configure(
                    text=str(e)
                )
            )

        finally:

            self.after(
                0,
                lambda: self.process_button.configure(
                    state="normal"
                )
            )


app = App()
app.mainloop()