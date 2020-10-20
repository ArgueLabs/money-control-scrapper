from os import path
import requests
from bs4 import BeautifulSoup
import re
import csv
import datetime


def get_price_and_change(url: str):

    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')
    price = soup.find(class_="inprice1").get_text()
    price = price.replace(",", "").replace("\n", "")

    change = soup.find(class_="pricupdn grn")
    is_neg = False
    if change:
        change = change.get_text()
    else:
        change = soup.find(class_="pricupdn red").get_text()
        is_neg = True
    change = change.split()
    change, change_pct = float(change[0].replace(
        ",", "")), re.findall(r'-?\d+\.?\d*', change[1])[0]
    if is_neg:
        change = -1 * change
    return price, change, change_pct


def write_to_csv(row, filepath: str):
    if path.exists(filepath):
        with open(filepath, 'a') as f:
            writer = csv.writer(f, delimiter=',', lineterminator='\n',)
            writer.writerow(row)
    else:
        with open(filepath, 'a') as f:
            writer = csv.writer(f, delimiter=',', lineterminator='\n',)
            writer.writerow(["Date", "Time", "Price", "Change", "Change Pct"])
            writer.writerow(row)


if __name__ == "__main__":

    nifty50_url = 'https://www.moneycontrol.com/indian-indices/bank-nifty-23.html'
    output_filepath = "./BankNifty_201020.csv"
    is_first = True
    previousTime = datetime.datetime.now()
    delta = datetime.timedelta(minutes=1)
    while True:
        currentTime = datetime.datetime.now()
        try:
            if currentTime > previousTime + delta or is_first:
                previousTime = currentTime
                is_first = False
                data = get_price_and_change(url=nifty50_url)
                date = currentTime.date().strftime('%y-%m-%d')
                time = f"{currentTime.hour}:{currentTime.minute}:{currentTime.second}"
                row = [date, time] + list(data)
                write_to_csv(row, output_filepath)
        except ConnectionResetError as e:
            pass
        except Exception as e:
            print(f"Error: {e}")
            break
