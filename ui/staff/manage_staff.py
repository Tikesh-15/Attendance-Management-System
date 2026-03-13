import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3

DB_FILE = "database.db" 

class ManageStaff(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="white")
        self.controller = controller

        # --- 1. Header ---
        header = tk.Frame(self, bg="white")
        header.pack(fill="x", padx=40, pady=(30, 10))
        tk.Label(header, text="Staff Directory", font=("Segoe UI", 26, "bold"), bg="white", fg="#0f172a").pack(anchor="w")
        tk.Label(header, text="Manage college faculty and administration records", font=("Segoe UI", 11), bg="white", fg="#64748b").pack(anchor="w")

        # --- 2. Toolbar (Search Only) ---
        toolbar = tk.Frame(self, bg="white")
        toolbar.pack(fill="x", padx=40, pady=20)

        search_bg = tk.Frame(toolbar, bg="#f8fafc", highlightthickness=1, highlightbackground="#e2e8f0")
        search_bg.pack(side="left", ipady=2)
        tk.Label(search_bg, text="  🔍  ", bg="#f8fafc", fg="#94a3b8", font=("Segoe UI", 12)).pack(side="left")
        
        self.search_var = tk.StringVar()
        self.search_ent = tk.Entry(search_bg, textvariable=self.search_var, font=("Segoe UI", 11), bd=0, bg="#f8fafc", width=35)
        self.search_ent.pack(side="left", padx=10, ipady=8)
        self.search_ent.insert(0, "Search by name or employee id...")
        
        # Search placeholder logic
        self.search_ent.bind("<FocusIn>", lambda e: self.search_ent.delete(0, tk.END) if self.search_var.get() == "Search by name or employee id..." else None)
        self.search_ent.bind("<FocusOut>", lambda e: self.search_ent.insert(0, "Search by name or employee id...") if self.search_var.get() == "" else None)

        # NOTE: Export CSV button has been removed as per your request.

        # --- 3. Table Headers ---
        self.header_frame = tk.Frame(self, bg="#f1f5f9")
        self.header_frame.pack(fill="x", padx=40)

        cols = [("EMP ID", 0), ("STAFF NAME", 1), ("DEPARTMENT", 2), ("DESIGNATION", 3), ("SALARY", 4), ("ACTIONS", 5)]
        for i in range(6):
            self.header_frame.columnconfigure(i, weight=1, uniform="staff_group")
            tk.Label(self.header_frame, text=cols[i][0], font=("Segoe UI", 10, "bold"), bg="#f1f5f9", fg="#475569", anchor="w", padx=15, pady=12).grid(row=0, column=cols[i][1], sticky="nsew")

        # --- 4. Scrollable Area ---
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

        # Live search trace
        self.search_var.trace_add("write", lambda *args: self.refresh_data())
        self.refresh_data()

    def refresh_data(self):
        """Database se data fetch karke list update karna"""
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()
            
        search_q = self.search_var.get().lower()
        if search_q == "search by name or employee id...":
            search_q = ""

        try:
            conn = sqlite3.connect(DB_FILE)
            cur = conn.cursor()
            # Yahan hum id (data[5]) bhi le rahe hain edit/delete ke liye
            cur.execute("SELECT emp_id, first || ' ' || last, dept, designation, salary, id FROM staff")
            rows = cur.fetchall()
            conn.close()

            for row in rows:
                if (search_q in str(row[0]).lower() or search_q in str(row[1]).lower()):
                    self.create_row(row)
        except Exception as e:
            print(f"DB Error in refresh_data: {e}")

    def create_row(self, data):
        """Har record ke liye ek row frame banana"""
        row_f = tk.Frame(self.scroll_frame, bg="white", highlightthickness=1, highlightbackground="#f1f5f9")
        row_f.pack(fill="x", pady=1)
        
        for i in range(6):
            row_f.columnconfigure(i, weight=1, uniform="staff_group")

        # Columns show karna (Emp ID, Name, Dept, Desig, Salary)
        for i in range(5):
            tk.Label(row_f, text=data[i], font=("Segoe UI", 9), bg="white", anchor="w", padx=15, pady=15).grid(row=0, column=i, sticky="nsew")

        btn_f = tk.Frame(row_f, bg="white")
        btn_f.grid(row=0, column=5, sticky="nsew")
        
        # EDIT Button
        tk.Button(btn_f, text="EDIT", font=("Segoe UI", 8, "bold"), fg="#2563eb", bg="#eff6ff", 
                  relief="flat", padx=10, pady=5, cursor="hand2", 
                  command=lambda sid=data[5]: self.edit_action(sid)).pack(side="left", padx=(15, 5), pady=12)

        # DELETE Button
        tk.Button(btn_f, text="DELETE", font=("Segoe UI", 8, "bold"), fg="#dc2626", bg="#fef2f2", 
                  relief="flat", padx=10, pady=5, cursor="hand2", 
                  command=lambda sid=data[5]: self.delete_staff(sid)).pack(side="left", padx=5, pady=12)

    def edit_action(self, sid):
        """EDIT button logic using central controller"""
        # App class (controller) se AddStaff ka frame/object mangwao
        add_staff_page = self.controller.get_page("AddStaff")
        
        if add_staff_page:
            # 1. AddStaff page ke andar details bharo (ID ke base par)
            add_staff_page.fill_form_for_edit(sid)
            # 2. Page ko switch karo
            self.controller.show_frame("AddStaff")
        else:
            messagebox.showerror("Error", "AddStaff page not found in frames dictionary!")

    def delete_staff(self, sid):
        """Database se record delete karna"""
        if messagebox.askyesno("Confirm", "Bhai, kya aap sach mein ye record delete karna chahte hain?"):
            try:
                conn = sqlite3.connect(DB_FILE)
                cur = conn.cursor()
                cur.execute("DELETE FROM staff WHERE id=?", (sid,))
                conn.commit()
                conn.close()
                self.refresh_data() # List ko refresh karo
                messagebox.showinfo("Success", "Record delete ho gaya hai!")
            except Exception as e:
                messagebox.showerror("Error", f"Delete nahi ho paya: {e}")