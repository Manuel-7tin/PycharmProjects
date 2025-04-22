from datetime import date, datetime
from flask import Flask, jsonify, request, abort, render_template, redirect, url_for, flash
# from flask_bootstrap import Bootstrap5
# from flask_ckeditor import CKEditor
# from flask_gravatar import Gravatar
from flask_login import UserMixin, login_user, LoginManager, current_user, logout_user
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship, DeclarativeBase, Mapped, mapped_column
from sqlalchemy.exc import IntegrityError
from sqlalchemy import Integer, String, Text, LargeBinary, DateTime, Boolean, Date, Column
from sqlalchemy import Table, ForeignKey
from sqlalchemy import func, select
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
import werkzeug.exceptions
from sqlalchemy.orm import relationship

import pandas as pd
from datetime import datetime
import re
# Import your forms from the forms.py
# from forms import CreatePostForm, RegisterForm, LoginForm, CommentForm

app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
# ckeditor = CKEditor(app)
# Bootstrap5(app)

# CREATE DATABASE
class Base(DeclarativeBase):
    pass

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ivyLeague.db'
db = SQLAlchemy(model_class=Base)
db.init_app(app)


student_paper = Table(
    "registrations",
    db.metadata,
    Column("student_reg_no", String, ForeignKey("students.reg_no")),
    Column("paper_code", String, ForeignKey("papers.code"))
)


class All(db.Model):
    __tablename__ = "all-students"
    reg_no: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    year: Mapped[str] = mapped_column(String(5), nullable=False)
    diet: Mapped[str] = mapped_column(String(1), nullable=False)


# Create a Staff table for all your registered staffs
class Staff(UserMixin, db.Model):
    __tablename__ = "staffs"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(100), unique=True)
    password: Mapped[str] = mapped_column(String(100))
    first_name: Mapped[str] = mapped_column(String(100))
    last_name: Mapped[str] = mapped_column(String(100))
    photo: Mapped[bytes] = mapped_column(LargeBinary, nullable=True)
    # This will act like a list of BlogPost objects attached to each User.
    # The "author" refers to the author property in the BlogPost class.
    tasks = relationship("Task", back_populates="DoneBy")
    # Parent relationship: "comment_author" refers to the comment_author property in the Comment class.
    # comments = relationship("Comment", back_populates="comment_author")


class Task(db.Model):
    __tablename__ = "tasks"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    # Create Foreign Key, "users.id" the users refers to the tablename of User.
    DoneBy_id: Mapped[int] = mapped_column(Integer, db.ForeignKey("staffs.id"))
    # Create reference to the User object. The "posts" refers to the posts property in the User class.
    DoneBy = relationship("Staff", back_populates="tasks")
    category: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    time: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    description: Mapped[str] = mapped_column(String(250), nullable=False)
    # Parent relationship to the comments
    comments: Mapped[str] = mapped_column(String(250), nullable=False)


class Intensive(db.Model):
    __tablename__ = "intensive_students"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    amount_paid: Mapped[int] = mapped_column(Integer, nullable=False)
    fee: Mapped[int] = mapped_column(Integer, nullable=False)
    scholarship_discount: Mapped[int] = mapped_column(Integer, nullable=False)
    normal_discount: Mapped[int] = mapped_column(Integer, nullable=False)
    deffered: Mapped[int] = mapped_column(Integer, nullable=False)
    papers: Mapped[str] = mapped_column(Text, nullable=False)
    student_id: Mapped[int] = mapped_column(Integer, db.ForeignKey("students.id"))
    student = relationship("Student", back_populates="intensive_papers")


class Standard(db.Model):
    __tablename__ = "standard_students"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    amount_paid: Mapped[int] = mapped_column(Integer, nullable=False)
    fee: Mapped[int] = mapped_column(Integer, nullable=False)
    scholarship_discount: Mapped[int] = mapped_column(Integer, nullable=False)
    normal_discount: Mapped[int] = mapped_column(Integer, nullable=False)
    deffered: Mapped[int] = mapped_column(Integer, nullable=False)
    papers: Mapped[str] = mapped_column(Text, nullable=False)
    # Child relationship:"users.id" The users refers to the tablename of the User class.
    # "comments" refers to the comments property in the User class.\
    student_id: Mapped[int] = mapped_column(Integer, db.ForeignKey("students.id"))
    student = relationship("Student", back_populates="standard_papers")


class Student(db.Model):
    __tablename__ = "students"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    # intensive_id: Mapped[int] = mapped_column(Integer, db.ForeignKey("intensive_students.id"))
    # standard_id: Mapped[int] = mapped_column(Integer, db.ForeignKey("standard_students.id"))
    first_name: Mapped[str] = mapped_column(String(100))
    last_name: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    reg_no: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    password: Mapped[str] = mapped_column(String(100), nullable=False)
    reg_date: Mapped[date] = mapped_column(Date, nullable=False)
    acca_reg_no: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    birth_date: Mapped[date] = mapped_column(Date, nullable=False)
    phone_number: Mapped[str] = mapped_column(String(100))
    new_student: Mapped[bool] = mapped_column(Boolean, nullable=False)
    sponsored: Mapped[bool] = mapped_column(Boolean, nullable=False)
    sponsored_papers: Mapped[str] = mapped_column(String(100))
    referral_source: Mapped[str] = mapped_column(String(100))
    employment_status:  Mapped[str] = mapped_column(String(100))
    intensive_papers = relationship("Intensive", back_populates="student")
    standard_papers = relationship("Standard", back_populates="student")
    papers = relationship("Paper", secondary=student_paper, back_populates="students")
    payments = relationship("Payment", back_populates="payer")
    payment_status: Mapped[str] = mapped_column(String(100))
    revision: Mapped[bool] = mapped_column(Boolean, nullable=False)
    total_fee: Mapped[int] = mapped_column(Integer, nullable=False)
    amount_paid: Mapped[int] = mapped_column(Integer, nullable=False)
    refund: Mapped[int] = mapped_column(Integer, nullable=False)
    receivable: Mapped[int] = mapped_column(Integer, nullable=False)


# Create a table for the comments on the blog posts
class Payment(db.Model):
    __tablename__ = "payments"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    post_id: Mapped[int] = mapped_column(Integer, db.ForeignKey("students.id"))
    payment_reference = mapped_column(String(100), nullable=False, unique=True)
    amount: Mapped[int] = mapped_column(Integer)
    payer = relationship("Student", back_populates="payments")


class Paper(db.Model):
    __tablename__ = "papers"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    students = relationship("Student", secondary=student_paper, back_populates="papers")
    code: Mapped[str] = mapped_column(Text, nullable=False)
    price: Mapped[int] = mapped_column(Integer, nullable=False)
    revision: Mapped[int] = mapped_column(Integer, nullable=False)


class Attempt(db.Model):
    __tablename__ = "attempts"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(120), nullable=False)
    first_name: Mapped[str] = mapped_column(String(100))
    last_name: Mapped[str] = mapped_column(String(100))
    user_type: Mapped[str] = mapped_column(String(20))
    phone_number: Mapped[str] = mapped_column(String(20))
    created_at = mapped_column(DateTime, default=datetime.now)
    payment_reference = mapped_column(String(100), nullable=False, unique=True)
    payment_status = mapped_column(String(20), default='pending')
    failure_cause = Mapped[str] = mapped_column(String(200))
    # Store everything else here
    other_data = mapped_column(db.JSON)  # holds dob, courses, etc.
    payment_data = mapped_column(db.JSON)


class Signee(db.Model):
    __tablename__ = "signees"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(5), nullable=False)
    email: Mapped[str] = mapped_column(String(120), nullable=False, unique=True)
    password: Mapped[str] = mapped_column(String(100), nullable=False)
    first_name: Mapped[str] = mapped_column(String(30), nullable=False)
    last_name: Mapped[str] = mapped_column(String(30), nullable=False)
    phone_number: Mapped[str] = mapped_column(String(15), unique=True)
    created_at = mapped_column(DateTime, default=datetime.now)
    birth_date: Mapped[date] = mapped_column(Date, nullable=False)
    gender = mapped_column(String(5), nullable=False)


# Creates all tables declared above, creates nothing if none is declared.
with app.app_context():
    db.create_all()



def encode_year(year: int, a=117, b=53, m=10000):
    return (a * year + b) % m

def decode_year(code: int, a=117, b=53, m=10000):
    a_inv = pow(a, -1, m)  # modular inverse
    return ((code - b) * a_inv) % m

def encode_serial(serial: int, a=211, b=79, m=10000):
    return (a * serial + b) % m

def decode_serial(code: int, a=211, b=79, m=10000):
    a_inv = pow(a, -1, m)
    return ((code - b) * a_inv) % m


def is_valid_password(password: str) -> tuple:
    """
    Checks if the password is at least 8 characters long and contains
    at least one letter, one number, and one special character.
    """
    if len(password) < 8:
        return False, "LEN: Too short"
    elif not re.search(r"[A-Za-z]", password):
        return False, "ALPH: No letter"
    elif not re.search(r"[0-9]", password):
        return False, "NUM: No number"
    elif not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        return False, "CHAR: No special character"
    return True, "Verified"


def log_attempt(data: dict):
    new_attempt = Attempt(

    )


def move_signee(info: dict, sponsored: bool):
    print(dict)

# Ideally set this in .env and load with dotenv
# PAYSTACK_SECRET_KEY = os.getenv("PAYSTACK_SECRET_KEY") or "sk_test_xxxxxx"
# BASE_URL = "https://api.paystack.co"


# -----------------------------
# Initialize Payment
# -----------------------------
@app.route("/initialize-payment", methods=["POST"])
def initialize_payment():
    data = request.get_json()
    amount = data.get("amount")
    email = data.get("email")
    metadata = data.get("metadata", {})
    kind = data.get("condition") #registration or payment
    if kind == "registration" or kind == "payment":
        try:
            log_attempt()
        except Exception as e:
            return jsonify(
                error={
                    "Initialization Error": f"Error {e} logging payment attempt",
                }
            ), 403

    else:
        return jsonify(
            error={
                "Initialization Error": "UNknown payment kind specified",
            }
        ), 403

    # headers = {
    #     "Authorization": f"Bearer {PAYSTACK_SECRET_KEY}",
    #     "Content-Type": "application/json"
    # }

    body = {
        "amount": amount * 100,  # Convert to kobo
        "email": email,
        "metadata": metadata
    }

    # response = requests.post(f"{BASE_URL}/transaction/initialize", json=body, headers=headers)

    # if response.status_code != 200:
    #     return jsonify({"error": "Failed to initialize payment"}), response.status_code
    #
    # return jsonify(response.json()), 200


# -----------------------------
# Verify Payment
# -----------------------------
@app.route("/verify/<reference>", methods=["GET"])
def verify_payment(reference):
    pass
    # headers = {
    #     "Authorization": f"Bearer {PAYSTACK_SECRET_KEY}"
    # }
    #
    # response = requests.get(f"{BASE_URL}/transaction/verify/{reference}", headers=headers)
    #
    # if response.status_code != 200:
    #     return jsonify({"error": "Verification failed"}), 500
    #
    # data = response.json()
    # return jsonify(data), 200


# -----------------------------
# Webhook
# -----------------------------
@app.route("/webhook", methods=["POST"])
def handle_webhook():
    event = request.json
    event_type = event.get("event")
    reference = event.get("data", {}).get("reference")

    print(f"Webhook event: {event_type} for reference: {reference}")

    # Here you’d typically update the DB
    # Example:
    # if event_type == 'charge.success':
    #     update_payment_status(reference, status='completed')

    return jsonify({"status": "received"}), 200


@app.route("/upload/file", methods=["POST"])
def add_students(file):
    if request.method == "POST":
        # data = pd.read_excel("STUDENT POSITION REPORTfor EMMANUEL.xlsx", header=0, sheet_name="STANDARD
        # CLASS")
        data = pd.read_excel(file, header=0, sheet_name="STANDARD CLASS")
        class_type = request.args.get("class")
        class_dict = {"intensive": Intensive, "standard": Standard}
        to_add = []
        L1 = ['DATE', 'FIRSTNAME ', 'LAST NAME', 'ACCA REG NO',
              'EMAIL ADDRESS', 'DOB', 'PHONE NUMBER', 'NEW STUDENT', 'PAPERS']
        # What if they add the file that has already been added in the past
        sponsor_prompt = "I am a sponsored students (Please state employer's name)"
        for (index, row) in data.iterrows():
            # Extract Course codes
            papers_column = [x for x in data.columns if "Papers of interest" in x]
            code_title = ""
            i = row[papers_column[0]]
            try:
                paper_name = i.split(", ")
            except AttributeError:
                print(type(i), "for value: ", i)
            else:
                for paper in paper_name:
                    code = paper.split(" ")[-1]
                    code = code.strip("()")
                    code_title = code_title + code + "/"

            # Calculate total price
            papers = db.session.execute(db.select(Paper)).scalars().all()
            paper_dict = {}
            price = 0
            amount_paid = 0
            for paper in papers:
                paper_code = paper.name.split(" ")[-1].lower()
                paper_dict[paper_code] = paper.price
            for title in code_title.split("/"):
                price += paper_dict[title.lower()]
            # Sort out sponsored students
            if not pd.isna(row[sponsor_prompt]):
                amount_paid = price

            new_student = Student(
                first_name=row.firstname,
                last_name=row.lastname,
                email=row.email,
                reg_no=row["ACCA REG NO"],
                birth_date=row.DOB,
                phone_number=row["PHONE NUMBER"],
                new_student=row["NEW STUDENT"],
                sponsored=row[sponsor_prompt],
                # intensive_papers = "wellwellwell",
                # standard_papers = "wellwellwell",
                revision=row["REVISION FEE"],
                total_fee=row["TOTAL FEE"],
                amount_paid=amount_paid,
                refund=0,
                receivable=0,
            )
            to_add.append(new_student)

            if class_dict.get(class_type.lower()):
                paper = class_dict[class_type.lower()](
                    amount_paid=amount_paid,
                    fee=price,
                    scholarship_discount=0,
                    normal_discount=0,
                    deffered=0,
                    papers=code_title,
                    student = new_student
                )
                to_add.append(paper)
            else:  # i.e a wrong class type was specified
                pass
            new_task = Task(
                DoneBy = current_user,
                category = "Data Upload", # Data Upload, Payment Upload, Stats Download, Data Change
                time = datetime.now(),
                description = "New student data upload",
                comments = request.args.get("comment")
            )
            to_add.append(new_task)
            db.session.add_all(to_add)


# HTTP GET - Read Record
@app.route("/students", methods=["GET"])
def get_all():
    """Retrieves and sends some data on all students from the database."""
    if request.method == "GET":
        # rand_pick = random.randint(0, 5)
        students_data = []
        with app.app_context():
            db.session.execute(db)
            all_students = db.session.execute(db.select(Student).order_by(Student.first_name)).scalars()
            # print(picked.name, "has been picked")
        for student in all_students:
            students_data.append(
                dict(
                    name=student.first_name + " " + student.last_name,
                    student_id=student.id,
                    reg_no=student.reg_no,
                    new_student=student.new_student,
                )
            )
        return jsonify(students_data)
    return "<h1>You are gonna be Great Man<h1>"


@app.route("/student/<int:student_id>", methods=["GET"])
def select_student(student_id):
    """Modifies the pricing information for the designated café."""
    if request.method == "GET":
        # student_id = request.args.get("id")
        # new_price = request.args.get("price")
        with app.app_context():
            try:
                student = db.get_or_404(Student, student_id)
            except werkzeug.exceptions.NotFound:
                return  jsonify(
                    error = {
                            "Not Found": "Sorry a student with that id was not found in the database",
                    },
                ), 404
            else:
                pass
        discount1 = student.intensive_papers.scholarship_discount + \
                    student.intensive_papers.normal_discount + student.intensive_papers.deffered
        discount2 = student.standard_papers.scholarship_discount + \
                    student.standard_papers.normal_discount + student.standard_papers.deffered
        return jsonify(
            dict(
                name=student.first_name + " " + student.last_name,
                student_id=student.id,
                reg_no=student.reg_no,
                email=student.email,
                d_o_b=student.birth_date,
                new_student=student.new_student,
                intensive_papers=student.intensive_papers.papers,
                standard_papers=student.standard_papers.papers,
                total_fee=student.total_fee,
                revision=student.revison,
                discounts=discount1 + discount2,
                owing=student.recievables,
                extra=student.refund,
                amount_paid=student.amount_paid
            )
        )


@app.route("/", methods=["POST", "GET"])
def temp():
    return "i dey come"


@app.route("/signup", methods=["POST"])
def sign_up():
    print("i dey come")
    if request.args.get("api-key") != "AyomideEmmanuel":
        # g = request.args.get("api-key")
        return jsonify(
            error={
                "Access Denied": f"You do not have access to this resource" #\n type:{type(g)}. it is {g}",
            }
        ), 403

    data = request.get_json()
    if isinstance(data.get("birthdate"), str):
        d_o_b = datetime.strptime(data.get("birthdate"), "%d/%m/%Y")
    else:
        d_o_b = data.get("birthdate")
    ver_pword = is_valid_password(data.get("password"))
    if not ver_pword[0]:
        return jsonify(
                error={
                    "Invalid Password": f"Error cause: [{ver_pword[1]}]",
                }
            ), 400
    hash_and_salted_password = generate_password_hash(
        data.get("password"),
        method='pbkdf2:sha256',
        salt_length=8
    )

    try:
        new_signee = Signee(
            # id=random.randint(3, 9),
            title=data.get("title"),
            email=data.get("email"),
            first_name=data.get("firstname"),
            last_name=data.get("lastname"),
            phone_number=data.get("phone"),
            birth_date=d_o_b,
            gender=data.get("sex"),
            password=hash_and_salted_password
        )
        with app.app_context():
            db.session.add(new_signee)
            db.session.commit()
    except IntegrityError as e:
        # print(str(IntegrityError))
        return jsonify(
            error={
                "DB Integrity Compromise": f"User email or phone number already exists",
            }
        ), 409
    except Exception as e:
        return jsonify(
            error={
                "Uncaught Error": f"This error wasn't expected or planned for.\n{e}",
            }
        ), 422
    else:
        return jsonify({
            "status": "success",
            "message": "Signup successful",
        }), 201


@app.route("/signin", methods=["GET"])
def sign_in():
    if request.args.get("api-key") != "AyomideEmmanuel":
        # g = request.args.get("api-key")
        return jsonify(
            error={
                "Access Denied": f"You do not have access to this resource" #\n type:{type(g)}. it is {g}",
            }
        ), 403
    data = request.get_json()
    login_type = data.get("type")

    if login_type == "email":
        result = db.session.execute(db.select(Student).where(Student.email == data.get("email")))
        user = result.scalar()

        if not user: # User is not a registered student
            result = db.session.execute(db.select(Signee).where(Signee.email == data.get("email")))
            user = result.scalar()
            if not user: # User is not a signee either
                return jsonify(
                    error={
                        "Incorrect Input": f"Email or password incorrect" #\n type:{type(g)}. it is {g}",
                    }
                ), 403

            password = data.get("password")
            if check_password_hash(user.password, password):
                return jsonify({
                    "title": user.title,
                    "firstname": user.first_name,
                    "lastname": user.last_name,
                    "email": user.email,
                    "sex": user.gender,
                    "user-type": "signee",
                })
            else:
                password_incorrect = True
        else:
            password = data.get("password")
            if check_password_hash(user.password, password):
                return jsonify({
                    "title": user.title,
                    "firstname": user.first_name,
                    "lastname": user.last_name,
                    "email": user.email,
                    "sex": user.gender,
                    "reg_no": user.reg_no,
                    "acca_reg_no": user.acca_reg_no,
                    "papers": [{paper.code:paper.name} for paper in user.papers],
                    "user-type": "student",

                })
            else:
                password_incorrect = True
        if password_incorrect:
            return jsonify(
                error={
                    "Incorrect Input": f"Email or Password incorrect"  # \n type:{type(g)}. it is {g}",
                }
            ), 403

    elif login_type == "reg":
        result = db.session.execute(db.select(Student).where(Student.reg_no == data.get("reg_no")))
        user = result.scalar()

        if not user: # User is not a registered student
            return jsonify(
                error={
                    "Incorrect Input": f"Registration number or password incorrect" #\n type:{type(g)}. it is {g}",
                }
            ), 403

        password = data.get("password")
        if check_password_hash(user.password, password):
            return jsonify({
                "title": user.title,
                "firstname": user.first_name,
                "lastname": user.last_name,
                "email": user.email,
                "sex": user.gender,
                "reg_no": user.reg_no,
                "acca_reg_no": user.acca_reg_no,
                "papers": [{paper.code: paper.name} for paper in user.papers],
                "user-type": "student",
            })
        else:
            return jsonify(
                error={
                    "Incorrect Input": f"Registration number     or Password incorrect"  # \n type:{type(g)}. it is {g}",
                }
            ), 403
    else:
        return jsonify(
            error={
                "Unknown Login Type": f"Log-in type {login_type} is not accepted",
            }
        ), 409


@app.route("/initialize-payment", methods=["POST"])
def initialize_payment(some_arg):
    print(some_arg)


@app.route("/register", methods=["POST"])
def register():
    api_key = request.args.get("api-key")
    if api_key != "AyomideEmmanuel":
        return jsonify(
            error={
                "Access Denied": "You do not have access to this resource",
            }
        ), 403
    data = request.get_json()
    user_type = data.get("user-type")
    if data.get("sponsored"): # User is sponsored by an organization
        if user_type == "signee":
                move_signee(data, sponsored=True)
    else: # User is sponsoring themselves
        pass
    email = request.args.get("email")
    # Check if user email is already present in the database.
    result = db.session.execute(db.select(Student).where(Student.email == email))
    user = result.scalar()
    if user:
        # User already exists
        return jsonify(
            error={
                "Redundant Action": "An account with this email already exists.",
            }
        ), 409

    hash_and_salted_password = generate_password_hash(
        request.args.get("p_word"),
        method='pbkdf2:sha256',
        salt_length=8
    )
    stmt = select(func.count()).select_from(Student)
    total_students = db.session.execute(stmt).scalar()
    year_code = encode_year(datetime.now().year)  # e.g., 6318
    serial_code = encode_serial(total_students)
    new_student = Student(
        first_name=request.args.get("firstname"),
        last_name=request.args.get("lastname"),
        email=email,
        reg_no=f"1331{year_code:04d}{serial_code:04d}",
        password=hash_and_salted_password,
        reg_date=datetime.now(),
        acca_reg_no=request.args.get("acca_reg"),
        birth_date=request.args.get("dob"),
        phone_number=request.args.get("phone"),
        new_student=request.args.get("first_timer"),
        sponsored=request.args.get("sponsored"),
        referral_source=request.args.get("referral_source"),
        employment_status=request.args.get("job"),
        payment_status
        # intensive_papers=[ppr for ppr in request.args.get("papers") if "int" in ppr],
        # standard_papers=[ppr for ppr in request.args.get("papers") if "std" in ppr],
        reg_no=request.args.get("email"),
    )
    db.session.add(new_user)
    db.session.commit()
    # This line will authenticate the user with Flask-Login
    login_user(new_user)
    return redirect(url_for("get_all_posts"))


# @app.route("/login", methods=["POST"])
# def login():
#     pass


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True, port=5001)

L1 = ['DATE', 'FIRSTNAME ', 'LAST NAME', 'ACCA REG NO',
       'EMAIL ADDRESS', 'DOB', 'PHONE NUMBER', 'NEW STUDENT', 'PAPERS']
l2 = ['DATE', 'FIRSTNAME ', 'LAST NAME', 'ACCA REG NO',
       'EMAIL ADDRESS', 'DOB', 'PHONE NUMBER', 'NEW STUDENT', 'PAPERS', 'CLASS FEE',
       'REVISION FEE', 'TOTAL FEE', 'AMOUNT PAID', 'SCHOLARSHIP DISCOUNT', 'NORMAL DISCOUNT',
       'REFUND', 'DEFFERED', 'RECEIVABLES']
tables = ["Staffs", "Intensive", "Standard", "Tasks"]
for i in l2:
    if i not in L1:
        print(i, end=", ")

        # user_type = request.args.get("type")
        # if user_type != "admin" and user_type != "student":
        #     return jsonify(
        #         error={
        #             f"Invalid User-Type": f"There is no user of type {user_type}",
        #         }
        #     ), 403
        # elif user_type == "admin":
