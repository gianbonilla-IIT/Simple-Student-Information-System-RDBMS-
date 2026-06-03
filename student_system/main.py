import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

import tkinter as tk
from tkinter import ttk

from core.database import initialize_schema
from core.seeder import seed
from ui.college_tab import CollegeTab
from ui.program_tab import ProgramTab
from ui.student_tab import StudentTab


def main():
    # Initialize DB and seed data before opening the window
    initialize_schema()
    seed()

    root = tk.Tk()
    root.title("Student Information System")
    root.geometry("980x660")
    root.minsize(800, 520)

    # Center on screen
    root.update_idletasks()
    x = (root.winfo_screenwidth()  // 2) - (980 // 2)
    y = (root.winfo_screenheight() // 2) - (660 // 2)
    root.geometry(f"980x660+{x}+{y}")

    # Style
    style = ttk.Style(root)
    style.theme_use("clam")
    style.configure("TNotebook.Tab", font=("Segoe UI", 10, "bold"), padding=[12, 5])
    style.configure("TFrame", background="#f0f4f8")
    style.configure("TLabelframe", background="#f0f4f8")
    style.configure("TLabelframe.Label", font=("Segoe UI", 10, "bold"), background="#f0f4f8")
    style.configure("Treeview.Heading", font=("Segoe UI", 9, "bold"))

    # Header
    header = tk.Frame(root, bg="#1a3a5c", height=50)
    header.pack(fill="x")
    tk.Label(header, text="Student Information System",
             bg="#1a3a5c", fg="white",
             font=("Segoe UI", 14, "bold"), pady=10).pack(side="left", padx=16)

    # Tabs
    notebook = ttk.Notebook(root)
    notebook.pack(fill="both", expand=True, padx=8, pady=8)

    bg = "#f0f4f8"
    college_tab = CollegeTab(notebook, bg=bg)
    program_tab = ProgramTab(notebook, bg=bg)
    student_tab = StudentTab(notebook, bg=bg)
    
    notebook.add(college_tab, text="  Colleges  ")
    notebook.add(program_tab, text="  Programs  ")
    notebook.add(student_tab, text="  Students  ")
    
    # Refresh dropdowns when tabs are shown
    def on_tab_changed(event):
        tab_index = notebook.index(notebook.select())
        if tab_index == 1:  # Programs tab
            program_tab.on_tab_shown()
        elif tab_index == 2:  # Students tab
            student_tab.on_tab_shown()
    
    notebook.bind("<<NotebookTabChanged>>", on_tab_changed)

    # Status bar
    tk.Label(root, text="Database: data/student_system.db  |  SQLite",
             anchor="w", bd=1, relief="sunken",
             font=("Segoe UI", 8), bg="#dde4ed", fg="#444").pack(fill="x", side="bottom")

    root.mainloop()


if __name__ == "__main__":
    main()
