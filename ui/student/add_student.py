import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3

class AddStudent(tk.Frame):
    def __init__(self, parent, controller=None, edit_data=None): 
        super().__init__(parent, bg="#f0f2f5")
        self.controller = controller
        self.db_name = "database.db" 
        self.editing_id = None 

        # --- Header ---
        header = tk.Frame(self, bg="#ffffff", height=100, bd=0, highlightthickness=1, highlightbackground="#e0e0e0")
        header.pack(fill="x", side="top")
        
        self.title_label = tk.Label(header, text="Student Enrollment Form", bg="white", fg="#1a73e8", 
                                   font=("Segoe UI", 24, "bold"))
        self.title_label.pack(pady=(20, 0), padx=30, anchor="w")
        tk.Label(header, text="College Management System | Database Driven", bg="white", fg="#5f6368", 
                 font=("Segoe UI", 10)).pack(pady=(0, 20), padx=30, anchor="w")

        # --- Main Layout with Scrollbar ---
        container = tk.Frame(self, bg="#f0f2f5")
        container.pack(fill="both", expand=True, padx=20, pady=10)

        self.canvas = tk.Canvas(container, bg="#f0f2f5", highlightthickness=0)
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=self.canvas.yview)
        
        self.form_frame = tk.Frame(self.canvas, bg="#f0f2f5")
        self.form_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas_window = self.canvas.create_window((0, 0), window=self.form_frame, anchor="nw", width=900)
        
        self.canvas.bind('<Configure>', lambda e: self.canvas.itemconfig(self.canvas_window, width=e.width))
        self.canvas.configure(yscrollcommand=scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.setup_sections()
        self.setup_buttons()

        # Database se course load karo dropdown mein
        self.load_courses_from_db()

        # Agar Edit data aaya hai toh form bharo
        if edit_data:
            self.fill_form_for_edit(edit_data)

    def create_section_card(self, title, icon_text):
        card = tk.Frame(self.form_frame, bg="white", bd=0, highlightthickness=1, highlightbackground="#dcdfe3")
        card.pack(fill="x", padx=20, pady=10, ipady=15)
        tk.Label(card, text=f"{icon_text} {title}", bg="white", fg="#202124", font=("Segoe UI", 14, "bold")).pack(anchor="w", padx=20, pady=(15, 10))
        grid_frame = tk.Frame(card, bg="white")
        grid_frame.pack(fill="x", padx=10)
        grid_frame.columnconfigure((0, 1), weight=1)
        return grid_frame

    def setup_sections(self):
        # 1. PERSONAL INFORMATION
        personal_grid = self.create_section_card("Personal Information", "👤")
        self.first = self.add_input(personal_grid, "First Name", 0, 0)
        self.last = self.add_input(personal_grid, "Last Name", 0, 1)
        self.email = self.add_input(personal_grid, "Email Address", 1, 0)
        self.phone = self.add_input(personal_grid, "Mobile Number", 1, 1)
        self.dob = self.add_input(personal_grid, "Date of Birth (YYYY-MM-DD)", 2, 0)
        
        tk.Label(personal_grid, text="Gender", bg="white", font=("Segoe UI", 10, "bold")).grid(row=4, column=1, sticky="w", padx=15)
        self.gender = ttk.Combobox(personal_grid, values=["Male", "Female", "Other"], state="readonly", font=("Segoe UI", 11))
        self.gender.grid(row=5, column=1, padx=15, pady=5, sticky="ew")

        # 2. ACADEMIC INFORMATION
        acad_grid = self.create_section_card("Academic Record", "🎓")
        self.roll = self.add_input(acad_grid, "University Roll Number", 0, 0)
        
        tk.Label(acad_grid, text="Course", bg="white", font=("Segoe UI", 10, "bold")).grid(row=0, column=1, sticky="w", padx=15)
        # Yahan values khali rakhi hain, load_courses_from_db se bharenge
        self.course_box = ttk.Combobox(acad_grid, values=[], state="readonly", font=("Segoe UI", 11))
        self.course_box.grid(row=1, column=1, padx=15, pady=5, sticky="ew")

        self.semester = ttk.Combobox(acad_grid, values=[f"Semester {i}" for i in range(1, 9)], state="readonly", font=("Segoe UI", 11))
        tk.Label(acad_grid, text="Semester", bg="white", font=("Segoe UI", 10, "bold")).grid(row=2, column=0, sticky="w", padx=15)
        self.semester.grid(row=3, column=0, padx=15, pady=5, sticky="ew")
        
        self.adm_date = self.add_input(acad_grid, "Admission Date", 2, 1)

    def load_courses_from_db(self):
        """Database se course names fetch karke dropdown mein dalna"""
        try:
            conn = sqlite3.connect(self.db_name)
            cur = conn.cursor()
            cur.execute("SELECT course_name FROM course")
            rows = cur.fetchall()
            courses = [r[0] for r in rows]
            self.course_box['values'] = courses
            conn.close()
        except Exception as e:
            print(f"Error loading courses: {e}")

    def add_input(self, frame, label, row, col):
        tk.Label(frame, text=label, bg="white", font=("Segoe UI", 10, "bold")).grid(row=row*2, column=col, sticky="w", padx=15, pady=(10, 0))
        entry = tk.Entry(frame, font=("Segoe UI", 11), highlightthickness=1, highlightbackground="#ced4da")
        entry.grid(row=row*2+1, column=col, padx=15, pady=(5, 10), ipady=8, sticky="ew")
        return entry

    def setup_buttons(self):
        btn_frame = tk.Frame(self.form_frame, bg="#f0f2f5")
        btn_frame.pack(fill="x", padx=40, pady=30)
        self.submit_btn = tk.Button(btn_frame, text="Submit Enrollment", bg="#1a73e8", fg="white", font=("Segoe UI", 12, "bold"), 
                                   relief="flat", padx=40, pady=12, cursor="hand2", command=self.save_data)
        self.submit_btn.pack(side="right", padx=10)
        tk.Button(btn_frame, text="Clear Form", bg="#dadce0", fg="#3c4043", font=("Segoe UI", 12), 
                 relief="flat", padx=30, pady=12, cursor="hand2", command=self.clear_fields).pack(side="right", padx=10)

    def fill_form_for_edit(self, sid):
        if not self.winfo_exists(): return
        self.clear_fields()
        # sid agar list/tuple hai toh uska pehla element ID hoga
        actual_id = sid[0] if isinstance(sid, (list, tuple)) else sid
        self.editing_id = actual_id 
        self.title_label.config(text="Edit Student Record", fg="#e67e22")
        self.submit_btn.config(text="Update Student Record", bg="#e67e22")

        try:
            conn = sqlite3.connect(self.db_name)
            cur = conn.cursor()
            cur.execute("SELECT * FROM students WHERE id=?", (actual_id,))
            row = cur.fetchone()
            conn.close()

            if row:
                self.first.insert(0, row[1]); self.last.insert(0, row[2])
                self.email.insert(0, row[3]); self.phone.insert(0, row[4])
                self.dob.insert(0, row[5]); self.gender.set(row[6])
                self.course_box.set(row[7]); self.semester.set(row[8])
                self.roll.insert(0, row[9]); self.adm_date.insert(0, row[10])
        except Exception as e: print(f"Load Error: {e}")

    def save_data(self):
        try:
            v = (
                self.first.get().strip(), self.last.get().strip(), self.email.get().strip(),
                self.phone.get().strip(), self.dob.get().strip(), self.gender.get(),
                self.course_box.get(), self.semester.get(), self.roll.get().strip(),
                self.adm_date.get().strip()
            )

            if not v[0] or not v[8] or not v[6]:
                messagebox.showwarning("Input Error", "Name, Roll No aur Course bharna zaroori hai!")
                return

            conn = sqlite3.connect(self.db_name)
            cur = conn.cursor()

            if self.editing_id: 
                query = """UPDATE students SET 
                           first=?, last=?, email=?, phone=?, dob=?, gender=?, 
                           course=?, semester=?, roll=?, adm_date=? 
                           WHERE id=?"""
                cur.execute(query, v + (self.editing_id,))
                msg = "Student record updated successfully!"
            else: 
                query = """INSERT INTO students 
                           (first, last, email, phone, dob, gender, course, semester, roll, adm_date) 
                           VALUES (?,?,?,?,?,?,?,?,?,?)"""
                cur.execute(query, v)
                msg = "New student enrolled successfully!"

            conn.commit()
            conn.close()
            messagebox.showinfo("Success", msg)

            if self.controller:
                m_page = self.controller.get_page("ManageStudent")
                if m_page and hasattr(m_page, "refresh_data"): 
                    m_page.refresh_data()
                self.clear_fields()
                self.controller.show_frame("ManageStudent")

        except Exception as e:
            messagebox.showerror("Database Error", f"Kuch gadbad hui: {e}")

    def clear_fields(self):
        self.editing_id = None
        self.title_label.config(text="Student Enrollment Form", fg="#1a73e8")
        self.submit_btn.config(text="Submit Enrollment", bg="#1a73e8")
        for attr in ['first', 'last', 'email', 'phone', 'dob', 'roll', 'adm_date']:
            getattr(self, attr).delete(0, tk.END)
        self.gender.set(''); self.course_box.set(''); self.semester.set('')