# Import main packages
from yfrake import client
import numpy as np
import tkinter as tk
from tkinter import ttk
import pandas as pd
import datetime
from datetime import date
import os
import time
import nltk
import requests
from bs4 import BeautifulSoup


@client.session
def loop_tickers(tickers, frame, canvas, root):

    # List of All Found Tickers
    true_tickers = []

    # Amount of Found Tickers
    true_tickers_amount = 0

    # Made it this far so wipe the frame
    for widget in frame.winfo_children():
        widget.destroy()

    # Set up scrollable window
    scrollbar = ttk.Scrollbar(frame, orient="vertical", command=canvas.yview)
    scrollable_frame = tk.Frame(canvas, bg="#121212")

    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(
            scrollregion=canvas.bbox("all")
        )
    )

    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set, bg="#121212")

    # Loop through all the tickers and analyse them
    for tick in tickers:

        # Get Stock News if It Exists
        resp = client.get('quote_type', symbol=tick)
        resp.wait()

        # Check if the result was an error or not
        if not resp.error:
            if resp.data.get('shortName'):
                # Let User Know in Console that Ticker is Being Analysed
                print("Found " + resp.data['shortName'] + "(" + tick + ")")

                # Since Ticker does exist add it to the true_tickers list
                true_tickers.append(tick)
                true_tickers_amount += 1

                # Add a place on the frame for this ticker
                tk.Label(scrollable_frame, text=resp.data['shortName'], padx=10, pady=10, bg="#BB86FC", fg="#000000", width=80).grid(column=0, row=(true_tickers_amount-1) * 4, padx=5, pady=5, sticky=tk.W)
                tk.Label(scrollable_frame, text="--%", padx=10, pady=10, bg="#BB86FC", fg="#000000",width=11).grid(column=1, row=(true_tickers_amount-1) * 4, padx=5, pady=5, sticky=tk.E)
            else:
                print("Ticker \"" + tick + "\" Not Found")
                continue
        else:
            print("Ticker \"" + tick + "\" Not Found")
            continue

    frame.pack()
    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    # Wait x seconds so that screen is drawn then analysed
    frame.after(2000, update_ticker_application, true_tickers, scrollable_frame)


# Function that loops through all confimred stock tickers and updates the application
def update_ticker_application(true_tickers, scrollable_frame):

    # Initiate the analysis
    stockanalysis(true_tickers, 0, scrollable_frame)


# Function Called From Application to Analyse Tickers via File
def analyse_ticker_file(frame, file_location, canvas, root):

    tickers = []  # The tickers retrieved from the file

    # Print the file location user has chosen
    print("File Location: " + file_location)

    # Set the comparison_stock_symbols
    tickers_df = pd.read_csv(file_location, delimiter=',')
    for col in tickers_df.columns:
        tickers.append(col)

    # Loop Through Tickers
    loop_tickers(tickers, frame, canvas, root)


# Function Called From Application to Analyse Ticker(s) via User Input
def analyse_ticker_input(frame, user_input, canvas, root):

    # The structured user input string (spaces removed)
    ui = ""

    # Print the tickers that are going to be analysed
    print("User Input: " + user_input)

    # Create an array of all tickers' user has input
    for char in user_input:
        if char != " ":
            ui = ui + char

    # Split the structured user input into separate tickers
    tickers = ui.split(",")

    # Loop Through Tickers
    loop_tickers(tickers, frame, canvas, root)


# This function analyses a stock given its ticker
@client.session
def stockanalysis(tickers, tick_pos, scrollable_frame):

    # Sentiment Analysis Percent
    sent_anal_perc = 0

    # Let the user know analysis has begun
    print("Analysing, " + tickers[tick_pos])

    # --- OBTAIN 3 LATEST ARTICLES ---
    # Get Stock News if It Exists
    resp = client.get('news', symbol=tickers[tick_pos])
    resp.wait()

    # Check if the result was an error or not
    if not resp.error:
        # Get 3 Working ARTICLES
        num_of_articles = len(resp.data.get('list'))
        articles_list = resp.data.get('list')

        count = 0
        for article in articles_list:
            if count < 3:

                # --- Obtain Main Text of Article ---
                url = article['link']

                # Try to open the url
                response = requests.get(url)
                if not response.ok:
                    print("Failed to load page {}".format(url))
                else:
                    # Convert webpage to a BeautifulSoup Object
                    page_content = response.text
                    doc = BeautifulSoup(page_content, "html.parser")

                    # Find all the <p> elements on the page
                    news_content_unfiltered = doc.find_all("p")

                    # Filter out the body paragraphs of the page
                    news_content_string = ""
                    for content in news_content_unfiltered:
                        news_content_string += content.text
                    print(news_content_string)

                    # Add the individual articles to application
                    tk.Label(scrollable_frame, text=article['title'], padx=10, pady=10, bg="#CF6679", fg="#000000",
                             width=80, height=1).grid(column=0, row=(tick_pos * 4) + count + 1, sticky=tk.W, padx=5)
                    tk.Label(scrollable_frame, text="--%", padx=10, pady=10, bg="#CF6679", fg="#000000", width=11, height=1).grid(
                        column=1, row=(tick_pos * 4) + count + 1, sticky=tk.E, padx=5)
                    count += 1

    # Let the user know the analysis is complete
    tk.Label(scrollable_frame, text=str(str(sent_anal_perc) + "%"), padx=10, pady=10, bg="#BB86FC", fg="#000000", width=11).grid(column=1, row=(tick_pos) * 4, padx=5, pady=5, sticky=tk.E)
    print("Analysis Complete , " + tickers[tick_pos] + ". (" + str(sent_anal_perc) + "%)")

    # Check if there is another ticker to analyse and if there is analyse it
    tick_pos += 1
    if tick_pos < len(tickers):
        scrollable_frame.after(50, stockanalysis, tickers, tick_pos, scrollable_frame)
    else:
        print("--- Analysis Complete ---")
