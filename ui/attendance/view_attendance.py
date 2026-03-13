import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import date

DB_FILE = "database.db"

class ViewAttendance(tk.Frame):
    def __init__(self, parent, controller=None):
        super().__init__(parent, bg="white")
        self.controller = controller

        # --- Header ---
        header = tk.Frame(self, bg="white")
        header.pack(fill="x", padx=40, pady=(30, 10))
        tk.Label(header, text="View Attendance Register", font=("Segoe UI", 24, "bold"), bg="white", fg="#0f172a").pack(anchor="w")
        tk.Label(header, text="Search and analyze student presence", font=("Segoe UI", 11), bg="white", fg="#64748b").pack(anchor="w")

        # --- Stats Cards ---
        stats_frame = tk.Frame(self, bg="white")
        stats_frame.pack(fill="x", padx=40, pady=10)
        self.total_card = self.create_stat_card(stats_frame, "Total Records", "0", "#0f172a", 0)
        self.present_card = self.create_stat_card(stats_frame, "Present", "0", "#10b981", 1)
        self.absent_card = self.create_stat_card(stats_frame, "Absent", "0", "#ef4444", 2)
        self.leave_card = self.create_stat_card(stats_frame, "On Leave", "0", "#f59e0b", 3)

        # --- Filter Section ---
        filter_card = tk.Frame(self, bg="white", highlightthickness=1, highlightbackground="#e2e8f0", padx=20, pady=20)
        filter_card.pack(fill="x", padx=40, pady=20)

        tk.Label(filter_card, text="Date (DD/MM/YYYY)", font=("Segoe UI", 9, "bold"), bg="white", fg="#475569").grid(row=0, column=0, sticky="w", padx=10)
        self.date_var = tk.StringVar(value=date.today().strftime("%d/%m/%Y"))
        tk.Entry(filter_card, textvariable=self.date_var, font=("Segoe UI", 10), bg="white", highlightthickness=1, highlightbackground="#e2e8f0", width=18).grid(row=1, column=0, padx=10, pady=5, ipady=4)

        tk.Label(filter_card, text="Course", font=("Segoe UI", 9, "bold"), bg="white", fg="#475569").grid(row=0, column=1, sticky="w", padx=10)
        self.course_var = tk.StringVar(value="All Courses")
        self.course_combo = ttk.Combobox(filter_card, textvariable=self.course_var, state="readonly", width=22)
        self.course_combo.grid(row=1, column=1, padx=10, pady=5)
        self.course_combo.bind("<<ComboboxSelected>>", self.load_subjects)

        tk.Label(filter_card, text="Subject", font=("Segoe UI", 9, "bold"), bg="white", fg="#475569").grid(row=0, column=2, sticky="w", padx=10)
        self.subject_var = tk.StringVar(value="All Subjects")
        self.subject_combo = ttk.Combobox(filter_card, textvariable=self.subject_var, state="readonly", width=22)
        self.subject_combo.grid(row=1, column=2, padx=10, pady=5)

        tk.Button(filter_card, text="🔍 Show Records", bg="#2563eb", fg="white", font=("Segoe UI", 9, "bold"), 
                  relief="flat", padx=25, pady=7, cursor="hand2", command=self.load_attendance).grid(row=1, column=3, padx=10)

        # --- Table Header ---
        t_header = tk.Frame(self, bg="#f1f5f9")
        t_header.pack(fill="x", padx=40)
        for i in range(5): t_header.columnconfigure(i, weight=1, uniform="va")
        heads = [("DATE", 0), ("ROLL NO.", 1), ("STUDENT NAME", 2), ("SUBJECT", 3), ("STATUS", 4)]
        for txt, col in heads:
            tk.Label(t_header, text=txt, font=("Segoe UI", 10, "bold"), bg="#f1f5f9", fg="#475569", anchor="w", padx=15, pady=12).grid(row=0, column=col, sticky="nsew")

        # --- Scrollable Area ---
        container = tk.Frame(self, bg="white")
        container.pack(fill="both", expand=True, padx=40)
        self.canvas = tk.Canvas(container, bg="white", highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(container, orient="vertical", command=self.canvas.yview)
        self.scroll_frame = tk.Frame(self.canvas, bg="white")
        self.scroll_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.create_window((0, 0), window=self.scroll_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        self.load_initial_data()

    def create_stat_card(self, parent, title, val, color, col):
        card = tk.Frame(parent, bg="white", highlightthickness=1, highlightbackground="#e2e8f0", padx=15, pady=15)
        card.grid(row=0, column=col, padx=(0, 20), sticky="nsew")
        tk.Label(card, text=title, font=("Segoe UI", 9), bg="white", fg="#64748b").pack(anchor="w")
        lbl_val = tk.Label(card, text=val, font=("Segoe UI", 20, "bold"), bg="white", fg=color)
        lbl_val.pack(anchor="w")
        return lbl_val

    def load_initial_data(self):
        try:
            conn = sqlite3.connect(DB_FILE)
            cur = conn.cursor()
            cur.execute("SELECT course_name FROM course")
            self.course_combo['values'] = ["All Courses"] + [r[0] for r in cur.fetchall()]
            conn.close()
        except: pass

    def load_subjects(self, event=None):
        c = self.course_var.get().strip()
        try:
            conn = sqlite3.connect(DB_FILE)
            cur = conn.cursor()
            if c == "All Courses":
                self.subject_combo['values'] = ["All Subjects"]
            else:
                cur.execute("SELECT subject_name FROM subjects WHERE course=?", (c,))
                self.subject_combo['values'] = ["All Subjects"] + [r[0] for r in cur.fetchall()]
            self.subject_var.set("All Subjects")
            conn.close()
        except: pass

    def load_attendance(self):
        for widget in self.scroll_frame.winfo_children(): widget.destroy()
        
        d = self.date_var.get().strip()
        c = self.course_var.get().strip()
        s = self.subject_var.get().strip()

        try:
            conn = sqlite3.connect(DB_FILE)
            cur = conn.cursor()
            
            # Base query - data mapping matching MarkAttendance save
            query = "SELECT date, roll_no, student_name, subject, status FROM attendance WHERE date = ?"
            params = [d]

            if c != "All Courses":
                query += " AND course = ?"
                params.append(c)
            if s != "All Subjects":
                query += " AND subject = ?"
                params.append(s)

            cur.execute(query, params)
            rows = cur.fetchall()
            conn.close()

            if not rows:
                tk.Label(self.scroll_frame, text="No records found.", bg="white", fg="red").pack(pady=20)
                self.update_stats(0, 0, 0, 0)
                return

            p, a, l = 0, 0, 0
            for row in rows:
                self.create_row(row)
                status = row[4].capitalize()
                if status == "Present": p += 1
                elif status == "Absent": a += 1
                elif status == "Leave": l += 1

            self.update_stats(len(rows), p, a, l)
        except Exception as e:
            messagebox.showerror("Error", f"Fetch Failed: {e}")

    def create_row(self, data):
        row = tk.Frame(self.scroll_frame, bg="white", highlightthickness=1, highlightbackground="#f1f5f9")
        row.pack(fill="x", pady=1)
        for i in range(5): row.columnconfigure(i, weight=1, uniform="va")

        tk.Label(row, text=data[0], font=("Segoe UI", 9), bg="white", anchor="w", padx=15, pady=12).grid(row=0, column=0, sticky="nsew")
        tk.Label(row, text=data[1], font=("Segoe UI", 9, "bold"), bg="white", anchor="w", padx=15).grid(row=0, column=1, sticky="nsew")
        tk.Label(row, text=data[2], font=("Segoe UI", 10), bg="white", anchor="w", padx=15).grid(row=0, column=2, sticky="nsew")
        tk.Label(row, text=data[3], font=("Segoe UI", 9), bg="white", anchor="w", padx=15, fg="#64748b").grid(row=0, column=3, sticky="nsew")

        colors = {"Present": ("#dcfce7", "#166534"), "Absent": ("#fee2e2", "#991b1b"), "Leave": ("#fef3c7", "#92400e")}
        st = data[4].capitalize()
        bg_c, fg_c = colors.get(st, ("#f1f5f9", "#475569"))
        
        lbl_status = tk.Label(row, text=st, font=("Segoe UI", 8, "bold"), bg=bg_c, fg=fg_c, padx=12, pady=2)
        lbl_status.grid(row=0, column=4, pady=10)

    def update_stats(self, t, p, a, l):
        self.total_card.config(text=str(t))
        self.present_card.config(text=str(p))
        self.absent_card.config(text=str(a))
        self.leave_card.config(text=str(l))