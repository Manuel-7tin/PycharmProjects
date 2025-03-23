from flask import Flask, abort, render_template, redirect, url_for, flash, request
from zipfile import ZipFile
print("hello")

def extract_zipfile(file):
    # loading the temp.zip and creating a zip object
    with ZipFile(file, 'r') as zObject:
        # Extracting all the members of the zip
        # into a specific location.
        zObject.extractall(
            path="./chat-details")

app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'

@app.route('/')
def welcome_user():
    # result = db.session.execute(db.select(BlogPost))
    # posts = result.scalars().all()
    # print(current_user.name)
    return render_template("index.html")

@app.route('/whatsapp_thingy')
def what():
    return render_template("whatsapp.html")

@app.route('/second')
def lesee():
    return render_template("second.html")

@app.route('/t', methods=["POST"])
def temp():
    return render_template("ivyindex.html")

@app.route("/upload", methods=["GET", "POST"])
def decipher():
    if request.method == "POST":
        uploaded_file = request.files.get("rarFile")
        filename = uploaded_file.filename
        print(f"Uploaded file {filename} of file type {type(uploaded_file)}")
        extract_zipfile(uploaded_file)
    return redirect("https://google.com/")

if __name__ == "__main__":
    app.run(debug=True, port=5001)
