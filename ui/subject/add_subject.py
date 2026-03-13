import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3

# Database configuration
DB_FILE = "database.db"

class AddSubject(tk.Frame):
    def __init__(self, parent, controller=None, edit_data=None):
        super().__init__(parent, bg="#f8fafc")
        self.controller = controller
        self.edit_id = None  # Edit mode track karne ke liye
        self.staff_map = {}  # Staff ID store karne ke liye

        # --- Header ---
        header = tk.Frame(self, bg="#ffffff", height=100, bd=0, highlightthickness=1, highlightbackground="#e0e0e0")
        header.pack(fill="x", side="top")
        
        self.title_lbl = tk.Label(header, text="Add New Subject", bg="white", fg="#1a73e8", 
                                 font=("Segoe UI", 24, "bold"))
        self.title_lbl.pack(pady=(20, 0), padx=30, anchor="w")
        
        tk.Label(header, text="Assign college subjects to courses and faculty members", bg="white", fg="#5f6368", 
                 font=("Segoe UI", 10)).pack(pady=(0, 20), padx=30, anchor="w")

        # --- Main Container ---
        container = tk.Frame(self, bg="#f8fafc")
        container.pack(fill="both", expand=True, padx=20, pady=10)

        # --- Scrollable Area ---
        self.canvas = tk.Canvas(container, bg="#f8fafc", highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(container, orient="vertical", command=self.canvas.yview)
        self.scroll_frame = tk.Frame(self.canvas, bg="#f8fafc")

        self.scroll_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas_window = self.canvas.create_window((0, 0), window=self.scroll_frame, anchor="nw")
        
        # Responsive Width Adjustment
        self.canvas.bind('<Configure>', lambda e: self.canvas.itemconfig(self.canvas_window, width=e.width))
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        # UI Setup call
        self.setup_ui()

    def setup_ui(self):
        # --- Form Card ---
        card = tk.Frame(self.scroll_frame, bg="white", highlightthickness=1, highlightbackground="#dcdfe3")
        card.pack(fill="x", padx=50, pady=40, ipady=30)
        
        tk.Label(card, text="📚 Subject Configuration", bg="white", fg="#202124", 
                 font=("Segoe UI", 16, "bold")).pack(anchor="w", padx=30, pady=(25, 20))

        grid = tk.Frame(card, bg="white")
        grid.pack(fill="x", padx=30)
        grid.columnconfigure((0, 1), weight=1)

        # 1. Subject Name
        tk.Label(grid, text="Subject Name", bg="white", font=("Segoe UI", 10, "bold"), fg="#444").grid(row=0, column=0, sticky="w", padx=15, pady=(10, 0))
        self.subject_name = tk.Entry(grid, font=("Segoe UI", 11), highlightthickness=1, highlightbackground="#ced4da", bd=0)
        self.subject_name.grid(row=1, column=0, padx=15, pady=(5, 15), ipady=10, sticky="ew")

        # 2. Select Course
        tk.Label(grid, text="Select Course", bg="white", font=("Segoe UI", 10, "bold"), fg="#444").grid(row=0, column=1, sticky="w", padx=15, pady=(10, 0))
        self.course_combo = ttk.Combobox(grid, state="readonly", font=("Segoe UI", 11))
        self.course_combo.grid(row=1, column=1, padx=15, pady=(5, 15), ipady=5, sticky="ew")

        # 3. Assign Staff
        tk.Label(grid, text="Assign Faculty Member", bg="white", font=("Segoe UI", 10, "bold"), fg="#444").grid(row=2, column=0, sticky="w", padx=15, pady=(10, 0))
        self.staff_combo = ttk.Combobox(grid, state="readonly", font=("Segoe UI", 11))
        self.staff_combo.grid(row=3, column=0, padx=15, pady=(5, 15), ipady=5, sticky="ew")

        # Dropdown Data Load
        self.load_dropdown_data()

        # --- Action Buttons ---
        btn_frame = tk.Frame(self.scroll_frame, bg="#f8fafc")
        btn_frame.pack(pady=20)

        self.submit_btn = tk.Button(btn_frame, text="Save Subject", bg="#1a73e8", fg="white", font=("Segoe UI", 12, "bold"), 
                                   relief="flat", padx=40, pady=12, cursor="hand2", command=self.save_subject)
        self.submit_btn.pack(side="left", padx=10)
        
        tk.Button(btn_frame, text="Clear Form", bg="#dadce0", fg="#3c4043", font=("Segoe UI", 12), 
                 relief="flat", padx=30, pady=12, cursor="hand2", command=self.clear_fields).pack(side="left", padx=10)

    def load_dropdown_data(self):
        """Dropdowns mein data load karna database se"""
        try:
            conn = sqlite3.connect(DB_FILE)
            cur = conn.cursor()
            
            # Courses load karein
            cur.execute("SELECT course_name FROM course")
            self.course_combo['values'] = [r[0] for r in cur.fetchall()]
            
            # Staff load karein (Mapping ID with Name)
            cur.execute("SELECT id, first, last FROM staff")
            staff_rows = cur.fetchall()
            self.staff_map = {f"{r[1]} {r[2]} (ID: {r[0]})": r[0] for r in staff_rows}
            self.staff_combo['values'] = list(self.staff_map.keys())
            
            conn.close()
        except Exception as e:
            print(f"Dropdown Loading Error: {e}")

    def fill_form_for_edit(self, data):
        """ManageSubject se data lake bharna (Edit mode)"""
        if not self.winfo_exists(): return
        
        # data: (id, name, course, staff_id)
        self.edit_id = data[0]
        self.subject_name.delete(0, tk.END)
        self.subject_name.insert(0, data[1])
        self.course_combo.set(data[2])
        
        # Staff ID se string match karna
        for name, sid in self.staff_map.items():
            if sid == data[3]:
                self.staff_combo.set(name)
                break
        
        self.title_lbl.config(text="Update Existing Subject", fg="#16a34a")
        self.submit_btn.config(text="Update Subject", bg="#16a34a")

    def save_subject(self):
        name = self.subject_name.get().strip()
        course = self.course_combo.get()
        staff_str = self.staff_combo.get()

        if not name or not course or not staff_str:
            messagebox.showwarning("Incomplete", "Bhai, saare fields bharna zaroori hai!")
            return

        conn = None # Connection pehle khali rakho
        try:
            conn = sqlite3.connect(DB_FILE)
            cur = conn.cursor()
            staff_id = self.staff_map[staff_str]

            if self.edit_id:
                # ✅ SAHI SYNTAX (Dots hata diye hain):
                query = "UPDATE subjects SET subject_name=?, course=?, staff_id=? WHERE id=?"
                cur.execute(query, (name, course, staff_id, self.edit_id))
                msg = "Subject successfully updated!"
            else:
                # Insert logic
                query = "INSERT INTO subjects (subject_name, course, staff_id) VALUES (?,?,?)"
                cur.execute(query, (name, course, staff_id))
                msg = "New Subject added successfully!"

            conn.commit()
            messagebox.showinfo("Success", msg)
            
            if self.controller:
                self.controller.show_frame("ManageSubject")
            
            self.clear_fields()

        except Exception as e:
            messagebox.showerror("Database Error", f"Locha ho gaya: {e}")
        finally:
            if conn:
                conn.close() # ✅ Database Lock hone se bachane ke liye hamesha close karein
            messagebox.showinfo("Success", msg)
            
            # Refresh Manage Page and Navigate Back
            if self.controller:
                manage_page = self.controller.get_page("ManageSubject")
                if manage_page and hasattr(manage_page, "refresh_data"):
                    manage_page.refresh_data()
                self.controller.show_frame("ManageSubject")
            
            
    def clear_fields(self):
        self.edit_id = None
        self.subject_name.delete(0, tk.END)
        self.course_combo.set('')
        self.staff_combo.set('')
        self.title_lbl.config(text="Add New Subject", fg="#1a73e8")
        self.submit_btn.config(text="Save Subject", bg="#1a73e8")