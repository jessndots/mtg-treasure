from builtins import classmethod, len
from multiprocessing.dummy import Array
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import CheckConstraint, func
from sqlalchemy.dialects import postgresql
from flask_bcrypt import Bcrypt
from datetime import datetime
import requests
from sqlalchemy.exc import IntegrityError
import json

db= SQLAlchemy()

bcrypt = Bcrypt()

def connect_db(app):
    db.app = app
    db.init_app(app)

symbology = requests.get('https://api.scryfall.com/symbology').json()['data']

class User(db.Model):
    """User model"""

    __tablename__ = 'users'

    id = db.Column(
        db.Integer, 
        primary_key=True,
        autoincrement=True
    )
    email = db.Column(
        db.String, 
        nullable=False,
    )
    username = db.Column(
        db.String, 
        nullable=False, 
        unique=True
    )
    password = db.Column(
        db.String, 
        nullable=False
    )
    date_created = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow()
    )

    decks = db.relationship('Deck')
    inventory = db.relationship('Inventory')
    wishlist = db.relationship('Wishlist')
    
    likes = db.relationship(
        'Deck', 
        secondary='likes'
    )


    def __repr__(self):
        return f"<User #{self.id}: {self.username}, {self.email}>"

    @classmethod
    def signup(cls, username, email, password):
        """Sign up user. Hash password. Add user to system with empty inventory and empty wishlist."""

        hashed_pwd = bcrypt.generate_password_hash(password).decode('UTF-8')

        user = User(
            username=username,
            email=email,
            password=hashed_pwd,
        )

        db.session.add(user)
        db.session.commit()

        inventory = Inventory(
            user_id=user.id,
        )

        wishlist = Wishlist(
            user_id=user.id,
        )

        db.session.add(inventory)
        db.session.add(wishlist)
        db.session.commit()

        return user


        

    @classmethod
    def authenticate(cls, username, password):
        """Find user with 'username' and 'password'. Returns that user object.
        
        If can't find user, returns False"""

        user = cls.query.filter_by(username=username).first()

        if user: 
            is_auth = bcrypt.check_password_hash(user.password, password)
            if is_auth:
                return user

        return False


class InventoryCard(db.Model):
    """Mapping cards to inventories"""
    __tablename__ = 'inventorycards'

    id = db.Column(
        db.Integer,
        primary_key=True,
        autoincrement=True
    )
    card_id = db.Column(
        # API id
        db.String,
        db.ForeignKey('cards.id', ondelete='cascade'),
        nullable=False
    )
    inventory_id = db.Column(
        db.Integer,
        db.ForeignKey('inventories.id', ondelete='CASCADE'),
        nullable=False
    )
    timestamp = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow()
    )
    foil = db.Column(
        db.Boolean,
        default=False
    )
    count = db.Column(
        db.Integer,
        default=1
    )

    inventory = db.relationship('Inventory')
    user = db.relationship('User', secondary='inventories')
    card = db.relationship('Card')

    def __init__(self, card_id, inventory_id):
        """Map card to inventory"""
        self.card_id = card_id
        self.inventory_id = inventory_id

class WishlistCard(db.Model):
    """Mapping cards to wishlists"""
    __tablename__ = 'wishlistcards'

    id = db.Column(
        db.Integer,
        primary_key=True,
        autoincrement=True
    )
    card_id = db.Column(
        db.String,
        db.ForeignKey('cards.id', ondelete='cascade'),
        nullable=False
    )
    wishlist_id = db.Column(
        db.Integer,
        db.ForeignKey('wishlists.id', ondelete='CASCADE'),
        nullable=False
    )
    timestamp = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow()
    )
    foil = db.Column(
        db.Boolean,
        default=False
    )
    count = db.Column(
        db.Integer,
        default=1
    )

    card = db.relationship('Card')
    wishlist = db.relationship('Wishlist')
    user = db.relationship('User', secondary='wishlists')

    def __init__(self, card_id, wishlist_id):
        """Map card to wishlist"""
        self.card_id = card_id
        self.wishlist_id = wishlist_id



class DeckCard(db.Model):
    """Mapping cards to decks"""
    __tablename__ = 'deckcards'

    id = db.Column(
        db.Integer,
        primary_key=True,
        autoincrement=True
    )
    card_id = db.Column(
        # API id
        db.String,
        db.ForeignKey('cards.id', ondelete='cascade'),
        nullable=False
    )
    deck_id = db.Column(
        db.Integer,
        db.ForeignKey('decks.id', ondelete='CASCADE'),
        nullable=False
    )
    timestamp = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow()
    )
    foil = db.Column(
        db.Boolean,
        default=False
    )
    count = db.Column(
        db.Integer, 
        default=1
    )
    board = db.Column(
        'board',
        db.String,
        db.CheckConstraint("board in ('main', 'sideboard', 'scratchpad')"),
        default = 'main'
    )

    user = db.relationship('User', secondary='decks')
    card = db.relationship('Card')
    deck = db.relationship('Deck')

    def __init__(self, card_id, deck_id):
        """Map card to inventory"""
        self.card_id = card_id
        self.deck_id = deck_id

class Deck(db.Model):
    """A set of cards put together to form a deck. Users can have as many decks as they want."""

    __tablename__ = 'decks'

    id = db.Column(
        db.Integer, 
        primary_key=True,
        autoincrement=True
    )

    name = db.Column(
        db.String(50), 
        nullable = False
    )

    description = db.Column(
        db.String,
        nullable = True
    )

    format = db.Column(
        'format',
        db.String,
        db.CheckConstraint("format in ('standard', 'pioneer', 'modern', 'legacy', 'vintage', 'commander', 'alchemy', 'brawl', 'historic', 'pauper', 'penny')"),
        nullable = True
    )

    type = db.Column(
        'type',
        db.String,
        db.CheckConstraint("type in ('built', 'idea')"),
        default = 'idea',
        nullable = False
    )

    date_created = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow()
    )
    notes = db.Column(
        db.Text,
        nullable=True
    )
    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete='CASCADE'),
        nullable = False
    )

    cardlist = db.relationship('Card', secondary='deckcards')
    user = db.relationship('User')
    

    def __init__(self, user_id, name):
        self.user_id = user_id
        self.name = name

    def __repr__(self):
        return f"<Deck #{self.id}, created by {self.user.username} on {self.date_created}>"

    likes = db.relationship(
        'User', 
        secondary='likes'
    )

    



class Like(db.Model):
    """Mapping user likes to decks"""

    __tablename__ = 'likes'

    id = db.Column(
        db.Integer, 
        primary_key=True,
        autoincrement=True
    )
    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete='CASCADE')
    )
    deck_id = db.Column(
        db.Integer,
        db.ForeignKey('decks.id', ondelete='CASCADE')
    )

    def __init__(self, user_id, deck_id):
        self.user_id = user_id
        self.deck_id = deck_id



class Card(db.Model):
    """Card details"""

    __tablename__ = 'cards'

    id = db.Column(
        db.String,
        primary_key=True
    )

    name = db.Column(
        db.String,
        nullable=False
    )

    set = db.Column(
        db.String,
        nullable =False
    )

    set_id = db.Column(
        db.String, 
        nullable=False
    )

    rarity = db.Column(
        db.String,
        nullable=False
    )

    type_line = db.Column(
        db.String,
        nullable=False
    )

    mana_cost = db.Column(
        db.String,
    )

    cmc = db.Column(
        db.Numeric
    )

    power = db.Column(
        db.Integer
    )

    toughness = db.Column(
        db.Integer
    )

    text = db.Column(
        db.String
    )

    artist = db.Column(
        db.String
    )

    image_uri = db.Column(
        db.String,
        nullable=False
    )

    loyalty = db.Column(
        db.Integer
    )

    rules_text = db.Column(
        db.String,
    )

    def __init__(self, id):
        """Map card to inventory"""
        self.id = id
        card = requests.get(f'https://api.scryfall.com/cards/{id}').json()

        self.name = card['name']
        self.set = card['set_name']
        self.set_id = card['set']
        self.rarity = card['rarity']
        self.type_line = card['type_line']

        mana_string = card['mana_cost']
        spaced = mana_string.replace("}", "} ")
        self.mana_cost = spaced


        self.cmc = card['cmc']
        if 'power' in card:
            self.power = card['power']
        if 'toughness' in card:
            self.toughness = card['toughness']
        if 'oracle_text' in card:
            self.text = card['oracle_text']
        self.artist = card['artist']
        self.image_uri = card['image_uris']['normal']
        if 'loyalty' in card:
            self.loyalty = card['loyalty']
        if 'oracle_text' in card:
            text_string = card['oracle_text']
            closing = text_string.replace("}", "} ")
            opening = closing.replace("{", " {")
            self.rules_text = opening

    def __repr__(self):
        return f"<Card #{self.id}: {self.name}>"

    def get_api_obj(self):
        """Get api obj for the card"""
        card = requests.get(f'https://api.scryfall.com/cards/{self.id}').json()

        return card
    
    def get_price(self):
        """Get current price for the card in USD"""
        card = requests.get(f'https://api.scryfall.com/cards/{self.id}').json()

        return card['prices']['usd']

    def get_price_foil(self):
        """Get current price for the card in USD"""
        card = json.dumps(requests.get(f'https://api.scryfall.com/cards/{self.id}').json())

        return card['prices']['usd_foil']


    def load(self):
        """Turns card response string to json object"""
        return requests.get(f'https://api.scryfall.com/cards/{self.id}').json()

    def inventory_count(self, inventory_id):
        """Returns number of this card name in logged in user's inventory"""

        # join the tables, sum up the count attribute of each card in inventory with the same card name
        join = InventoryCard.query.join(Card)
        q = join.with_entities(func.sum(InventoryCard.count)).filter(InventoryCard.inventory_id==inventory_id).filter(Card.name==self.name).group_by(Card.name).one_or_none()

        if(q == None):
            return 0
        else:
            return q[0]

    def wishlist_count(self, wishlist_id):
        """Returns number of this card name in logged in user's wishlist"""

        # join the tables, sum up the count attribute of each card in inventory with the same card name
        join = WishlistCard.query.join(Card)
        q = join.with_entities(func.sum(WishlistCard.count)).filter(WishlistCard.wishlist_id==wishlist_id).filter(Card.name==self.name).group_by(Card.name).one_or_none()

        if(q == None):
            return 0
        else:
            return q[0]

    def deck_count(self, user_id):
        """Returns number of this card in logged-in user's decks"""
        # find user
        user = User.query.get_or_404(user_id)

        join = DeckCard.query.join(Card).join(Deck)
        q = join.with_entities(func.sum(DeckCard.count)).filter(Card.name==self.name).filter(Deck.user_id == user_id).filter(DeckCard.board=='main').group_by(Card.name).one_or_none()

        if(q == None):
            return 0
        else:
            return q[0]

    def built_count(self, user_id):
        """Returns number of this card in logged-in user's built decks"""
        
        join = DeckCard.query.join(Card).join(Deck)

        q = join.with_entities(func.sum(DeckCard.count)).filter(Card.name==self.name).filter(Deck.type == 'built').filter(Deck.user_id==user_id).filter(DeckCard.board=='main').group_by(Card.name).one_or_none()

        if(q == None):
            return 0
        else:
            return q[0]

    def idea_count(self, user_id):
        """Returns number of this card in logged-in user's deck ideas"""
        
        join = DeckCard.query.join(Card).join(Deck)
        
        q = join.with_entities(func.sum(DeckCard.count)).filter(Card.name==self.name).filter(Deck.user_id==user_id).filter(Deck.type == 'idea').filter(DeckCard.board=='main').group_by(Card.name).one_or_none()

        if(q == None):
            return 0
        else:
            return q[0]


    def get_icon_uri(self, symbol):
        # extract proper svg-uri
        obj = [item for item in symbology if item['symbol']==symbol]
        if obj:
            uri = obj[0]['svg_uri']
        else:
            return False

        # return svg-uri
        return uri

    def get_set(self):
        return requests.get(f'https://api.scryfall.com/sets/{self.set_id}').json()

    def get_set_icon(self):
        return requests.get('http://api.mtgapi.com/v2/sets', params={'code': self.set_id})

    def get_alt_sets(self):
        cards = requests.get(f'https://api.scryfall.com/cards/search', params={'q': f'name:{self.name}', 'unique':'art'}).json()

        sets = [(card['set_name'], card['collector_number']) for card in cards['data']]
        return sets


    
class Inventory(db.Model):
    """A set of cards owned by the user. When a user is created, so is their inventory. A user can only have one Inventory set."""

    __tablename__ = 'inventories'

    id = db.Column(
        db.Integer, 
        primary_key=True,
        autoincrement=True
    )
    
    date_created = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow()
    )
    notes = db.Column(
        db.Text,
        nullable=True
    )
    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete='CASCADE'),
        nullable = False
    )

    user = db.relationship('User')
    inventory_cards = db.relationship('InventoryCard')
    cardlist = db.relationship('Card', secondary='inventorycards')
    

    def __init__(self, user_id):
        """Create inventory for user"""
        self.user_id = user_id


    def __repr__(self):
        return f"<Inventory #{self.id} of user {self.user.username}>"

    def count_cards(self):
        """Return number of cards in inventory."""
        q = InventoryCard.query.with_entities(func.sum(InventoryCard.count)).filter(InventoryCard.inventory_id==self.id).group_by(InventoryCard.inventory_id).one_or_none()

        if(q == None):
            return 0
        else:
            return q[0]
        
    
    def count_cards_distinct(self):
        """Return number of distinct cards in inventory."""
        return len(self.cardlist)


class Wishlist(db.Model):
    """A set of cards the user would like to own. When a user is created, so is their wishlist. A user can only have one Wishlist set."""

    __tablename__ = 'wishlists'

    id = db.Column(
        db.Integer, 
        primary_key=True,
        autoincrement=True
    )

    date_created = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow()
    )
    notes = db.Column(
        db.Text,
        nullable=True
    )
    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete='CASCADE'),
        nullable = False
    )

    user = db.relationship('User')
    wishlist_cards = db.relationship('WishlistCard')
    cardlist = db.relationship('Card', secondary='wishlistcards')
    

    def __init__(self, user_id):
        """Create Wishlist for user, optional notes."""
        self.user_id = user_id


    def __repr__(self):
        return f"<Wishlist #{self.id} of user {self.user.username}>"

    def count_cards(self):
        """Return number of cards in wishlist."""
        q = WishlistCard.query.with_entities(func.sum(WishlistCard.count)).filter(WishlistCard.wishlist_id==self.id).group_by(WishlistCard.wishlist_id).one_or_none()

        if(q == None):
            return 0
        else:
            return q[0]
        
    
    def count_cards_distinct(self):
        """Return number of distinct cards in wishlist."""
        count = len(self.cardlist)
        return count



