import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3

# डेटाबेस का नाम
DB_NAME = "database.db"

COLLEGE_DEPARTMENTS = [
    "Computer Science", "Information Technology", "Commerce", 
    "Management", "Arts & Humanities", "Science (PCB/PCM)", 
    "Mechanical Eng.", "Civil Eng.", "Library"
]

# 1. DATABASE INITIALIZER (Sahi Syntax ke saath)
def initialize_database():
    try:
        conn = sqlite3.connect(DB_NAME)
        cur = conn.cursor()
        # Table creation query (Extra comma hataya gaya)
        cur.execute("""CREATE TABLE IF NOT EXISTS course (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            course_name TEXT UNIQUE, 
            course_code TEXT, 
            department TEXT,
            duration TEXT, 
            description TEXT
        )""")
        conn.commit()
        conn.close()
        print("✅ Database Initialized Successfully!")
    except Exception as e:
        print(f"❌ DB Error: {e}")

class FormHelper:
    @staticmethod
    def add_input(frame, label, row, col, placeholder="", colspan=1):
        tk.Label(frame, text=label, bg="white", font=("Segoe UI", 10, "bold"), fg="#444").grid(row=row*2, column=col, columnspan=colspan, sticky="w", padx=15, pady=(10, 0))
        entry = tk.Entry(frame, font=("Segoe UI", 11), bd=0, highlightthickness=1, highlightbackground="#ced4da", highlightcolor="#1a73e8")
        entry.grid(row=row*2+1, column=col, columnspan=colspan, padx=15, pady=(5, 10), ipady=8, sticky="ew")
        if placeholder:
            entry.insert(0, placeholder)
            entry.config(fg="grey")
            entry.bind("<FocusIn>", lambda e: (entry.delete(0, tk.END), entry.config(fg="black")) if entry.get()==placeholder else None)
        return entry

# ========================== ADD / EDIT COURSE SECTION ==========================
class AddCourse(tk.Frame):
    def __init__(self, parent, controller=None, edit_data=None):
        super().__init__(parent, bg="#f0f2f5")
        self.controller = controller
        
        # मोड और डेटा सेट करें
        self.edit_mode = True if edit_data else False
        self.course_id = edit_data[0] if edit_data else None

        # --- Dynamic Header ---
        header_text = "Edit Course Details" if self.edit_mode else "Add New Course"
        header = tk.Frame(self, bg="white", height=80, highlightthickness=1, highlightbackground="#e0e0e0")
        header.pack(fill="x")
        
        # ✅ 'self' ke saath label define kiya taaki error na aaye
        self.title_label = tk.Label(header, text=header_text, bg="white", fg="#1a73e8", font=("Segoe UI", 20, "bold"))
        self.title_label.pack(pady=15, padx=30, anchor="w")

        # --- Scroll Setup ---
        self.canvas = tk.Canvas(self, bg="#f0f2f5", highlightthickness=0)
        self.form_frame = tk.Frame(self.canvas, bg="#f0f2f5")
        sb = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=sb.set)
        
        sb.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)
        self.canvas.create_window((0,0), window=self.form_frame, anchor="nw", width=850)
        self.form_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))

        self.canvas.bind('<Enter>', lambda e: self.canvas.bind_all("<MouseWheel>", self._on_mousewheel))
        self.canvas.bind('<Leave>', lambda e: self.canvas.unbind_all("<MouseWheel>"))

        self.setup_ui()

        # अगर Edit Mode है, तो डेटा भरें
        if self.edit_mode:
            self.fill_data(edit_data)

    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")

    def setup_ui(self):
        card = tk.Frame(self.form_frame, bg="white", highlightthickness=1, highlightbackground="#dcdfe3")
        card.pack(pady=20, padx=50, fill="x")
        grid = tk.Frame(card, bg="white"); grid.pack(fill="x", padx=20, pady=20); grid.columnconfigure((0, 1), weight=1)
        
        self.course_name = FormHelper.add_input(grid, "Course Name", 0, 0, "e.g., BCA")
        self.course_code = FormHelper.add_input(grid, "Course Code", 0, 1, "e.g., CS101")
        
        tk.Label(grid, text="Department", bg="white", font=("Segoe UI", 10, "bold")).grid(row=2, column=0, sticky="w", padx=15)
        self.dept = ttk.Combobox(grid, values=COLLEGE_DEPARTMENTS, state="readonly", font=("Segoe UI", 11))
        self.dept.grid(row=3, column=0, padx=15, pady=5, sticky="ew")

        tk.Label(grid, text="Duration", bg="white", font=("Segoe UI", 10, "bold")).grid(row=2, column=1, sticky="w", padx=15)
        self.duration = ttk.Combobox(grid, values=["1 Year", "2 Years", "3 Years", "4 Years"], state="readonly", font=("Segoe UI", 11))
        self.duration.grid(row=3, column=1, padx=15, pady=5, sticky="ew")

        self.desc = FormHelper.add_input(grid, "Course Description", 2, 0, colspan=2)

        btn_f = tk.Frame(self.form_frame, bg="#f0f2f5"); btn_f.pack(pady=20)
        
        btn_text = "Update Course" if self.edit_mode else "Save Course"
        btn_bg = "#28a745" if self.edit_mode else "#1a73e8"

        # ✅ 'self' ke saath submit_btn define kiya
        self.submit_btn = tk.Button(btn_f, text=btn_text, bg=btn_bg, fg="white", font=("Segoe UI", 12, "bold"), 
                                   padx=30, command=self.save_data)
        self.submit_btn.pack(side="left", padx=10)
        
        if self.edit_mode:
            tk.Button(btn_f, text="Cancel", bg="#6c757d", fg="white", font=("Segoe UI", 12, "bold"), 
                      padx=30, command=self.go_back).pack(side="left", padx=10)

    def fill_data(self, data):
        """Manage Page se aaya data entries mein bharna"""
        self.edit_mode = True
        self.course_id = data[0]
        
        # Text fields
        self.course_name.delete(0, tk.END)
        self.course_name.insert(0, data[1])
        self.course_name.config(fg="black")

        self.course_code.delete(0, tk.END)
        self.course_code.insert(0, data[2])
        self.course_code.config(fg="black")

        # Comboboxes
        if len(data) >= 4: self.dept.set(data[3])
        if len(data) >= 5: self.duration.set(data[4])
        
        # Description
        self.desc.delete(0, tk.END)
        if len(data) >= 6: self.desc.insert(0, data[5])
        self.desc.config(fg="black")

        # UI updates
        self.title_label.config(text="Edit Course Details", fg="#e67e22")
        self.submit_btn.config(text="Update Course", bg="#e67e22")

    def save_data(self):
        name = self.course_name.get().strip()
        code = self.course_code.get().strip()
        dept = self.dept.get()
        dur = self.duration.get()
        description = self.desc.get().strip()

        if not name or not code or not dept:
            messagebox.showwarning("Input Error", "Bhai, Name, Code aur Department bharna zaruri hai!")
            return

        conn = None
        try:
            conn = sqlite3.connect(DB_NAME)
            cur = conn.cursor()

            if self.edit_mode:
                # ✅ UPDATE Logic
                query = """UPDATE course SET 
                           course_name=?, course_code=?, department=?, duration=?, description=? 
                           WHERE id=?"""
                cur.execute(query, (name, code, dept, dur, description, self.course_id))
                messagebox.showinfo("Success", "Course Updated Successfully!")
                self.go_back()
            else:
                # ✅ INSERT Logic
                query = """INSERT INTO course 
                           (course_name, course_code, department, duration, description) 
                           VALUES (?, ?, ?, ?, ?)"""
                cur.execute(query, (name, code, dept, dur, description))
                messagebox.showinfo("Success", "New Course Saved!")
                self.clear_fields()

            conn.commit()
        except sqlite3.IntegrityError:
            messagebox.showerror("Duplicate Error", f"Bhai, '{name}' naam ka course pehle se hai!")
        except Exception as e:
            messagebox.showerror("DB Error", f"Error: {e}")
        finally:
            if conn: conn.close()

    def go_back(self):
        if self.controller:
            # Manage Course page par wapas jao
            self.controller.show_frame("ManageCourse")

    def clear_fields(self):
        self.course_name.delete(0, tk.END)
        self.course_code.delete(0, tk.END)
        self.desc.delete(0, tk.END)
        self.dept.set('')
        self.duration.set('')