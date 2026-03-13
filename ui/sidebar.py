import tkinter as tk
from tkinter import ttk, messagebox

# ===== IMPORT PAGES =====
from ui.home import HomePage
from ui.student.add_student import AddStudent
from ui.student.manage_student import ManageStudent
from ui.staff.add_staff import AddStaff
from ui.staff.manage_staff import ManageStaff
from ui.course.add_course import AddCourse
from ui.course.manage_course import ManageCourse
from ui.subject.add_subject import AddSubject 
from ui.subject.manage_subject import ManageSubject 
from ui.attendance.mark_attendance import MarkAttendance
from ui.attendance.view_attendance import ViewAttendance

class Sidebar(tk.Frame):
    def __init__(self, parent, controller, content_frame):
        super().__init__(parent, bg="#ffffff", width=280, highlightthickness=1, highlightbackground="#f1f5f9")

        self.controller = controller
        self.content_frame = content_frame
        self.pack_propagate(False)
        self.open_menu = None

        # 1. Header (Logo)
        self.setup_header()

        # 2. Fixed Logout (नीचे फिक्स रहेगा)
        self.setup_fixed_logout()

        # 3. Middle Scrollable Menu Area
        self.setup_scrollable_menu()
        
        # मेनू आइटम्स बनाना
        self.build_menu()

    def setup_header(self):
        brand_frame = tk.Frame(self, bg="#ffffff", pady=25)
        brand_frame.pack(fill="x", side="top")
        
        tk.Label(brand_frame, text="🎓 EduManage", font=("Segoe UI", 22, "bold"), 
                 bg="#ffffff", fg="#2563eb").pack(anchor="w", padx=25)
        tk.Label(brand_frame, text="ADMIN PANEL", font=("Segoe UI", 8, "bold"), 
                 bg="#ffffff", fg="#94a3b8").pack(anchor="w", padx=25)
        
        tk.Frame(self, bg="#f1f5f9", height=2).pack(fill="x", padx=20)

    def setup_scrollable_menu(self):
        # मेनू कंटेनर
        self.menu_container = tk.Frame(self, bg="#ffffff")
        self.menu_container.pack(fill="both", expand=True)

        # Canvas और Scrollbar
        self.canvas = tk.Canvas(self.menu_container, bg="#ffffff", highlightthickness=0)
        self.scroll_frame = tk.Frame(self.canvas, bg="#ffffff")

        # विन्डो सेटअप
        self.canvas_window = self.canvas.create_window((0, 0), window=self.scroll_frame, anchor="nw", width=260)

        # स्क्रॉल बाइंडिंग (Canvas और Scroll Frame दोनों पर)
        self.canvas.bind('<Enter>', self._bind_mouse)
        self.canvas.bind('<Leave>', self._unbind_mouse)
        self.scroll_frame.bind('<Enter>', self._bind_mouse)
        self.scroll_frame.bind('<Leave>', self._unbind_mouse)

        # ऑटो स्क्रॉल रीजन अपडेट
        self.scroll_frame.bind("<Configure>", self._on_frame_configure)
        
        self.canvas.pack(side="left", fill="both", expand=True)

    def _on_frame_configure(self, event):
        # कंटेंट के हिसाब से स्क्रॉल एरिया अपडेट करना
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    # --- माउस व्हील लॉजिक ---
    def _bind_mouse(self, event):
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)

    def _unbind_mouse(self, event):
        self.canvas.unbind_all("<MouseWheel>")

    def _on_mousewheel(self, event):
        try:
            # -1 * (delta/120) विंडोज के लिए सटीक स्क्रॉल देता है
            self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        except:
            pass

    def build_menu(self):
        self.add_section_label("GENERAL")
        self.menu_button("🏠   Dashboard", HomePage)

        self.add_section_label("MANAGEMENT")
        
        self.create_dropdown("👨‍🎓   Students", [
            ("Add Student", AddStudent),
            ("Manage Students", ManageStudent)
        ])

        self.create_dropdown("👨‍💼   Staff Members", [
            ("Add Staff", AddStaff),
            ("Manage Staff", ManageStaff)
        ])

        self.create_dropdown("📚   Subject Records", [
            ("Add Subject", AddSubject),
            ("Manage Subjects", ManageSubject)
        ])

        self.create_dropdown("📘   Course Catalog", [
            ("Add Course", AddCourse),
            ("Manage Courses", ManageCourse)
        ])

        self.add_section_label("OPERATIONS")
        
        self.create_dropdown("📝   Attendance", [
            ("Mark Attendance", MarkAttendance),
            ("View Logs", ViewAttendance)
        ])

    def add_section_label(self, text):
        lbl = tk.Label(self.scroll_frame, text=text, font=("Segoe UI", 9, "bold"),
                       bg="#ffffff", fg="#94a3b8", pady=15)
        lbl.pack(anchor="w", padx=25)
        # लेबल पर भी बाइंडिंग ताकि यहाँ भी स्क्रॉल चले
        lbl.bind('<Enter>', self._bind_mouse)

    def menu_button(self, text, page):
        btn = tk.Button(self.scroll_frame, text=f"   {text}", font=("Segoe UI", 11, "bold"),
                       bg="#ffffff", fg="#334155", relief="flat", anchor="w",
                       padx=10, pady=12, cursor="hand2", activebackground="#f1f5f9",
                       command=lambda: self.show_page(page))
        btn.pack(fill="x", padx=15, pady=2)
        
        # बटन पर बाइंडिंग (सबसे ज़रूरी!)
        btn.bind("<Enter>", lambda e: (btn.config(bg="#f8fafc", fg="#2563eb"), self._bind_mouse(e)))
        btn.bind("<Leave>", lambda e: (btn.config(bg="#ffffff", fg="#334155"), self._unbind_mouse(e)))

    def create_dropdown(self, title, items):
        container = tk.Frame(self.scroll_frame, bg="#ffffff")
        container.pack(fill="x", padx=15, pady=2)

        btn = tk.Button(container, text=f"   {title}", font=("Segoe UI", 11, "bold"),
                       bg="#ffffff", fg="#334155", relief="flat", anchor="w",
                       padx=10, pady=12, cursor="hand2", activebackground="#f1f5f9")
        btn.pack(fill="x")

        sub_frame = tk.Frame(container, bg="#ffffff")

        def toggle():
            if self.open_menu and self.open_menu != sub_frame:
                self.open_menu.pack_forget()
            
            if sub_frame.winfo_ismapped():
                sub_frame.pack_forget()
                self.open_menu = None
            else:
                sub_frame.pack(fill="x", pady=(0, 5))
                self.open_menu = sub_frame
            # ड्रॉपडाउन खुलने पर स्क्रॉल रीजन अपडेट करें
            self._on_frame_configure(None)

        btn.config(command=toggle)
        btn.bind("<Enter>", self._bind_mouse)

        for text, page in items:
            sub_btn = tk.Button(sub_frame, text=f"      ○   {text}", font=("Segoe UI", 10, "bold"),
                               bg="#ffffff", fg="#64748b", relief="flat", anchor="w",
                               padx=10, pady=8, cursor="hand2", activebackground="#eff6ff",
                               command=lambda p=page: self.show_page(p))
            sub_btn.pack(fill="x")
            sub_btn.bind("<Enter>", lambda e, b=sub_btn: (b.config(bg="#eff6ff", fg="#2563eb"), self._bind_mouse(e)))
            sub_btn.bind("<Leave>", lambda e, b=sub_btn: (b.config(bg="#ffffff", fg="#64748b"), self._unbind_mouse(e)))

    def setup_fixed_logout(self):
        logout_container = tk.Frame(self, bg="#ffffff", pady=20)
        logout_container.pack(side="bottom", fill="x")
        
        # यहाँ command=self.logout_action जोड़ना है
        logout_btn = tk.Button(logout_container, text="  ⎋   Logout System", 
                               font=("Segoe UI", 11, "bold"),
                               bg="#fff1f2", fg="#e11d48", relief="flat", 
                               cursor="hand2", command=self.logout_action) 
        logout_btn.pack(fill="x", padx=20)

    def logout_action(self):
        if messagebox.askyesno("Logout", "Kya aap login page par jana chahte hain?"):
            # self.controller hamesha App class honi chahiye
            self.controller.show_frame("LoginPage")

    # ui/sidebar.py ke andar
    def show_page(self, page_class):
        # Seedha controller ka show_frame call karo
        self.controller.show_frame(page_class)
    def logout_action(self):
        if messagebox.askyesno("Logout", "Do you want to logout?"):
            # Yahan controller use karo na ki self
            self.controller.show_frame("LoginPage")
             

    def get_page(self, page_name):
          return self.frames[page_name]