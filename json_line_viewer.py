import tkinter as tk
from tkinter import ttk, filedialog
import json
import jsonlines
import threading

class JsonLineViewer:
    def __init__(self, master):
        self.master = master
        self.index = 0
        self.loading_text = "Loading..."
        self.loading_done = threading.Event()
        
        self.master.title("JSON Line Viewer")
        
        self.frame = ttk.Frame(master, padding="20")
        self.frame.pack(fill="both", expand=True)
        
        self.label = ttk.Label(self.frame, text="JSON Line Viewer", font=("Segoe UI", 16, "bold"))
        self.label.grid(row=0, column=0, columnspan=5, pady=(0, 10))
        
        self.counter_label = ttk.Label(self.frame, text="")
        self.counter_label.grid(row=1, column=0, columnspan=5, pady=(0, 10))
        
        self.text = tk.Text(self.frame, height=20, width=80, font=('Segoe UI', 12))
        self.text.grid(row=2, column=0, columnspan=5, pady=(0, 10))
        
        self.scrollbar = ttk.Scrollbar(self.frame, orient="vertical", command=self.text.yview)
        self.scrollbar.grid(row=2, column=5, sticky="ns")
        
        self.text.config(yscrollcommand=self.scrollbar.set)
        
        self.prev_button = ttk.Button(self.frame, text="Previous", command=self.prev_json, state=tk.DISABLED)
        self.prev_button.grid(row=3, column=1, pady=5)
        
        self.next_button = ttk.Button(self.frame, text="Next", command=self.next_json, state=tk.DISABLED)
        self.next_button.grid(row=3, column=3, pady=5)
        
        self.choose_file_button = ttk.Button(self.frame, text="Choose File", command=self.choose_file)
        self.choose_file_button.grid(row=4, column=0, columnspan=5, pady=(10, 0))

        self.go_to_label = ttk.Label(self.frame, text="Go to line:")
        self.go_to_label.grid(row=5, column=0, pady=5)

        self.go_to_entry = ttk.Entry(self.frame)
        self.go_to_entry.grid(row=5, column=1, pady=5)

        self.go_to_button = ttk.Button(self.frame, text="Go", command=self.go_to_line)
        self.go_to_button.grid(row=5, column=2, pady=5)
        
    def choose_file(self):
        file_path = filedialog.askopenfilename()
        if file_path:
            self.loading_text = "Loading..."
            self.update_loading_status()
            self.jsonl_file = file_path
            loading_thread = threading.Thread(target=self.load_json)
            loading_thread.start()
    
    def load_json(self):
        try:
            with jsonlines.open(self.jsonl_file) as reader:
                self.json_data = list(reader)
                self.loading_text = ""
        except (jsonlines.jsonlines.InvalidLineError, AttributeError) as e:
            self.json_data = []
            self.loading_text = f"Error loading JSON: {str(e)}"
        finally:
            self.loading_done.set()
            self.update_loading_status()
            self.show_json()
    
    def show_json(self):
        self.text.delete(1.0, tk.END)
        if self.json_data:
            json_object = self.json_data[self.index]
            self.text.insert(tk.END, json.dumps(json_object, indent=4, ensure_ascii=False))
            self.update_counter()
            self.update_button_state()
    
    def update_loading_status(self):
        self.counter_label.config(text=self.loading_text)
    
    def update_counter(self):
        lines_visited = self.index + 1
        lines_left = len(self.json_data) - lines_visited
        self.counter_label.config(text=f"Lines visited: {lines_visited} | Lines left: {lines_left}")
    
    def update_button_state(self):
        if self.index == 0:
            self.prev_button.config(state=tk.DISABLED)
        else:
            self.prev_button.config(state=tk.NORMAL)
        
        if self.index == len(self.json_data) - 1:
            self.next_button.config(state=tk.DISABLED)
        else:
            self.next_button.config(state=tk.NORMAL)
    
    def prev_json(self):
        if self.index > 0:
            self.index -= 1
            self.show_json()
    
    def next_json(self):
        if self.index < len(self.json_data) - 1:
            self.index += 1
            self.show_json()

    def go_to_line(self):
        line_number = int(self.go_to_entry.get())
        if 1 <= line_number <= len(self.json_data):
            self.index = line_number - 1
            self.show_json()

def main():
    root = tk.Tk()
    app = JsonLineViewer(root)
    root.mainloop()

if __name__ == "__main__":
    main()