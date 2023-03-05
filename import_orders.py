import requests
import pandas as pd
import keys
from IPython.display import display

api_key = keys.api_key
api_password = keys.api_password
access_token = keys.access_token
store_name = "tusk-toothpowder"
headers = {'X-Shopify-Access-Token': access_token}

# TESTS 
def getShopInfo(): 
    url = f"https://{api_key}:{api_password}@{store_name}.myshopify.com/admin/shop.json"
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        shop_info = response.json()
        print(shop_info)
    else:
        raise Exception("Failed to retrieve shop information from Shopify API.")

def getProductNames():
    url = f"https://{api_key}:{api_password}@{store_name}.myshopify.com/admin/products.json"
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        products = response.json()
        product_names = [product['title'] for product in products['products']]
        print(product_names)
    else:
        raise Exception("Failed to retrieve products from Shopify API.")

# Returns a DataFrame of 50 most recent orders
def getOrders():
    url = f"https://{api_key}:{api_password}@{store_name}.myshopify.com/admin/orders.json?status=any"
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        orders = response.json()["orders"]
        for order in orders:
            order["shipping_address"] = order["shipping_address"] if order["shipping_address"] else {}
        df = pd.DataFrame(orders)
        return df
    else:
        raise Exception("Failed to retrieve fulfilled orders from Shopify API")


# Returns a DataFrame of all orders (by making multiple API calls)
def getAllOrders():
    orders = []
    url = f"https://{api_key}:{api_password}@{store_name}.myshopify.com/admin/orders.json?status=any"
    while url:
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            raise Exception("Failed to retrieve orders from Shopify API")
        response_json = response.json()
        orders.extend(response_json["orders"])
        url = response.links.get("next", {}).get("url")

        for order in response_json['orders']:
            print(order)
            for item in order['line_items']:
                print(item['name'])
                print(item['quantity'])
    return orders

# Adds to the DataFrame a tidied version of the line_items column, called items
def createItemsCol(dataframe):
    items = []
    packages = []
    for order in dataframe["line_items"]:
        refill_count = 0
        tin_count = 0
        well_formatted_order = []
        for item in order:
            well_formatted_item = []
            well_formatted_item.append(item["quantity"])
            well_formatted_item.append(item["title"])
            if "refill" in item["title"].lower():
                refill_count += item["quantity"]
            if "tin" in item["title"].lower():
                tin_count += item["quantity"]
            well_formatted_order.append(well_formatted_item)
        items.append(well_formatted_order)
        packages.append(f"Refill: {refill_count}, Tin: {tin_count}")
    dataframe = dataframe.assign(items=items, packages=packages)
    return dataframe

# Keeps the columns listed below and drops everything else
def dropUnusedCols(dataframe):
    keep_cols = ["order_number",
                "created_at",
                "items",
                "packages",
                "subtotal_price",
                "total_discounts",
                "total_line_items_price",
                "total_tax",
                "total_price",
                "currency",
                "discount_codes",
                "financial_status",
                "fulfillment_status",
                "gateway",
                "payment_gateway_names",
                "referring_site",
                "tags",
                "refunds",
                "email",
                "customer",
                "shipping_address"]
    dataframe = dataframe[keep_cols]
    return dataframe

df = getOrders()
df = createItemsCol(df)
df = dropUnusedCols(df)
df.to_csv('orders.csv', index=False)