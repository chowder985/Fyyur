from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func

db = SQLAlchemy()

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#


class Venue(db.Model):
    __tablename__ = 'venues'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    genres = db.Column(db.ARRAY(db.String), nullable=False)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    website = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean, nullable=False, default=False)
    seeking_description = db.Column(db.String())
    shows = db.relationship('Show', backref='venue',
                            lazy=True, cascade="all, delete-orphan")
    past_shows_count = db.Column(
        db.Integer, nullable=False, default=0)
    upcoming_shows_count = db.Column(
        db.Integer, nullable=False, default=0)

    def __repr__(self):
        return f'<Venue ID: {self.id}, name: {self.name}>'


class Artist(db.Model):
    __tablename__ = 'artists'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    genres = db.Column(db.ARRAY(db.String), nullable=False)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    website = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean, nullable=False, default=False)
    seeking_description = db.Column(db.String())
    shows = db.relationship('Show', backref='artist',
                            lazy=True, cascade="all, delete-orphan")
    past_shows_count = db.Column(
        db.Integer, nullable=False, default=0)
    upcoming_shows_count = db.Column(
        db.Integer, nullable=False, default=0)

    def __repr__(self):
        return f'<Artist ID: {self.id}, name: {self.name}>'


class Show(db.Model):
    __tablename__ = 'shows'

    id = db.Column(db.Integer, primary_key=True)
    venue_id = db.Column(db.Integer, db.ForeignKey(
        'venues.id'), nullable=False)
    venue_name = db.Column(db.String(), nullable=False)
    venue_image_link = db.Column(db.String(500))
    artist_id = db.Column(db.Integer, db.ForeignKey(
        'artists.id'), nullable=False)
    artist_name = db.Column(db.String(), nullable=False)
    artist_image_link = db.Column(db.String(500))
    start_time = db.Column(db.DateTime(timezone=True),
                           nullable=False, server_default=func.now())

    def __repr__(self):
        return f'<Show ID: {self.id}, venue_id: {self.venue_id}, artist_id: {self.artist_id}>'
