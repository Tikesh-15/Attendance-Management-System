import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3

DB_FILE = "database.db"

class ManageSubject(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="white")
        self.controller = controller

        # --- 1. Header (Modern Style) ---
        header = tk.Frame(self, bg="white")
        header.pack(fill="x", padx=40, pady=(30, 10))
        tk.Label(header, text="Manage Subjects", font=("Segoe UI", 24, "bold"), bg="white", fg="#0f172a").pack(anchor="w")
        tk.Label(header, text="Assign and manage courses for college staff", font=("Segoe UI", 11), bg="white", fg="#64748b").pack(anchor="w")

        # --- 2. Toolbar ---
        toolbar = tk.Frame(self, bg="white")
        toolbar.pack(fill="x", padx=40, pady=20)
        
        search_bg = tk.Frame(toolbar, bg="#f8fafc", highlightthickness=1, highlightbackground="#e2e8f0")
        search_bg.pack(side="left", ipady=2)
        tk.Label(search_bg, text="  🔍  ", bg="#f8fafc", fg="#94a3b8", font=("Segoe UI", 12)).pack(side="left")
        
        self.search_var = tk.StringVar()
        tk.Entry(search_bg, textvariable=self.search_var, font=("Segoe UI", 11), bd=0, bg="#f8fafc", width=35).pack(side="left", padx=10, ipady=8)
        self.search_var.trace_add("write", lambda *args: self.refresh_data())

        # + Add Subject Button (Using show_page)
        tk.Button(toolbar, text="+ Add Subject", bg="#2563eb", fg="white", font=("Segoe UI", 10, "bold"), 
                  relief="flat", padx=20, pady=8, cursor="hand2", command=self.open_add_subject).pack(side="right")

        # --- 3. FIXED HEADERS ---
        self.header_frame = tk.Frame(self, bg="#f1f5f9")
        self.header_frame.pack(fill="x", padx=40)

        self.grid_cols = [
            ("ID", 0), ("SUBJECT NAME", 1), ("COURSE", 2), ("STAFF NAME", 3), ("ACTIONS", 4)
        ]
        for i in range(5):
            self.header_frame.columnconfigure(i, weight=1, uniform="sub_group")

        for text, col in self.grid_cols:
            tk.Label(self.header_frame, text=text, font=("Segoe UI", 10, "bold"), 
                     bg="#f1f5f9", fg="#475569", anchor="w", padx=15, pady=12).grid(row=0, column=col, sticky="nsew")

        # --- 4. Scrollable Content Area ---
        container = tk.Frame(self, bg="white")
        container.pack(fill="both", expand=True, padx=40, pady=(0, 20))
        self.canvas = tk.Canvas(container, bg="white", highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(container, orient="vertical", command=self.canvas.yview)
        self.scroll_frame = tk.Frame(self.canvas, bg="white")
        self.scroll_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas_window = self.canvas.create_window((0, 0), window=self.scroll_frame, anchor="nw")
        self.canvas.bind('<Configure>', lambda e: self.canvas.itemconfig(self.canvas_window, width=e.width))
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        self.refresh_data()

    def refresh_data(self):
        """Database se data fetch karna"""
        for widget in self.scroll_frame.winfo_children(): widget.destroy()
        search_q = self.search_var.get().lower()

        try:
            conn = sqlite3.connect(DB_FILE)
            cur = conn.cursor()
            # Query updated to fetch staff names via LEFT JOIN
            cur.execute("""
                SELECT subjects.id, subjects.subject_name, subjects.course, (staff.first || ' ' || staff.last)
                FROM subjects
                LEFT JOIN staff ON subjects.staff_id = staff.id
            """)
            rows = cur.fetchall()
            conn.close()

            for row in rows:
                if search_q in str(row[1]).lower() or search_q in str(row[2]).lower():
                    self.create_row(row)
        except Exception as e: 
            print(f"Load Error: {e}")

    def create_row(self, data):
        """Har row ka design"""
        row_f = tk.Frame(self.scroll_frame, bg="white", highlightthickness=1, highlightbackground="#f1f5f9")
        row_f.pack(fill="x", pady=1)
        for i in range(5): row_f.columnconfigure(i, weight=1, uniform="sub_group")

        tk.Label(row_f, text=data[0], font=("Segoe UI", 9), bg="white", anchor="w", padx=15, pady=15).grid(row=0, column=0, sticky="nsew")
        tk.Label(row_f, text=data[1], font=("Segoe UI", 10, "bold"), bg="white", anchor="w", padx=15).grid(row=0, column=1, sticky="nsew")
        tk.Label(row_f, text=data[2], font=("Segoe UI", 9), bg="white", anchor="w", padx=15).grid(row=0, column=2, sticky="nsew")
        tk.Label(row_f, text=data[3] if data[3] else "N/A", font=("Segoe UI", 9), bg="white", anchor="w", padx=15).grid(row=0, column=3, sticky="nsew")

        # Action Buttons
        btn_f = tk.Frame(row_f, bg="white")
        btn_f.grid(row=0, column=4, sticky="nsew")
        
        # Edit Button (Using edit_subject logic)
        tk.Button(btn_f, text="EDIT", font=("Segoe UI", 8, "bold"), fg="#2563eb", bg="#eff6ff", 
                  relief="flat", padx=10, pady=5, cursor="hand2", command=lambda d=data: self.edit_subject(d)).pack(side="left", padx=(15, 5), pady=12)
        
        # Delete Button
        tk.Button(btn_f, text="DELETE", font=("Segoe UI", 8, "bold"), fg="#dc2626", bg="#fef2f2", 
                  relief="flat", padx=10, pady=5, cursor="hand2", command=lambda d=data[0]: self.delete_subject(d)).pack(side="left", padx=5, pady=12)

    def open_add_subject(self):
        """Add Subject frame par switch karna (Course page jaisa logic)"""
        try:
            from ui.subject.add_subject import AddSubject
            self.controller.show_page(AddSubject)
        except Exception as e:
            messagebox.showerror("Nav Error", f"AddSubject page error: {e}")

    def edit_subject(self, data_tuple):
        """Subject edit karne ke liye full data fetch karke bhej dena"""
        try:
            from ui.subject.add_subject import AddSubject
            conn = sqlite3.connect(DB_FILE)
            cur = conn.cursor()
            # Pure columns fetch karein edit form ke liye
            cur.execute("SELECT * FROM subjects WHERE id=?", (data_tuple[0],))
            full_data = cur.fetchone()
            conn.close()

            if full_data:
                # show_page use karein edit_data bhejte hue
                self.controller.show_frame(AddSubject, edit_data=full_data)
        except Exception as e:
            messagebox.showerror("Error", f"Edit Failed: {e}")

    def delete_subject(self, sid):
        if messagebox.askyesno("Confirm", "Delete this subject?"):
            try:
                conn = sqlite3.connect(DB_FILE)
                cur = conn.cursor()
                cur.execute("DELETE FROM subjects WHERE id=?", (sid,))
                conn.commit()
                conn.close()
                self.refresh_data()
            except Exception as e:
                messagebox.showerror("Error", f"Delete Failed: {e}")