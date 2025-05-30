from datetime import date
from threading import Thread
from flask import Flask, jsonify, request #, abort, render_template, redirect, url_for, flash
# from flask_bootstrap import Bootstrap5
# from flask_ckeditor import CKEditor
# from flask_gravatar import Gravatar
from flask_login import UserMixin #, current_user, login_user, LoginManager, logout_user
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship, DeclarativeBase, Mapped, mapped_column
from sqlalchemy.exc import IntegrityError
from sqlalchemy import Integer, String, Text, LargeBinary, DateTime, Boolean, Date, Column, ARRAY
from sqlalchemy import Table, ForeignKey
from sqlalchemy import func, select
# from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
import werkzeug.exceptions
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

import pandas as pd
from datetime import datetime
import re
import os
import uuid
import requests
from alembic.config import Config
from alembic import command

BASE_URL = "https://api.paystack.co/"
PAYSTACK_SECRET_KEY = "sk_test_962200b3c9d32ad7f9b0a2db706d11c86d3d9b3a"

app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
# ckeditor = CKEditor(app)
# Bootstrap5(app)

# CREATE DATABASE
class Base(DeclarativeBase):
    pass


def create_postgres_db_if_not_exists(db_name, user, password, host="localhost", port=5432):
    try:
        # Connect to default postgres database
        conn = psycopg2.connect(dbname='postgres', user=user, password=password, host=host, port=port)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)

        cur = conn.cursor()
        cur.execute(f"SELECT 1 FROM pg_database WHERE datname = '{db_name}';")
        exists = cur.fetchone()

        if not exists:
            cur.execute(f"CREATE DATABASE {db_name};")
            print(f"✅ Database '{db_name}' created.")
        else:
            print(f"⚠️ Database '{db_name}' already exists.")

        cur.close()
        conn.close()

    except Exception as e:
        print(f"❌ Failed to create database: {e}")


create_postgres_db_if_not_exists("ivyleague", "postgres", "root")

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:root@localhost:5432/ivyleague'
db = SQLAlchemy(model_class=Base)
db.init_app(app)


student_paper = Table(
    "registrations",
    db.metadata,
    Column("student_id", Integer, ForeignKey("students.id")),
    Column("paper_id", Integer, ForeignKey("papers.id"))
)


class All(db.Model):
    __tablename__ = "all-students"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    reg_no: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    year: Mapped[list] = mapped_column(ARRAY(String), nullable=False)
    diet: Mapped[list] = mapped_column(ARRAY(String), nullable=False)


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


class Student(db.Model):
    __tablename__ = "students"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    first_name: Mapped[str] = mapped_column(String(100))
    last_name: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    reg_no: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    password: Mapped[str] = mapped_column(String(100), nullable=False)
    reg_date: Mapped[date] = mapped_column(Date, nullable=False, default=datetime.now())
    acca_reg_no: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    birth_date: Mapped[date] = mapped_column(Date, nullable=False)
    phone_number: Mapped[str] = mapped_column(String(20), unique=True)
    gender = mapped_column(String(5), nullable=False)
    joined: Mapped[date] = mapped_column(Date, nullable=False)
    new_student: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    sponsored: Mapped[bool] = mapped_column(Boolean, nullable=False)
    sponsor: Mapped[str] = mapped_column(String(10))
    sponsored_papers: Mapped[str] = mapped_column(String(30))
    total_fee: Mapped[int] = mapped_column(Integer, nullable=False)
    amount_paid: Mapped[int] = mapped_column(Integer, nullable=False)
    payment_status: Mapped[str] = mapped_column(String(20))
    house_address: Mapped[str] = mapped_column(String(200))
    referral_source: Mapped[str] = mapped_column(String(100)) # friend, (tiktok/insta/fb/tw) ad, flyer etc
    referrer: Mapped[str] = mapped_column(String(100))
    employment_status:  Mapped[str] = mapped_column(String(30))
    revision: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    retake: Mapped[bool] = mapped_column(Boolean, default=False)
    discount: Mapped[int] = mapped_column(Integer, default=0)
    discount_papers: Mapped[list] = mapped_column(ARRAY(String), default=[])
    oxford_brookes: Mapped[bool] = mapped_column(Boolean)
    accurate_data: Mapped[bool] = mapped_column(Boolean, nullable=False)
    alp_consent: Mapped[bool] = mapped_column(Boolean, nullable=False)
    terms_and_cond: Mapped[bool] = mapped_column(Boolean, nullable=False)
    refund: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    receivable: Mapped[int] = mapped_column(Integer, nullable=False)
    papers = relationship("Paper", secondary=student_paper, back_populates="students")
    payments = relationship("Payment", back_populates="student")


# Create a table for the comments on the blog posts
class Payment(db.Model):
    __tablename__ = "payments"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    amount: Mapped[int] = mapped_column(Integer, nullable=False)
    payment_reference: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    sponsored: Mapped[bool] = mapped_column(Boolean, default=False)
    paystack_id: Mapped[int] = mapped_column(Integer, nullable=False)
    message : Mapped[str] = mapped_column(String(100))
    medium : Mapped[str] = mapped_column(String(100), nullable=False)
    currency : Mapped[str] = mapped_column(String(100), nullable=False)
    ip : Mapped[str] = mapped_column(String(100))
    attempts: Mapped[int] = mapped_column(Integer)
    history: Mapped[dict] = mapped_column(db.JSON)
    fee: Mapped[int] = mapped_column(Integer)
    auth_data: Mapped[dict] = mapped_column(db.JSON)
    fee_breakdown: Mapped[dict] = mapped_column(db.JSON)
    customer_data: Mapped[dict] = mapped_column(db.JSON)
    created_at: Mapped[date] = mapped_column(Date, nullable=False)
    paid_at: Mapped[date] = mapped_column(Date, nullable=False)
    student_id: Mapped[int] = mapped_column(Integer, db.ForeignKey("students.id"))
    student = relationship("Student", back_populates="payments")


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
    first_name: Mapped[str] = mapped_column(String(30), nullable=False)
    last_name: Mapped[str] = mapped_column(String(30), nullable=False)
    user_type: Mapped[str] = mapped_column(String(20), nullable=False)
    phone_number: Mapped[str] = mapped_column(String(20), nullable=False)
    created_at: Mapped[date] = mapped_column(DateTime, default=datetime.now)
    purpose: Mapped[str] = mapped_column(String(30), nullable=False)
    context: Mapped[list] = mapped_column(ARRAY(String), nullable=False)
    amount: Mapped[int] = mapped_column(Integer, nullable=False)
    closed_at: Mapped[date] = mapped_column(DateTime)
    payment_reference: Mapped[str] = mapped_column(String(30), nullable=False, unique=True)
    payment_status: Mapped[str] = mapped_column(String(20), default='pending')
    failure_cause: Mapped[str] = mapped_column(String(200))
    # Store everything else here
    other_data: Mapped[dict] = mapped_column(db.JSON)  # holds dob, courses, etc.
    # payment_data: Mapped[dict] = mapped_column(db.JSON)


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


class Sponsored(db.Model):
    __tablename__ = "sponsored"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    first_name: Mapped[str] = mapped_column(String(20), nullable=False)
    last_name: Mapped[str] = mapped_column(String(20), nullable=False)
    company: Mapped[str] = mapped_column(String(20), nullable=False)
    papers: Mapped[list] = mapped_column(ARRAY(String), nullable=False)
    token: Mapped[str] = mapped_column(String(20), nullable=False)


class Action(db.Model):
    __tablename__ = "actions"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    date: Mapped[date] = mapped_column(DateTime, default=datetime.now())
    actor: Mapped[str] = mapped_column(String(40), nullable=False)
    action: Mapped[str] = mapped_column(String(30), nullable=False)
    description: Mapped[str] = mapped_column(String(150), nullable=False)


def migrate(message: str = "Auto migration"):
    # Ensure alembic.ini path is correct (adjust if needed)
    alembic_ini_path = os.path.join(os.path.dirname(__file__), "alembic.ini")

    alembic_cfg = Config(alembic_ini_path)

    # OPTIONAL: set database URL dynamically
    # alembic_cfg.set_main_option("sqlalchemy.url", "postgresql+psycopg2://user:pass@host/db")

    print("📦 Generating migration script...")
    command.revision(alembic_cfg, message=message, autogenerate=True)

    print("🚀 Applying migration...")
    command.upgrade(alembic_cfg, "head")
# Creates all tables declared above, creates nothing if none is declared.

with app.app_context():
    # db.drop_all() # For development purposes
    db.create_all()
# if __name__ =="__main__":
#     migrate("Make referrer nullable")

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


def log_attempt(data: dict, purpose: str, ref: str):
    user_data = data["user_data"]
    new_attempt = Attempt(
        email=data.get("email"),
        first_name=data.get("firstname"),
        last_name=data.get("lastname"),
        user_type=data.get("user_status"),
        phone_number=data.get("phone"),
        purpose=purpose,
        context=user_data.get("paper") if user_data.get("paper") else user_data.get("context"),
        amount=data.get("amount"),
        payment_reference=ref,
        other_data=user_data,
    )
    db.session.add(new_attempt)
    db.session.commit()


def generate_payment_reference(prefix: str):
    unique_part = uuid.uuid4().hex  # 32-char hex string
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    return f"{prefix}-{timestamp}-{unique_part[:8]}"


def calculate_payment_status(full_payment: int, paid:int):
    if full_payment < paid:
        payment_status = "Partly paid"
    elif full_payment == paid:
        payment_status = "Fully paid"
    else:
        payment_status = "Overpaid"
    return payment_status


def move_signee(info: dict, sponsored: bool, email: str, paid: any, spons_details: any=None):
    stmt = select(func.count()).select_from(Student)
    total_students = db.session.execute(stmt).scalar()
    year_code = encode_year(datetime.now().year)  # e.g., 6318
    serial_code = encode_serial(total_students)
    if sponsored:
        sponsor = spons_details.company
        sponsored_papers = ",".join([paper.split("-")[0] for paper in spons_details.papers])
        employment = "Fully/Self employed"
        papers = db.session.query(Paper).filter(Paper.code.in_(spons_details.papers)).all()
        paid = sum([paper.price for paper in papers])
    else:
        sponsor = None
        sponsored_papers = ""
        employment = info.get("employed")
        papers = db.session.query(Paper).filter(Paper.code.in_(info.get("papers"))).all()
        # paid = "get paid"
    full_payment = sum([paper.price for paper in papers])
    full_payment = int(full_payment - (full_payment * info.get("discount", 0)/100))
    payment_status = calculate_payment_status(full_payment, paid)

    signee = db.session.execute(db.select(Signee).where(Signee.email == email)).scalar()
    new_student = Student(
        first_name=signee.first_name,
        last_name=signee.last_name,
        email=email,
        reg_no=f"1331{year_code:04d}{serial_code:04d}",
        password=signee.password,
        acca_reg_no=info.get("acca_reg"),
        birth_date=signee.birth_date,
        phone_number=signee.phone_number,
        gender=signee.gender,
        joined=signee.created_at,
        new_student=True,
        sponsored=sponsored,
        sponsor=sponsor,
        sponsored_papers=sponsored_papers,
        total_fee=full_payment,
        amount_paid=paid,
        payment_status=payment_status,
        house_address=info.get("address"),
        referral_source=info.get("referral_source"),
        referrer=info.get("friend"),
        employment_status=employment,
        discount=info.get("discount"),
        discount_papers=info.get("discount_papers", []),
        oxford_brookes=info.get("oxford"),
        accurate_data=info.get("accuracy"),
        alp_consent=info.get("alp_consent"),
        terms_and_cond=info.get("terms"),
        refund=paid-full_payment if payment_status == "Overpaid" else 0,
        receivable=full_payment-paid if payment_status == "Partly paid" else 0,
        papers=papers,
    )
    db.session.add(new_student)
    db.session.commit()


def update_action(email, action, details):
    new_action = Action(
        actor=email,
        action=action,
        description=details
    )
    db.session.add(new_action)
    db.session.commit()


def update_payment(sponsored: bool, email: str, payment_data: dict=None, spons_details: any=None):
    student = db.session.execute(db.select(Student).where(Student.email == email)).scalar()
    if sponsored:
        papers = db.session.query(Paper).filter(Paper.code.in_(spons_details.papers)).all()
        new_payment = Payment(
            amount=sum([paper.price for paper in papers]),
            payment_reference=spons_details.token,
            sponsored=sponsored,
            paystack_id=0000000000,
            medium=spons_details.company,
            currency="Unknown",
            created_at=datetime.now(),
            paid_at=datetime(2060, 12, 31),
            student=student
        )
    else:
        new_payment = Payment(
            amount=payment_data.get("amount"),
            payment_reference=payment_data.get("reference"),
            paystack_id=payment_data.get("id"),
            medium=payment_data.get("channel"),
            currency=payment_data.get("currency"),
            ip=payment_data.get("ip_address"),
            attempts=payment_data.get("log")["attempts"],
            history=payment_data.get("log")["history"],
            fee=payment_data.get("fee"),
            auth_data=payment_data.get("authorization"),
            fee_breakdown=payment_data.get("fee_split"),
            customer_data=payment_data.get("customer"),
            created_at=payment_data.get("created_at"),
            paid_at=payment_data.get("paid_at"),
            student=student
        )
    db.session.add(new_payment)
    db.session.commit()


def insert_sponsored_row(firstname, lastname, org, papers, token):
    new_sponsor = Sponsored(
        first_name=firstname,
        last_name=lastname,
        company=org,
        papers=papers,
        token=token
    )
    db.session.add(new_sponsor)
    db.session.commit()


def post_payment_executions(reference: str, payment_data: dict) -> tuple:
    """ This function is currently only capable of processing payments for registrations """
    # attempt = db.session.query(Attempt).filter_by(payment_reference=reference).first()
    attempt = db.session.query(Attempt).filter_by(payment_reference=reference).scalar()
    user_type = attempt.user_type
    email = attempt.email
    if user_type.lower() == "signee":
        try:
            move_signee(attempt.other_data, sponsored=False, paid=payment_data["amount"], email=email)
            update_payment(sponsored=False, email=email, payment_data=payment_data)
        except Exception as e:
            return jsonify(
                error={"Error in post payment func": f"Unknown error {e}"}
            ), 500
        else:
            operation_details = f"User registered their first ever course, payments made, [{attempt.context}]"
            update_action(email, "Registered a course.", operation_details)
            db.session.delete(attempt)
            db.session.commit()
            user = db.session.query(Student).filter_by(email=email).scalar()
            return jsonify({
                "title": user.title,
                "firstname": user.first_name,
                "lastname": user.last_name,
                "email": user.email,
                "sex": user.gender,
                "reg_no": user.reg_no,
                "acca_reg_no": user.acca_reg_no,
                "papers": [{paper.code: paper.name} for paper in user.papers],
                "user_status": "student",

            }), 200
    elif user_type.lower() == "student":
        try:
            student = db.session.query(Student).filter_by(email=email).scalar()
            papers = db.session.query(Paper).filter(Paper.code.in_(attempt.other_data.get("papers"))).all()

            full_payment = sum([paper.price for paper in papers])
            full_payment = full_payment - (full_payment * attempt.other_data.get("discount")/100)
            retaking = attempt.other_data.get("retaking")

            student.papers.append(papers) # Relevant ones in the absence of sponsors
            student.total_fee += full_payment # Relevant ones in the absence of sponsors
            student.amount_paid += payment_data.get("amount") # Relevant ones in the absence of sponsors
            student.payment_status = calculate_payment_status(full_payment, student.amount_paid)
            student.retake = retaking if not student.retake else student.retake
            student.discount = attempt.other_data.get("discount")
            student.discount_papers = attempt.other_data.get("discount_papers")
            db.session.commit()
            update_payment(sponsored=False, email=email, payment_data=payment_data)
        except Exception as e:
            return jsonify(
                error={"Error in post payment func": f"Unknown error {e}"}
            ), 400
        else:
            operation_details = f"User registered a new course, they were a student already, payments made, [{attempt.context}]"
            update_action(email, "Registered a course.", operation_details)
            db.session.delete(attempt)
            db.session.commit()
            user = db.session.query(Student).filter_by(email=email).scalar()
            return jsonify({
                "title": user.title,
                "firstname": user.first_name,
                "lastname": user.last_name,
                "email": user.email,
                "sex": user.gender,
                "reg_no": user.reg_no,
                "acca_reg_no": user.acca_reg_no,
                "papers": [{paper.code: paper.name} for paper in user.papers],
                "user_status": "student",

            }), 200
    elif user_type.lower() == "old_student":
        return False, 500 # This functionality is not available yet
    else:
        return jsonify(
            error={"Error in post payment func": f"Unknown user type"}
        ), 400


def post_webhook_process(ref, data):
    print(post_payment_executions(ref, data))


with app.app_context():
    insert_sponsored_row("John", "Doe", "KPMG", ["APM-std", "BT-int"], "KPMG12345")
    insert_sponsored_row("Jane", "Doe", "PWC", ["FM-std", "MA-int"], "PWC12345")

#fill into the papers db
with app.app_context():
    papers = pd.read_excel("resource/ivy pricing.xlsx")
    """ name: Mapped[str] = mapped_column(Text, nullable=False)
    students = relationship("Student", secondary=student_paper, back_populates="papers")
    code: Mapped[str] = mapped_column(Text, nullable=False)
    price: Mapped[int] = mapped_column(Integer, nullable=False)
    revision: Mapped[int] = mapped_column(Integer, nullable=False)"""
    for i, paper in papers.iterrows():
        if not isinstance(paper["Knowledge papers"], float):
            if "papers" in paper["Knowledge papers"].lower():
                continue
            variations = [(" Standard", "std"), (" Intensive", "int")]
            for i in range(2):
                code = paper["Knowledge papers"].split()[-1]
                if code in ["BT", "FA", "MA", "CBL", "OBU", "DipIFRS"] and i != 0:
                    continue
                if code in ["OBU", "DipIFRS"]:
                    revision = 0
                    extension = ""
                    price = paper.Standard
                else:
                    code = "TX" if code == "TAX" else code
                    code = f"{code}-{variations[i][1]}"
                    extension = variations[i][0]
                    price = paper.Standard + (paper.revision if code[-3:] == "std" else 0)
                    revision = 20_000 if code[-3:] == "std" else 0

                new_paper = Paper(
                    name=" ".join(paper["Knowledge papers"].split()[:-1]).title()+extension,
                    code=code,
                    price=int(price),
                    revision=revision
                )
                db.session.add(new_paper)
    db.session.commit()


# -----------------------------
# Initialize Payment
# -----------------------------
# @app.route("/initialize-payment", methods=["POST"])
def initialize_payment(data: dict, type_:str):
    """ type: as in what are they paying for? reg? rev? vid? kit? etc """
    amount = data.get("amount")
    email = data.get("email")
    reference_id = generate_payment_reference(type_.split()[1]) #type_ can be REG, REV, KIT
    try:
        log_attempt(data, type_.split()[0], reference_id)
    except Exception as e:
        return jsonify(
            error={
                "Initialization Error": f"Error logging payment attempt [{e}]",
            }
        ), 403

    headers = {
        "Authorization": f"Bearer {PAYSTACK_SECRET_KEY}",
        "Content-Type": "application/json"
    }
    body = {
        "amount": amount * 100,  # Convert to kobo
        "email": email,
        "reference": reference_id,
        # "metadata": {"cart_id": 398,}
    }

    response = requests.post(f"{BASE_URL}/transaction/initialize", json=body, headers=headers)
    if response.status_code != 200:
        attempt = db.session.execute(db.select(Attempt).where(Attempt.payment_reference == reference_id)).scalar()
        attempt.closed_at = datetime.now()
        attempt.payment_status = "failed"
        attempt.failure_cause = "Failed transaction initialization"
        return jsonify(
            error={
                "Initialization Error": f"Failed to initialize transaction"
            }
        ), response.status_code
    else:
        return jsonify(response.json()), 200


# -----------------------------
# Verify Payment
# -----------------------------
@app.route("/verify/<reference>", methods=["GET"])
def verify_payment(reference):
    verified = db.session.query(Payment).filter_by(payment_reference=reference).scalar()
    if verified:
        user = verified.student
        return jsonify({
            "title": user.title,
            "firstname": user.first_name,
            "lastname": user.last_name,
            "email": user.email,
            "sex": user.gender,
            "reg_no": user.reg_no,
            "acca_reg_no": user.acca_reg_no,
            "papers": [{paper.code: paper.name} for paper in user.papers],
            "user_status": "student",
        }), 200

    headers = {
        "Authorization": f"Bearer {PAYSTACK_SECRET_KEY}"
    }

    response = requests.get(f"{BASE_URL}/transaction/verify/{reference}", headers=headers)

    if response.status_code != 200 or not response.json().get("status"):
        return jsonify({"error": "Verification failed"}), 500
    else:
        feedback = response.json()["data"]
        if feedback.get("status") == "success":
            exec_response = post_payment_executions(reference, feedback)
            if exec_response[1] != 200:
                return jsonify(
                    {
                        "status": "error",
                        "message": "Payment confirmed but internal db error, na gbese be this.",
                        "paystack_says": response.json()["message"],
                        "user_data": exec_response[0].json
                    }
                ), exec_response[1]
            return jsonify(
                {
                    "status": "success",
                    "message": "Payment confirmed, all db updated",
                    "paystack_says": response.json()["message"],
                    "user_data": exec_response[0].json
                }
            ), 200
        elif feedback.get("status") in ["ongoing", "pending", "processing", "queued"]:
            return jsonify(
                {
                    "status": "patience",
                    "message": "Payment underway, exercise patience bros.",
                    "paystack_says": response.json()["message"],
                }
            ), 200
        elif feedback.get("status") in ["failed", "abandoned", "reversed"]:
            return jsonify(
                {
                    "status": "obliterated",
                    "message": "The payment is either abandoned, failed or reversed.",
                    "paystack_says": response.json()["message"],
                }
            ), 200
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
    thread = Thread(target=post_webhook_process, args=(reference, event.get("data", {})))
    thread.start()

    return jsonify({"status": "received"}), 200


# @app.route("/upload/file", methods=["POST"])
# def add_students(file):
#     if request.method == "POST":
#         # data = pd.read_excel("STUDENT POSITION REPORTfor EMMANUEL.xlsx", header=0, sheet_name="STANDARD
#         # CLASS")
#         data = pd.read_excel(file, header=0, sheet_name="STANDARD CLASS")
#         class_type = request.args.get("class")
#         class_dict = {"intensive": Intensive, "standard": Standard}
#         to_add = []
#         # L1 = ['DATE', 'FIRSTNAME ', 'LAST NAME', 'ACCA REG NO',
#         #       'EMAIL ADDRESS', 'DOB', 'PHONE NUMBER', 'NEW STUDENT', 'PAPERS']
#         # What if they add the file that has already been added in the past
#         sponsor_prompt = "I am a sponsored students (Please state employer's name)"
#         for (index, row) in data.iterrows():
#             # Extract Course codes
#             papers_column = [x for x in data.columns if "Papers of interest" in x]
#             code_title = ""
#             i = row[papers_column[0]]
#             try:
#                 paper_name = i.split(", ")
#             except AttributeError:
#                 print(type(i), "for value: ", i)
#             else:
#                 for paper in paper_name:
#                     code = paper.split(" ")[-1]
#                     code = code.strip("()")
#                     code_title = code_title + code + "/"
#
#             # Calculate total price
#             papers = db.session.execute(db.select(Paper)).scalars().all()
#             paper_dict = {}
#             price = 0
#             amount_paid = 0
#             for paper in papers:
#                 paper_code = paper.name.split(" ")[-1].lower()
#                 paper_dict[paper_code] = paper.price
#             for title in code_title.split("/"):
#                 price += paper_dict[title.lower()]
#             # Sort out sponsored students
#             if not pd.isna(row[sponsor_prompt]):
#                 amount_paid = price
#
#             new_student = Student(
#                 first_name=row.firstname,
#                 last_name=row.lastname,
#                 email=row.email,
#                 reg_no=row["ACCA REG NO"],
#                 birth_date=row.DOB,
#                 phone_number=row["PHONE NUMBER"],
#                 new_student=row["NEW STUDENT"],
#                 sponsored=row[sponsor_prompt],
#                 # intensive_papers = "wellwellwell",
#                 # standard_papers = "wellwellwell",
#                 revision=row["REVISION FEE"],
#                 total_fee=row["TOTAL FEE"],
#                 amount_paid=amount_paid,
#                 refund=0,
#                 receivable=0,
#             )
#             to_add.append(new_student)
#
#             if class_dict.get(class_type.lower()):
#                 paper = class_dict[class_type.lower()](
#                     amount_paid=amount_paid,
#                     fee=price,
#                     scholarship_discount=0,
#                     normal_discount=0,
#                     deffered=0,
#                     papers=code_title,
#                     student = new_student
#                 )
#                 to_add.append(paper)
#             else:  # i.e a wrong class type was specified
#                 pass
#             new_task = Task(
#                 DoneBy = current_user,
#                 category = "Data Upload", # Data Upload, Payment Upload, Stats Download, Data Change
#                 time = datetime.now(),
#                 description = "New student data upload",
#                 comments = request.args.get("comment")
#             )
#             to_add.append(new_task)
#             db.session.add_all(to_add)


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
            first_name=data.get("firstname").title(),
            last_name=data.get("lastname").title(),
            phone_number=data.get("phone"),
            birth_date=d_o_b,
            gender=data.get("sex"),
            password=hash_and_salted_password
        )
        with app.app_context():
            db.session.add(new_signee)
            db.session.commit()
    except IntegrityError:
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
                    "user_status": "signee",
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
                    "user_status": "student",

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
                "user_status": "student",
            })
        else:
            return jsonify(
                error={
                    "Incorrect Input": f"Registration number or Password incorrect"  # \n type:{type(g)}. it is {g}",
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
    # Each diet has its own tables that would be named as such, the table to open will be determined by the diet
    # This is for future updates purposes
    print("tiypiee:", type(data.get("diet")))
    user_type = data.get("user_status")
    if user_type.lower() != "signee" and user_type.lower() != "student":
        return jsonify(
            error={
                "Unknown User Type": f"User type {user_type} is not accepted"
            }
        )
    if data.get("sponsored"): # User is sponsored by an organization
        sponsorship = db.session.execute(db.select(Sponsored).where(Sponsored.token == data.get("token"))).scalar()
        if not sponsorship:
            return jsonify(
                error={
                    "Invalid Token": "The inputted token is invalid, try again.",
                }
            ), 409

        if user_type.lower() == "signee":
            # try:
            move_signee(data.get("info"), sponsored=True, paid=None, spons_details=sponsorship, email=data.get("email"))
            operation_details = f"User registered their first ever course, courses are sponsored, [{sponsorship.papers}]"
            update_action(data.get("email"), "Became a student.", operation_details)
            update_payment(sponsored=True, email=data.get("email"), spons_details=sponsorship)
            # except Exception as e:
            #     return jsonify(
            #         error={
            #             "Some kinda DB Error": f"Error is {e}.",
            #         }
            #     ), 409
            # else:
            return jsonify({
                "status": "success",
                "message": "Registration successful",
            }), 201
        elif user_type.lower() == "student":
            student = db.session.execute(db.select(Student).where(Student.reg_no == data.get("reg_no"))).scalar()
            student.sponsored = True
            student.sponsors = sponsorship.company
            student.sponsored_papers = ",".join([paper.split("-")[0] for paper in sponsorship.papers])
            student.employment_status = "Fully/Self employed"
            papers = db.session.query(Paper).filter(Paper.code.in_(sponsorship.papers)).all()
            student.papers.append(papers) # Relevant ones in the absence of sponsors
            student.total_fee += sum([paper.price for paper in papers]) # Relevant ones in the absence of sponsors
            student.amount_paid += sum([paper.price for paper in papers]) # Relevant ones in the absence of sponsors
            db.session.commit()
            operation_details = f"User registered a new course, they were a student already, courses are sponsored, [{sponsorship.papers}]"
            update_action(data.get("email"), "Registered a course.", operation_details)
            return jsonify({
                "status": "success",
                "message": "Registration successful",
            }), 201
        elif user_type == "old student":
            pass
    else: # User is sponsoring themselves
        return initialize_payment(data, "registration REG")


# GET request to biodata endpoint  ✔🎉
# GET request for a courses endpoint types=[int, std, all] 👎
# the courses endpoint should also check and return if student is scholarship qualified ✔🎉
# with old students and students the courses endpoint should return all courses they took in the last diet ("history" so to speak) ⏸️✋
# Change the way you get serial number, instead of getting the db len you should decode the last reg number ✔🎉
# Update to above, what if the last person has completely deferred and they are no longer in the students db, the last reg will be misleading. Ask Gpt ✔🎉
# When they defer you have to update the all_students db with the change in case of a total  ⏸️✋
# It makes sense to set the retake value only for oldees but what if the oldee became a current student before retaking, reason am ✔🎉
# Might need to send an additional fee charge dict when a request is made to the courses endpoint {fee:123, reason:"ds"} ✔🎉
# when a scholarship has been used the email key should be set to email += " |used" ✔🎉
# Might want to change the reg number algorithm to account for diet too ⏸️✋
# Add a usewd column to the sponsiored table so a key can't be used multiple times ✔🎉
# Add a payment breakdown kini in the payment info ⏸️✋
# Add category option to papers db ✔🎉
# ADD availability option to papers db ✔🎉
#--NEW
# With the courses endpoint i should send the students current courses ✔🎉
# Check before registering that are not already doing the course ✔🎉
# There is a problem of id increasing whenever a commit is made and for some reason it fails ⏸️✋
# Fix problem of 2+ paper scholarship where one is used and the entire entry in db is set to used even though there's still 1+ left ✔🎉
# As per last issue i will fix it by removing the unique constraint from "email", " |used" will only be added to the used once, using a list to loop throu... ✔🎉
# Feature to mark a transaction as abandoned after a timeframe, like days or hours ✔🎉
# Update sign up and sign in process to chack "all" db to account for those who already have an account ✔🎉
# Do not forget to make students db account for diet and year i.e sumn like student202502
# Do not forget token issues so they do not access a page if they aren't signed in
# Check that acca reg no is not being duplicated ✔🎉
# Verify how many digits is an acca reg no?
# Handle password reset token multi-use case security issue
#

# @app.route("/login", methods=["POST"])
# def login():
#     pass

##-----ADMIN------##
# Make a course available or unavailable
# Create a course
# Create Sponsored
# Create Scholarship

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True, port=5001)

L1 = ['DATE', 'FIRSTNAME ', 'LAST NAME', 'ACCA REG NO',
       'EMAIL ADDRESS', 'DOB', 'PHONE NUMBER', 'NEW STUDENT', 'PAPERS']
l2 = ['DATE', 'FIRSTNAME ', 'LAST NAME', 'ACCA REG NO',
       'EMAIL ADDRESS', 'DOB', 'PHONE NUMBER', 'NEW STUDENT', 'PAPERS', 'CLASS FEE',
       'REVISION FEE', 'TOTAL FEE', 'AMOUNT PAID', 'SCHOLARSHIP DISCOUNT', 'NORMAL DISCOUNT',
       'REFUND', 'DEFFERED', 'RECEIVABLES']
tables = ["Staffs", "Intensive", "Standard", "Tasks"]
# for i in l2:
#     if i not in L1:
#         print(i, end=", ")

        # user_type = request.args.get("type")
        # if user_type != "admin" and user_type != "student":
        #     return jsonify(
        #         error={
        #             f"Invalid User-Type": f"There is no user of type {user_type}",
        #         }
        #     ), 403
        # elif user_type == "admin":
