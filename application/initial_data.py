from .model import db, Admin, Company, Student, Job
from app import app

with app.app_context():
    db.create_all()

    if not Admin.query.first():
        admin = Admin(email="admin@g.com", password="pass")
        db.session.add(admin)

    if not Company.query.first():
        comp1 = Company(company_name="TCS", email="c1@g.com", password="pass")
        comp2 = Company(company_name="Infosys", email="c2@g.com", password="pass")
        db.session.add_all([comp1, comp2])

    if not Student.query.first():
        stud1 = Student(name="Rahul", email="s1@g.com", password="pass", phone="1234567890")
        stud2 = Student(name="Priya", email="s2@g.com", password="pass", phone="9876543210")
        db.session.add_all([stud1, stud2])

    db.session.commit()

    if not Job.query.first():
        job1 = Job(title="Software Engineer", description="Dev role", company_id=1)
        job2 = Job(title="Data Analyst", description="Data role", company_id=2)
        db.session.add_all([job1, job2])

    db.session.commit()