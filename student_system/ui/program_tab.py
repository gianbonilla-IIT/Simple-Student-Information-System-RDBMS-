"""
program_tab.py
UI tab for Program CRUDL operations.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from core import program as repo
from core import college as college_repo
from ui.table_widget import TableWidget

COLUMNS = ["name", "code", "college"]


class ProgramTab(tk.Frame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self._build()

    def _build(self):
        self.table = TableWidget(
            self, columns=COLUMNS,
            load_fn=repo.list_all,
            on_select=self._on_row_select,
            bg=self["bg"],
        )
        self.table.pack(fill="both", expand=True)

        form_frame = ttk.LabelFrame(self, text="Program Details", padding=10)
        form_frame.pack(fill="x", padx=8, pady=(0, 8))

        self._vars = {
            "name": tk.StringVar(),
            "code": tk.StringVar(),
            "college": tk.StringVar(),
        }

        tk.Label(form_frame, text="Name:").grid(row=0, column=0, sticky="e", padx=4)
        ttk.Entry(form_frame, textvariable=self._vars["name"], width=40).grid(
            row=0, column=1, sticky="w", padx=4)

        tk.Label(form_frame, text="Code:").grid(row=0, column=2, sticky="e", padx=4)
        ttk.Entry(form_frame, textvariable=self._vars["code"], width=12).grid(
            row=0, column=3, sticky="w", padx=4)

        tk.Label(form_frame, text="College:").grid(row=0, column=4, sticky="e", padx=4)
        self._college_combo = ttk.Combobox(
            form_frame, textvariable=self._vars["college"], width=10, state="readonly")
        self._college_combo.grid(row=0, column=5, sticky="w", padx=4)
        self._refresh_colleges()

        btn_frame = tk.Frame(self)
        btn_frame.pack(fill="x", padx=8, pady=(0, 8))
        for text, cmd in [("Add", self._add), ("Update", self._update),
                          ("Delete", self._delete), ("Clear", self._clear),
                          ("Refresh Colleges", self._refresh_colleges)]:
            ttk.Button(btn_frame, text=text, command=cmd).pack(side="left", padx=4)

    def _refresh_colleges(self):
        colleges, _ = college_repo.list_all(page_size=200)
        self._college_combo["values"] = [c["code"] for c in colleges]

    def _on_row_select(self, row: dict):
        for k, v in self._vars.items():
            v.set(row.get(k, ""))

    def _clear(self):
        for v in self._vars.values():
            v.set("")

    def _add(self):
        try:
            repo.create(self._vars["code"].get(), self._vars["name"].get(),
                        self._vars["college"].get())
            self.table.refresh()
            self._clear()
            messagebox.showinfo("Success", "Program added.")
        except ValueError as e:
            messagebox.showerror("Error", str(e))

    def _update(self):
        try:
            repo.update(self._vars["code"].get(), self._vars["name"].get(),
                        self._vars["college"].get())
            self.table.refresh()
            messagebox.showinfo("Success", "Program updated.")
        except ValueError as e:
            messagebox.showerror("Error", str(e))

    def _delete(self):
        code = self._vars["code"].get()
        if not code:
            messagebox.showwarning("Warning", "Select a program first.")
            return
        if not messagebox.askyesno("Confirm", f"Delete program '{code}'?"):
            return
        try:
            repo.delete(code)
            self.table.refresh()
            self._clear()
            messagebox.showinfo("Success", "Program deleted.")
        except ValueError as e:
            messagebox.showerror("Error", str(e))
