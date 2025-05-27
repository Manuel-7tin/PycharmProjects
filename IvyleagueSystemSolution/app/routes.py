import json
import requests
import pandas as pd
from config import Config
from threading import Thread
from datetime import datetime
from flask import jsonify, request
from sqlalchemy.exc import IntegrityError
from .errors import UserNotFoundError
from services.db_services import insert_sponsored_row, is_valid_password
from werkzeug.security import generate_password_hash, check_password_hash
from services.db_services import post_payment_executions, post_webhook_process, exists_in_models
from services.db_services import move_signee, update_action, update_payment, initialize_payment
from .models import db, All, Payment, Signee, Student, Sponsored, Paper, SystemData, Scholarship, Attempt


def register_routes(app):


    # -----------------------------
    # Verify Payment
    # -----------------------------
    @app.route("/api/v1/verify/<reference>", methods=["GET"])
    def verify_payment(reference):
        verified = db.session.query(Payment).filter_by(payment_reference=reference).scalar()
        if verified:
            user = verified.student
            return jsonify({
                "title": user.title,
                "firstname": user.first_name,
                "lastname": user.last_name,
                "email": user.email,
                "gender": user.gender,
                "reg_no": user.reg_no,
                "acca_reg_no": user.acca_reg_no,
                "papers": [{paper.code: paper.name} for paper in user.papers],
                "user_status": "student",
            }), 200

        headers = {
            "Authorization": f"Bearer {Config.PAYSTACK_SECRET_KEY}"
        }

        try:
            response = requests.get(f"{Config.BASE_URL}/transaction/verify/{reference}", headers=headers)
        except ConnectionError as e:
            return jsonify(
                error={
                    "Connection Error": "Failed to connect to paystack"
                }
            )

        if response.status_code != 200 or not response.json().get("status"):
            return jsonify({"error": "Verification failed"}), 500
        else:
            from pprint import pprint
            feedback = response.json()["data"]
            pprint(feedback)
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
            elif feedback.get("status") == "abandoned":
                return jsonify(
                    {
                        "status": "some patience needed",
                        "message": "Payment underway, it probably hasn't started.",
                        "paystack_says": response.json()["message"],
                    }
                ), 200
            elif feedback.get("status") in ["failed", "reversed"]:
                attempt = db.session.execute(db.select(Attempt).where(Attempt.payment_reference == reference)).scalar()
                attempt.closed_at = datetime.now()
                attempt.payment_status = "failed"
                attempt.failure_cause = "Transaction declined or reversed"
                db.session.commit()
                return jsonify(
                    {
                        "status": "obliterated",
                        "message": "The payment is either failed or reversed.",
                        "paystack_says": response.json()["message"],
                    }
                ), 200
        # data = response.json()
        # return jsonify(data), 200


    # -----------------------------
    # Webhook
    # -----------------------------
    @app.route("/api/v1/webhook", methods=["POST"])
    def handle_webhook():
        print("They don call webhook oo")
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


    @app.route("/api/v1/signup", methods=["POST"])
    def sign_up():
        print("i dey come")
        if request.args.get("api-key") != "AyomideEmmanuel":
            # g = request.args.get("api-key")
            return jsonify(
                error={
                    "Access Denied": f"You do not have access to this resource"  # \n type:{type(g)}. it is {g}",
                }
            ), 403
        data = request.get_json()

        # Check if they are already signed up
        already_exists = [False]
        if exists_in_models("email", data.get("email"), Signee, Student, All):
            already_exists = [True, "Email"]
        elif exists_in_models("phone", data.get("phone"), Signee, Student):
            already_exists = [True, "Phone number"]
        if already_exists[0]:
            return jsonify(
                error={
                    "Tautology,": f"{already_exists[1]} already in use!"
                }
            ), 403
        if isinstance(data.get("dob"), str):
            try:
                d_o_b = datetime.fromisoformat(data.get("dob").replace("Z", "+00:00"))
            except:
                d_o_b = datetime.strptime(data.get("dob"), "%d/%m/%Y")
        else:
            d_o_b = data.get("dob")
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
            print(f"data is {request.method}")
            new_signee = Signee(
                # id=random.randint(3, 9),
                title=data.get("title"),
                email=data.get("email"),
                first_name=data.get("firstname").title(),
                last_name=data.get("lastname").title(),
                phone_number=data.get("phone"),
                birth_date=d_o_b,
                gender=data.get("gender"),
                password=hash_and_salted_password
            )
            with app.app_context():
                db.session.add(new_signee)
                db.session.commit()
        except IntegrityError as e:
            print(str(e))
            print(data)
            return jsonify(
                error={
                    "DB Integrity Compromise": f"User email or phone number already exists",
                }
            ), 409
        except AttributeError as e:
            print(type(data), data)
            return jsonify(
                error={
                    "Invalid Key": f"You missed a key.\n{e} required keys: [firstname, lastname, title, email, gender, dob, phone, password",
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


    @app.route("/api/v1/signin", methods=["POST"])
    def sign_in():
        if request.args.get("api-key") != "AyomideEmmanuel":
            # g = request.args.get("api-key")
            return jsonify(
                error={
                    "Access Denied": f"You do not have access to this resource"  # \n type:{type(g)}. it is {g}",
                }
            ), 403
        data = request.get_json()
        login_type = data.get("type")

        if login_type == "email":
            result = db.session.execute(db.select(Student).where(Student.email == data.get("email")))
            user = result.scalar()

            if not user:  # User is not a registered student
                result = db.session.execute(db.select(Signee).where(Signee.email == data.get("email")))
                user = result.scalar()
                if not user:  # User is not a signee either
                    return jsonify(
                        error={
                            "Incorrect Input": f"Email or password incorrect"  # \n type:{type(g)}. it is {g}",
                        }
                    ), 403

                password = data.get("password")
                if check_password_hash(user.password, password):
                    return jsonify({
                        "title": user.title,
                        "firstname": user.first_name,
                        "lastname": user.last_name,
                        "email": user.email,
                        "gender": user.gender,
                        "user_status": "signee",
                        "dob": user.birth_date,
                        "phone_no": user.phone_number,
                        "address": "",
                        "reg_no": "",
                        "acca_reg": ""
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
                        "gender": user.gender,
                        "dob": user.birth_date,
                        "phone_no": user.phone_number,
                        "address": user.address,
                        "reg_no": user.reg_no,
                        "acca_reg": user.acca_reg_no,
                        "papers": [{paper.code: paper.name} for paper in user.papers],
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

            if not user:  # User is not a registered student
                return jsonify(
                    error={
                        "Incorrect Input": f"Registration number or password incorrect"
                        # \n type:{type(g)}. it is {g}",
                    }
                ), 403

            password = data.get("password")
            if check_password_hash(user.password, password):
                return jsonify({
                    "title": user.title,
                    "firstname": user.first_name,
                    "lastname": user.last_name,
                    "email": user.email,
                    "gender": user.gender,
                    "reg_no": user.reg_no,
                    "acca_reg_no": user.acca_reg_no,
                    "papers": [{paper.code: paper.name} for paper in user.papers],
                    "user_status": "student",
                })
            else:
                return jsonify(
                    error={
                        "Incorrect Input": f"Registration number or Password incorrect"
                        # \n type:{type(g)}. it is {g}",
                    }
                ), 403
        else:
            return jsonify(
                error={
                    "Unknown Login Type": f"Log-in type {login_type} is not accepted",
                }
            ), 409

    @app.route("/api/v1/register", methods=["POST"])
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
        if data.get("sponsored"):  # User is sponsored by an organization
            sponsorship = db.session.execute(db.select(Sponsored).where(Sponsored.token == data.get("token"))).scalar()
            if not sponsorship:
                return jsonify(
                    error={
                        "Invalid Token": f"The token is invalid, try again. {(data.get("token"), Sponsored.token)}",
                    }
                ), 409
            elif not (sponsorship.first_name.title() == data.get("firstname") and sponsorship.last_name.title() == data.get("lastname")):
                hello = (sponsorship.first_name.title(), data.get("firstname"), sponsorship.last_name.title(), data.get("lastname"))
                return jsonify(
                    error={
                        "Name Mismatch": f"Your registered name contrasts with our records {hello}.",
                    }
                ), 409
            elif sponsorship.used:
                return jsonify(
                    error={
                        "Expired Token": "The inputted token is expired, try again.",
                    }
                ), 409

            if user_type.lower() == "signee":
                try:
                    move_signee(data.get("info"), sponsored=True, paid=None, spons_details=sponsorship,
                                email=data.get("email"))
                    operation_details = f"User registered their first ever course, courses are sponsored, [{sponsorship.papers}]"
                    update_action(data.get("email"), "Became a student.", operation_details)
                    update_payment(sponsored=True, email=data.get("email"), spons_details=sponsorship)
                except UserNotFoundError as e:
                    return jsonify(
                        error={
                            "In-Existent User": f"User not found [{e}].",
                        }
                    ), 409
                else:
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
                student.papers.append(papers)  # Relevant ones in the absence of sponsors
                student.total_fee += sum([paper.price for paper in papers])  # Relevant ones in the absence of sponsors
                student.amount_paid += sum(
                    [paper.price for paper in papers])  # Relevant ones in the absence of sponsors
                sponsorship.used = True
                db.session.commit()
                operation_details = f"User registered a new course, they were a student already, courses are sponsored, [{sponsorship.papers}]"
                update_action(data.get("email"), "Registered a course.", operation_details)
                return jsonify({
                    "status": "success",
                    "message": "Registration successful",
                }), 201
            elif user_type == "old student":
                pass
        else:  # User is sponsoring themselves
            if data.get("user_status").lower() == "student":
                done_list = []
                student = db.session.query(Student).filter_by(email=data.get("email")).scalar()
                for i in data.get("user_data")["papers"]:
                    if i in [paper.code for paper in student.papers]:
                        done_list.append(i)
                if done_list:
                    return jsonify(
                        error={
                        "Error": "User cannot register a paper they are already taking."
                    }
                    ), 403

            return initialize_payment(data, "registration REG")

    # with app.app_context():
    #     papers = pd.read_excel("resource/ivy pricing.xlsx")
    #     """ name: Mapped[str] = mapped_column(Text, nullable=False)
    #     students = relationship("Student", secondary=student_paper, back_populates="papers")
    #     code: Mapped[str] = mapped_column(Text, nullable=False)
    #     price: Mapped[int] = mapped_column(Integer, nullable=False)
    #     revision: Mapped[int] = mapped_column(Integer, nullable=False)"""
    #     for i, paper in papers.iterrows():
    #         if not isinstance(paper["Knowledge papers"], float):
    #             if "papers" in paper["Knowledge papers"].lower():
    #                 continue
    #             variations = [(" Standard", "std"), (" Intensive", "int")]
    #             for i in range(2):
    #                 code = paper["Knowledge papers"].split()[-1]
    #                 if code in ["BT", "FA", "MA", "CBL", "OBU", "DipIFRS"] and i != 0:
    #                     continue
    #                 if code in ["OBU", "DipIFRS"]:
    #                     revision = 0
    #                     extension = ""
    #                     category = "Additional"
    #                     price = paper.Standard
    #                 else:
    #                     if code in ["BT", "FA", "MA"]:
    #                         category = "Knowledge"
    #                     elif code in ["PM", "FR", "AA", "TAX", "FM", "CBL"]:
    #                         category = "Skill"
    #                     else:
    #                         category = "Professional"
    #                     code = "TX" if code == "TAX" else code
    #                     code = f"{code}-{variations[i][1]}"
    #                     extension = variations[i][0]
    #                     price = paper.Standard + (paper.revision if code[-3:] == "std" else 0)
    #                     revision = 20_000 if code[-3:] == "std" else 0
    #
    #                 new_paper = Paper(
    #                     name=" ".join(paper["Knowledge papers"].split()[:-1]).title() + extension,
    #                     code=code,
    #                     price=int(price),
    #                     revision=revision,
    #                     category=category
    #                 )
    #                 db.session.add(new_paper)
    #         db.session.commit()
    #
    #     with app.app_context():
    #         with open("questions.json", mode="r") as file:
    #             data = json.load(file)
    #         new_data = SystemData(
    #             data_name="reg_form_info",
    #             data=data
    #         )
    #         db.session.add(new_data)
    #         db.session.commit()



    @app.route("/api/v1/required-info", methods=["GET"])
    def needed_info():
        if request.args.get("api-key") != "AyomideEmmanuel":
            return jsonify(
                error={
                    "Access Denied": "You do not have access to this resource",
                }
            ), 403
        data_name = request.args.get("title")
        data = db.session.query(SystemData).filter_by(data_name=data_name).scalar()
        if data:
            return jsonify(data.data), 200
        else:
            return jsonify(
                error={
                    "Inexistent Data": f"The requested data {data_name} does not exist."
                }
            ), 400

    @app.route("/api/v1/courses", methods=["GET"])
    def get_courses():
        if request.args.get("api-key") != "AyomideEmmanuel":
            return jsonify(
                error={
                    "Access Denied": f"You do not have access to this resource",
                }
            ), 403
        user_type = request.args.get("user_status").lower()
        if user_type.lower() not in ["signee", "student", "old_student"]:
            return jsonify(
                error={
                    "Unknown User Type": f"User type {user_type} is not accepted"
                }
            )
        details = {}
        if request.args.get("reg").lower() in ["true", 1, "t", "y", "yes", "yeah"]:
            scholarships = db.session.query(Scholarship).filter_by(email=request.args.get("email")).all()
            details["scholarships"] = [(i.paper, i.discount) for i in scholarships]
            details["fee"] = [{"amount":5000, "reason": "One time student registration."}] if user_type == "signee" else []
            acca_reg_no = request.args.get("acca_reg")
            if db.session.query(Student).filter_by(acca_reg_no=acca_reg_no).scalar() and acca_reg_no != "001":
                return jsonify(
                    error={
                        "Tautology": f"ACCA registration number already used."
                    }
                )
            elif len(acca_reg_no) < 7 and acca_reg_no != "001":
                return jsonify(
                    error={
                        "Invalid Error": f"ACCA registration number invalid."
                    }
                )
            if user_type == "student":
                student = db.session.query(Student).filter_by(email=request.args.get("email")).scalar()
                if not student:
                    return jsonify(
                        error={
                            "Some Kinda Error": "Student not found!!"
                        }
                    )
                details["current_papers"] = [paper.code for paper in student.papers]
            #if student is scholarship qualified
        try:
            papers = db.session.query(Paper).all()
            paper_details = []
            for i in papers:
                paper_details.append(
                    {
                        "name": i.name,
                        "category": i.category,
                        "code": i.code,
                        "price": i.price,
                    }
                )
            details["papers"] = paper_details
        except Exception as e:
            return jsonify(
                error={
                    "Internal Error": f"Error message: [{e}]",
                }
            ), 500
        else:
            return jsonify(details), 200


    @app.route("/api/v1/reset-password")
    def recover_password():
        print("hello")

    @app.route("/api/v1/temp", methods=["GET"])
    def gy():
        s = request.args.get("api-key").lower() == "true"
        print(type(s), s)
        return jsonify({"res":s})



    # with app.app_context():
    #     insert_sponsored_row("John", "Doe", "KPMG", ["APM-std", "BT-int"], "KPMG12345")
    #     insert_sponsored_row("Ojutalayo", "Ayomide", "Deloitte", ["AFM-std", "SBL-int"], "Deloitte789")
    #     insert_sponsored_row("Jane", "Doe", "PWC", ["FM-std", "MA-int"], "PWC12345")
    #
    # with app.app_context():
    #     new_schols = Scholarship(
    #         email="Jan@samp.com",
    #         paper=["TX-std", "CBL-int"],
    #         discount=15,
    #     )
    #     db.session.add(new_schols)
    #     db.session.commit()

"ibbd bmzf qwra jbwv"