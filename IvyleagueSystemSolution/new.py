from datetime import date, datetime
from flask import Flask, jsonify, request, abort, render_template, redirect, url_for, flash
# from flask_bootstrap import Bootstrap5
# from flask_ckeditor import CKEditor
# from flask_gravatar import Gravatar
from flask_login import UserMixin, login_user, LoginManager, current_user, logout_user
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship, DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Text, LargeBinary, DateTime, Boolean, Date, Column
from sqlalchemy import Table, ForeignKey
from sqlalchemy import func, select
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
import werkzeug.exceptions
from sqlalchemy.orm import relationship

import pandas as pd
from datetime import datetime
# Import your forms from the forms.py
# from forms import CreatePostForm, RegisterForm, LoginForm, CommentForm

app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
# ckeditor = CKEditor(app)
# Bootstrap5(app)

# CREATE DATABASE
class Base(DeclarativeBase):
    pass


import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

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
create_postgres_db_if_not_exists("test2", "postgres", "root")



app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:root@localhost:5432/test2' #'postgresql://test2.db'
db = SQLAlchemy(model_class=Base)
db.init_app(app)


class Signee(db.Model):
    __tablename__ = "signees"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(5), nullable=True)
    email: Mapped[str] = mapped_column(String(120), nullable=False, unique=True)
    first_name: Mapped[str] = mapped_column(String(30), nullable=False)
    last_name: Mapped[str] = mapped_column(String(30), nullable=False)
    phone_number: Mapped[str] = mapped_column(String(15))
    created_at = mapped_column(DateTime, default=datetime.now)
    birth_date: Mapped[date] = mapped_column(Date, nullable=False)
    gender = mapped_column(String(5), nullable=False)


with app.app_context():
    db.create_all()

@app.route("/signup", methods=["POST"])
def sign_up():
    print("i dey come")
    if request.args.get("api-key") != "AyomideEmmanuel":
        g = request.args.get("api-key")
        return jsonify(
            error={
                "Access Denied": f"You do not have access to this resource\n type:{type(g)}. it is {g}",
            }
        ), 403
    data = request.get_json()
    print(dict(data))
    if isinstance(data.get("birthdate"), str):
        d_o_b = datetime.strptime(data.get("birthdate"), "%d/%m/%Y")
    else:
        d_o_b = data.get("birthdate")
    import random
    # try:
    new_signee = Signee(
        # id=random.randint(3, 9),
        title=data.get("title"),
        email=data.get("email"),
        first_name=data.get("firstname"),
        last_name=data.get("lastname"),
        phone_number=data.get("phone"),
        birth_date=d_o_b,
        gender=data.get("sex"),
    )
    with app.app_context():
        db.session.add(new_signee)
        db.session.commit()
    return jsonify({
            "status": "success",
            "message": "Signup successful",
        }), 201

@app.route("/geng", methods=["POST"])
def temp():
    body = request.get_json()
    data = request.args
    data2 = request.data
    print("1", dict(data))
    print("2", data2)
    print("3", dict(body))
    return jsonify({
            "status": "success",
            "message": "Signup successful",
        }), 201

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True, port=5001)