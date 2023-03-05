from blabel import LabelWriter
import pandas as pd
import csv

# Read the orders.csv file into a DataFrame
df = pd.read_csv('orders.csv')

# Extract the data from the shipping_address column
shipping_addresses = []
for address in df['shipping_address']:
    shipping_addresses.append(eval(address)) # convert string to dictionary using eval()

for i in shipping_addresses:
    i['first_name'] = i['first_name'].upper()
    i['last_name'] = i['last_name'].upper()
    if i['address2'] == None:
        i['address2'] = ""

label_writer = LabelWriter("item_template.html", default_stylesheets=("style.css",))

label_writer.write_labels(shipping_addresses, target="qrcode_and_date.pdf")