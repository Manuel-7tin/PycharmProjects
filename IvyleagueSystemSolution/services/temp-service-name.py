from email.message import EmailMessage


mail_sender = "opolopothings@gmail.com"
PASSWORD = "lxdmjkyryqwqxbml"
msg_subject = "**Welcome to Ivy League Associates! Please Confirm Your Email**"

def send_signup_message(username: str, user_email: str):
    try:
        # Read the original HTML content
        with open(f"../letters/signup-message.html", 'r', encoding='utf-8') as file:
            html_content = file.read()
        html_content = html_content.replace("[User's First Name]", username)
    except FileNotFoundError:
        print(f"Error: The signup html file was not found.")
        return 0
    except Exception as e:
        print(f"An error occurred: {e}")
        return 0

    # 4. Send the letter generated in step 3 to that person's email address.
    message = EmailMessage()
    message["From"] = f"Ivy League Updates <{mail_sender}>"
    message["To"] = user_email
    message["Subject"] = msg_subject
    attach_image(images, message, image_cid)
    # message.set_content(personalized_letter)
    message.add_alternative(personalized_letter, subtype='html')
    message.add_header("Reply-to", "updates@ivyleaguenigeria.com")

    context = ssl.create_default_context()
    breaks = 0
    while True:
        try:
            with smtplib.SMTP_SSL(host="smtp.gmail.com", port=465, context=context) as mail:
                mail.login(user=mail_sender, password=PASSWORD)
                mail.sendmail(from_addr=mail_sender, to_addrs=person["email"], msg=message.as_string())
        except smtplib.SMTPConnectError as f:
            print("error as", f)
        except smtplib.SMTPException as e:
            print("Encountered smtp error :", e)
            break
        except socket.gaierror as e:
            print("there is an error:", e)
            breaks += 1
            time.sleep(3)
            if breaks > 4:
                # error404()
                break
        else:
            break
