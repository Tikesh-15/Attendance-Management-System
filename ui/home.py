import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

DB_FILE = "database.db"  # सुनिश्चित करें कि नाम सही है

class HomePage(tk.Frame):
    def __init__(self, parent, controller=None):
        super().__init__(parent, bg="#f8fafc")
        self.controller = controller

        # DATABASE Connection
        try:
            self.conn = sqlite3.connect(DB_FILE)
            self.cursor = self.conn.cursor()
        except Exception as e:
            print(f"Database Connection Error: {e}")
        
        # ग्राफ की स्थिति (Bar या Pie)
        self.chart_states = {
            "staff": "bar",
            "subjects": "bar",
            "students": "bar",
            "attendance": "pie"
        }

        self.setup_scroll_area()
        self.create_top_header()
        self.create_cards()
        self.create_all_charts()
        self.create_recent_activities_section()

    def setup_scroll_area(self):
        self.canvas = tk.Canvas(self, bg="#f8fafc", highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.scroll_frame = tk.Frame(self.canvas, bg="#f8fafc")

        self.scroll_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas_win = self.canvas.create_window((0, 0), window=self.scroll_frame, anchor="nw", width=1050)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        # स्मार्ट स्क्रॉल बाइंडिंग
        self.canvas.bind('<Enter>', lambda e: self.canvas.bind_all("<MouseWheel>", self._on_mousewheel))
        self.canvas.bind('<Leave>', lambda e: self.canvas.unbind_all("<MouseWheel>"))

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

    def _on_mousewheel(self, event):
        try: self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        except: pass

    def create_top_header(self):
        header = tk.Frame(self.scroll_frame, bg="#f8fafc")
        header.pack(fill="x", padx=30, pady=(30, 10))
        tk.Label(header, text="Dashboard Overview", font=("Segoe UI", 26, "bold"), bg="#f8fafc", fg="#1e293b").pack(anchor="w")
        tk.Label(header, text="Welcome back! Real-time analytics from your database.", font=("Segoe UI", 11), bg="#f8fafc", fg="#64748b").pack(anchor="w")

    def get_count(self, table):
        try:
            self.cursor.execute(f"SELECT COUNT(*) FROM {table}")
            return self.cursor.fetchone()[0]
        except: return 0

    def create_cards(self):
        frame = tk.Frame(self.scroll_frame, bg="#f8fafc")
        frame.pack(fill="x", padx=20, pady=20)

        cards_data = [
            ("Total Students", "students", "#3b82f6", "👥", "ManageStudent"),
            ("Total Staff", "staff", "#10b981", "👨‍🏫", "ManageStaff"),
            ("Total Courses", "course", "#8b5cf6", "📖", "ManageCourse"),
            ("Total Subjects", "subjects", "#f59e0b", "📚", "ManageSubject")
        ]

        for i, (title, table, color, icon, page) in enumerate(cards_data):
            count = self.get_count(table)
            card = tk.Frame(frame, bg="white", highlightthickness=1, highlightbackground="#e2e8f0", cursor="hand2")
            card.grid(row=0, column=i, padx=12, pady=10, sticky="nsew")
            frame.columnconfigure(i, weight=1)

            # क्लिक इवेंट (Controller logic)
            card.bind("<Button-1>", lambda e, p=page: self.controller.show_page_by_name(p) if self.controller else None)

            inner = tk.Frame(card, bg="white", padx=20, pady=20)
            inner.pack(fill="both")
            inner.bind("<Button-1>", lambda e, p=page: self.controller.show_page_by_name(p) if self.controller else None)

            top = tk.Frame(inner, bg="white")
            top.pack(fill="x")
            tk.Label(top, text=title, font=("Segoe UI", 10, "bold"), bg="white", fg="#64748b").pack(side="left")
            tk.Label(top, text=icon, font=("Segoe UI", 14), bg="#f1f5f9", fg=color, width=3).pack(side="right")

            tk.Label(inner, text=str(count), font=("Segoe UI", 24, "bold"), bg="white", fg="#1e293b").pack(anchor="w", pady=(5, 0))
            tk.Label(inner, text="Click to Manage →", font=("Segoe UI", 8), bg="white", fg=color).pack(anchor="w", pady=(10, 0))

    def create_all_charts(self):
        row1 = tk.Frame(self.scroll_frame, bg="#f8fafc"); row1.pack(fill="x", padx=20)
        self.chart_container(row1, "Students vs Staff", "staff", self.student_staff_chart, 0)
        self.chart_container(row1, "Subject Analysis", "subjects", self.subject_per_course_chart, 1)

        row2 = tk.Frame(self.scroll_frame, bg="#f8fafc"); row2.pack(fill="x", padx=20, pady=20)
        self.chart_container(row2, "Course Enrollment", "students", self.students_per_course_chart, 0)
        self.chart_container(row2, "Attendance Overview", "attendance", self.student_attendance_chart, 1)

    def chart_container(self, parent, title, state_key, chart_func, col):
        card = tk.Frame(parent, bg="white", highlightthickness=1, highlightbackground="#e2e8f0")
        card.grid(row=0, column=col, padx=12, pady=10, sticky="nsew")
        parent.columnconfigure(col, weight=1)

        header = tk.Frame(card, bg="white"); header.pack(fill="x", padx=20, pady=15)
        tk.Label(header, text=title, font=("Segoe UI", 13, "bold"), bg="white", fg="#1e293b").pack(side="left")
        
        toggle_btn = tk.Button(header, text="🔄 Switch", bg="#eff6ff", fg="#2563eb", font=("Segoe UI", 8, "bold"), relief="flat", padx=10, cursor="hand2")
        toggle_btn.pack(side="right")

        chart_area = tk.Frame(card, bg="white", height=300); chart_area.pack(fill="both", expand=True, padx=10, pady=(0, 15))

        def toggle():
            self.chart_states[state_key] = "pie" if self.chart_states[state_key] == "bar" else "bar"
            chart_func(chart_area, self.chart_states[state_key])

        toggle_btn.config(command=toggle)
        chart_func(chart_area, self.chart_states[state_key])

    def create_recent_activities_section(self):
        card = tk.Frame(self.scroll_frame, bg="white", highlightthickness=1, highlightbackground="#e2e8f0")
        card.pack(fill="x", padx=32, pady=25)
        tk.Label(card, text="Recent Activities", font=("Segoe UI", 14, "bold"), bg="white", fg="#1e293b", padx=25, pady=20).pack(anchor="w")
        
        try:
            # Table name should match your DB (e.g., 'students')
            self.cursor.execute("SELECT first, last, course FROM students ORDER BY id DESC LIMIT 3")
            recent = self.cursor.fetchall()
            if not recent:
                tk.Label(card, text="No recent activities found.", font=("Segoe UI", 10, "italic"), bg="white", fg="#94a3b8").pack(pady=10)
            for stu in recent:
                item = tk.Frame(card, bg="white", pady=10); item.pack(fill="x", padx=25)
                tk.Label(item, text=f"✨ New Enrollment: {stu[0]} {stu[1]} joined {stu[2]}", font=("Segoe UI", 10), bg="white").pack(side="left")
                tk.Label(item, text="Just now", font=("Segoe UI", 9), bg="white", fg="#94a3b8").pack(side="right")
                tk.Frame(card, bg="#f1f5f9", height=1).pack(fill="x", padx=25)
        except: 
            tk.Label(card, text="Waiting for new data...", font=("Segoe UI", 10), bg="white").pack(pady=10)

    # --- CHART GENERATION LOGIC ---
    def plot_chart_base(self, frame, labels, values, colors, chart_type):
        for w in frame.winfo_children(): w.destroy()
        if not values or sum(values) == 0:
            tk.Label(frame, text="No Data Available", bg="white").pack(expand=True)
            return

        fig = Figure(figsize=(4, 3), dpi=100)
        ax = fig.add_subplot(111)
        
        if chart_type == "pie":
            ax.pie(values, labels=labels, autopct='%1.1f%%', startangle=140, colors=colors)
        else:
            # ✅ यहाँ फिक्स है: पहले set_xticks करें, फिर set_xticklabels
            x_pos = range(len(labels))
            ax.set_xticks(x_pos) 
            ax.set_xticklabels(labels, rotation=15, ha='right', fontsize=8)
            
            ax.bar(x_pos, values, color=colors[0] if colors else "#3b82f6", width=0.5)
            ax.grid(axis='y', linestyle='--', alpha=0.3)
        
        fig.tight_layout()
        canvas = FigureCanvasTkAgg(fig, frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

    def student_staff_chart(self, frame, chart_type="bar"):
        s_count = self.get_count("students")
        st_count = self.get_count("staff")
        self.plot_chart_base(frame, ["Students", "Staff"], [s_count, st_count], ["#3b82f6", "#ef4444"], chart_type)

    def subject_per_course_chart(self, frame, chart_type="bar"):
        try:
            self.cursor.execute("SELECT department, COUNT(*) FROM course GROUP BY department")
            data = self.cursor.fetchall()
            labels = [i[0] if i[0] else "N/A" for i in data]
            values = [i[1] for i in data]
            self.plot_chart_base(frame, labels, values, ["#8b5cf6"], chart_type)
        except: self.plot_chart_base(frame, [], [], [], "bar")

    def students_per_course_chart(self, frame, chart_type="bar"):
        try:
            self.cursor.execute("SELECT course, COUNT(*) FROM students GROUP BY course")
            data = self.cursor.fetchall()
            labels = [i[0] if i[0] else "Unknown" for i in data]
            values = [i[1] for i in data]
            self.plot_chart_base(frame, labels, values, ["#10b981"], chart_type)
        except: self.plot_chart_base(frame, [], [], [], "bar")

    def student_attendance_chart(self, frame, chart_type="pie"):
        try:
            # Attendance table should have 'status' (Present/Absent)
            self.cursor.execute("SELECT status, COUNT(*) FROM attendance GROUP BY status")
            data = self.cursor.fetchall()
            labels = [i[0] for i in data]
            values = [i[1] for i in data]
            self.plot_chart_base(frame, labels, values, ["#3b82f6", "#ef4444", "#f59e0b"], chart_type)
        except: self.plot_chart_base(frame, ["Present", "Absent"], [0, 0], ["#3b82f6", "#ef4444"], chart_type)


    