import tkinter as tk
from config import APP_TITLE, WINDOW_SIZE
from database.models import create_tables

# --- 1. SARE PAGES KO IMPORT KAREIN ---
from ui.login_page import LoginPage
from ui.home import HomePage
from ui.sidebar import Sidebar 
from ui.staff.manage_staff import ManageStaff
from ui.staff.add_staff import AddStaff 
from ui.student.add_student import AddStudent
from ui.student.manage_student import ManageStudent
from ui.signup_page import SignupPage
from ui.forgetpassword import forgotpassword 

# --- MISSING IMPORTS (YAHAN GADBAD THI) ---
from ui.course.add_course import AddCourse
from ui.course.manage_course import ManageCourse
from ui.subject.add_subject import AddSubject
from ui.subject.manage_subject import ManageSubject
from ui.attendance.mark_attendance import MarkAttendance
from ui.attendance.view_attendance import ViewAttendance

class App(tk.Tk):
    def __init__(self):
        super().__init__()

        # ================= WINDOW SETTINGS =================
        self.title(APP_TITLE)
        self.geometry(WINDOW_SIZE)
        self.minsize(1100, 700)
        self.frames = {}
        
        # Database Setup
        create_tables()

        # ================= LAYOUT STRUCTURE =================
        # 1. Sidebar (Left side) 
        try:
            self.sidebar_frame = Sidebar(parent=self, controller=self, content_frame=None)
        except:
            from ui.sidebar import Sidebar as sidebar_class
            self.sidebar_frame = sidebar_class(parent=self, controller=self, content_frame=None)
        
        # 2. Container (Right side jisme saare pages load honge)
        self.container = tk.Frame(self)
        self.container.pack(side="right", fill="both", expand=True)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        # Sidebar ko container assign karein
        self.sidebar_frame.content_frame = self.container

        # ================= FRAME INITIALIZATION =================
        # Sabhi pages ko yahan register karna zaruri hai
        page_list = (
            LoginPage, HomePage, 
            ManageStaff, AddStaff, 
            ManageStudent, AddStudent, 
            SignupPage, forgotpassword,
            AddCourse, ManageCourse,        # <--- Fixed
            AddSubject, ManageSubject,      # <--- Fixed
            MarkAttendance, ViewAttendance  # <--- Fixed
        )

        for F in page_list:
            page_name = F.__name__
            try:
                # Har page ko container ke andar grid kar rahe hain
                # Sabhi pages __init__(self, parent, controller) accept karne chahiye
                frame = F(parent=self.container, controller=self) 
                self.frames[page_name] = frame
                frame.grid(row=0, column=0, sticky="nsew")
            except Exception as e:
                print(f"Error loading {page_name}: {e}")

        # Dashboard alias setup
        if "HomePage" in self.frames:
            self.frames["Dashboard"] = self.frames["HomePage"]

        # Default page load
        self.show_frame("LoginPage")

    # main.py ke andar
    def show_frame(self, page_name, edit_data=None):
        # 1. Agar page_name ek CLASS hai, toh uska naam (string) nikal lo
        if not isinstance(page_name, str):
            try:
                page_name = page_name.__name__
            except:
                # Agar tab bhi na mile toh dashboard pe bhej do backup ke liye
                page_name = "HomePage"

        if page_name == "Dashboard": 
            page_name = "HomePage"

        if page_name in self.frames:
            frame = self.frames[page_name]
            
            # Sidebar logic
            no_sidebar_pages = ["LoginPage", "SignupPage", "forgotpassword"]
            if page_name in no_sidebar_pages:
                if hasattr(self, 'sidebar_frame'): self.sidebar_frame.pack_forget()
            else:
                if hasattr(self, 'sidebar_frame'):
                    self.sidebar_frame.pack(side="left", fill="y", before=self.container)

            # --- EDIT DATA LOGIC ---
            if edit_data is not None:
                # AddStudent/AddStaff ke liye fill_form_for_edit use hota hai
                if hasattr(frame, "fill_form_for_edit"):
                    frame.fill_form_for_edit(edit_data)
                # AddCourse ke liye fill_data use hota hai
                elif hasattr(frame, "fill_data"):
                    frame.fill_data(edit_data)

            frame.tkraise()
            
            if hasattr(frame, "refresh_data"):
                try: frame.refresh_data()
                except: pass
        else:
            print(f"Bhai, {page_name} frames dictionary mein nahi mila!")

    # Backup function agar koi page show_page call kare
    def show_page(self, page_name, edit_data=None):
        self.show_frame(page_name, edit_data=edit_data)

    def get_page(self, page_name):
        """Frames return karne ke liye (Edit/Data passing ke liye)"""
        return self.frames.get(page_name)

def main():
    app = App()
    app.mainloop()

if __name__ == "__main__":
    main()