# Adekunle Kofoworola, reporting for duty.
# Import the necessary modules
import tkinter as tk
from tkinter import LEFT, Button, Entry, IntVar, Label, StringVar, messagebox
from tkinter import filedialog
from pathlib import Path
from pypdf import PdfReader, PdfWriter
import pyttsx3
from speech_recognition import Recognizer, AudioFile
from pydub import AudioSegment
import os

root = tk.Tk()  # Create a root Tkinter window
root.withdraw()

# Define variables globally
start_pgNo = tk.IntVar()
end_pgNo = tk.IntVar()

# Define speaker globally
speaker = pyttsx3.init()


def stop_speech():
    global speaker
    # Stops the speaker.
    speaker.stop()
    speaker = pyttsx3.init()


# Open the selected PDF and read text from it as an audio.
def read():
    global speaker
    global end_pgNo, start_pgNo
    path = filedialog.askopenfilename()  # Get the path of the PDF based on the user's location selection
    pdfLoc = open(path, 'rb')  # Opening the PDF
    pdfreader = PdfReader(pdfLoc)  # Creating a PDF reader object for the opened PDF

    start = int(start_pgNo.get())  # Get start and end page and convert input to integer
    end = int(end_pgNo.get())

    # Reading all the pages from start to end page number
    for i in range(start, end + 1):
        page = pdfreader.pages[i]  # Getting the page of the PDF
        txt = page.extract_text()  # Extracting the text from the PDF
        speaker.say(txt)  # Getting the audio output of the text
        speaker.runAndWait()  # Processing the voice commands


# Function to create a GUI and get required inputs for PDF to Audio Conversion
def pdf_to_audio():
    # Creating a window
    wn1 = tk.Tk()
    wn1.title("Kofo's PDF to Audio converter")
    wn1.geometry('500x400')
    wn1.config(bg='lightblue')

    Label(wn1, text='Kofo PDF to Audio converter',
          fg='black', font=('Verdana', 15)).place(x=100, y=10)

    Label(wn1, text='Enter the start and the end page to read.', anchor="e", justify=LEFT).place(x=120, y=90)

    # Getting the input of the starting page
    Label(wn1, text='Start Page No:').place(x=100, y=140)

    startPg = Entry(wn1, width=20, textvariable=start_pgNo)
    startPg.place(x=80, y=170)

    # Getting the input of the ending page
    Label(wn1, text='End Page No:').place(x=290, y=140)

    endPg = Entry(wn1, width=20, textvariable=end_pgNo)
    endPg.place(x=280, y=170)

    # Button to select the PDF and get the audio input
    Label(wn1, text='Choose a PDF file to convert to audio and click Stop to stop the audio.').place(x=70, y=230)
    Button(wn1, text="Choose PDF", bg='darkgray', font=('Consolas', 13),
           command=read).place(x=140, y=270)

    # Stop Button
    stop_button = Button(wn1, text="Stop", command=stop_speech, bg="darkgray", fg="black", font=("Consolas", 13),
                         width=7, height=1)
    stop_button.place(x=260, y=270)
    wn1.mainloop()


# Declaring global variable for PDF to Speech conversion
global pdfPath


# Function to update the PDF file with the text, both given as parameters
def write_text(filename, text):
    writer = PdfWriter()  # Creating a PDF writer object
    writer.addBlankPage(72, 72)  # Creating a blank page
    pdfPath = Path(filename)  # Getting the path of the PDF
    with pdfPath.open('ab') as output_file:  # Opening the PDF
        writer.write(output_file)  # saving the text in the writer object
        output_file.write(text)  # writing the text in the PDF


# Function to convert audio into text
def convert():
    path = filedialog.askopenfilename()  # Getting the location of the audio file
    audioLoc = open(path, 'rb')  # Opening the audio file

    pdf_loc = pdfPath.get()  # Getting the path of the PDF

    # Getting the name and extension of the audio file and confirming if it is mp3 or wav
    audioFileName = os.path.basename(audioLoc).split('.')[0]
    audioFileExt = os.path.basename(audioLoc).split('.')[1]
    if audioFileExt != 'wav' and audioFileExt != 'mp3':
        messagebox.showerror('Error!', 'The format of the audio file should be either "wav" and "mp3".')

    # If it's mp3 file, converting it into wav file
    if audioFileExt == 'mp3':
        audio_file = AudioSegment.from_file(Path(audioLoc), format='mp3')
        audio_file.export(f'{audioFileName}.wav', format='wav')
    source_file = f'{audioFileName}.wav'

    # Creating a recognizer object and converting the audio into text
    recog = Recognizer()
    with AudioFile(source_file) as source:
        recog.pause_threshold = 5
        speech = recog.record(source)
        text = recog.recognize_google(speech)
        write_text(pdf_loc, text)


# Function to create a GUI and get required inputs for Audio to PDF Conversion
def audio_to_pdf():
    # Creating a window
    wn2 = tk.Tk()
    wn2.title("Kofo's Audio to PDF converter")
    wn2.geometry('500x400')
    wn2.config(bg='lightblue')

    pdfPath = StringVar(wn2)  # Variable to get the PDF path

    Label(wn2, text='Kofo Audio to PDF converter',
          fg='black', font=('Verdana', 15)).place(x=60, y=10)

    # Getting the PDF path
    Label(wn2, text='Enter the PDF File location where you want to save:').place(x=20, y=70)
    Entry(wn2, width=50, textvariable=pdfPath).place(x=20, y=100)

    Label(wn2, text='Choose the Audio File that you want to convert to PDF (.wav and .mp3 extensions only):',
          fg='black').place(x=20, y=150)

    # Button to select the audio file and convert it
    Button(wn2, text='Choose', bg='darkgray', font=('Courier', 13),
           command=convert).place(x=170, y=190)
    wn2.mainloop()  # Runs the window till it is closed


# Create the main window
wn = tk.Tk()
wn.title("Kofo's PDF to Audio and Audio to PDF converter")
wn.geometry('700x300')
wn.config(bg='lightpink')

Label(wn, text='Kofo PDF to Audio and Audio to PDF converter',
      fg='black', font=('Verdana', 15)).place(x=40, y=10)

# Button to convert PDF to Audio
Button(wn, text="Convert PDF to Audio", bg='darkgray', font=('Consolas', 15),
       command=pdf_to_audio).place(x=230, y=80)

# Button to convert Audio to PDF
Button(wn, text="Convert Audio to PDF", bg='darkgray', font=('Consolas', 15),
       command=audio_to_pdf).place(x=230, y=150)

# Runs the window till it is closed
wn.mainloop()