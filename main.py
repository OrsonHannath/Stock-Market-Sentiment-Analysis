# Import main packages
import tkinter as tk
from tkinter import filedialog
import stockanalysis as sa

training = True
training_btn_txt_file = "Find Data"
training_btn_txt_input = "Find Data"

analyse_btn_txt_file = "Analyse File"
analyse_btn_txt_input = "Analyse Ticker(s)"


def analyse_ticker_input():
    # Check if trying to train data set or trying to get Evaluation
    if not training:
        if anlyTickerInput.get() != "" and anlyTickerInput.get() != "Ticker or Tickers (ticker1, ticker2)":
            print("Analysing Input Ticker(s)")
            sa.analyse_ticker_input(frame, anlyTickerInput.get(), canvas, root)
        else:
            print("Invalid Input Ticker(s)")
    else:
        if anlyTickerInput.get() != "" and anlyTickerInput.get() != "Ticker or Tickers (ticker1, ticker2)":
            print("Analysing Input Ticker(s)")
            sa.analyse_sentiment_ticker_input(anlyTickerInput.get())
        else:
            print("Invalid Input Ticker(s)")


def analyse_ticker_file():
    # Check if trying to train data set or trying to get Evaluation
    if not training:
        if fileLocation != "":
            print("Analysing Input Ticker(s) From File")
            sa.analyse_ticker_file(frame, fileLocation, canvas, root)
        else:
            print("Invalid File Path")
    else:
        if fileLocation != "":
            print("Analysing Input Ticker(s) From File")
            sa.analyse_sentiment_ticker_file(fileLocation)
        else:
            print("Invalid File Path")

# --- Tkinter Canvas Setup ---
root = tk.Tk()
root.resizable(0, 0)
canvas = tk.Canvas(root, height=300, width=700, bg="#121212")
canvas.pack()

# Tkinter Frame Setup
frame = tk.Frame(root, bg="#121212")
frame.place(relwidth=1, relheight=1)

# Start Menu Layout Setup
# Called When Text Box is Clicked (Allows for placeholder text)
anlyFileClicked = False
def anly_file_click(*args):
    global anlyFileClicked
    if not anlyFileClicked or anlyFileInput.get() == "Ticker File (Comma Seperated)":
        anlyFileInput.delete(0, 'end')
        anlyFileClicked = True


# Called When Entry is Unfocused (Unfocus the text if nothing in it)
def anly_file_left(*args):
    if anlyFileInput.get() == "":
        anlyFileInput.insert(0, "Ticker File (Comma Seperated)")
        root.focus()


anlyFileInput = tk.Entry(frame, justify="center", fg="#000000", bg="#BB86FC")
anlyFileInput.insert(0, "Ticker File (Comma Seperated)")
anlyFileInput.place(relwidth=0.5, relheight=0.1, relx=0.14, rely=0.4)
anlyFileInput.bind("<Button-1>", anly_file_click)
anlyFileInput.bind("<Leave>", anly_file_left)

# Called When Open File Button is Clicked
fileLocation = ""
def open_file_func():
    filename = filedialog.askopenfilename(initialdir="/", title="Select File", filetypes=(("csv", "*.csv"), ("all files", "*.*")))
    global fileLocation
    fileLocation = filename
    global anlyFileClicked
    anlyFileClicked = True
    anlyFileInput.insert(0, fileLocation)


openFileBtn = tk.Button(frame, text="Open File", padx=15, pady=10, fg="#000000", bg="#CF6679", command=open_file_func)
openFileBtn.place(relwidth=0.1, relheight=0.1, relx=0.5 + 0.14 + 0.01, rely=0.4)

anlyFileBtn = tk.Button(frame, text=training_btn_txt_file if training else analyse_btn_txt_file, padx=15, pady=10, fg="#000000", bg="#CF6679", command=analyse_ticker_file)
anlyFileBtn.place(relwidth=0.1, relheight=0.1, relx=0.5 + 0.14 + 0.1 + 0.01 + 0.01, rely=0.4)

# Called When Text Box is Clicked (Allows for placeholder text)
anlyTickerClicked = False
def anly_ticker_click(*args):
    global anlyTickerClicked
    if not anlyTickerClicked or anlyTickerInput.get() == "Ticker or Tickers (ticker1, ticker2)":
        anlyTickerInput.delete(0, 'end')
        anlyTickerClicked = True


# Called When Entry is Unfocused (Unfocus the text if nothing in it)
def anly_ticker_left(*args):
    if anlyTickerInput.get() == "":
        anlyTickerInput.insert(0, "Ticker or Tickers (ticker1, ticker2)")
        root.focus()


anlyTickerInput = tk.Entry(frame, justify="center", fg="#000000", bg="#BB86FC")
anlyTickerInput.insert(0, "Ticker or Tickers (ticker1, ticker2)")
anlyTickerInput.place(relwidth=0.5, relheight=0.1, relx=0.14, rely=0.52)
anlyTickerInput.bind("<Button-1>", anly_ticker_click)
anlyTickerInput.bind("<Leave>", anly_ticker_left)

anlyTickerBtn = tk.Button(frame, text=training_btn_txt_input if training else analyse_btn_txt_input, padx=15, pady=10, fg="#000000", bg="#CF6679", command=analyse_ticker_input)
anlyTickerBtn.place(relwidth=0.21, relheight=0.1, relx=0.5 + 0.14 + 0.01, rely=0.52)

# Start Application Window
root.mainloop()