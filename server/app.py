#!/usr/bin/env python3
from models import db, Restaurant, RestaurantPizza, Pizza
from flask_migrate import Migrate
from flask import Flask, request, make_response, jsonify
from flask_restful import Api, Resource
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get("DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

api = Api(app)


@app.route("/restaurants", methods = ['GET'])
def index():
    restaurants = Restaurant.query.all()
    return jsonify([{"address":restaurant.address, "id": restaurant.id, "name":restaurant.name}for restaurant in restaurants])
@app.route("/restaurants/<int:id>", methods = ["GET"])
def get_by_id(id):
    restaurant = db.session.get(Restaurant,id)
    if  restaurant is None:
        return jsonify({'error':'Restaurant not found'}),404
    restaurant_data = {
        "address": restaurant.address,
        "id": restaurant.id,
        "name": restaurant.name,
        "restaurant_pizzas": [
            {
                "id": acepiz.id,
                "pizza": {
                    "id": acepiz.pizza.id,
                    "ingredients": acepiz.pizza.ingredients,
                    "name": acepiz.pizza.name
                },
                "pizza_id": acepiz.pizza_id,
                "price": acepiz.price,
                "restaurant_id": acepiz.restaurant_id
            }
            for acepiz in restaurant.restaurant_pizzas
        ]
    }

    return jsonify(restaurant_data)
@app.route("/restaurants/<int:id>", methods = ["DELETE"])
def delete(id):
    restaurant = db.session.get(Restaurant,id)
    if restaurant is None:
        return jsonify({ "error": "Restaurant not found"}), 404
    db.session.delete(restaurant)
    db.session.commit()
    return jsonify({"message": "Restaurant deleted successfully"}), 204
@app.route("/pizzas", methods = ["GET"])
def pizza():
    pizzas = Pizza.query.all()
    return jsonify ([{"id":pizza.id, "ingredients":pizza.ingredients,"name":pizza.name}for pizza in pizzas])

@app.route("/restaurant_pizzas", methods=["POST"])
def add():
    data = request.get_json()
    
   
    restaurant = db.session.get(Restaurant, data.get('restaurant_id'))
    pizza = db.session.get(Pizza, data.get('pizza_id'))
    if not restaurant or not pizza:
        return jsonify({"errors": ["validation errors"]}), 400

    try:
        new_restaurant_pizza = RestaurantPizza(price=data['price'], pizza_id=data['pizza_id'], restaurant_id=data['restaurant_id'])
        db.session.add(new_restaurant_pizza)
        db.session.commit()

        response_data = {
            "id": new_restaurant_pizza.id,
            "pizza": {
                "id": pizza.id,
                "ingredients": pizza.ingredients,
                "name": pizza.name
            },
            "pizza_id": pizza.id,
            "price": new_restaurant_pizza.price,
            "restaurant": {
                "address": restaurant.address,
                "id": restaurant.id,
                "name": restaurant.name
            },
            "restaurant_id": restaurant.id
        }

        return jsonify(response_data), 201

    except ValueError as e:
        return jsonify({"errors": ["validation errors"]}), 400



if __name__ == "__main__":
    app.run(port=5555, debug=True)