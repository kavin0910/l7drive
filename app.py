from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SECRET_KEY'] = 'your_secret_key'  # Required for session management
db = SQLAlchemy(app)

# Models
class Offering(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    flavor = db.Column(db.String(100), nullable=False)
    is_seasonal = db.Column(db.Boolean, default=False)

class Inventory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ingredient = db.Column(db.String(100), nullable=False)
    quantity = db.Column(db.Integer, default=0)

class Suggestion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    allergen = db.Column(db.String(100), nullable=True)

# Initialize cart in session
@app.before_request
def init_cart():
    if 'cart' not in session:
        session['cart'] = []

# Routes
@app.route('/')
def home():
    offerings = Offering.query.all()
    return render_template('home.html', offerings=offerings)

@app.route('/manage', methods=['GET', 'POST'])
def manage():
    if request.method == 'POST':
        if 'add_flavor' in request.form:
            flavor = request.form['flavor']
            is_seasonal = 'seasonal' in request.form
            new_offering = Offering(flavor=flavor, is_seasonal=is_seasonal)
            db.session.add(new_offering)
            db.session.commit()
        elif 'add_ingredient' in request.form:
            ingredient = request.form['ingredient']
            quantity = int(request.form['quantity'])
            new_inventory = Inventory(ingredient=ingredient, quantity=quantity)
            db.session.add(new_inventory)
            db.session.commit()
    inventory = Inventory.query.all()
    return render_template('manage.html', inventory=inventory)

@app.route('/suggest', methods=['POST'])
def suggest():
    name = request.form['name']
    allergen = request.form['allergen']
    suggestion = Suggestion(name=name, allergen=allergen)
    db.session.add(suggestion)
    db.session.commit()
    return redirect(url_for('home'))

@app.route('/add_to_cart/<int:offering_id>')
def add_to_cart(offering_id):
    offering = Offering.query.get_or_404(offering_id)
    cart = session['cart']
    cart.append({'id': offering.id, 'flavor': offering.flavor})
    session['cart'] = cart
    return redirect(url_for('cart'))

@app.route('/remove_from_cart/<int:offering_id>')
def remove_from_cart(offering_id):
    cart = session['cart']
    cart = [item for item in cart if item['id'] != offering_id]
    session['cart'] = cart
    return redirect(url_for('cart'))

@app.route('/cart')
def cart():
    return render_template('cart.html', cart=session['cart'])

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
