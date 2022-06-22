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
def analyse_tickers(tickers):

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
        stockanalysis(ticker)


def analyse_ticker_file(file_location):

    tickers = []  # The tickers retrieved from the file

    # Print the file location user has chosen
    print("File Location: " + file_location)

    # Set the comparison_stock_symbols
    tickers_df = pd.read_csv(file_location, delimiter=',')
    for col in tickers_df.columns:
        tickers.append(col)

    # Loop Through Tickers
    analyse_tickers(tickers)


# Function Called From Application to Analyse Ticker(s) via User Input
def analyse_ticker_input(user_input):

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
    analyse_tickers(tickers)


# This function analyses a stock given its ticker
@client.session
def stockanalysis(ticker):

    positive_sentiment = []
    negative_sentiment = []
    neutral_sentiment = []

    # Let the user know analysis has begun
    print("Analysing, " + ticker)

    # --- OBTAIN 3 LATEST ARTICLES ---
    # Get Stock News if It Exists
    resp = client.get('news', symbol=ticker)
    resp.wait()

    # Check if the result was an error or not
    if not resp.error:

        # Go over all available articles
        num_of_articles = len(resp.data.get('list'))
        articles_list = resp.data.get('list')

        print(len(articles_list))

        for article in articles_list:

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
