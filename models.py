from multiprocessing.dummy import Array
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects import postgresql
from flask_bcrypt import Bcrypt

db= SQLAlchemy()

bcrypt = Bcrypt()

def connect_db(app):
    db.app = app
    db.init_app(app)

class User(db.Model):
    """User model"""

    __tablename__ = 'users'

    id = db.Column(
        db.Integer, 
        primary_key=True
    )
    email = db.Column(
        db.String, 
        nullable=False, 
        unique=True
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

    sets = db.relationship('Set')
    likes = db.relationship(
        'Set', 
        secondary='likes'
    )

    def __repr__(self):
        return f"<User #{self.id}: {self.username}, {self.email}>"

    @classmethod
    def signup(cls, username, email, password):
        """Sign up user. Hash password. Add user to system."""

        hashed_pwd = bcrypt.generate_password_hash(password).decode('UTF-8')

        user = User(
            username=username,
            email=email,
            password=hashed_pwd,
        )

        db.session.add(user)
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


class Set(db.Model):
    """Card set model - includes user inventory, decks, wishlist"""

    __tablename__ = 'sets'

    id = db.Column(
        db.Integer, 
        primary_key=True
    )
    type = db.Column(
        db.String, 
        nullable=False
    )
    name = db.Column(
        db.String, 
        nullable=False
    )
    format = db.Column(
        db.Text, 
        nullable=True
    )
    description = db.Column(
        db.Text, 
        nullable=True
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
    # cards = db.Column(
    #     ,
    #     nullable = True
    # )
    # sideboard = db.Column(
    #     ,
    #     nullable = True
    # )

    # scratchpad = db.relationship('Card')
    user = db.relationship('User')
    likes = db.relationship(
        'User', 
        secondary='likes'
    )

    def __repr__(self):
        return f"<Set #{self.id}: {self.type}, created by {self.user.username}"

    @classmethod
    def create_built_deck(cls, name, format, description, user_id):
        """Create built deck for user
        
        Cards in these sets will increase the 'deck count' for that card."""

        deck = Set(
            type = 'Built Deck',
            name=name,
            format=format,
            description=description,
            user_id=user_id
        )

        db.session.add(deck)
        db.session.commit()
        return deck

    @classmethod
    def create_deck_idea(cls, name, format, description, user_id):
        """Create deck idea for user. 
        
        Cards in these sets will not increase the 'deck count' for that card."""

        deck = Set(
            type='Deck Idea',
            name=name,
            format=format,
            description=description,
            user_id=user_id
        )
        db.session.add(deck)
        db.session.commit()
        return deck


class Like(db.Model):
    """Mapping user likes to decks"""

    __tablename__ = 'likes'

    id = db.Column(
        db.Integer, 
        primary_key=True
    )
    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete='CASCADE')
    )
    set_id = db.Column(
        db.Integer,
        db.ForeignKey('sets.id', ondelete='CASCADE')
    )

