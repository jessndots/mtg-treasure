from sqlite3 import connect
from models import User, Deck, Inventory, Card, Wishlist, DeckCard, WishlistCard, WishlistCard, connect_db, db

from app import app

db.drop_all()
db.create_all()


user = User.signup('jdots', 'jndoty@live.com', 'password')

db.session.add(user)
db.session.commit()
