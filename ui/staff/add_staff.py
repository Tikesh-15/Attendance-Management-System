import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3

class AddStaff(tk.Frame):
    def __init__(self, parent, controller=None, edit_data=None): 
        super().__init__(parent, bg="#f0f2f5")
        self.controller = controller
        self.db_name = "database.db"
        self.editing_id = None 

        # --- Header ---
        header = tk.Frame(self, bg="#ffffff", height=100, bd=0, highlightthickness=1, highlightbackground="#e0e0e0")
        header.pack(fill="x", side="top")
        self.title_label = tk.Label(header, text="Staff Enrollment Form", bg="white", fg="#1a73e8", font=("Segoe UI", 24, "bold"))
        self.title_label.pack(pady=(20, 0), padx=30, anchor="w")
        tk.Label(header, text="Management System | Staff Database Entry", bg="white", fg="#5f6368", font=("Segoe UI", 10)).pack(pady=(0, 20), padx=30, anchor="w")

        # --- Main Layout ---
        container = tk.Frame(self, bg="#f0f2f5")
        container.pack(fill="both", expand=True, padx=20, pady=10)

        self.canvas = tk.Canvas(container, bg="#f0f2f5", highlightthickness=0)
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=self.canvas.yview)
        self.form_frame = tk.Frame(self.canvas, bg="#f0f2f5")
        self.form_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.create_window((0, 0), window=self.form_frame, anchor="nw", width=900)
        self.canvas.configure(yscrollcommand=scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.setup_sections()
        self.setup_buttons()

        # ✅ EDIT LOGIC: अगर ManageStaff से ID आई है
        if edit_data:
            sid = edit_data[0] if isinstance(edit_data, list) else edit_data
            self.fill_form_for_edit(sid)

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
        
        tk.Label(personal_grid, text="Gender", bg="white", font=("Segoe UI", 10, "bold")).grid(row=4, column=0, sticky="w", padx=15)
        self.gender = ttk.Combobox(personal_grid, values=["Male", "Female", "Other"], state="readonly", font=("Segoe UI", 11))
        self.gender.grid(row=5, column=0, padx=15, pady=5, sticky="ew")

        # 2. PROFESSIONAL DETAILS
        prof_grid = self.create_section_card("Professional Details", "💼")
        self.emp_id = self.add_input(prof_grid, "Employee ID (Unique)", 0, 0)
        
        tk.Label(prof_grid, text="Department", bg="white", font=("Segoe UI", 10, "bold")).grid(row=0, column=1, sticky="w", padx=15)
        self.dept = ttk.Combobox(prof_grid, values=["Admin", "Teaching", "Library", "Accounts", "IT Support"], state="readonly", font=("Segoe UI", 11))
        self.dept.grid(row=1, column=1, padx=15, pady=5, sticky="ew")

        self.designation = self.add_input(prof_grid, "Designation", 1, 0) 
        self.salary = self.add_input(prof_grid, "Monthly Salary", 1, 1)

        # 3. QUALIFICATION
        qual_grid = self.create_section_card("Qualification & Experience", "📜")
        self.qualification = self.add_input(qual_grid, "Highest Qualification", 0, 0)
        self.experience = self.add_input(qual_grid, "Years of Experience", 0, 1)

    def add_input(self, frame, label, row, col, colspan=1):
        tk.Label(frame, text=label, bg="white", font=("Segoe UI", 10, "bold"), fg="#444").grid(row=row*2, column=col, columnspan=colspan, sticky="w", padx=15, pady=(10, 0))
        entry = tk.Entry(frame, font=("Segoe UI", 11), bd=0, highlightthickness=1, highlightbackground="#ced4da", highlightcolor="#1a73e8")
        entry.grid(row=row*2+1, column=col, columnspan=colspan, padx=15, pady=(5, 10), ipady=8, sticky="ew")
        return entry

    def setup_buttons(self):
        btn_frame = tk.Frame(self.form_frame, bg="#f0f2f5")
        btn_frame.pack(fill="x", padx=40, pady=30)
        self.submit_btn = tk.Button(btn_frame, text="Save Staff Member", bg="#1a73e8", fg="white", font=("Segoe UI", 12, "bold"), relief="flat", padx=40, pady=12, cursor="hand2", command=self.save_data)
        self.submit_btn.pack(side="right", padx=10)
        tk.Button(btn_frame, text="Clear Form", bg="#dadce0", fg="#3c4043", font=("Segoe UI", 12), relief="flat", padx=30, pady=12, cursor="hand2", command=self.clear_fields).pack(side="right", padx=10)

    # ✅ सही से डेटा भरने का फंक्शन
    def fill_form_for_edit(self, sid):
        self.clear_fields() # पुराने डेटा को हटाना ज़रूरी है
        self.editing_id = sid 
        self.title_label.config(text="Edit Staff Member", fg="#e67e22")
        self.submit_btn.config(text="Update Staff Details", bg="#e67e22")

        try:
            conn = sqlite3.connect(self.db_name)
            cur = conn.cursor()
            cur.execute("SELECT * FROM staff WHERE id=?", (sid,))
            row = cur.fetchone()
            conn.close()

            if row:
                # insert(0, data) से पहले delete(0, END) करना ज़रूरी है (जो clear_fields कर रहा है)
                self.first.insert(0, str(row[1]) if row[1] else "")
                self.last.insert(0, str(row[2]) if row[2] else "")
                self.email.insert(0, str(row[3]) if row[3] else "")
                self.phone.insert(0, str(row[4]) if row[4] else "")
                self.gender.set(str(row[5]) if row[5] else "Select")
                self.emp_id.insert(0, str(row[6]) if row[6] else "")
                self.dept.set(str(row[7]) if row[7] else "Select")
                self.designation.insert(0, str(row[8]) if row[8] else "")
                self.salary.insert(0, str(row[9]) if row[9] else "")
                self.qualification.insert(0, str(row[10]) if row[10] else "")
                self.experience.insert(0, str(row[11]) if row[11] else "")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load data: {e}")

    def save_data(self):
        try:
            # 1. Saare input fields se data nikal kar 'vals' tuple banao
            vals = (
                self.first.get().strip(),
                self.last.get().strip(),
                self.email.get().strip(),
                self.phone.get().strip(),
                self.gender.get(),
                self.emp_id.get().strip(),
                self.dept.get(),
                self.designation.get().strip(),
                self.salary.get().strip(),
                self.qualification.get().strip(),
                self.experience.get().strip()
            )

            # Validation: Name aur Emp ID compulsory rakhte hain
            if not vals[0] or not vals[5]:
                messagebox.showwarning("Input Error", "Bhai, First Name aur Employee ID bharna zaruri hai!")
                return

            conn = sqlite3.connect(self.db_name)
            cur = conn.cursor()

            if self.editing_id:
                # ✅ UPDATE Logic (Agar hum edit kar rahe hain)
                query = """UPDATE staff SET 
                           first=?, last=?, email=?, phone=?, gender=?, 
                           emp_id=?, dept=?, designation=?, salary=?, 
                           qualification=?, experience=? 
                           WHERE id=?"""
                cur.execute(query, vals + (self.editing_id,))
                msg = "Staff details updated successfully!"
            else:
                # ✅ INSERT Logic (Naya staff enrollment)
                query = """INSERT INTO staff (first, last, email, phone, gender, emp_id, 
                           dept, designation, salary, qualification, experience) 
                           VALUES (?,?,?,?,?,?,?,?,?,?,?)"""
                cur.execute(query, vals)
                msg = "New staff registered successfully!"

            conn.commit()
            conn.close()
            messagebox.showinfo("Success", msg)

            # 2. UI Refresh aur Switch
            if self.controller:
                # ManageStaff page ko refresh karo taaki naya data dikhe
                manage_page = self.controller.get_page("ManageStaff")
                if manage_page and hasattr(manage_page, "refresh_data"):
                    manage_page.refresh_data()
                
                # Form clear karo aur wapas list page par jao
                self.clear_fields()
                self.controller.show_frame("ManageStaff")

        except Exception as e:
            messagebox.showerror("Database Error", f"Lafda ho gaya: {e}")

    def clear_fields(self):
        self.editing_id = None
        self.title_label.config(text="Staff Enrollment Form", fg="#1a73e8")
        self.submit_btn.config(text="Save Staff Member", bg="#1a73e8")
        
        # सभी Entry boxes को साफ़ करना
        entries = [self.first, self.last, self.email, self.phone, self.emp_id, 
                   self.designation, self.salary, self.qualification, self.experience]
        for e in entries:
            e.delete(0, tk.END)
            
        # Comboboxes को रिसेट करना
        self.gender.set('')
        self.dept.set('')

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Add Staff")
    root.geometry("1000x800")
    app = AddStaff(root)
    app.pack(fill="both", expand=True)
    root.mainloop()