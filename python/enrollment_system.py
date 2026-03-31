"""
Course Enrollment System — Python Version (Student Registration Use Case)

This is a Python recreation of the Student portion of the Java Course Enrollment System.
It supports: viewing the course catalog, registering for courses (with prerequisite,
capacity, and time-conflict checks), dropping courses, viewing schedules, billing,
and editing student profiles. Data is persisted as JSON.
"""

import json
import os
from dataclasses import dataclass, field
from typing import Optional


# ─────────────────────────────────────────────────────────────────────────────
# Models
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class TimeSlot:
    days: str = ""
    start_time: str = ""
    end_time: str = ""

    def _to_minutes(self, time_str: str) -> int:
        """Convert 'HH:mm' to total minutes. Returns -1 on error."""
        if not time_str or ":" not in time_str:
            return -1
        try:
            parts = time_str.split(":")
            return int(parts[0]) * 60 + int(parts[1])
        except (ValueError, IndexError):
            return -1

    def _share_days(self, d1: str, d2: str) -> bool:
        """Return True when two day-strings share at least one day token."""
        a, b = d1.upper(), d2.upper()
        for token in ["TH", "M", "T", "W", "F", "S", "U"]:
            if token in a and token in b:
                return True
        return False

    def overlaps(self, other: "TimeSlot") -> bool:
        if not other or not self.days or not other.days:
            return False
        if not self._share_days(self.days, other.days):
            return False
        s1, e1 = self._to_minutes(self.start_time), self._to_minutes(self.end_time)
        s2, e2 = self._to_minutes(other.start_time), self._to_minutes(other.end_time)
        if any(v < 0 for v in (s1, e1, s2, e2)):
            return False
        return s1 < e2 and s2 < e1

    def __str__(self) -> str:
        return f"{self.days} {self.start_time}-{self.end_time}"


@dataclass
class Course:
    code: str = ""
    title: str = ""
    credits: int = 0
    capacity: int = 0
    time_slot: Optional[TimeSlot] = None
    prerequisites: list[str] = field(default_factory=list)
    enrolled_students: list[str] = field(default_factory=list)

    def is_full(self) -> bool:
        return len(self.enrolled_students) >= self.capacity

    def available_seats(self) -> int:
        return max(0, self.capacity - len(self.enrolled_students))

    def has_student(self, student_id: str) -> bool:
        return student_id in self.enrolled_students

    def enroll_student(self, student_id: str) -> bool:
        if self.is_full() or self.has_student(student_id):
            return False
        self.enrolled_students.append(student_id)
        return True

    def remove_student(self, student_id: str) -> bool:
        if student_id in self.enrolled_students:
            self.enrolled_students.remove(student_id)
            return True
        return False

    def __str__(self) -> str:
        prereq = ", ".join(self.prerequisites) if self.prerequisites else "None"
        time_str = str(self.time_slot) if self.time_slot else "TBA"
        return (f"{self.code:<10} {self.title:<40} Credits: {self.credits}  "
                f"Capacity: {len(self.enrolled_students)}/{self.capacity}  "
                f"Time: {time_str:<18}  Prerequisites: {prereq}")


@dataclass
class Student:
    id: str = ""
    name: str = ""
    major: str = ""
    enrolled_courses: list[str] = field(default_factory=list)
    completed_courses: list[str] = field(default_factory=list)

    def is_enrolled_in(self, course_code: str) -> bool:
        return course_code in self.enrolled_courses

    def has_completed(self, course_code: str) -> bool:
        return course_code in self.completed_courses

    def enroll_in(self, course_code: str) -> bool:
        if self.is_enrolled_in(course_code):
            return False
        self.enrolled_courses.append(course_code)
        return True

    def drop_course(self, course_code: str) -> bool:
        if course_code in self.enrolled_courses:
            self.enrolled_courses.remove(course_code)
            return True
        return False

    def __str__(self) -> str:
        return f"ID: {self.id:<12}  Name: {self.name:<25}  Major: {self.major}"


# ─────────────────────────────────────────────────────────────────────────────
# Enrollment Result
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class EnrollmentResult:
    success: bool
    message: str


# ─────────────────────────────────────────────────────────────────────────────
# Enrollment System (Business Logic)
# ─────────────────────────────────────────────────────────────────────────────

class EnrollmentSystem:
    TUITION_PER_CREDIT = 300.0

    def __init__(self):
        self.students: dict[str, Student] = {}
        self.courses: dict[str, Course] = {}

    # ── Student management ──────────────────────────────────────────────
    def add_student(self, student: Student) -> bool:
        if not student or student.id in self.students:
            return False
        self.students[student.id] = student
        return True

    def get_student(self, sid: str) -> Optional[Student]:
        return self.students.get(sid)

    def update_student(self, sid: str, new_name: str, new_major: str) -> bool:
        student = self.students.get(sid)
        if not student:
            return False
        if new_name and new_name.strip():
            student.name = new_name.strip()
        if new_major and new_major.strip():
            student.major = new_major.strip()
        return True

    def get_all_students(self) -> list[Student]:
        return list(self.students.values())

    # ── Course management ───────────────────────────────────────────────
    def add_course(self, course: Course) -> bool:
        if not course or course.code in self.courses:
            return False
        self.courses[course.code] = course
        return True

    def get_course(self, code: str) -> Optional[Course]:
        return self.courses.get(code)

    def get_all_courses(self) -> list[Course]:
        return list(self.courses.values())

    # ── Registration logic ──────────────────────────────────────────────
    def register_course(self, student_id: str, course_code: str) -> EnrollmentResult:
        student = self.students.get(student_id)
        if not student:
            return EnrollmentResult(False, f"Student not found: {student_id}")

        course = self.courses.get(course_code)
        if not course:
            return EnrollmentResult(False, f"Course not found: {course_code}")

        if student.is_enrolled_in(course_code):
            return EnrollmentResult(False, f"You are already enrolled in {course_code}.")

        if course.is_full():
            return EnrollmentResult(False,
                f"Course {course_code} is full (capacity: {course.capacity}).")

        # Prerequisite check
        for prereq in course.prerequisites:
            if not student.has_completed(prereq):
                prereq_course = self.courses.get(prereq)
                prereq_title = prereq_course.title if prereq_course else prereq
                return EnrollmentResult(False,
                    f'Prerequisite not met: you must complete "{prereq_title}" '
                    f'({prereq}) before enrolling in {course_code}.')

        # Time conflict check
        for enrolled_code in student.enrolled_courses:
            enrolled = self.courses.get(enrolled_code)
            if (enrolled and enrolled.time_slot and course.time_slot
                    and enrolled.time_slot.overlaps(course.time_slot)):
                return EnrollmentResult(False,
                    f"Schedule conflict: {course_code} ({course.time_slot}) "
                    f"overlaps with {enrolled_code} ({enrolled.time_slot}).")

        student.enroll_in(course_code)
        course.enroll_student(student_id)
        return EnrollmentResult(True,
            f"Successfully enrolled in {course_code} – {course.title}.")

    def drop_course(self, student_id: str, course_code: str) -> EnrollmentResult:
        student = self.students.get(student_id)
        if not student:
            return EnrollmentResult(False, f"Student not found: {student_id}")

        course = self.courses.get(course_code)
        if not course:
            return EnrollmentResult(False, f"Course not found: {course_code}")

        if not student.is_enrolled_in(course_code):
            return EnrollmentResult(False, f"You are not enrolled in {course_code}.")

        student.drop_course(course_code)
        course.remove_student(student_id)
        return EnrollmentResult(True,
            f"Successfully dropped {course_code} – {course.title}.")

    # ── Reporting ───────────────────────────────────────────────────────
    def get_student_schedule(self, student_id: str) -> list[Course]:
        student = self.students.get(student_id)
        if not student:
            return []
        return [self.courses[c] for c in student.enrolled_courses if c in self.courses]

    def calculate_tuition(self, student_id: str) -> float:
        student = self.students.get(student_id)
        if not student:
            return -1.0
        total = sum(self.courses[c].credits
                    for c in student.enrolled_courses if c in self.courses)
        return total * self.TUITION_PER_CREDIT


# ─────────────────────────────────────────────────────────────────────────────
# Data Manager (JSON Persistence)
# ─────────────────────────────────────────────────────────────────────────────

class DataManager:
    DATA_DIR = "data"
    STUDENTS_FILE = os.path.join(DATA_DIR, "students.json")
    COURSES_FILE = os.path.join(DATA_DIR, "courses.json")

    def data_files_exist(self) -> bool:
        return (os.path.isfile(self.STUDENTS_FILE)
                and os.path.isfile(self.COURSES_FILE))

    def save_data(self, system: EnrollmentSystem) -> None:
        os.makedirs(self.DATA_DIR, exist_ok=True)
        with open(self.STUDENTS_FILE, "w") as f:
            json.dump([self._student_to_dict(s) for s in system.get_all_students()],
                      f, indent=2)
        with open(self.COURSES_FILE, "w") as f:
            json.dump([self._course_to_dict(c) for c in system.get_all_courses()],
                      f, indent=2)

    def load_data(self, system: EnrollmentSystem) -> None:
        if os.path.isfile(self.COURSES_FILE):
            with open(self.COURSES_FILE) as f:
                for c in json.load(f):
                    ts = c.get("timeSlot") or {}
                    course = Course(
                        code=c["code"], title=c["title"],
                        credits=c["credits"], capacity=c["capacity"],
                        time_slot=TimeSlot(ts.get("days", ""),
                                           ts.get("startTime", ""),
                                           ts.get("endTime", "")),
                        prerequisites=c.get("prerequisites", []),
                        enrolled_students=c.get("enrolledStudents", []),
                    )
                    system.courses[course.code] = course

        if os.path.isfile(self.STUDENTS_FILE):
            with open(self.STUDENTS_FILE) as f:
                for s in json.load(f):
                    student = Student(
                        id=s["id"], name=s["name"], major=s["major"],
                        enrolled_courses=s.get("enrolledCourses", []),
                        completed_courses=s.get("completedCourses", []),
                    )
                    system.students[student.id] = student

    def seed_default_data(self, system: EnrollmentSystem) -> None:
        courses = [
            Course("CS101", "Intro to Programming", 3, 30,
                   TimeSlot("MWF", "09:00", "10:00")),
            Course("CS201", "Data Structures", 3, 25,
                   TimeSlot("MWF", "10:00", "11:00"), prerequisites=["CS101"]),
            Course("CS301", "Algorithms", 3, 25,
                   TimeSlot("TTh", "09:00", "10:30"), prerequisites=["CS201"]),
            Course("CS401", "Operating Systems", 3, 20,
                   TimeSlot("TTh", "10:30", "12:00"), prerequisites=["CS301"]),
            Course("MATH101", "Calculus I", 4, 35,
                   TimeSlot("MWF", "08:00", "09:00")),
            Course("MATH201", "Calculus II", 4, 30,
                   TimeSlot("MWF", "11:00", "12:00")),
            Course("ENG101", "Technical Writing", 2, 40,
                   TimeSlot("TTh", "13:00", "14:00")),
            Course("NET101", "Computer Networks", 3, 25,
                   TimeSlot("MWF", "14:00", "15:00")),
            Course("DB101", "Database Systems", 3, 25,
                   TimeSlot("TTh", "14:00", "15:30")),
            Course("SE101", "Software Engineering", 3, 30,
                   TimeSlot("MWF", "15:00", "16:00")),
        ]
        for c in courses:
            system.add_course(c)

        alice = Student("STU001", "Alice Johnson", "Computer Science",
                        completed_courses=["CS101"])
        bob = Student("STU002", "Bob Smith", "Mathematics")
        carol = Student("STU003", "Carol Williams", "Information Technology",
                        completed_courses=["CS101", "CS201"])
        for s in (alice, bob, carol):
            system.add_student(s)

    # ── Serialisation helpers ───────────────────────────────────────────
    @staticmethod
    def _student_to_dict(s: Student) -> dict:
        return {
            "id": s.id, "name": s.name, "major": s.major,
            "enrolledCourses": s.enrolled_courses,
            "completedCourses": s.completed_courses,
        }

    @staticmethod
    def _course_to_dict(c: Course) -> dict:
        ts = {"days": c.time_slot.days,
              "startTime": c.time_slot.start_time,
              "endTime": c.time_slot.end_time} if c.time_slot else None
        return {
            "code": c.code, "title": c.title,
            "credits": c.credits, "capacity": c.capacity,
            "timeSlot": ts,
            "prerequisites": c.prerequisites,
            "enrolledStudents": c.enrolled_students,
        }


# ─────────────────────────────────────────────────────────────────────────────
# CLI Application (Student Use Case)
# ─────────────────────────────────────────────────────────────────────────────

SEP = "=" * 70
THIN = "-" * 70


def print_course_header():
    print(f"  {'Code':<10} {'Title':<40} {'Credits':<8} {'Seats':<12} "
          f"{'Time':<18} Prerequisites")
    print(f"  {THIN}")


def view_catalog(system: EnrollmentSystem):
    print(f"\n{SEP}")
    print("  COURSE CATALOG")
    print(SEP)
    courses = system.get_all_courses()
    if not courses:
        print("  No courses available.")
        return
    print_course_header()
    for c in courses:
        print(f"  {c}")


def register_for_course(system: EnrollmentSystem, student: Student):
    print("\n  --- Register for a Course ---")
    view_catalog(system)
    code = input("\n  Enter course code to register (or press Enter to cancel): ").strip().upper()
    if not code:
        return
    result = system.register_course(student.id, code)
    symbol = "✓" if result.success else "✗"
    print(f"  [{symbol}] {result.message}")


def drop_course(system: EnrollmentSystem, student: Student):
    print("\n  --- Drop a Course ---")
    schedule = system.get_student_schedule(student.id)
    if not schedule:
        print("  You are not enrolled in any courses.")
        return
    print("  Your current courses:")
    for c in schedule:
        print(f"    {c.code} – {c.title}")
    code = input("\n  Enter course code to drop (or press Enter to cancel): ").strip().upper()
    if not code:
        return
    result = system.drop_course(student.id, code)
    symbol = "✓" if result.success else "✗"
    print(f"  [{symbol}] {result.message}")


def view_schedule(system: EnrollmentSystem, student: Student):
    print(f"\n{SEP}")
    print(f"  SCHEDULE FOR: {student.name} [{student.id}]")
    print(SEP)
    schedule = system.get_student_schedule(student.id)
    if not schedule:
        print("  You are not enrolled in any courses.")
        return
    print_course_header()
    for c in schedule:
        print(f"  {c}")
    total = sum(c.credits for c in schedule)
    print(f"\n  Total Credits Enrolled: {total}")


def billing_summary(system: EnrollmentSystem, student: Student):
    print(f"\n{SEP}")
    print(f"  BILLING SUMMARY FOR: {student.name} [{student.id}]")
    print(SEP)
    schedule = system.get_student_schedule(student.id)
    if not schedule:
        print("  You are not enrolled in any courses. Tuition: $0.00")
        return
    print(f"  {'Code':<10} {'Title':<40} Credits")
    print(f"  {THIN}")
    total_credits = 0
    for c in schedule:
        print(f"  {c.code:<10} {c.title:<40} {c.credits}")
        total_credits += c.credits
    tuition = system.calculate_tuition(student.id)
    print(f"  {THIN}")
    print(f"  Total Credits : {total_credits}")
    print(f"  Rate per Credit: $300.00")
    print(f"  {'TOTAL TUITION:':<42} ${tuition:.2f}")


def edit_profile(system: EnrollmentSystem, student: Student):
    print("\n  --- Edit My Profile ---")
    print(f"  Current: {student}")
    print("  (Press Enter to keep current value)")
    name = input(f"  New Name  [{student.name}]: ").strip()
    major = input(f"  New Major [{student.major}]: ").strip()
    system.update_student(student.id, name, major)
    print(f"  [✓] Profile updated.")
    print(f"  Updated: {student}")


def create_student_profile(system: EnrollmentSystem) -> Optional[Student]:
    print("\n  --- Create New Student Profile ---")
    sid = input("  Student ID: ").strip()
    if not sid:
        print("  [!] Student ID cannot be empty.")
        return None
    if system.get_student(sid):
        print("  [!] Student ID already exists.")
        return None
    name = input("  Full Name : ").strip()
    if not name:
        print("  [!] Name cannot be empty.")
        return None
    major = input("  Major     : ").strip() or "Undeclared"
    student = Student(sid, name, major)
    system.add_student(student)
    print(f"  [✓] New student profile created: {student}")
    return student


def student_menu(system: EnrollmentSystem, student: Student):
    while True:
        print(f"\n{SEP}")
        print(f"  STUDENT MENU  –  {student.name} [{student.id}]")
        print(SEP)
        print("  [1] View Course Catalog")
        print("  [2] Register for a Course")
        print("  [3] Drop a Course")
        print("  [4] View My Schedule")
        print("  [5] Billing Summary")
        print("  [6] Edit My Profile")
        print("  [7] Logout and Save")
        print(THIN)
        choice = input("  Select option: ").strip()

        if choice == "1":
            view_catalog(system)
        elif choice == "2":
            register_for_course(system, student)
        elif choice == "3":
            drop_course(system, student)
        elif choice == "4":
            view_schedule(system, student)
        elif choice == "5":
            billing_summary(system, student)
        elif choice == "6":
            edit_profile(system, student)
        elif choice == "7":
            return
        else:
            print("  [!] Invalid option.")


def student_login(system: EnrollmentSystem) -> None:
    print("\n  --- Student Login ---")
    sid = input("  Enter your Student ID (or 'new' to create a new profile): \n  > ").strip()
    if sid.lower() == "new":
        new_student = create_student_profile(system)
        if new_student:
            student_menu(system, new_student)
        return
    student = system.get_student(sid)
    if not student:
        print("  [!] Student ID not found. Type 'new' to create a new profile.")
        return
    print(f"  Welcome, {student.name}!")
    student_menu(system, student)


def main():
    system = EnrollmentSystem()
    dm = DataManager()

    # ── Startup ──
    print(SEP)
    print("       COURSE ENROLLMENT SYSTEM (Python)")
    print(SEP)

    if dm.data_files_exist():
        try:
            dm.load_data(system)
            print("[INFO] Data loaded from disk.")
        except Exception as e:
            print(f"[WARN] Could not load saved data: {e}")
            print("[INFO] Starting with default data.")
            dm.seed_default_data(system)
    else:
        print("[INFO] First run detected — loading default course catalog and sample students.")
        dm.seed_default_data(system)

    # ── Main loop ──
    while True:
        print(f"\n{SEP}")
        print("  LOGIN")
        print(SEP)
        print("  [1] Login as Student")
        print("  [2] Exit")
        print(THIN)
        choice = input("  Select option: ").strip()

        if choice == "1":
            student_login(system)
            try:
                dm.save_data(system)
                print("  [✓] Data saved successfully.")
            except IOError as e:
                print(f"  [!] Error saving data: {e}")
        elif choice == "2":
            try:
                dm.save_data(system)
                print("  [✓] Data saved successfully.")
            except IOError as e:
                print(f"  [!] Error saving data: {e}")
            print(f"\n  Thank you for using the Course Enrollment System. Goodbye!")
            print(SEP)
            break
        else:
            print("  [!] Invalid option. Please enter 1 or 2.")


if __name__ == "__main__":
    main()
