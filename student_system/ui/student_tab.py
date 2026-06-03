import tkinter as tk
from tkinter import ttk, messagebox
from core import student as repo
from core import program as program_repo
from ui.table_widget import TableWidget

COLUMNS = ["id", "firstname", "lastname", "course", "year", "gender"]


class StudentTab(tk.Frame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self._all_codes = []
        self._build()

    def _build(self):
        self.table = TableWidget(
            self, columns=COLUMNS,
            load_fn=repo.list_all,
            on_select=self._on_row_select,
            page_size=50,
            bg=self["bg"],
        )
        self.table.pack(fill="both", expand=True)

        form_frame = ttk.LabelFrame(self, text="Student Details", padding=10)
        form_frame.pack(fill="x", padx=8, pady=(0, 8))

        self._vars = {
            "id":        tk.StringVar(),
            "firstname": tk.StringVar(),
            "lastname":  tk.StringVar(),
            "course":    tk.StringVar(),
            "year":      tk.StringVar(),
            "gender":    tk.StringVar(),
        }

        # Row 0 — ID, First Name, Last Name
        for col, (lbl, key) in enumerate([("ID (YYYY-NNNN)", "id"),
                                           ("First Name", "firstname"),
                                           ("Last Name", "lastname")]):
            tk.Label(form_frame, text=lbl+":").grid(
                row=0, column=col*2, sticky="e", padx=4, pady=3)
            ttk.Entry(form_frame, textvariable=self._vars[key], width=18).grid(
                row=0, column=col*2+1, sticky="w", padx=4)

        # Row 1 — Course (custom dropdown), Year, Gender
        tk.Label(form_frame, text="Course:").grid(row=1, column=0, sticky="e", padx=4, pady=3)

        self._course_entry = ttk.Entry(form_frame, textvariable=self._vars["course"], width=16)
        self._course_entry.grid(row=1, column=1, sticky="w", padx=4)
        self._dropdown_btn = ttk.Button(form_frame, text="▼", width=2,
                                 command=self._show_all_courses,
                                 padding=(0, 0))
        self._dropdown_btn.grid(row=1, column=1, sticky="e", padx=(0, 4))
        self._vars["course"].trace_add("write", self._filter_courses)
        self._course_entry.bind("<FocusOut>", self._on_entry_focus_out)
        self._course_entry.bind("<Escape>", self._hide_dropdown)
        self._course_entry.bind("<Down>", self._focus_listbox)
        self._course_entry.bind("<FocusIn>", self._show_all_courses)

        # Floating suggestion listbox
        self._listbox_frame = tk.Toplevel(self)
        self._listbox_frame.withdraw()
        self._listbox_frame.overrideredirect(True)
        self.winfo_toplevel().bind("<Button-1>", self._on_global_click, add="+")

        self._listbox = tk.Listbox(
            self._listbox_frame, height=6, width=22,
            font=("Segoe UI", 9), selectbackground="#1a3a5c", selectforeground="white"
        )
        self._listbox.pack()
        self._listbox.bind("<ButtonRelease-1>", self._select_from_listbox)
        self._listbox.bind("<Return>", self._select_from_listbox)
        self._listbox.bind("<Escape>", self._hide_dropdown)
        self._listbox.bind("<FocusOut>", self._on_listbox_focus_out)

        tk.Label(form_frame, text="Year:").grid(row=1, column=2, sticky="e", padx=4)
        ttk.Entry(form_frame, textvariable=self._vars["year"], width=5).grid(
            row=1, column=3, sticky="w", padx=4)

        tk.Label(form_frame, text="Gender:").grid(row=1, column=4, sticky="e", padx=4)
        ttk.Combobox(form_frame, textvariable=self._vars["gender"],
                     values=["Male", "Female", "Other"],
                     width=10, state="readonly").grid(row=1, column=5, sticky="w", padx=4)

        # Buttons
        btn_frame = tk.Frame(self)
        btn_frame.pack(fill="x", padx=8, pady=(0, 8))
        for text, cmd in [("Add", self._add), ("Update", self._update),
                          ("Delete", self._delete), ("Clear", self._clear),
                          ("Refresh Programs", self._refresh_programs)]:
            ttk.Button(btn_frame, text=text, command=cmd).pack(side="left", padx=4)

        self._refresh_programs()

    def on_tab_shown(self):
        """Called when this tab becomes visible. Refreshes the programs dropdown."""
        self._refresh_programs()

    # ── Course autocomplete ───────────────────────────────────────

    def _refresh_programs(self):
        self._all_codes = program_repo.get_all_codes()

    def _filter_courses(self, *_):
        typed = self._vars["course"].get().upper()
        filtered = [c for c in self._all_codes if typed in c] if typed else self._all_codes
    
        self._listbox.delete(0, "end")
        for code in filtered:
            self._listbox.insert("end", code)
    
        # Only show the dropdown if the user is actually typing in the box (has focus)
        if filtered and typed and self.focus_get() == self._course_entry:
            x = self._course_entry.winfo_rootx()
            y = self._course_entry.winfo_rooty() + self._course_entry.winfo_height()
            self._listbox_frame.geometry(f"+{x}+{y}")
            self._listbox_frame.deiconify()
            self._listbox_frame.lift()
        else:
            self._listbox_frame.withdraw()

    def _hide_dropdown(self, *_):
        self._listbox_frame.withdraw()

    def _focus_listbox(self, *_):
        if self._listbox.size() > 0:
            self._listbox.focus_set()
            self._listbox.selection_set(0)

    def _select_from_listbox(self, *_):
        selection = self._listbox.curselection()
        if selection:
            self._vars["course"].set(self._listbox.get(selection[0]))
        self._hide_dropdown()
        self._course_entry.focus_set()

    def _on_entry_focus_out(self, _event):
        # Delay so a listbox click can register before hiding
        self.after(150, self._hide_dropdown)

    def _on_listbox_focus_out(self, _event):
        self.after(150, self._hide_dropdown)

    def _show_all_courses(self, *_):
        self._listbox.delete(0, "end")
        for code in self._all_codes:
            self._listbox.insert("end", code)
        if self._all_codes:
            x = self._course_entry.winfo_rootx()
            y = self._course_entry.winfo_rooty() + self._course_entry.winfo_height()
            self._listbox_frame.geometry(f"+{x}+{y}")
            self._listbox_frame.deiconify()
            self._listbox_frame.lift()
    
    def _on_global_click(self, event):
        widget = event.widget
        if widget not in (self._course_entry, self._listbox, self._dropdown_btn):
            self._hide_dropdown()   
    
    # ── Row selection ──────   ───────────────────────────────────────

    def _on_row_select(self, row: dict):
        for k, v in self._vars.items():
            v.set(row.get(k, ""))

    def _clear(self):
        for v in self._vars.values():
            v.set("")

    # ── CRUD ──────────────────────────────────────────────────────

    def _add(self):
        d = {k: v.get() for k, v in self._vars.items()}
        # Convert "NOT ENROLLED" back to empty string for submission
        d["course"] = "" if d["course"] == "NOT ENROLLED" else d["course"]
        try:
            repo.create(d["id"], d["firstname"], d["lastname"],
                        d["course"], d["year"], d["gender"])
            self.table.refresh()
            self._clear()
            self._refresh_programs()
            messagebox.showinfo("Success", f"Student '{d['id']}' added.")
        except ValueError as e:
            messagebox.showerror("Error", str(e))

    def _update(self):
        d = {k: v.get() for k, v in self._vars.items()}
        # Convert "NOT ENROLLED" back to empty string for submission
        d["course"] = "" if d["course"] == "NOT ENROLLED" else d["course"]
        try:
            repo.update(d["id"], d["firstname"], d["lastname"],
                        d["course"], d["year"], d["gender"])
            self.table.refresh()
            self._refresh_programs()
            messagebox.showinfo("Success", f"Student '{d['id']}' updated.")
        except ValueError as e:
            messagebox.showerror("Error", str(e))

    def _delete(self):
        sid = self._vars["id"].get()
        if not sid:
            messagebox.showwarning("Warning", "Select a student first.")
            return
        if not messagebox.askyesno("Confirm", f"Delete student '{sid}'?"):
            return
        try:
            repo.delete(sid)
            self.table.refresh()
            self._clear()
            self._refresh_programs()
            messagebox.showinfo("Success", f"Student '{sid}' deleted.")
        except ValueError as e:
            messagebox.showerror("Error", str(e))
