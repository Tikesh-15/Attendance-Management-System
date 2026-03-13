import sqlite3
from database.db_connection import get_connection

def create_tables():
    conn = get_connection()
    # Foreign Key support enable करना ज़रूरी है ताकि CASCADE डिलीट काम करे
    conn.execute("PRAGMA foreign_keys = ON") 
    cursor = conn.cursor()

    # ================= 1. USERS TABLE (Admin Login) =================
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT UNIQUE NOT NULL,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL
    )
    """)

    # ================= 2. COURSES TABLE =================
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS course(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        course_name TEXT UNIQUE NOT NULL,
        course_code TEXT UNIQUE, 
        department TEXT,
        duration TEXT,
        description TEXT,
        teacher TEXT DEFAULT 'Not Assigned',
        students_count INTEGER DEFAULT 0
    )
    """)

    # ================= 3. STAFF TABLE (इसे Subjects से पहले रखना होगा) =================
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS staff(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        first TEXT, last TEXT, email TEXT UNIQUE, phone TEXT, 
        dob TEXT, gender TEXT, address TEXT, city TEXT, 
        state TEXT, zip TEXT, emp_id TEXT UNIQUE, dept TEXT, 
        designation TEXT, join_date TEXT, qualification TEXT,
        experience TEXT, salary TEXT
    )
    """)

    # ================= 4. SUBJECTS TABLE =================
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS subjects(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        subject_name TEXT NOT NULL,
        course TEXT,
        staff_id INTEGER,
        FOREIGN KEY(staff_id) REFERENCES staff(id) ON DELETE SET NULL
    )
    """)

    # ================= 5. STUDENTS TABLE =================
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS students (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        first TEXT, last TEXT, 
        email TEXT UNIQUE, -- ईमेल भी यूनिक होना चाहिए
        phone TEXT, dob TEXT, gender TEXT,
        address TEXT, city TEXT, state TEXT, zip TEXT,
        guardian TEXT, g_phone TEXT, 
        course TEXT, semester TEXT, 
        roll TEXT UNIQUE NOT NULL, 
        adm_date TEXT
    )
    """)

    # ================= 6. ATTENDANCE TABLE =================
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS attendance (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER,
        subject_id INTEGER, 
        roll_no TEXT,
        student_name TEXT,
        course TEXT,
        subject TEXT,
        semester TEXT, -- एक्स्ट्रा सेफ्टी के लिए
        date TEXT,
        status TEXT CHECK(status IN ('Present','Absent','Leave')),
        FOREIGN KEY(student_id) REFERENCES students(id) ON DELETE CASCADE,
        FOREIGN KEY(subject_id) REFERENCES subjects(id) ON DELETE CASCADE
    )
    """)

    conn.commit()
    conn.close()
    print("✅ सभी टेबल्स (Attendance और Staff सहित) सफलतापूर्वक सिंक हो गई हैं!")

if __name__ == "__main__":
    create_tables()