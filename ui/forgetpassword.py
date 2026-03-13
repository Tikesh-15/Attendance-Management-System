import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk

# डेटाबेस कनेक्शन को सुरक्षित तरीके से इम्पोर्ट करें
try:
    from database.db_connection import get_connection
except ImportError:
    get_connection = None

class forgotpassword(tk.Frame):
    def __init__(self, parent, controller):
        # सॉफ्ट नीला-सफ़ेद बैकग्राउंड कलर
        super().__init__(parent, bg="#E9F3FC")
        self.parent = parent
        self.controller = controller
        self.grid(row=0, column=0, sticky="nsew")
        # पासवर्ड शो/हाइड की स्थिति
        self.is_pwd_hidden = True

        self.create_ui()

    def create_ui(self):
        # --- Main Card Area (Rounded Canvas Trick) ---
        self.main_container = tk.Frame(self, bg="#E9F3FC")
        self.main_container.place(relx=0.5, rely=0.5, anchor="center")

        # व्हाइट बैकग्राउंड कार्ड (लॉगिन जैसा चौड़ा और साफ़)
        self.card = tk.Canvas(self.main_container, bg="white", width=420, height=620, 
                             bd=0, highlightthickness=0)
        self.card.pack()

        # कर्व्ड लुक के लिए रेक्टेंगल ड्रा करें
        self.card.create_rectangle(0, 0, 420, 620, fill="white", outline="#E0E0E0")

        # 1. LOGO (Blue Box with Icon)
        logo_frame = tk.Frame(self.card, bg="#1A73E8", width=70, height=70)
        logo_frame.pack_propagate(False)
        self.card.create_window(210, 70, window=logo_frame)
        tk.Label(logo_frame, text="🎓", font=("Arial", 35), bg="#1A73E8", fg="white").pack(expand=True)

        # 2. TITLES
        tk.Label(self.card, text="Reset Password", font=("Segoe UI", 22, "bold"), bg="white", fg="#111827").place(x=210, y=140, anchor="center")
        tk.Label(self.card, text="Enter details to update your account", font=("Segoe UI", 10), bg="white", fg="#6B7280").place(x=210, y=175, anchor="center")

        # --- INPUT FIELDS HELPER ---
        def create_modern_entry(label_text, icon_text, y_pos, is_pass=False):
            tk.Label(self.card, text=label_text, font=("Segoe UI", 10, "bold"), bg="white", fg="#374151").place(x=45, y=y_pos)
            
            entry_frame = tk.Frame(self.card, bg="white", highlightthickness=1, highlightbackground="#D1D5DB", bd=0)
            entry_frame.place(x=45, y=y_pos + 25, width=330, height=45)
            
            tk.Label(entry_frame, text=f" {icon_text} ", font=("Arial", 12), bg="white", fg="#9CA3AF").pack(side="left", padx=5)
            
            entry = tk.Entry(entry_frame, font=("Segoe UI", 11), bg="white", bd=0, fg="#111827")
            if is_pass: entry.config(show="•")
            entry.pack(side="left", fill="both", expand=True, padx=5)
            
            return entry, entry_frame

        # 3. FIELDS (लॉगिन जैसा आइकॉन स्टाइल)
        self.email_entry, _ = create_modern_entry("Email Address", "✉", 220)
        self.new_pass_entry, self.p_frame = create_modern_entry("New Password", "🔒", 300, is_pass=True)
        self.confirm_pass_entry, self.cp_frame = create_modern_entry("Confirm New Password", "🔒", 380, is_pass=True)

        # Show Password Button
        self.show_btn = tk.Button(self.card, text="👁", font=("Arial", 11), bg="white", bd=0, cursor="hand2", command=self.toggle_password)
        self.card.create_window(350, 348, window=self.show_btn)

        # 4. UPDATE BUTTON (Blue & Large)
        self.update_btn = tk.Button(self.card, text="Update Password", font=("Segoe UI", 12, "bold"), 
                                   bg="#1A73E8", fg="white", activebackground="#1557B0", 
                                   activeforeground="white", bd=0, cursor="hand2", command=self.reset_password_logic)
        self.update_btn.place(x=45, y=480, width=330, height=50)

        # 5. FOOTER (Back to Login)
        footer_frame = tk.Frame(self.card, bg="white")
        footer_frame.place(x=210, y=560, anchor="center")
        tk.Label(footer_frame, text="Remembered your password?", font=("Segoe UI", 10), bg="white", fg="#6B7280").pack(side="left")
        
        login_btn = tk.Button(footer_frame, text="Sign in", font=("Segoe UI", 10, "bold"), bg="white", bd=0, fg="#1A73E8", cursor="hand2", command=self.back_to_login)
        login_btn.pack(side="left", padx=5)

    # ================= LOGIC SECTION =================

    def toggle_password(self):
        """पासवर्ड दिखाने और छुपाने के लिए"""
        if self.is_pwd_hidden:
            self.new_pass_entry.config(show="")
            self.confirm_pass_entry.config(show="")
            self.show_btn.config(text="🙈")
            self.is_pwd_hidden = False
        else:
            self.new_pass_entry.config(show="•")
            self.confirm_pass_entry.config(show="•")
            self.show_btn.config(text="👁")
            self.is_pwd_hidden = True

    def clear_fields(self):
        """सबमिट के बाद सब साफ़ करने के लिए"""
        self.email_entry.delete(0, tk.END)
        self.new_pass_entry.delete(0, tk.END)
        self.confirm_pass_entry.delete(0, tk.END)

    def reset_password_logic(self):
        email = self.email_entry.get().strip()
        new_pwd = self.new_pass_entry.get().strip()
        conf_pwd = self.confirm_pass_entry.get().strip()

        if not email or not new_pwd or not conf_pwd:
            messagebox.showwarning("Form Error", "Bhai, sabhi details bharna zaruri hai!")
            return

        if new_pwd != conf_pwd:
            messagebox.showerror("Error", "Passwords match nahi kar rahe!")
            return

        try:
            if get_connection is None:
                messagebox.showerror("System Error", "Database connection missing!")
                return

            conn = get_connection()
            cursor = conn.cursor()

            # चेक करें कि ईमेल मौजूद है या नहीं
            cursor.execute("SELECT * FROM users WHERE email=?", (email,))
            if cursor.fetchone():
                cursor.execute("UPDATE users SET password=? WHERE email=?", (new_pwd, email))
                conn.commit()
                messagebox.showinfo("Success", "Password updated successfully! Clearing form...")
                self.clear_fields() # <--- फॉर्म साफ़ हो गया
                self.back_to_login()
            else:
                messagebox.showerror("Error", "Ye Email database mein nahi mili!")

            conn.close()
        except Exception as e:
            messagebox.showerror("DB Error", f"Something went wrong: {e}")

    def back_to_login(self):
        """सिर्फ लॉगिन पेज पर वापस जाने के लिए (Safe Way)"""
        try:
            # ❌ self.destroy() बिल्कुल नहीं करना है
            # ❌ LoginPage(self.parent) नया नहीं बनाना है
            
            # ✅ सिर्फ Controller को बोलो कि पुराना बना हुआ LoginPage दिखाओ
            self.controller.show_frame("LoginPage")
        except Exception as e:
            messagebox.showerror("Error", f"Navigation Error: {e}")