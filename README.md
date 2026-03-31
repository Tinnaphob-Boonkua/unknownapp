# unknownapp
This is an unknown application written in Java

## What is this program?

This is a **Course Enrollment System** — a command-line application that allows **Students** and **Administrators** to manage course registrations at a university.

### Key Features
- **Student role**: View course catalog, register/drop courses (with prerequisite, capacity, and time-conflict checks), view schedule, view billing summary, and edit profile.
- **Admin role**: All student features plus managing students and courses, viewing class rosters, and viewing any student's schedule/billing.
- **Data persistence**: All data is saved to and loaded from JSON files (`data/students.json`, `data/courses.json`).

---- For Submission (you must fill in the information below) ----

### Use Case Diagram

```mermaid
graph LR
    subgraph Course Enrollment System
        UC1["View Course Catalog"]
        UC2["Register for a Course"]
        UC3["Drop a Course"]
        UC4["View My Schedule"]
        UC5["View Billing Summary"]
        UC6["Edit My Profile"]
        UC7["Create Student Profile"]
        UC8["Login / Logout"]
        UC9["View Class Roster"]
        UC10["View All Students"]
        UC11["Add New Student"]
        UC12["Edit Student Profile"]
        UC13["Add New Course"]
        UC14["Edit Course"]
        UC15["View Student Schedule"]
        UC16["Billing Summary - Any Student"]
        UC17["Save / Load Data"]
    end

    Student((Student))
    Admin((Admin))

    Student --> UC8
    Student --> UC1
    Student --> UC2
    Student --> UC3
    Student --> UC4
    Student --> UC5
    Student --> UC6
    Student --> UC7

    Admin --> UC8
    Admin --> UC1
    Admin --> UC9
    Admin --> UC10
    Admin --> UC11
    Admin --> UC12
    Admin --> UC13
    Admin --> UC14
    Admin --> UC15
    Admin --> UC16

    UC2 -.->|includes| UC17
    UC3 -.->|includes| UC17
    UC8 -.->|includes| UC17
```

### Flowchart of the main workflow

```mermaid
flowchart TD
    A[Start] --> B[Load Data]
    B --> C{Login Menu}
    C -->|1 - Student Login| D{Enter Student ID}
    C -->|2 - Admin Login| E{Enter Password}
    C -->|3 - Exit| F[Save Data & Exit]

    D -->|Type 'new'| G[Create New Student Profile]
    D -->|Existing ID| H{Student Found?}
    H -->|No| C
    H -->|Yes| I[Student Menu]
    G --> I

    E -->|Correct| J[Admin Menu]
    E -->|Incorrect| C

    I --> I1{Select Option}
    I1 -->|1| I2[View Course Catalog]
    I1 -->|2| I3[Register for a Course]
    I1 -->|3| I4[Drop a Course]
    I1 -->|4| I5[View My Schedule]
    I1 -->|5| I6[Billing Summary]
    I1 -->|6| I7[Edit My Profile]
    I1 -->|7 - Logout| I8[Save Data]
    I2 --> I1
    I3 --> I1
    I4 --> I1
    I5 --> I1
    I6 --> I1
    I7 --> I1
    I8 --> C

    J --> J1{Select Option}
    J1 -->|1| J2[View Course Catalog]
    J1 -->|2| J3[View Class Roster]
    J1 -->|3| J4[View All Students]
    J1 -->|4| J5[Add New Student]
    J1 -->|5| J6[Edit Student Profile]
    J1 -->|6| J7[Add New Course]
    J1 -->|7| J8[Edit Course]
    J1 -->|8| J9[View Student Schedule]
    J1 -->|9| J10[Billing Summary]
    J1 -->|10 - Logout| J11[Save Data]
    J2 --> J1
    J3 --> J1
    J4 --> J1
    J5 --> J1
    J6 --> J1
    J7 --> J1
    J8 --> J1
    J9 --> J1
    J10 --> J1
    J11 --> C
```

### Prompts

I used the following prompts with an AI assistant to help create the Python version of the Student Course Registration use case:


**Prompt 2 — Generating the Python code:**
> "Create a Python command-line program that replicates the Student portion of this Java Course Enrollment System. It should:
> 1. Load courses and students from JSON files (same format as the Java version).
> 2. Let a student log in by ID or create a new profile.
> 3. Provide a menu with: View Catalog, Register for a Course, Drop a Course, View Schedule, Billing Summary, Edit Profile, Logout.
> 4. When registering, enforce: no duplicate enrollment, capacity limits, prerequisite checks, and time-slot conflict detection.
> 5. Save data back to JSON on logout or exit.
> Use classes for Course, Student, TimeSlot, EnrollmentSystem, and DataManager, mirroring the Java structure."

