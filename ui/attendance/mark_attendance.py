import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import date

DB_FILE = "database.db"

class MarkAttendance(tk.Frame):
    def __init__(self, parent, controller=None):
        super().__init__(parent, bg="white")
        self.controller = controller
        self.attendance_vars = {} # {student_id: StringVar}

        # --- 1. Top Header ---
        header = tk.Frame(self, bg="white")
        header.pack(fill="x", padx=40, pady=(20, 5))
        tk.Label(header, text="Mark Attendance", font=("Segoe UI", 22, "bold"), bg="white", fg="#0f172a").pack(anchor="w")
        tk.Label(header, text="Record student attendance for today", font=("Segoe UI", 10), bg="white", fg="#64748b").pack(anchor="w")

        # --- 2. Fixed Filter Section ---
        filter_card = tk.Frame(self, bg="white", highlightthickness=1, highlightbackground="#e2e8f0", padx=20, pady=15)
        filter_card.pack(fill="x", padx=40, pady=10)

        # Labels & Combos in Grid
        tk.Label(filter_card, text="Course", font=("Segoe UI", 9, "bold"), bg="white", fg="#475569").grid(row=0, column=0, sticky="w", padx=10)
        self.course_var = tk.StringVar()
        self.course_combo = ttk.Combobox(filter_card, textvariable=self.course_var, state="readonly", width=25)
        self.course_combo.grid(row=1, column=0, padx=10, pady=5)
        self.course_combo.bind("<<ComboboxSelected>>", self.load_subjects)

        tk.Label(filter_card, text="Subject", font=("Segoe UI", 9, "bold"), bg="white", fg="#475569").grid(row=0, column=1, sticky="w", padx=10)
        self.subject_var = tk.StringVar()
        self.subject_combo = ttk.Combobox(filter_card, textvariable=self.subject_var, state="readonly", width=25)
        self.subject_combo.grid(row=1, column=1, padx=10, pady=5)
        self.subject_combo.bind("<<ComboboxSelected>>", self.refresh_student_list)

        tk.Label(filter_card, text="Date", font=("Segoe UI", 9, "bold"), bg="white", fg="#475569").grid(row=0, column=2, sticky="w", padx=10)
        self.date_var = tk.StringVar(value=date.today().strftime("%d/%m/%Y"))
        tk.Entry(filter_card, textvariable=self.date_var, font=("Segoe UI", 10), bg="white", highlightthickness=1, highlightbackground="#e2e8f0", width=20).grid(row=1, column=2, padx=10, pady=5, ipady=3)

        # Mark All Present/Absent Buttons
        bulk_f = tk.Frame(filter_card, bg="white")
        bulk_f.grid(row=2, column=0, columnspan=3, sticky="w", pady=(10, 0), padx=10)
        tk.Button(bulk_f, text="Mark All Present", bg="#dcfce7", fg="#166534", relief="flat", font=("Segoe UI", 8, "bold"), padx=12, pady=4, command=lambda: self.bulk_mark("Present")).pack(side="left", padx=(0, 10))
        tk.Button(bulk_f, text="Mark All Absent", bg="#fee2e2", fg="#991b1b", relief="flat", font=("Segoe UI", 8, "bold"), padx=12, pady=4, command=lambda: self.bulk_mark("Absent")).pack(side="left")

        # --- 3. Table Header (Sticky Below Filters) ---
        t_header = tk.Frame(self, bg="#f1f5f9")
        t_header.pack(fill="x", padx=40, pady=(10, 0))
        for i in range(5): t_header.columnconfigure(i, weight=1, uniform="att")
        heads = [("ROLL NO.", 0), ("STUDENT NAME", 1), ("PRESENT", 2), ("ABSENT", 3), ("LEAVE", 4)]
        for txt, col in heads:
            tk.Label(t_header, text=txt, font=("Segoe UI", 9, "bold"), bg="#f1f5f9", fg="#475569", anchor="w", padx=15, pady=10).grid(row=0, column=col, sticky="nsew")

        # --- 4. Scrollable List (Middle Section Only) ---
        self.list_container = tk.Frame(self, bg="white")
        self.list_container.pack(fill="both", expand=True, padx=40)
        
        self.canvas = tk.Canvas(self.list_container, bg="white", highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self.list_container, orient="vertical", command=self.canvas.yview)
        self.scroll_frame = tk.Frame(self.canvas, bg="white")
        
        self.scroll_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas_win = self.canvas.create_window((0, 0), window=self.scroll_frame, anchor="nw")
        self.canvas.bind('<Configure>', lambda e: self.canvas.itemconfig(self.canvas_win, width=e.width))
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        
        # Mouse Wheel Support
        self.canvas.bind_all("<MouseWheel>", lambda e: self.canvas.yview_scroll(int(-1*(e.delta/120)), "units"))

        # --- 5. FIXED BOTTOM ACTION BAR (Submit Button) ---
        # यह हिस्सा कभी नहीं हिलेगा, हमेशा नीचे रहेगा
        footer = tk.Frame(self, bg="white", highlightthickness=1, highlightbackground="#f1f5f9", pady=15)
        footer.pack(fill="x", side="bottom")

        # Live Counts
        self.stats_lbl = tk.Label(footer, text="Present: 0   Absent: 0   Leave: 0", font=("Segoe UI", 10, "bold"), bg="white", fg="#475569")
        self.stats_lbl.pack(side="left", padx=40)

        # Blue Save Button (Exactly like image)
        tk.Button(footer, text="💾 Save Attendance", bg="#2563eb", fg="white", font=("Segoe UI", 10, "bold"), 
                  relief="flat", padx=30, pady=10, cursor="hand2", command=self.save_data).pack(side="right", padx=40)
        
        tk.Button(footer, text="Cancel", bg="#f1f5f9", fg="#475569", font=("Segoe UI", 10), 
                  relief="flat", padx=20, pady=10, cursor="hand2").pack(side="right")

        self.load_courses()

    def load_courses(self):
        try:
            conn = sqlite3.connect(DB_FILE)
            cur = conn.cursor()
            cur.execute("SELECT course_name FROM course")
            self.course_combo['values'] = [r[0] for r in cur.fetchall()]
            conn.close()
        except: pass

    def load_subjects(self, e=None):
        course = self.course_var.get()
        try:
            conn = sqlite3.connect(DB_FILE)
            cur = conn.cursor()
            cur.execute("SELECT subject_name FROM subjects WHERE course=?", (course,))
            self.subject_combo['values'] = [r[0] for r in cur.fetchall()]
            conn.close()
        except: pass

    def refresh_student_list(self, e=None):
        for widget in self.scroll_frame.winfo_children(): widget.destroy()
        self.attendance_vars = {}
        course = self.course_var.get()
        
        try:
            conn = sqlite3.connect(DB_FILE)
            cur = conn.cursor()
            cur.execute("SELECT roll, first || ' ' || last, id FROM students WHERE course=?", (course,))
            rows = cur.fetchall()
            conn.close()

            for roll, name, sid in rows:
                row = tk.Frame(self.scroll_frame, bg="white", highlightthickness=1, highlightbackground="#f8fafc")
                row.pack(fill="x", pady=0)
                for i in range(5): row.columnconfigure(i, weight=1, uniform="att")

                tk.Label(row, text=roll, font=("Segoe UI", 9, "bold"), bg="white", anchor="w", padx=15, pady=18).grid(row=0, column=0, sticky="nsew")
                tk.Label(row, text=name, font=("Segoe UI", 10), bg="white", anchor="w", padx=15).grid(row=0, column=1, sticky="nsew")

                var = tk.StringVar(value="Present")
                self.attendance_vars[sid] = (var, name, roll)
                
                # Selection Dots (Image Style)
                for i, val in enumerate(["Present", "Absent", "Leave"]):
                    rb = tk.Radiobutton(row, variable=var, value=val, bg="white", activebackground="white", command=self.update_stats)
                    rb.grid(row=0, column=i+2)

            self.update_stats()
        except: pass

    def update_stats(self):
        p, a, l = 0, 0, 0
        for v, n, r in self.attendance_vars.values():
            val = v.get()
            if val == "Present": p += 1
            elif val == "Absent": a += 1
            else: l += 1
        self.stats_lbl.config(text=f"Present: {p}   Absent: {a}   Leave: {l}")

    def bulk_mark(self, status):
        for v, n, r in self.attendance_vars.values(): v.set(status)
        self.update_stats()

    def save_data(self):
        sub = self.subject_var.get()
        dt = self.date_var.get()
        course = self.course_var.get() # Course bhi uthao
        
        if not sub: return messagebox.showwarning("Error", "Select Subject!")

        try:
            conn = sqlite3.connect(DB_FILE)
            cur = conn.cursor()

            # Purani attendance delete karo taaki duplicate na ho
            cur.execute("DELETE FROM attendance WHERE subject=? AND date=? AND course=?", (sub, dt, course))

            for sid, (var, name, roll) in self.attendance_vars.items():
                # Note: Hum student_id, name, subject, date, status, course aur roll_no sab save kar rahe hain
                cur.execute("""INSERT INTO attendance 
                               (student_id, student_name, subject, date, status, course, roll_no) 
                               VALUES (?,?,?,?,?,?,?)""",
                            (sid, name, sub, dt, var.get(), course, roll))
            
            conn.commit()
            conn.close()
            messagebox.showinfo("Success", "Attendance Saved Successfully!")
        except Exception as e: 
            messagebox.showerror("Error", f"Save Failed: {e}")