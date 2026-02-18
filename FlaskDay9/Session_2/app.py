from flask import Flask, render_template, request, jsonify
from database import init_db, db
from models import Product, Order, Post

app = Flask(__name__)
init_db(app)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/api/products")
def get_products():
    products = Product.query.all()
    return jsonify([
        {"id": p.id, "name": p.name, "price": p.price, "qty": p.qty}
        for p in products
    ])

@app.route("/api/products", methods=["POST"])
def add_product():
    data = request.get_json()

    if not data:
        return jsonify({"error": "Send JSON data"}), 400

    try:
        p = Product(name=data["name"], price=data["price"], qty=data["qty"])
        db.session.add(p)
        db.session.commit()
        return jsonify({"msg": "Product added"})
    except KeyError:
        return jsonify({"error": "Missing fields"}), 400



@app.route("/api/order", methods=["POST"])
def create_order():
    data = request.get_json()

    if not data:
        return jsonify({"error": "Send JSON data"}), 400

    product = Product.query.get(data["product_id"])

    if not product:
        return jsonify({"error": "Product not found"}), 404

    if product.qty < data["quantity"]:
        return jsonify({"error": "Not enough stock"}), 400

    product.qty -= data["quantity"]
    order = Order(product_id=data["product_id"], quantity=data["quantity"])
    db.session.add(order)
    db.session.commit()

    return jsonify({"msg": "Order placed"})

@app.route("/api/orders")
def get_orders():
    orders = Order.query.all()
    return jsonify([
        {
            "id": o.id,
            "product_id": o.product_id,
            "quantity": o.quantity
        }
        for o in orders
    ])

@app.route("/api/posts")
def get_posts():
    posts = Post.query.all()
    return jsonify([
        {"id": p.id, "title": p.title, "content": p.content}
        for p in posts
    ])

@app.route("/api/posts", methods=["POST"])
def add_post():
    data = request.get_json()

    if not data:
        return jsonify({"error": "Send JSON data"}), 400

    try:
        post = Post(title=data["title"], content=data["content"])
        db.session.add(post)
        db.session.commit()
        return jsonify({"msg": "Post created"})
    except KeyError:
        return jsonify({"error": "Missing fields"}), 400


if __name__ == "__main__":
    app.run(debug=True)
