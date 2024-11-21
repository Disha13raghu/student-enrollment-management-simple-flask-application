from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy

# Initialize Flask app and configure database
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///week7_database.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your-secret-key'

# Initialize SQLAlchemy and Flask-Migrate
db = SQLAlchemy(app)

# Models
class Student(db.Model):
    __tablename__ = 'student'
    student_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    roll_number = db.Column(db.String, nullable=False, unique=True)
    first_name = db.Column(db.String, nullable=False)
    last_name = db.Column(db.String)

    enrollments = db.relationship('Enrollment', back_populates='student', cascade="all, delete-orphan")


class Course(db.Model):
    __tablename__ = 'course'
    course_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    course_name = db.Column(db.String, nullable=False)
    course_description = db.Column(db.String)
    course_code = db.Column(db.String, nullable=False, unique=True)

    enrollments = db.relationship('Enrollment', back_populates='course', cascade="all, delete-orphan")


class Enrollment(db.Model):
    __tablename__ = 'enrollments'
    enrollment_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    estudent_id = db.Column(db.Integer, db.ForeignKey("student.student_id", ondelete='CASCADE'), nullable=False)
    ecourse_id = db.Column(db.Integer, db.ForeignKey("course.course_id", ondelete='CASCADE'), nullable=False)

    student = db.relationship('Student', back_populates='enrollments')
    course = db.relationship('Course', back_populates='enrollments')

# Routes
@app.route('/')
def home():
    students = Student.query.all()
    num_students = len(students)
    return render_template("index.html", students=students, n=num_students)

@app.route('/student/create', methods=["GET", "POST"])
def add():
    if request.method == "GET":
        courses = Course.query.all()
        return render_template("add.html", courses=courses, n=2)
    else:
        roll = request.form.get("roll")
        first_name = request.form.get("f_name")
        last_name = request.form.get("l_name")
        #courses = request.form.getlist("courses")

        # Check for duplicate roll number
        existing_student = Student.query.filter_by(roll_number=roll).first()
        if existing_student:
            return render_template("add.html", n=0)  # Duplicate roll number
        
        # Add new student
        new_student = Student(roll_number=roll, first_name=first_name, last_name=last_name)
        db.session.add(new_student)
        db.session.commit()

        # Add enrollments
       # for course_id in courses:
       #     enrollment = Enrollment(estudent_id=new_student.student_id, ecourse_id=int(course_id))
        #    db.session.add(enrollment)
       # db.session.commit()

        return redirect("/")

@app.route("/student/<int:student_id>/update", methods=["GET", "POST"])
def update(student_id):
    stu= Student.query.filter_by(student_id=student_id).first()
    course=Course.query.all()
    if request.method=="POST":
      fn=request.form.get("f_name")
      ln=request.form.get("l_name")
      course_id=request.form.get("course")
      stu.first_name=fn 
      stu.last_name= ln 
      
      Enrollment.query.filter_by(estudent_id=student_id,ecourse_id=course_id).delete()
  
      ne= Enrollment(estudent_id=stu.student_id, ecourse_id=course_id)
      db.session.add(ne)
      
      db.session.commit()    
      return redirect("/")
    return render_template("update.html",st=stu, course=course)


@app.route("/student/<int:student_id>/delete", methods=["GET"])
def delete(student_id):
    student = Student.query.get_or_404(student_id)
    db.session.delete(student)
    db.session.commit()
    return redirect("/")

@app.route("/student/<int:student_id>", methods=["GET"])
def enroll(student_id):
    student = Student.query.get(student_id)
    courses = [enrollment.course for enrollment in student.enrollments]
    return render_template("enroll.html", c=courses, stu=student)

@app.route("/courses", methods=["GET"])
def courses():
    courses= Course.query.all()
    n= len(courses)
    return render_template("courses.html",courses=courses,n=n)

@app.route("/course/create", methods=["GET","POST"])
def add_course():
    if request.method=="POST":
        course_name=request.form.get("c_name")
        course_code=request.form.get("code")
        course_description=request.form.get("desc")
        course= Course(course_name=course_name,course_code=course_code,course_description=course_description)
        
        existing_course = Course.query.filter_by(course_code=course_code).first()
        if existing_course:
            return render_template("add.html", n=0) 
        db.session.add(course)
        db.session.commit()
        return redirect("/courses")
    return render_template("add_courses.html",n=2)
    
@ app.route("/student/<int:student_id>/withdraw/<int:course_id>")   
def withdraw(student_id,course_id):
    Enrollment.query.filter_by(estudent_id=student_id,ecourse_id=course_id).delete()
    db.session.commit()
    return redirect(f"/student/{student_id}")
    

@ app.route("/course/<int:course_id>")
def enrollment_courses(course_id):
    course = Course.query.filter_by(course_id=course_id).first()
    enrollments = Enrollment.query.filter_by(ecourse_id=course_id).all()
    students = [enrollment.student for enrollment in enrollments]
    
    return render_template("course_enrollment.html", c=course, students=students)

@app.route("/course/<int:course_id>/update", methods=["GET","POST"])
def course_update(course_id):
    curr_course= Course.query.filter_by(course_id=course_id).first()
    if request.method=="POST":
        course_name=request.form.get("c_name")
        course_description=request.form.get("desc")
        curr_course.course_name=course_name
        curr_course.course_description=course_description
        db.session.commit()
        return redirect("/courses")
    
    return render_template("update_course.html", c=curr_course)
    
        
        
        

@app.route("/course/<int:course_id>/delete")
def course_delete(course_id):
    Course.query.filter_by(course_id=course_id).delete()
    db.session.commit()
    return redirect("/courses")

    

# Run the application
if __name__ == '__main__':
    app.run(debug=True)
