from flask import Flask, request, render_template, flash, redirect, session, jsonify, g, url_for
from flask_debugtoolbar import DebugToolbarExtension
from models import db, connect_db, User, Set
from forms import SignupForm, LoginForm, UpdateProfileForm
from sqlalchemy.exc import IntegrityError
from mtgsdk import Card, Set, Type, Supertype, Subtype
from datetime import date

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
    sets = [set for set in Set.all() if set.type == "expansion"]
    dates = [set.release_date for set in sets if set.release_date <= str(date.today())]
    new_set = sets[dates.index(max(dates))]

    # Get cards of rarity "Mythic" or "Rare"
    mythics = [card for card in Card.where(set=new_set.code).where(rarity="Mythic|Rare").where(page=1).where(pageSize=500).all()]  

    return render_template("home.html", set=new_set, mythics=mythics)

@app.route("/signup", methods=["GET", "POST"])
def sign_up():
    """Show signup form, handle form on submit"""

    form = SignupForm()

    if form.validate_on_submit():
        try:
            user = User.signup(
                username=form.username.data,
                password=form.password.data,
                email=form.email.data
            )
            db.session.commit()
        except IntegrityError:
            flash("That username is already taken.", 'danger')
            return render_template('users/signup.html, form=form')

        do_login(user)
        flash(f"Account was successfully created.")
        return redirect(url_for('sign-up'))

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

@app.route("/users/wishlist")
def show_wishlist():
    """show cards in current user's wishlist"""

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

@app.route("/cards/<int:card_id>")
def show_card():
    """show card details"""

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



