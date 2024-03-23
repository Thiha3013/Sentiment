import subprocess
import time
import os
import requests
import re
import sys
import yfinance
from bs4 import BeautifulSoup
import csv
import pandas as pd
from security import safe_command


def getNewsData(ticker):
    ticker = yfinance.Ticker(ticker)
    name = ticker.info["shortName"]
    headers = {
        "User-Agent":
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.54 Safari/537.36"
    }
    response = requests.get(
        f"https://www.google.com/search?q={name}s&gl=us&tbm=nws&num=100", headers=headers
    )
    soup = BeautifulSoup(response.content, "html.parser")
    news_results = []
 
    for el in soup.select("div.SoaBEf"):
        news_results.append(
            {
                "link": el.find("a")["href"],
                "title": el.select_one("div.MBeuO").get_text(),
                "snippet": el.select_one(".GI74Re").get_text(),
                "date": el.select_one(".LfVVr").get_text(),
                "source": el.select_one(".NUnG9d span").get_text()
            }
        )
  
    #print(json.dumps(news_results, indent=2))


    name = name.replace(" ", "_").lower()
    name = re.sub(r'\.(?!com\b)|[^\w\s.]', "", name)

    csv_name = f"{name}.csv"
    file_path = os.path.join('data', csv_name)

    with open(file_path, "w", newline="") as csv_file:
        fieldnames = ["link", "title", "snippet", "date", "source"]
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(news_results)
    print(f"Created file: {csv_name}")


    return str(file_path)
    


def open_in_r(strFile):
    try:
        safe_command.run(subprocess.run, ["Rscript", "analysis/sentiment.R", strFile], check=True)
    except subprocess.CalledProcessError:
        print("Error running the script")



def open_from_r(input_name):
    while not os.path.exists(input_name):
        time.sleep(1)

    if os.path.isfile(input_name):
        try:
            safe_command.run(subprocess.run, ["python3", "news_scraper/ai.py", input_name], check=True)
        except subprocess.CalledProcessError:
            print("Error running the script")
        

    else:
        print("Error: Output file not found")
    
    
def main(ticker):
    strFile = getNewsData(ticker)
    open_in_r(strFile)
    input_name = strFile.replace(".csv","_sentiment.csv")
    open_from_r(input_name)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        tikr = str(sys.argv[1])
        main(tikr)
    else:
        print("No ticker symbol provided")
