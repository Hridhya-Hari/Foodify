from flask import Flask, render_template, request, redirect, url_for
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
import time
from datetime import datetime, timedelta

app = Flask(__name__)


app.config["MONGO_URI"] = "mongodb://localhost:27017/Foodify"
mongo = PyMongo(app)


@app.route('/')
def menu():
    menu_items = list(mongo.db.menu.find())  # Fetch menu items from the MongoDB collection
    print(menu_items)
    return render_template('menu.html', menu_items=menu_items)


@app.route('/order', methods=['POST'])
def place_order():
    selected_items = request.form.getlist('items')
    order = {
        "items": selected_items,
        "status": "preparing",
        "order_datetime": datetime.utcnow()  # Store the current UTC time
    }
    order_id = mongo.db.orders.insert_one(order).inserted_id
    return redirect(url_for('order_status', order_id=order_id))


@app.route('/status/<order_id>')
def order_status(order_id):
    order = mongo.db.orders.find_one({"_id": ObjectId(order_id)})
    
    if order:
        order_time = order.get("order_datetime")
        if order_time:
            # Calculate the time difference
            time_difference = datetime.utcnow() - order_time
            # Check if more than 10 seconds have passed
            if time_difference > timedelta(seconds=10):
                status = "delivered"
                # Update the status in the database
                mongo.db.orders.update_one({"_id": ObjectId(order_id)}, {"$set": {"status": "delivered"}})
            else:
                status = "preparing"
        else:
            status = "unknown"
    else:
        status = "not found"

    return render_template('status.html', order=order, status=status, order_id=order_id)


if __name__ == '__main__':
    app.run(debug=True)