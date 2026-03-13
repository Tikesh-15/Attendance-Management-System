import tkinter as tk
from tkinter import ttk, messagebox
import re  # Validation के लिए

try:
    from database.db_connection import get_connection
except ImportError:
    get_connection = None

class SignupPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#E9F3FC")
        self.parent = parent
        self.controller = controller
        self.grid(row=0, column=0, sticky="nsew")        
        self.show_pwd = False
        self.show_cpwd = False

        self.create_scrollable_ui()

    def create_scrollable_ui(self):
        # --- Canvas & Scrollbar ---
        self.main_canvas = tk.Canvas(self, bg="#E9F3FC", highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.main_canvas.yview)
        self.scrollable_frame = tk.Frame(self.main_canvas, bg="#E9F3FC")

        self.scrollable_frame.bind("<Configure>", lambda e: self.main_canvas.configure(scrollregion=self.main_canvas.bbox("all")))
        self.canvas_window = self.main_canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.main_canvas.bind("<Configure>", lambda e: self.main_canvas.itemconfig(self.canvas_window, width=e.width))
        
        self.main_canvas.configure(yscrollcommand=self.scrollbar.set)
        self.main_canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        self.main_canvas.bind_all("<MouseWheel>", lambda e: self.main_canvas.yview_scroll(int(-1*(e.delta/120)), "units"))

        # --- Content Area ---
        content = tk.Frame(self.scrollable_frame, bg="#E9F3FC")
        content.pack(fill="both", expand=True, pady=40)

        self.card = tk.Frame(content, bg="white", padx=50, pady=40, highlightthickness=1, highlightbackground="#E0E6ED")
        self.card.pack(expand=True)

        # Header
        tk.Label(self.card, text="🎓", font=("Arial", 35), bg="#1A73E8", fg="white", width=2).pack(pady=(0, 10))
        tk.Label(self.card, text="Create Account", font=("Segoe UI", 24, "bold"), bg="white", fg="#111827").pack()
        tk.Label(self.card, text="Sign up for a new admin account", font=("Segoe UI", 11), bg="white", fg="#6B7280").pack(pady=(5, 25))

        # --- Fields ---
        self.name_entry = self.create_field("Full Name", "👤")
        self.email_entry = self.create_field("Email Address", "✉")
        self.org_entry = self.create_field("Organization Name", "🏢")
        self.pass_entry, self.pass_btn = self.create_password_field("Password", "🔒", self.toggle_pass)
        self.confirm_entry, self.confirm_btn = self.create_password_field("Confirm Password", "🔒", self.toggle_cpass)

        # Terms
        self.terms_var = tk.BooleanVar()
        t_f = tk.Frame(self.card, bg="white")
        t_f.pack(fill="x", pady=20)
        tk.Checkbutton(t_f, variable=self.terms_var, bg="white", bd=0, activebackground="white").pack(side="left")
        tk.Label(t_f, text="I agree to the Terms & Privacy Policy", font=("Segoe UI", 10), bg="white", fg="#4B5563").pack(side="left", padx=5)

        # Button
        tk.Button(self.card, text="Create Account", font=("Segoe UI", 13, "bold"), bg="#1A73E8", fg="white", 
                  activebackground="#1557B0", bd=0, cursor="hand2", command=self.signup_logic).pack(fill="x", pady=10, ipady=10)

        # Footer
        footer = tk.Frame(self.card, bg="white")
        footer.pack(pady=10)
        tk.Label(footer, text="Already have an account?", font=("Segoe UI", 10), bg="white", fg="#6B7280").pack(side="left")
        login_btn = tk.Label(footer, text="Sign in", font=("Segoe UI", 10, "bold"), bg="white", fg="#1A73E8", cursor="hand2")
        login_btn.pack(side="left", padx=5)
        login_btn.bind("<Button-1>", lambda e: self.back_to_login())

        tk.Frame(self.scrollable_frame, bg="#E9F3FC", height=60).pack()

    # --- Utility Functions ---
    def create_field(self, label, icon):
        f_wrap = tk.Frame(self.card, bg="white")
        f_wrap.pack(fill="x", pady=8)
        tk.Label(f_wrap, text=label, font=("Segoe UI", 10, "bold"), bg="white", fg="#374151").pack(anchor="w", pady=(0, 5))
        entry_f = tk.Frame(f_wrap, bg="white", highlightthickness=1, highlightbackground="#D1D5DB", bd=0)
        entry_f.pack(fill="x", ipady=8)
        tk.Label(entry_f, text=f" {icon} ", font=("Arial", 12), bg="white", fg="#9CA3AF").pack(side="left", padx=8)
        entry = tk.Entry(entry_f, font=("Segoe UI", 12), bg="white", bd=0, fg="#111827")
        entry.pack(side="left", fill="both", expand=True, padx=8)
        return entry

    def create_password_field(self, label, icon, command):
        f_wrap = tk.Frame(self.card, bg="white")
        f_wrap.pack(fill="x", pady=8)
        tk.Label(f_wrap, text=label, font=("Segoe UI", 10, "bold"), bg="white", fg="#374151").pack(anchor="w", pady=(0, 5))
        entry_f = tk.Frame(f_wrap, bg="white", highlightthickness=1, highlightbackground="#D1D5DB", bd=0)
        entry_f.pack(fill="x", ipady=8)
        tk.Label(entry_f, text=f" {icon} ", font=("Arial", 12), bg="white", fg="#9CA3AF").pack(side="left", padx=8)
        entry = tk.Entry(entry_f, font=("Segoe UI", 12), bg="white", bd=0, fg="#111827", show="•")
        entry.pack(side="left", fill="both", expand=True, padx=8)
        btn = tk.Button(entry_f, text="👁", font=("Arial", 12), bg="white", bd=0, cursor="hand2", command=command)
        btn.pack(side="right", padx=10)
        return entry, btn

    def toggle_pass(self):
        self.show_pwd = not self.show_pwd
        self.pass_entry.config(show="" if self.show_pwd else "•")
        self.pass_btn.config(text="🙈" if self.show_pwd else "👁")

    def toggle_cpass(self):
        self.show_cpwd = not self.show_cpwd
        self.confirm_entry.config(show="" if self.show_cpwd else "•")
        self.confirm_btn.config(text="🙈" if self.show_cpwd else "👁")

    def validate_password(self, password):
        """Pro-level Validation Logic"""
        if len(password) < 8:
            return "Password कम से कम 8 अक्षर का होना चाहिए!"
        if not re.search("[0-9]", password):
            return "Password में कम से कम एक नंबर होना चाहिए!"
        if not re.search("[@#$%^&+=]", password):
            return "Password में एक स्पेशल कैरेक्टर (@#$%^&+=) होना चाहिए!"
        return None

    def clear_fields(self):
        self.name_entry.delete(0, tk.END)
        self.email_entry.delete(0, tk.END)
        self.org_entry.delete(0, tk.END)
        self.pass_entry.delete(0, tk.END)
        self.confirm_entry.delete(0, tk.END)
        self.terms_var.set(False)

    # --- Main Pro Logic ---
    # --- Main Pro Logic ---
    def signup_logic(self):
        name = self.name_entry.get().strip()
        email = self.email_entry.get().strip()
        pwd = self.pass_entry.get().strip()
        cpwd = self.confirm_entry.get().strip()

        # 1. Validation Checks (वही रहेंगे जो तूने लिखे हैं)
        if not all([name, email, pwd, cpwd]):
            messagebox.showwarning("Pro Tip", "भाई, पहले फॉर्म तो पूरा भरो!")
            return
        
        if pwd != cpwd:
            messagebox.showerror("Error", "Passwords मैच नहीं हो रहे!")
            return

        error_msg = self.validate_password(pwd)
        if error_msg:
            messagebox.showerror("Weak Password", error_msg)
            return

        if not self.terms_var.get():
            messagebox.showwarning("Terms", "Privacy policy एक्सेप्ट करें!")
            return

        # 2. Database Saving (यहाँ ध्यान दे)
        try:
            if get_connection:
                conn = get_connection()
                cursor = conn.cursor()
                cursor.execute("INSERT INTO users (username, email, password) VALUES (?,?,?)", (name, email, pwd))
                conn.commit()
                conn.close() # ✅ कनेक्शन बंद किया
                
                # ✅ सफलता का मैसेज यहाँ आएगा
                messagebox.showinfo("Success", "Account Created! अब लॉगिन करें।")
                self.clear_fields()
                
                # ✅ अकाउंट बनने के बाद सीधे लॉगिन पेज पर भेजें
                self.controller.show_frame("LoginPage")
            else:
                messagebox.showerror("Error", "Database connected नहीं है!")
        except Exception as e:
            messagebox.showerror("DB Error", f"DB Error: {e}")

    def back_to_login(self):
        """सिर्फ लॉगिन पेज पर वापस जाने के लिए"""
        # माउस व्हील अनबाइंड करें ताकि दूसरे पेज पर दिक्कत न आए
        self.main_canvas.unbind_all("<MouseWheel>")
        # ✅ सिर्फ फ्रेम स्विच करें
        self.controller.show_frame("LoginPage")