import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3

DB_FILE = "database.db" 

class ManageStudent(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="white")
        self.controller = controller

        # --- 1. Header ---
        header = tk.Frame(self, bg="white")
        header.pack(fill="x", padx=40, pady=(30, 10))
        tk.Label(header, text="Manage Students", font=("Segoe UI", 26, "bold"), bg="white", fg="#0f172a").pack(anchor="w")
        tk.Label(header, text="Government V.Y.T. PG Autonomous College, Durg", font=("Segoe UI", 11), bg="white", fg="#64748b").pack(anchor="w")

        # --- 2. Toolbar (Search & Filter) ---
        toolbar = tk.Frame(self, bg="white")
        toolbar.pack(fill="x", padx=40, pady=20)

        # Search box
        search_bg = tk.Frame(toolbar, bg="#f8fafc", highlightthickness=1, highlightbackground="#e2e8f0")
        search_bg.pack(side="left", ipady=2)
        tk.Label(search_bg, text="  🔍  ", bg="#f8fafc", fg="#94a3b8", font=("Segoe UI", 12)).pack(side="left")
        
        self.search_var = tk.StringVar()
        self.search_ent = tk.Entry(search_bg, textvariable=self.search_var, font=("Segoe UI", 11), bd=0, bg="#f8fafc", width=35)
        self.search_ent.pack(side="left", padx=10, ipady=8)
        self.search_ent.insert(0, "Search by name or roll...")
        self.search_ent.bind("<FocusIn>", lambda e: self.search_ent.delete(0, tk.END) if self.search_var.get() == "Search by name or roll..." else None)

        # Course Filter
        self.filter_var = tk.StringVar(value="All Courses")
        self.filter_cb = ttk.Combobox(toolbar, textvariable=self.filter_var, state="readonly", width=20, font=("Segoe UI", 10))
        self.filter_cb.pack(side="right", padx=10)

        # --- 3. FIXED HEADERS ---
        self.header_frame = tk.Frame(self, bg="#f1f5f9")
        self.header_frame.pack(fill="x", padx=40)

        self.cols_config = [
            ("ROLL NO.", 0), ("STUDENT NAME", 1), ("COURSE", 2), 
            ("PHONE", 3), ("STATUS", 4), ("ACTIONS", 5)
        ]

        for i in range(6):
            self.header_frame.columnconfigure(i, weight=1, uniform="group1")

        for text, col in self.cols_config:
            tk.Label(self.header_frame, text=text, font=("Segoe UI", 10, "bold"), 
                     bg="#f1f5f9", fg="#475569", anchor="w", padx=15, pady=12).grid(row=0, column=col, sticky="nsew")

        # --- 4. Scrollable Data Area ---
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

        # Binds
        self.search_var.trace_add("write", lambda *args: self.refresh_data())
        self.filter_cb.bind("<<ComboboxSelected>>", lambda e: self.refresh_data())

        self.load_courses()
        self.refresh_data()

    def load_courses(self):
        try:
            conn = sqlite3.connect(DB_FILE)
            cur = conn.cursor()
            cur.execute("SELECT course_name FROM course")
            self.filter_cb['values'] = ["All Courses"] + [r[0] for r in cur.fetchall()]
            conn.close()
        except: self.filter_cb['values'] = ["All Courses"]

    def refresh_data(self):
        """Search और Filter के हिसाब से डेटा दिखाना"""
        for widget in self.scroll_frame.winfo_children(): widget.destroy()
        
        search_q = self.search_var.get().lower()
        if search_q == "search by name or roll...": search_q = ""
        course_f = self.filter_var.get()

        try:
            conn = sqlite3.connect(DB_FILE)
            cur = conn.cursor()
            cur.execute("SELECT roll, first || ' ' || last, course, phone, id FROM students")
            rows = cur.fetchall()
            conn.close()

            for row in rows:
                roll, name, course, phone, s_id = row
                if (search_q in str(roll).lower() or search_q in name.lower()):
                    if course_f == "All Courses" or course == course_f:
                        self.create_row(roll, name, course, phone, s_id)
        except Exception as e: print(f"Error: {e}")

    def create_row(self, roll, name, course, phone, s_id):
        row_container = tk.Frame(self.scroll_frame, bg="white", highlightthickness=1, highlightbackground="#f1f5f9")
        row_container.pack(fill="x", pady=1)

        for i in range(6):
            row_container.columnconfigure(i, weight=1, uniform="group1")

        tk.Label(row_container, text=roll, font=("Segoe UI", 9, "bold"), bg="white", anchor="w", padx=15, pady=15).grid(row=0, column=0, sticky="nsew")
        tk.Label(row_container, text=name, font=("Segoe UI", 10), bg="white", anchor="w", padx=15).grid(row=0, column=1, sticky="nsew")
        tk.Label(row_container, text=course, font=("Segoe UI", 9), bg="white", anchor="w", padx=15).grid(row=0, column=2, sticky="nsew")
        tk.Label(row_container, text=phone, font=("Segoe UI", 9), bg="white", anchor="w", padx=15).grid(row=0, column=3, sticky="nsew")

        # Status
        st_f = tk.Frame(row_container, bg="white")
        st_f.grid(row=0, column=4, sticky="nsew")
        tk.Label(st_f, text="Active", font=("Segoe UI", 8, "bold"), bg="#dcfce7", fg="#166534", padx=12, pady=2).pack(pady=12, padx=15, anchor="w")

        # Actions
        btn_f = tk.Frame(row_container, bg="white")
        btn_f.grid(row=0, column=5, sticky="nsew")
        
        # ✅ EDIT Button Logic
        tk.Button(btn_f, text="EDIT", font=("Segoe UI", 8, "bold"), fg="#2563eb", bg="#eff6ff", 
                  relief="flat", padx=10, pady=5, cursor="hand2", 
                  command=lambda sid=s_id: self.edit_student(sid)).pack(side="left", padx=(15, 5), pady=12)

        tk.Button(btn_f, text="DELETE", font=("Segoe UI", 8, "bold"), fg="#dc2626", bg="#fef2f2", 
                  relief="flat", padx=10, pady=5, cursor="hand2", 
                  command=lambda sid=s_id: self.del_std(sid)).pack(side="left", padx=5, pady=12)

    def edit_student(self, sid):
        try:
            app = self.winfo_toplevel()
            # 1. AddStudent ka object nikalo
            add_page = app.get_page("AddStudent")
            
            if add_page:
                # 2. AddStudent page ke andar ye function call karo (Data bharne ke liye)
                add_page.fill_form_for_edit(sid)
                # 3. Phir page switch karo
                app.show_frame("AddStudent")
        except Exception as e:
            messagebox.showerror("Error", f"Navigation failed: {e}")
    def del_std(self, sid):
        if messagebox.askyesno("Confirm", "Bhai, Student delete karoge toh uski attendance bhi ud jayegi. Pakka?"):
            conn = sqlite3.connect(DB_FILE)
            cur = conn.cursor()
            # 1. Pehle attendance udao
            cur.execute("DELETE FROM attendance WHERE student_id=?", (sid,))
            # 2. Phir student udao
            cur.execute("DELETE FROM students WHERE id=?", (sid,))
            conn.commit()
            conn.close()
            self.refresh_data()