# Import main packages
from yfrake import client
import numpy as np
import pandas as pd
import datetime
from datetime import date
import os


@client.configure(limit=100, timeout=1)
def loop_tickers(tickers):

    # Loop through all the tickers and analyse them
    for tick in tickers:

        # Get Stock News if It Exists
        resp = client.get('quote_type', symbol=tick)
        resp.wait_for_result()

        # Check if the result was an error or not
        if not resp.error:
            print(resp.endpoint)
            print(resp.data)


# Function Called From Application to Analyse Tickers via File
def analyse_ticker_file(canvas, file_location):

    tickers = []  # The tickers retrieved from the file

    # Print the file location user has chosen
    print("File Location: " + file_location)

    # Set the comparison_stock_symbols
    tickers_df = pd.read_csv(file_location, delimiter=',')
    for col in tickers_df.columns:
        tickers.append(col)

    # Loop Through Tickers
    loop_tickers(tickers)


# Function Called From Application to Analyse Ticker(s) via User Input
def analyse_ticker_input(canvas, user_input):

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
    loop_tickers(tickers)


# This function analyses a stock given its ticker
def stockanalysis(tk):

    print("Analysing, " + tk)