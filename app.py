from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
import os
from werkzeug.utils import secure_filename

# Initialize Flask app
app = Flask(__name__)
app.secret_key = "secret123"

# Database setup
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///grocery.db'   # ✅ keep only one DB
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Upload folder setup
UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


# User Model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(50), nullable=False)


# Product Model
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    image = db.Column(db.String(200), nullable=True)  # store image filename


# Create DB tables before first request
@app.before_request
def create_tables():
    db.create_all()


# Admin route to add and list products
@app.route('/admin', methods=["GET", "POST"])
def admin():
    if request.method == "POST":
        name = request.form["name"]
        price = float(request.form["price"])
        quantity = int(request.form["quantity"])

        # Handle image upload
        image_file = request.files.get("image")
        image_filename = None
        if image_file and image_file.filename != "":
            filename = secure_filename(image_file.filename)
            os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            image_file.save(image_path)
            image_filename = filename

        # Save product to DB
        new_product = Product(
            name=name,
            price=price,
            quantity=quantity,
            image=image_filename
        )
        db.session.add(new_product)
        db.session.commit()

        return redirect(url_for('admin'))

    products = Product.query.all()
    return render_template("admin.html", products=products)


# Home page
@app.route('/')
def index():
    return render_template("index.html")


# User Registration
@app.route('/register', methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        # Check if user exists
        if User.query.filter_by(username=username).first():
            return "User already exists"

        # Save user
        new_user = User(username=username, password=password)
        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for('login'))

    return render_template("register.html")


# User Login
@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        # Validate user
        user = User.query.filter_by(username=username, password=password).first()
        if user:
            session["user"] = username
            return redirect(url_for("products"))
        else:
            return "Invalid credentials"

    return render_template("login.html")


# Logout
@app.route('/logout')
def logout():
    session.pop("user", None)
    return redirect(url_for('index'))


# Show products
@app.route('/products')
def products():
    all_products = Product.query.all()
    return render_template("products.html", products=all_products)


# Shopping Cart
@app.route('/cart', methods=["GET", "POST"])
def cart():
    if "cart" not in session:
        session["cart"] = []

    if request.method == "POST":
        product_id = int(request.form["product_id"])
        session["cart"].append(product_id)
        session.modified = True

    cart_items = Product.query.filter(Product.id.in_(session["cart"])).all()
    return render_template("cart.html", cart=cart_items)


@app.route('/placeorder', methods=["GET", "POST"])
def placeorder():
    return render_template("placeorder.html")



if __name__ == "__main__": 
    with app.app_context():
         db.create_all()
         app.run(debug=True)
