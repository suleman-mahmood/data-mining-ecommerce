import requests
import bs4
import time
import csv
import random

stock = []
new_file_rows = []


def get_stock_from_url(url):

    res = requests.get(url)

    try:
        # checks if there was no error fetching the website
        res.raise_for_status()
    except:
        return -1

    data = bs4.BeautifulSoup(res.text, 'html.parser')
    elems = data.select("script")

    # gets the script tag with "stock" string
    script_tag_str = ""

    for e in elems:
        if "\"stock\"" in str(e):
            script_tag_str = str(e)

    index_of_stock = script_tag_str.index("\"stock\"")
    index_of_comma = script_tag_str.index(",", index_of_stock)

    current_stock = int(script_tag_str[index_of_stock + 8:index_of_comma])

    # sleeps for seconds
    time.sleep(random.randint(2, 5))
    print("stock:", current_stock)
    return current_stock


data_file = open("data.csv")
file_reader = csv.reader(data_file)
file_data = list(file_reader)

for row in file_data:
    # backup your data
    new_file_rows.append(row)

    # the first column has all the links
    url = row[0]

    if "http" in url:
        # bug fixing / removing junk values before http
        url = url[url.index("h"):]
        current_stock = get_stock_from_url(url)
        stock.append(current_stock)

data_file.close()

# Now write data back to the file
output_file = open("data.csv", "w", newline="")
output_writer = csv.writer(output_file)

i = 0

for row in new_file_rows:
    url = row[0]

    if "http" in url:
        row.append(stock[i])
        i += 1

    output_writer.writerow(row)

output_file.close()
