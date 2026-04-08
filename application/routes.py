from app import app
from .model import db, Admin, Student, Company, Job, Application, Placement
from flask import render_template, request, redirect, session
from flask import flash
from datetime import datetime
from sqlalchemy import or_
import os
from werkzeug.utils import secure_filename
import os
import uuid


@app.route("/")
def home():
    return render_template("home.html")


@app.route("/register/student", methods=["GET", "POST"])
def register_student():
    if request.method == "GET":
        return render_template("student/register.html")

    name = request.form.get("name")
    email = request.form.get("email")
    password = request.form.get("password")
    phone = request.form.get("phone")
    file = request.files.get("resume")

    if not name or not email or not password:
        flash("Fill all required fields")
        return redirect("/register/student")
    existing_student = Student.query.filter_by(email=email).first()

    if existing_student:
        flash("You are already registered! Please login.", "warning")
        return redirect("/login")
    
    student = Student(name=name, email=email, password=password, phone=phone)
    db.session.add(student)
    db.session.commit()

    flash("Registration successful! Please login.", "success")
    return redirect("/login")

@app.route("/register/company", methods=["GET", "POST"])
def register_company():
    if request.method == "GET":
        return render_template("company/register.html")

    name = request.form.get("company_name")
    email = request.form.get("email")
    password = request.form.get("password")
    hr_contact = request.form.get("hr_contact")
    website = request.form.get("website")
    if not name or not email or not password:
        flash("Please fill all fields", "danger")
        return redirect("/register/company")

    if Company.query.filter_by(email=email).first():
        flash("Company already registered!", "warning")
        return redirect("/login")
    
    if Company.query.filter_by(email=email).first():
        flash("You are already registered! Please login.", "warning")
        return redirect("/login")

    company = Company(company_name=name, email=email, password=password,hr_contact=hr_contact,
        website=website)
    db.session.add(company)
    db.session.commit()

    flash("Company registered successfully!", "success")  
    return redirect("/login")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")

    email = request.form.get("email")
    password = request.form.get("password")
    role = request.form.get("role")
    

    user = None

    # ROLE-BASED LOGIN (IMPORTANT)
    if role == "student":
        user = Student.query.filter_by(email=email).first()
    elif role == "company":
        user = Company.query.filter_by(email=email).first()
    elif role == "admin":
        user = Admin.query.filter_by(email=email).first()

    if role == "student":
        if not user:
            flash("User not found", "danger")
            return redirect("/login")
    
        
        if not user:
            flash("User not found", "danger")
            return redirect("/login")

        if not user.is_active:
            flash("Your account is inactive", "danger")
            return redirect("/login")

    elif role == "company":

        if not user:
                flash("User not found", "danger")
                return redirect("/login")


       
        if user.is_blacklisted:
            flash("You are blacklisted!", "danger")
            return redirect("/login")

        if not user.is_approved:
            flash("Waiting for admin approval", "warning")
            return redirect("/login")



    if not user or user.password != password:
        flash("Invalid credentials-password", "danger")
        return redirect("/login")


    session["user_id"] = user.id
    session["role"] = role
    flash("Login successful!", "success")

    if role == "student":
        return redirect("/student/dashboard")
    elif role == "company":
        return redirect("/company/dashboard")
    elif role == "admin":
        return redirect("/admin/dashboard")


@app.route("/home")
def give_home():
    return render_template("home.html") 


@app.route("/student/dashboard")
def student_dashboard():
    if session.get("role") != "student":
        return "Unauthorized"

    student_id = session.get("user_id")
    student = Student.query.get(student_id) 

    jobs = Job.query.filter_by(is_approved=True).all()
    applications = Application.query.filter_by(student_id=student_id).all()

    applied = {a.job_id: a.status for a in applications}

    return render_template("student/dashboard.html", jobs=jobs, applied=applied,student=student,applications=applications)

@app.route("/student/apply")
def student_apply():
    if session.get("role") != "student":
        return "Unauthorized"

    student_id = session.get("user_id")

    jobs = Job.query.filter_by(is_approved=True).all()
    applications = Application.query.filter_by(student_id=student_id).all()

    applied = {a.job_id for a in applications}

    return render_template(
        "student/apply.html",
        jobs=jobs,
        applied=applied
    )
@app.route("/student/edit-profile", methods=["POST"])
def edit_profile():
    if session.get("role") != "student":
        return "Unauthorized"

    student = Student.query.get(session.get("user_id"))

    student.name = request.form.get("name")
    student.email = request.form.get("email")
    student.phone = request.form.get("phone")

    db.session.commit()

    flash("Profile updated successfully!", "success")
    return redirect("/student/dashboard")
@app.route("/apply/<int:job_id>", methods=["POST"])
def student_apply2(job_id):
    if session.get("role") != "student":
        return "Unauthorized"

    student_id = session.get("user_id")

    existing = Application.query.filter_by(
        job_id=job_id,
        student_id=student_id
    ).first()

    if existing:
        flash("Already applied!", "warning")
    else:
        app_obj = Application(job_id=job_id, student_id=student_id)
        db.session.add(app_obj)
        db.session.commit()
        flash("Applied successfully!", "success")

    return redirect("/student/apply")   


@app.route("/student/applications")
def student_applications():
    if session.get("role") != "student":
        return "Unauthorized"

    student_id = session.get("user_id")
    apps = Application.query.filter_by(student_id=student_id).all()

    return render_template("student/applications.html", apps=apps)

import os
import uuid

@app.route('/student/upload-resume', methods=['GET', 'POST'])
def upload_resume():
    student = Student.query.get(session.get("user_id"))
    if request.method == 'POST':
        file = request.files['resume']

        if file:
            
            upload_folder = os.path.join('static', 'resumes')
            os.makedirs(upload_folder, exist_ok=True)

            
            filename = str(uuid.uuid4()) + "_" + file.filename

            filepath = os.path.join(upload_folder, filename)

            
            file.save(filepath)

            
            student.resume = f"resumes/{filename}"
            db.session.commit()

            
            flash("Resume uploaded successfully!", "success")

            
            
            return redirect("/student/dashboard")

    return render_template('student/upload_resume.html',student=student)


@app.route("/student/placements")
def placements():
    if session.get("role") != "student":
        return "Unauthorized"

    student_id = session.get("user_id")
    data = Placement.query.filter_by(student_id=student_id).all()

    return render_template("student/placements.html", data=data)


@app.route("/student/profile", methods=["GET", "POST"])
def profile():
    if session.get("role") != "student":
        return "Unauthorized"

    student = Student.query.get(session.get("user_id"))

    if request.method == "POST":
        student.name = request.form.get("name")
        student.phone = request.form.get("phone")
        db.session.commit()
        return redirect("/student/dashboard")

    return render_template("student/profile.html", student=student)


@app.route("/company/dashboard")
def company_dashboard():
    if session.get("role") != "company":
        return "Unauthorized"
    
    user_id = session.get("user_id")
    company = Company.query.get(user_id)   
    jobs = Job.query.filter_by(company_id=user_id,is_closed=False).all()
    closed_jobs = Job.query.filter_by(
        company_id=company.id,
        is_closed=True
    ).all()
    return render_template(
        "company/dashboard.html",
        jobs=jobs,
        company=company,
        closed_jobs=closed_jobs)


@app.route("/company/view-drive/<int:job_id>")
def company_view_drive(job_id):   
    if session.get("role") != "company":
        return "Unauthorized"

    job = Job.query.get(job_id) 
    apps = Application.query.filter_by(job_id=job_id).all()

    return render_template(
        "company/view_drive.html",
        job=job,
        applications=apps
    )

@app.route("/company/close-drive/<int:job_id>")
def close_drive(job_id):
    job = Job.query.get_or_404(job_id)
    job.is_closed = True
    db.session.commit()
    flash("Drive closed successfully")
    return redirect("/company/dashboard")

@app.route("/company/create-drive", methods=["GET", "POST"])
def create_job():
    if session.get("role") != "company":
        return "Unauthorized"
    if request.method == "GET":
        return render_template("company/create_drive.html")

    
    deadline_str = request.form.get("deadline")   # string
    deadline = datetime.strptime(deadline_str, "%Y-%m-%d")
    salary = request.form.get("package")

    job = Job(
        title=request.form.get("title"),
        description=request.form.get("description"),
        eligibility=request.form.get("eligibility"),
        deadline = deadline,
        salary=int(salary) if salary else None,
        company_id=session.get("user_id")
        
    )

    db.session.add(job)
    db.session.commit()

    return redirect("/company/dashboard")
    
@app.route("/company/delete-job/<int:id>")
def delete_job(id):
    if session.get("role") != "company":
        return "Unauthorized"

    job = Job.query.get(id)

    db.session.delete(job)
    db.session.commit()

    flash("Job deleted successfully!", "danger")
    return redirect("/company/dashboard")
@app.route("/company/edit-profile", methods=["POST"])
def edit_company_profile():
    if session.get("role") != "company":
        return "Unauthorized"

    company = Company.query.get(session.get("user_id"))

    if not company:
        flash("Company not found", "danger")
        return redirect("/company/dashboard")

    company_name = request.form.get("company_name")
    email = request.form.get("email")
    hr_contact = request.form.get("hr_contact")
    website = request.form.get("website")

    
    company.company_name = company_name
    company.email = email
    company.hr_contact = hr_contact
    company.website = website

    db.session.commit()

    flash("Profile updated successfully!", "success")
    return redirect("/company/dashboard")



@app.route("/company/edit-job/<int:id>", methods=["GET", "POST"])
def edit_job(id):
    if session.get("role") != "company":
        return "Unauthorized"

    job = Job.query.get(id)

    if request.method == "POST":
        job.title = request.form.get("title")
        job.description = request.form.get("description")
        job.eligibility = request.form.get("eligibility")
        deadline_str = request.form.get("deadline")
        if deadline_str:
            job.deadline = datetime.strptime(deadline_str, "%Y-%m-%d").date()

        job.package = request.form.get("package")
        db.session.commit()

        flash("Job updated successfully!", "success")
        return redirect("/company/dashboard")

    return render_template("company/edit_job.html", job=job)


@app.route("/shortlist/<int:id>")
def shortlist(id):
    app_obj = Application.query.get(id)
    app_obj.status = "Shortlisted"
    db.session.commit()
    flash("Student shortlisted successfully!", "success")
    return redirect(request.referrer)


@app.route("/reject/<int:id>")
def reject(id):
    app_obj = Application.query.get(id)
    app_obj.status = "Rejected"
    db.session.commit()
    flash("Student rejected successfully!", "danger")  
    return redirect(request.referrer)

@app.route("/admin/dashboard")
def admin_dashboard():
    if session.get("role") != "admin":
        return redirect("/login")

    return render_template(
        "admin/dashboard.html",
        students=Student.query.count(),
        companies=Company.query.count(),
        jobs=Job.query.count(),
        applications=Application.query.count()
    )
@app.route("/admin/companies")
def view_company():
    if session.get("role") != "admin":
        return redirect("/login")

    companies = Company.query.all()
    return render_template("admin/companies.html", companies=companies)


@app.route("/admin/companies/approve/<int:id>")
def approve_company(id):
    if session.get("role") != "admin":
        return redirect("/login")

    company = Company.query.get(id)

    company.is_approved = True
    company.is_blacklisted = False
    company.status = "Approved"

    db.session.commit()

    flash("Company approved successfully!", "success")
    return redirect("/admin/companies")


@app.route("/admin/companies/reject/<int:id>")
def reject_company(id):
    if session.get("role") != "admin":
        return redirect("/login")

    company = Company.query.get(id)

    company.is_approved = False
    company.is_blacklisted = False
    company.status = "Rejected"

    db.session.commit()

    flash("Company rejected!", "danger")
    return redirect("/admin/companies")


@app.route("/admin/companies/blacklist/<int:id>")
def blacklist_company(id):
    if session.get("role") != "admin":
        return redirect("/login")

    company = Company.query.get(id)

    company.is_blacklisted = True
    company.is_approved = False
    company.status = "Blacklisted"

    db.session.commit()

    flash("Company blacklisted!", "warning")
    return redirect("/admin/companies")




@app.route("/admin/students")
def view_student():
    if session.get("role") != "admin":
        return redirect("/login")

    students = Student.query.all()
    return render_template("admin/students.html", students=students)

@app.route("/admin/students/approve/<int:id>")
def approve_student(id):
    if session.get("role") != "admin":
        return redirect("/login")

    student = Student.query.get(id)

    student.is_active = True
    student.is_blacklisted = False

    db.session.commit()

    flash("Student activated successfully!", "success")
    return redirect("/admin/students")

@app.route("/admin/students/reject/<int:id>")
def reject_student(id):
    if session.get("role") != "admin":
        return redirect("/login")

    student = Student.query.get(id)

    student.is_active = False
    student.is_blacklisted = False

    db.session.commit()

    flash("Student rejected!", "danger")
    return redirect("/admin/students")


@app.route("/admin/students/deactivate/<int:id>")
def deactivate_student(id):
    if session.get("role") != "admin":
        return redirect("/login")

    student = Student.query.get(id)

    student.is_active = False

    db.session.commit()

    flash("Student deactivated!", "warning")
    return redirect("/admin/students")

@app.route("/admin/view_drive")
def view_drive():
    if session.get("role") != "admin":
        return redirect("/login")

    drives = Job.query.all()
    return render_template("admin/view_drive.html", drives=drives)


@app.route("/admin/search")
def search():
    category = request.args.get("category")
    query = request.args.get("query")

    results = []

    if category == "student":
        if category == "student":

        
            if query.isdigit() and len(query) <= 5:
                results = Student.query.filter_by(id=int(query)).all()

            else:
           
                results = Student.query.filter(
                    or_(
                    Student.name.like(f"%{query}%"),
                    Student.email.like(f"%{query}%"),
                    Student.phone.like(f"%{query}%")
                    )
                ).all()


    elif category == "company":
        results = Company.query.filter(
            Company.company_name.ilike(f"%{query}%") 
            
        ).all()

    

    return render_template("/admin/search.html", results=results)

@app.route("/admin/view_drive/approve/<int:id>")
def approve_drive(id):
    if session.get("role") != "admin":
        return redirect("/login")

    job = Job.query.get(id)
    if not job:
        flash("Drive not found", "danger")
        return redirect("/admin/view_drive")
    job.is_approved = True
    job.is_rejected = False

    db.session.commit()

    flash("Drive approved!", "success")
    return redirect("/admin/view_drive")

@app.route("/admin/view_drive/reject/<int:id>")
def reject_drive(id):
    if session.get("role") != "admin":
        return redirect("/login")

    job = Job.query.get(id)
    if not job:
        flash("Drive not found", "danger")
        return redirect("/admin/view_drive")
    job.is_approved = False
    job.is_rejected = True

    db.session.commit()

    flash("Drive rejected!", "danger")
    return redirect("/admin/view_drive")

@app.route("/admin/view_application/<int:drive_id>")
def view_applications(drive_id):
    if session.get("role") != "admin":
        return "Unauthorized"

    drive = Job.query.get(drive_id)

    applications = Application.query.filter_by(job_id=drive_id).all()

    return render_template(
        "admin/view_application.html",
        applications=applications,
        drive=drive
    )
@app.route("/admin/student/<int:student_id>/history")
def student_history(student_id):
    if session.get("role") != "admin":
        return "Unauthorized"

    student = Student.query.get(student_id)

    applications = Application.query.filter_by(student_id=student_id).all()

    return render_template(
        "admin/student_history.html",
        student=student,
        applications=applications
    )


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")