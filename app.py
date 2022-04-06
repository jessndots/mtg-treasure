from flask import Flask, request, render_template, flash, redirect, session, jsonify, g, url_for
import requests
from flask_debugtoolbar import DebugToolbarExtension
from models import db, connect_db, User, Like, Card, Inventory, Wishlist, Deck, WishlistCard, InventoryCard, DeckCard
from forms import SignupForm, LoginForm, UpdateProfileForm
from sqlalchemy.exc import IntegrityError
from datetime import date, datetime

CURR_USER_KEY = "curr_user"

app = Flask(__name__)

app.config['SECRET_KEY'] = "oh-so-secret" 
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///mtg'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True

debug=DebugToolbarExtension(app)

connect_db(app)


@app.before_request
def add_user_to_g():
    """If logged in, add curr user to Flask global."""

    if CURR_USER_KEY in session:
        g.user = User.query.get(session[CURR_USER_KEY])

    else:
        g.user = None

def do_login(user):
    """Log in user."""

    session[CURR_USER_KEY] = user.id

def do_logout():
    """Logout user."""

    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]

@app.route("/")
def show_home():
    """Show popular decks maybe? nav bar, login/signup buttons, """

    # Get newest set 
    resp = requests.get("https://api.scryfall.com/sets")
    data = resp.json()
    sets = [set for set in data['data'] if set['set_type']=="expansion" and set['released_at'] <= str(date.today())] 
    # sets = [set for set in Set.all() if set.type == "expansion"]
    dates = [set['released_at'] for set in sets]
    new_set = sets[dates.index(max(dates))]

    # Get cards of rarity "Mythic" or "Rare"
    cards = requests.get(f'https://api.scryfall.com/cards/search?q=r>%3Dr+set%3D{new_set["code"]}').json()['data']

    return render_template("home.html", set=new_set, cards=cards)

@app.route("/signup", methods=["GET", "POST"])
def sign_up():
    """Show signup form, handle form on submit"""

    form = SignupForm()

    if form.validate_on_submit():

        user = User.signup(
            username=form.username.data,
            password=form.password.data,
            email=form.email.data
        )

        do_login(user)
        flash(f"Account was successfully created.", 'success')
        return redirect(url_for('show_home'))

    else:
        return render_template('users/signup.html', form=form)

@app.route("/login", methods=['GET', 'POST'])
def log_in():
    """Show login form, handle form on submit"""

    form = LoginForm()

    if form.validate_on_submit():
        user = User.authenticate(form.username.data, form.password.data)

        if user:
            do_login(user)
            return redirect(url_for('show_home'))
        
        flash("Invalid credentials.", 'danger')

    return render_template('users/login.html', form=form)
        
@app.route("/logout")
def log_out():
    """Handle logout of user"""
    do_logout()
    return redirect(url_for('log_in'))


#########################################################
# User routes

@app.route("/users/<int:user_id>")
def show_profile():
    """Show user profile"""

@app.route("/users/profile", methods=["GET", "POST"])
def update_profile():
    """Update profile for current user"""

@app.route("/users/delete", methods=["POST"])
def delete_user():
    """Delete user account"""

@app.route("/users/inventory")
def show_inventory():
    """show cards in current user's inventory"""
    if not g.user:
        flash('You must log in to view your inventory.', 'danger')
        return redirect(url_for('log_in'))

    inventory=[]
    if g.user.inventory:
        inventory = g.user.inventory[0]
    
    inventory_cards = inventory.inventory_cards

    return render_template('cards/inventory.html', inventory=inventory, cardlist=inventory_cards)
    
@app.route("/users/inventory/add/<card_id>", methods=['POST'])
def add_to_inventory(card_id):
    if not g.user:
        flash('You must be logged in to add a card to your inventory.', 'danger')
        return redirect(url_for('log_in'))

    try:
        new = Card(card_id)
        db.session.add(new)
        db.session.commit()
    except:
        db.session.rollback()
        exit

    if Card.query.get(card_id) in g.user.inventory[0].cardlist:
        q = InventoryCard.query.filter(InventoryCard.inventory_id==g.user.inventory[0].id).filter(InventoryCard.card_id==card_id).one_or_none()
        q.count += 1
        q.timestamp = datetime.utcnow()
        db.session.commit()
    else:
    
        add = InventoryCard(card_id, g.user.inventory[0].id)
        db.session.add(add)
        db.session.commit()

    if Card.query.get(card_id) in g.user.inventory[0].cardlist:
        flash(f'Successfully added to inventory.', 'success')
        

    else:
        flash(f'Something went wrong.', 'danger')

    return redirect(url_for('show_card', card_id=card_id)) 
        


@app.route("/users/wishlist")
def show_wishlist():
    """show cards in current user's wishlist"""
    if not g.user:
        flash('You must log in to view your wishlist.', 'danger')
        return redirect(url_for('log_in'))

    wishlist=[]
    if g.user.wishlist:
        wishlist = g.user.wishlist[0]
    
    wishlist_cards = wishlist.wishlist_cards

    return render_template('cards/wishlist.html', wishlist=wishlist, cardlist=wishlist_cards)

@app.route("/users/wishlist/add/<card_id>", methods=['POST'])
def add_to_wishlist(card_id):
    if not g.user:
        flash('You must be logged in to add a card to your wishlist.', 'danger')
        return redirect(url_for('log_in'))

    try:
        new = Card(card_id)
        db.session.add(new)
        db.session.commit()
    except:
        db.session.rollback()
        exit

    if Card.query.get(card_id) in g.user.wishlist[0].cardlist:
        q = WishlistCard.query.filter(WishlistCard.inventory_id==g.user.inventory[0].id).filter(WishlistCard.card_id==card_id).one_or_none()
        q.count += 1
        q.timestamp = datetime.utcnow()
        db.session.commit()
    else:
    
        add = WishlistCard(card_id, g.user.inventory[0].id)
        db.session.add(add)
        db.session.commit()

    if Card.query.get(card_id) in g.user.inventory[0].cardlist:
        flash(f'Successfully added to inventory.', 'success')
        

    else:
        flash(f'Something went wrong.', 'danger')

    return redirect(url_for('show_card', card_id=card_id)) 

@app.route("/users/likes")
def show_likes():
    """show current user's liked decks"""


###########################################################
# Collection routes

@app.route("/cards")
def list_cards():
    """show cards, 50 per page"""

@app.route("/cards/new")
def list_new_cards():
    """show cards from newest set"""

@app.route("/cards/<card_id>")
def show_card(card_id):
    """show card details"""
    exists = Card.query.filter_by(id=card_id).one_or_none()

    if exists:
        # rulings = requests.get(card['rulings_uri']).json()['data']
        card = Card.query.get(card_id)
        

    else:
        new = Card(card_id)
        db.session.add(new)
        db.session.commit()
        card = new


    # rulings = requests.get(card.load()['rulings_uri']).json()['data']
    api = card.load()

    return render_template('cards/card.html', card=card, api=api)

@app.route("/decks")
def list_decks():
    """show public decks, 50 per page"""

@app.route("/decks/<int:deck_id>")
def show_deck():
    """show deck details"""

@app.route("/decks/create", methods=['GET', 'POST'])
def create_deck():
    """show form for new deck and handle submission"""

# @app.route("/users/inventory/import")
# @app.route("/users/inventory/export")



