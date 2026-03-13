import tkinter as tk
from tkinter import ttk, messagebox

# डेटाबेस कनेक्शन हैंडलिंग
try:
    from database.db_connection import get_connection
except ImportError:
    get_connection = None

class LoginPage(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#E9F3FC")
        self.parent = parent
        self.controller = controller
        # self.pack(fill="both", expand=True) # main.py इसे खुद मैनेज करेगा

        self.create_ui()
        
        # Cursor focus
        self.username_entry.focus_set()
        self.bind_all("<Return>", lambda e: self.login())

    def create_ui(self):
        # --- Main Card Area ---
        self.main_container = tk.Frame(self, bg="#E9F3FC")
        self.main_container.place(relx=0.5, rely=0.5, anchor="center")

        self.card = tk.Canvas(self.main_container, bg="white", width=420, height=580, 
                             bd=0, highlightthickness=0)
        self.card.pack()

        self.draw_rounded_card()

        # --- Content inside Card ---
        logo_frame = tk.Frame(self.card, bg="#1A73E8", width=70, height=70)
        logo_frame.pack_propagate(False)
        self.card.create_window(210, 80, window=logo_frame)
        tk.Label(logo_frame, text="🎓", font=("Arial", 35), bg="#1A73E8", fg="white").pack(expand=True)

        tk.Label(self.card, text="Welcome Back", font=("Segoe UI", 24, "bold"), bg="white", fg="#111827").place(x=210, y=150, anchor="center")
        tk.Label(self.card, text="Login to your admin account", font=("Segoe UI", 11), bg="white", fg="#6B7280").place(x=210, y=190, anchor="center")

        # --- Input Fields ---
        tk.Label(self.card, text="Email Address", font=("Segoe UI", 10, "bold"), bg="white", fg="#374151").place(x=45, y=230)
        u_frame = tk.Frame(self.card, bg="white", highlightthickness=1, highlightbackground="#D1D5DB", bd=0)
        u_frame.place(x=45, y=255, width=330, height=45)
        
        tk.Label(u_frame, text=" ✉ ", font=("Arial", 12), bg="white", fg="#9CA3AF").pack(side="left", padx=5)
        self.username_entry = tk.Entry(u_frame, font=("Segoe UI", 11), bg="white", bd=0, fg="#111827")
        self.username_entry.pack(side="left", fill="both", expand=True, padx=5)

        tk.Label(self.card, text="Password", font=("Segoe UI", 10, "bold"), bg="white", fg="#374151").place(x=45, y=320)
        p_frame = tk.Frame(self.card, bg="white", highlightthickness=1, highlightbackground="#D1D5DB", bd=0)
        p_frame.place(x=45, y=345, width=330, height=45)
        
        tk.Label(p_frame, text=" 🔒 ", font=("Arial", 12), bg="white", fg="#9CA3AF").pack(side="left", padx=5)
        self.password_entry = tk.Entry(p_frame, font=("Segoe UI", 11), bg="white", bd=0, show="•", fg="#111827")
        self.password_entry.pack(side="left", fill="both", expand=True, padx=5)

        # Remember Me & Forgot Pass
        self.rem_var = tk.BooleanVar()
        tk.Checkbutton(self.card, text="Remember me", variable=self.rem_var, bg="white", activebackground="white", font=("Segoe UI", 9)).place(x=45, y=405)
        
        tk.Button(self.card, text="Forgot password?", bg="white", bd=0, fg="#1A73E8", 
                  font=("Segoe UI", 9, "bold"), cursor="hand2", command=self.go_to_forgot).place(x=265, y=405)

        self.login_btn = tk.Button(self.card, text="Sign In", font=("Segoe UI", 12, "bold"), 
                                   bg="#1A73E8", fg="white", activebackground="#1557B0", 
                                   activeforeground="white", bd=0, cursor="hand2", command=self.login)
        self.login_btn.place(x=45, y=450, width=330, height=50)

        footer_frame = tk.Frame(self.card, bg="white")
        footer_frame.place(x=210, y=530, anchor="center")
        tk.Label(footer_frame, text="Don't have an account?", font=("Segoe UI", 10), bg="white", fg="#6B7280").pack(side="left")
        tk.Button(footer_frame, text="Sign up", font=("Segoe UI", 10, "bold"), bg="white", bd=0, fg="#1A73E8", cursor="hand2", command=self.open_signup).pack(side="left", padx=5)

    def draw_rounded_card(self):
        self.card.create_rectangle(0, 0, 420, 580, fill="white", outline="#E0E0E0")

    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        if not get_connection:
            messagebox.showwarning("Database", "Database connection not found!")
            return

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE email=? AND password=?", (username, password))
        user = cursor.fetchone()
        conn.close()

        if user:
            # ✅ यहाँ मैंने लाइनों को अलग-अलग कर दिया है ताकि Syntax Error न आए
            self.controller.show_frame("Dashboard") 
        else:
            messagebox.showerror("Error", "Invalid email or Password")

    def open_signup(self):
        try:
            # ❌ तूने लिखा था: "signup_page"
            # ✅ सही नाम है: "SignupPage" (S और P कैपिटल, जैसा main.py में है)
            self.controller.show_frame("SignupPage")
        except Exception as e:
            messagebox.showerror("Error", f"Signup Page Load Error: {e}")

    def go_to_forgot(self):
        try:
            # ❌ तूने लिखा था: "forgetpassword"
            # ✅ सही नाम है: "forgotpassword" (O लगाओ, जैसा main.py के import में है)
            self.controller.show_frame("forgotpassword") 
        except Exception as e:
            messagebox.showerror("Error", f"Forgot Password Error: {e}")