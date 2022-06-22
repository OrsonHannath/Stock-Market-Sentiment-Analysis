# Import main packages
from yfrake import client
import yfinance as yf
import numpy as np
import tkinter as tk
from tkinter import ttk
import pandas as pd
import datetime
from datetime import timedelta
from datetime import datetime
import os
import time
import nltk
import requests
from bs4 import BeautifulSoup
from selenium.webdriver.chrome.service import Service
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager


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


@client.session
def analyse_sentiment_tickers(tickers):

    positive_sent_final = []
    negative_sent_final = []
    neutral_sent_final = []

    # List of All Found Tickers
    true_tickers = []

    # Loop through all the tickers and analyse them
    for tick in tickers:

        # Check if the stock has data
        resp = client.get('quote_type', symbol=tick)
        resp.wait()

        # Check if the result was an error or not
        if not resp.error:
            if resp.data.get('shortName'):

                # Let User Know in Console that Ticker is Being Analysed
                print("Found " + resp.data['shortName'] + "(" + tick + ")")

                # Since Ticker does exist add it to the true_tickers list
                true_tickers.append(tick)

            else:
                print("Ticker \"" + tick + "\" Not Found")
                continue
        else:
            print("Ticker \"" + tick + "\" Not Found")
            continue

    # Loop through all the true tickers and analyse them
    for ticker in true_tickers:
        sentiments = stockanalysis_sentiment(ticker, client)
        positive_sent_final.append(sentiments[0])
        negative_sent_final.append(sentiments[1])
        neutral_sent_final.append(sentiments[2])

    # Save the analysis to file
    pos_sent_df = pd.DataFrame(positive_sent_final)
    neg_sent_df = pd.DataFrame(negative_sent_final)
    neu_sent_df = pd.DataFrame(neutral_sent_final)
    pos_sent_df.to_csv("training_data/positive_sentiment.csv")
    neg_sent_df.to_csv("training_data/negative_sentiment.csv")
    neu_sent_df.to_csv("training_data/neutral_sentiment.csv")

    # Let user know analysis has been completed
    print("Sentiment Analysis Complete")


def analyse_sentiment_ticker_file(file_location):

    tickers = []  # The tickers retrieved from the file

    # Print the file location user has chosen
    print("File Location: " + file_location)

    # Set the comparison_stock_symbols
    tickers_df = pd.read_csv(file_location, delimiter=',')
    for col in tickers_df.columns:
        tickers.append(col)

    # Loop Through Tickers
    analyse_sentiment_tickers(tickers)


# Function Called From Application to Analyse Ticker(s) via User Input
def analyse_sentiment_ticker_input(user_input):

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
    analyse_sentiment_tickers(tickers)


# This function analyses a stock given its ticker
def stockanalysis_sentiment(ticker, client):

    # URL dataframe
    urls = []
    publish_dates = []

    positive_sentiment = []
    negative_sentiment = []
    neutral_sentiment = []

    # Let the user know analysis has begun
    print("Analysing, " + ticker)

    # Obtain News Articles For the Stock
    service = Service(executable_path=ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service)

    # Create the url link for the stock then open it on the browser
    stock_yahoo_url = "https://au.finance.yahoo.com/quotes/" + str(ticker)
    driver.get(stock_yahoo_url)

    # Convert the page to BS4
    doc = BeautifulSoup(driver.page_source, "html.parser")

    # Check if there are any articles that are older than 7 days
    for tag in doc.find_all('li', {"class": "Mb(15px)"}):
        title_date = tag.find('span').text

        if len(title_date.split('•')) > 1:
            title_date = title_date.split('•')[1]

            url = ""
            page_urls = []
            for link in tag.findAll("a"):
                page_urls.append(link.get("href"))

            # Check if the articles are x amount of days old and make sure it is a yahoo finance article
            for i in range(14):
                if title_date == str(" " + str(7 + i) + " days ago") and page_urls[1][0:33] == "https://au.finance.yahoo.com/news":
                    urls.append(page_urls[1])
                    publish_dates.append((datetime.today() - timedelta(days=7+i)).strftime("%Y-%m-%d"))

    articles_d = {'url': urls, 'publish_date': publish_dates}
    articles_df = pd.DataFrame(data=articles_d)
    print(articles_df)

    # Check if the result was an error or not
    if not articles_df.empty:

        # Get Historical Price Data
        hist_price_data = yf.Ticker(ticker).history(period="3mo")
        hist = pd.DataFrame(hist_price_data)
        hist = hist.filter(['Open', 'Close'])

        for index, row in articles_df.iterrows():

            # --- Obtain Main Text of Article ---
            url = row['url']

            # Try to open the url
            response = requests.get(url)
            if not response.ok:
                print("Failed to load page {}".format(url))
            else:

                # Date String in Format YYYY-MM-DD
                publish_date = datetime.strptime(row['publish_date'], "%Y-%m-%d")
                most_current_date = hist.iloc[-1].name
                date_delta = most_current_date - publish_date

                # print(publish_date)
                # print(most_current_date)
                # print(date_delta)

                if date_delta.days >= 7:

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

                    # Get average price movement over the 7 days
                    avg_movement = 0
                    count = 0
                    for i in range(7):

                        date = publish_date + timedelta(days=i)

                        if date.strftime("%Y-%m-%d") in hist.index:
                            open = hist.loc[date.strftime("%Y-%m-%d")]['Open']
                            close = hist.loc[date.strftime("%Y-%m-%d")]['Close']

                            avg_movement += (abs(open-close)/open)
                            count += 1
                            print(avg_movement)

                    if count > 0:
                        avg_movement /= count
                        print("-- " + str(avg_movement) + " --")
                    else:
                        avg_movement = 0

                    # Rank the news article based on its average movement
                    if avg_movement >= 0.025:
                        positive_sentiment.append(news_content_string)
                    elif avg_movement <= -0.025:
                        negative_sentiment.append(news_content_string)
                    else:
                        neutral_sentiment.append(news_content_string)
                else:
                    print("Article Not Old Enough")

    else:
        print("No News Articles Found For: " + ticker)

    return positive_sentiment, negative_sentiment, neutral_sentiment
