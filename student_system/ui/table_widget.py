import tkinter as tk
from tkinter import ttk


class TableWidget(tk.Frame):
    def __init__(self, parent, columns: list[str], load_fn,
                 on_select=None, page_size: int = 50, **kwargs):
        """
        columns   : list of column field keys
        load_fn   : callable(sort_by, reverse, search, page, page_size)
                    -> (list[dict], total_count)
        on_select : optional callback(selected_row_dict)
        page_size : rows per page
        """
        super().__init__(parent, **kwargs)
        self.columns = columns
        self.load_fn = load_fn
        self.on_select = on_select
        self.page_size = page_size
        self._sort_col = columns[0]
        self._sort_rev = False
        self._page = 1
        self._total = 0

        self._build()
        self.refresh()

    def _build(self):
        # ── Search bar ──────────────────────────────────────────
        top = tk.Frame(self, bg=self["bg"])
        top.pack(fill="x", padx=8, pady=(8, 4))

        tk.Label(top, text="Search:", bg=self["bg"],
                 font=("Segoe UI", 10)).pack(side="left")
        self._search_var = tk.StringVar()
        self._search_var.trace_add("write", lambda *_: self._on_search())
        ttk.Entry(top, textvariable=self._search_var, width=30).pack(side="left", padx=6)
        ttk.Button(top, text="Clear", command=self._clear_search).pack(side="left")

        # Row count label
        self._count_label = tk.Label(top, text="", bg=self["bg"],
                                     font=("Segoe UI", 9), fg="#555")
        self._count_label.pack(side="right", padx=8)

        # ── Treeview ─────────────────────────────────────────────
        tree_frame = tk.Frame(self)
        tree_frame.pack(fill="both", expand=True, padx=8)

        self.tree = ttk.Treeview(tree_frame, columns=self.columns,
                                 show="headings", selectmode="browse")
        for col in self.columns:
            self.tree.heading(col, text=col.capitalize(),
                              command=lambda c=col: self._sort(c))
            self.tree.column(col, anchor="w", minwidth=60, width=130)

        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(tree_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        tree_frame.rowconfigure(0, weight=1)
        tree_frame.columnconfigure(0, weight=1)

        self.tree.bind("<<TreeviewSelect>>", self._on_select_event)

        # ── Pagination bar ────────────────────────────────────────
        pag = tk.Frame(self, bg=self["bg"])
        pag.pack(fill="x", padx=8, pady=(4, 8))

        self._first_btn  = ttk.Button(pag, text="|<", width=3, command=self._go_first)
        self._prev_btn   = ttk.Button(pag, text="<",  width=3, command=self._go_prev)
        self._next_btn   = ttk.Button(pag, text=">",  width=3, command=self._go_next)
        self._last_btn   = ttk.Button(pag, text=">|", width=3, command=self._go_last)

        self._first_btn.pack(side="left", padx=2)
        self._prev_btn.pack(side="left", padx=2)
        self._next_btn.pack(side="left", padx=2)
        self._last_btn.pack(side="left", padx=2)

        self._page_label = tk.Label(pag, text="", bg=self["bg"],
                                    font=("Segoe UI", 9))
        self._page_label.pack(side="left", padx=10)

        # Page size selector
        tk.Label(pag, text="Rows/page:", bg=self["bg"],
                 font=("Segoe UI", 9)).pack(side="right", padx=(0, 4))
        self._page_size_var = tk.StringVar(value=str(self.page_size))
        ps_combo = ttk.Combobox(pag, textvariable=self._page_size_var,
                                values=["25", "50", "100", "200"],
                                width=5, state="readonly")
        ps_combo.pack(side="right", padx=2)
        ps_combo.bind("<<ComboboxSelected>>", self._on_page_size_change)

    # ── Internal helpers ─────────────────────────────────────────

    def _on_search(self):
        self._page = 1
        self.refresh()

    def _clear_search(self):
        self._search_var.set("")

    def _sort(self, col: str):
        if self._sort_col == col:
            self._sort_rev = not self._sort_rev
        else:
            self._sort_col = col
            self._sort_rev = False
        self._page = 1
        self.refresh()

    def _on_page_size_change(self, _event=None):
        self.page_size = int(self._page_size_var.get())
        self._page = 1
        self.refresh()

    def _go_first(self):  self._page = 1;                    self.refresh()
    def _go_prev(self):   self._page = max(1, self._page-1); self.refresh()
    def _go_next(self):   self._page = min(self._max_page(), self._page+1); self.refresh()
    def _go_last(self):   self._page = self._max_page();     self.refresh()

    def _max_page(self) -> int:
        import math
        return max(1, math.ceil(self._total / self.page_size))

    # ── Public ───────────────────────────────────────────────────

    def refresh(self):
        search = self._search_var.get().strip()
        try:
            rows, total = self.load_fn(
                sort_by=self._sort_col,
                reverse=self._sort_rev,
                search=search,
                page=self._page,
                page_size=self.page_size,
            )
            self._total = total
        except Exception as e:
            rows, self._total = [], 0
            print(f"[TableWidget] load error: {e}")

        for item in self.tree.get_children():
            self.tree.delete(item)
        for row in rows:
            self.tree.insert("", "end", values=[row.get(c, "") for c in self.columns])

        # Update headers with sort arrows
        for col in self.columns:
            arrow = (" ▼" if self._sort_rev else " ▲") if col == self._sort_col else ""
            self.tree.heading(col, text=col.capitalize() + arrow)

        # Update pagination info
        max_p = self._max_page()
        self._page = min(self._page, max_p)
        self._page_label.config(text=f"Page {self._page} of {max_p}")
        self._count_label.config(text=f"{self._total} record(s)")

        self._first_btn.config(state="disabled" if self._page <= 1 else "normal")
        self._prev_btn.config(state="disabled" if self._page <= 1 else "normal")
        self._next_btn.config(state="disabled" if self._page >= max_p else "normal")
        self._last_btn.config(state="disabled" if self._page >= max_p else "normal")

    def get_selected(self) -> dict | None:
        sel = self.tree.selection()
        if not sel:
            return None
        values = self.tree.item(sel[0], "values")
        return dict(zip(self.columns, values))

    def _on_select_event(self, _event):
        if self.on_select:
            row = self.get_selected()
            if row:
                self.on_select(row)
