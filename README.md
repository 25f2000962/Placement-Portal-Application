Placement Portal

Overview
The Placement Portal is a web-based application that connects students and companies for campus recruitment. It allows students to apply for jobs, companies to post job drives, and admins to manage the entire system.

Features

Student
- Register and login
- View available job drives
- Apply for jobs
- Upload resume
- Track application status
- Edit profile

Company
- Register and login
- Create job drives
- View applicants
- Shortlist or reject candidates
- Manage job postings
- Edit profile

Admin
- Manage students and companies
- Approve/reject companies
- View all job drives
- Approve/reject drives
- View system statistics

Tech Stack
- Backend: Flask (Python)
- Frontend: HTML, CSS, Bootstrap
- Database: SQLite (SQLAlchemy ORM)
- Other Tools: Jinja2 Templates

Project Structure

placement-portal/
│── app.py
│── model.py
│── templates/
│── static/
│── api.yaml
│── README.md
│── venv/


How to Run

1. Clone the repository
2. Create virtual environment:
    python -m venv venv

3. Activate virtual environment:
 Windows:
  ```
  venv\Scripts\activate
  ```
4. Install dependencies:

pip install flask sqlalchemy

5. Run the application:

python app.py

6. Open browser:

http://127.0.0.1:5000/