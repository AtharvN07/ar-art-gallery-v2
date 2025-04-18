from flask import Flask, render_template, request, jsonify, redirect, url_for
import csv
import os
from datetime import datetime

app = Flask(__name__)

# Single CSV file for all orders
ORDERS_FILE = 'instances/orders.csv'

# Ensure instances directory exists
os.makedirs('instances', exist_ok=True)

# Initialize CSV file if it doesn't exist
def init_csv_file():
    if not os.path.exists(ORDERS_FILE):
        with open(ORDERS_FILE, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['order_id', 'customer_name', 'email', 'address', 'total_price', 'number_of_items', 'payment_status', 'order_date'])

# Initialize CSV file
init_csv_file()

# Helper functions for CSV operations
def get_next_id():
    with open(ORDERS_FILE, 'r') as f:
        reader = csv.DictReader(f)
        ids = [int(row['order_id']) for row in reader]
        return max(ids) + 1 if ids else 1

def append_to_csv(data):
    with open(ORDERS_FILE, 'a', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=data.keys())
        writer.writerow(data)

def read_csv():
    with open(ORDERS_FILE, 'r') as f:
        reader = csv.DictReader(f)
        return list(reader)

# Dummy data for paintings
paintings = [
    {
        "id": 1, 
        "name": "Sunset Bliss", 
        "category": "Nature", 
        "price": 200, 
        "image": "static/images/sunset.jpg",
        "description": "A breathtaking sunset painting capturing the golden hour over a serene landscape.",
        "collection_id": 1
    },
    {
        "id": 2, 
        "name": "City Lights", 
        "category": "Urban", 
        "price": 250, 
        "image": "static/images/city.jpg",
        "description": "An urban landscape painting showcasing the vibrant energy of city life at night.",
        "collection_id": 2
    },
    {
        "id": 3, 
        "name": "Ocean Breeze", 
        "category": "Nature", 
        "price": 300, 
        "image": "static/images/ocean.jpg",
        "description": "A calming seascape that brings the tranquility of the ocean into your space.",
        "collection_id": 1
    },
    {
        "id": 4,
        "name": "Mountain Majesty",
        "category": "Nature",
        "price": 350,
        "image": "static/images/mountain.jpg",
        "description": "A majestic mountain landscape capturing the grandeur of nature.",
        "collection_id": 1
    }
]

# Dummy data for collections
collections = [
    {
        "id": 1,
        "name": "Nature's Beauty",
        "description": "A collection of stunning landscape paintings capturing the essence of nature.",
        "image": "static/images/nature-collection.jpg"
    },
    {
        "id": 2,
        "name": "Urban Stories",
        "description": "Contemporary paintings depicting the dynamic energy of city life.",
        "image": "static/images/urban-collection.jpg"
    }
]

cart = []

@app.route('/')
def home():
    return render_template('index.html', paintings=paintings, collections=collections)

@app.route('/collections')
def collections_page():
    return render_template('collections.html', collections=collections)

@app.route('/collection/<int:collection_id>')
def collection(collection_id):
    collection_paintings = [p for p in paintings if p['collection_id'] == collection_id]
    collection = next((c for c in collections if c['id'] == collection_id), None)
    if not collection:
        return "Collection not found", 404
    return render_template('category.html', paintings=collection_paintings, collection=collection)

@app.route('/product/<int:painting_id>')
def product(painting_id):
    painting = next((p for p in paintings if p['id'] == painting_id), None)
    if not painting:
        return "Painting not found", 404
    return render_template('product.html', painting=painting)

@app.route('/category/<category>')
def category(category):
    filtered_paintings = [p for p in paintings if p['category'].lower() == category.lower()]
    return render_template('category.html', paintings=filtered_paintings)

@app.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    painting_id = request.json.get('id')
    painting = next((p for p in paintings if p['id'] == painting_id), None)
    if painting:
        cart.append(painting)
        return jsonify({"message": "Painting added to cart!", "cart": cart})
    return jsonify({"message": "Painting not found!"}), 404

@app.route('/cart')
def view_cart():
    return render_template('cart.html', cart=cart)

@app.route('/room_view/<int:painting_id>')
def room_view(painting_id):
    painting = next((p for p in paintings if p['id'] == painting_id), None)
    if not painting:
        return "Painting not found", 404
    return render_template('room_view.html', painting=painting)

@app.route('/remove_from_cart', methods=['POST'])
def remove_from_cart():
    painting_id = request.json.get('id')
    global cart
    cart = [item for item in cart if item['id'] != painting_id]
    return jsonify({"message": "Item removed from cart!", "cart": cart})

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/checkout')
def checkout():
    if not cart:
        return redirect(url_for('view_cart'))
    return render_template('checkout.html', cart=cart)

@app.route('/process_order', methods=['POST'])
def process_order():
    if not cart:
        return redirect(url_for('view_cart'))
    
    # Get form data
    name = request.form.get('name')
    email = request.form.get('email')
    address = request.form.get('address')
    city = request.form.get('city')
    state = request.form.get('state')
    zip_code = request.form.get('zip_code')
    
    # Test payment processing (simulated)
    card_number = request.form.get('card_number')
    expiry = request.form.get('expiry')
    cvv = request.form.get('cvv')
    
    # Simulate payment processing
    if not all([card_number, expiry, cvv]):
        return "Payment information missing", 400
    
    # Calculate order details
    total_price = sum(item['price'] for item in cart)
    number_of_items = len(cart)
    
    # Create order record
    order_data = {
        'order_id': get_next_id(),
        'customer_name': name,
        'email': email,
        'address': f"{address}, {city}, {state} {zip_code}",
        'total_price': total_price,
        'number_of_items': number_of_items,
        'payment_status': 'Completed',
        'order_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    
    # Save to CSV
    append_to_csv(order_data)
    
    # Clear the cart
    cart.clear()
    
    return redirect(url_for('order_confirmation', order_id=order_data['order_id']))

@app.route('/order_confirmation/<int:order_id>')
def order_confirmation(order_id):
    # Read order data
    orders = read_csv()
    order = next((o for o in orders if int(o['order_id']) == order_id), None)
    if not order:
        return "Order not found", 404
    
    return render_template('order_confirmation.html', order=order)

if __name__ == '__main__':
    app.run(debug=True)
