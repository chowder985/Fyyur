#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#
from typing import final
from forms import *
from flask_wtf import FlaskForm
from logging import Formatter, FileHandler
import logging
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
from flask_moment import Moment
from flask import Flask, render_template, request, Response, flash, redirect, url_for, jsonify, abort
from flask_migrate import Migrate
from datetime import datetime
import babel
import dateutil.parser
import json
import collections
import collections.abc
import sys
collections.Callable = collections.abc.Callable
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)

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


#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#


def format_datetime(value, format='medium'):
    date = dateutil.parser.parse(value)
    if format == 'full':
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == 'medium':
        format = "EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, format, locale='en')


app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#


@app.route('/')
def index():
    return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
    # TODO: replace with real venues data.
    #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue.
    data = []
    appended = False
    try:
        venues = Venue.query.order_by(Venue.state).all()
        if venues:
            for venue in venues:
                venue.upcoming_shows_count = Show.query.filter(
                    venue.id == Show.venue_id, Show.start_time > datetime.now()).count()
                for i in range(len(data)):
                    if data and data[i]['city'] == venue.city:
                        m_venue = {
                            "id": venue.id,
                            "name": venue.name,
                            "num_upcoming_shows": venue.upcoming_shows_count
                        }
                        data[i]['venues'].append(m_venue)
                        appended = True
                if not (data and appended):
                    f_venue = {
                        "city": venue.city,
                        "state": venue.state,
                        "venues": [{
                            "id": venue.id,
                            "name": venue.name,
                            "num_upcoming_shows": venue.upcoming_shows_count
                        }]
                    }
                    data.append(f_venue)
                appended = False
        db.session.commit()
    except:
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()

    return render_template('pages/venues.html', areas=data)


@app.route('/venues/search', methods=['POST'])
def search_venues():
    # TODO: implement search on venues with partial string search. Ensure it is case-insensitive.
    # seach for Hop should return "The Musical Hop".
    # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
    response = {
        "count": 0,
        "data": []
    }

    try:
        searched_venues = Venue.query.filter(Venue.name.ilike(
            f"%{request.form.get('search_term', '')}%")).with_entities(Venue.id, Venue.name, Venue.upcoming_shows_count).all()
        for searched_venue in searched_venues:
            response['data'].append(searched_venue)
        response['count'] = len(searched_venues)
    except:
        print(sys.exc_info())

    return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    # shows the venue page with the given venue_id
    # TODO: replace with real venue data from the venues table, using venue_id
    data = {}
    try:
        venue = Venue.query.filter_by(id=venue_id).first()
        past_shows_query = Show.query.filter(
            venue.id == Show.venue_id, Show.start_time <= datetime.now()).all()
        past_shows = []
        for past_show in past_shows_query:
            past_shows.append({
                "artist_id": past_show.artist_id,
                "artist_name": past_show.artist_name,
                "artist_image_link": past_show.artist_image_link,
                "start_time": str(past_show.start_time)
            })
        upcoming_shows_query = Show.query.filter(
            venue.id == Show.venue_id, Show.start_time > datetime.now()).all()
        upcoming_shows = []
        for upcoming_show in upcoming_shows_query:
            upcoming_shows.append({
                "artist_id": upcoming_show.artist_id,
                "artist_name": upcoming_show.artist_name,
                "artist_image_link": upcoming_show.artist_image_link,
                "start_time": str(upcoming_show.start_time)
            })

        venue.past_shows_count = len(past_shows)
        venue.upcoming_shows_count = len(upcoming_shows)
        db.session.commit()

        data = {
            "id": venue.id,
            "name": venue.name,
            "genres": venue.genres,
            "address": venue.address,
            "city": venue.city,
            "state": venue.state,
            "phone": venue.phone,
            "website": venue.website,
            "facebook_link": venue.facebook_link,
            "seeking_talent": venue.seeking_talent,
            "seeking_description": venue.seeking_description,
            "image_link": venue.image_link,
            "past_shows": past_shows,
            "upcoming_shows": upcoming_shows,
            "past_shows_count": venue.past_shows_count,
            "upcoming_shows_count": venue.upcoming_shows_count
        }
    except:
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()

    return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------


@app.route('/venues/create', methods=['GET'])
def create_venue_form():
    form = VenueForm()
    return render_template('forms/new_venue.html', form=form)


@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    # TODO: insert form data as a new Venue record in the db, instead
    # TODO: modify data to be the data object returned from db insertion
    form = VenueForm(request.form)
    try:
        # on successful db insert, flash success
        venue = Venue(name=form.name.data, genres=form.genres.data, city=form.city.data, state=form.state.data, address=form.address.data, phone=form.phone.data, image_link=form.image_link.data,
                      facebook_link=form.facebook_link.data, website=form.website_link.data, seeking_talent=form.seeking_talent.data, seeking_description=form.seeking_description.data)
        db.session.add(venue)
        db.session.commit()
        flash('Venue ' + venue.name + ' was successfully listed!')
    except:
        db.session.rollback()
        print(sys.exc_info())
        flash('An error occurred. Venue ' +
              form.name.data + ' could not be listed.')
    finally:
        db.session.close()
    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    return redirect(url_for('index'))


@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
    # TODO: Complete this endpoint for taking a venue_id, and using
    # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

    # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
    # clicking that button delete it from the db then redirect the user to the homepage
    error = False
    venue_name = ""
    try:
        venue_to_delete = Venue.query.filter_by(id=venue_id).first()
        venue_name = venue_to_delete.name
        db.session.delete(venue_to_delete)
        db.session.commit()
        flash('Venue ' + venue_name + ' was successfully deleted!')
    except:
        print(sys.exc_info())
        error = True
        flash('An error occurred. Venue ' +
              venue_name + ' could not be deleted.')
    finally:
        if error:
            return abort(500)
        else:
            return jsonify({'success': True})

#  Artists
#  ----------------------------------------------------------------


@app.route('/artists')
def artists():
    # TODO: replace with real data returned from querying the database
    data = []
    artists = Artist.query.with_entities(Artist.id, Artist.name).all()
    for artist in artists:
        data.append(artist)
    return render_template('pages/artists.html', artists=data)


@app.route('/artists/search', methods=['POST'])
def search_artists():
    # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
    # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
    # search for "band" should return "The Wild Sax Band".
    response = {
        "count": 0,
        "data": []
    }

    try:
        searched_artists = Artist.query.filter(Artist.name.ilike(
            f"%{request.form.get('search_term', '')}%")).with_entities(Artist.id, Artist.name, Artist.upcoming_shows_count).all()
        for searched_artist in searched_artists:
            response['data'].append(searched_artist)
        response['count'] = len(searched_artists)
    except:
        print(sys.exc_info())
    return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    # shows the artist page with the given artist_id
    # TODO: replace with real artist data from the artist table, using artist_id
    data = {}
    try:
        artist = Artist.query.filter_by(id=artist_id).first()
        past_shows_query = Show.query.filter(
            artist.id == Show.artist_id, Show.start_time <= datetime.now()).all()
        past_shows = []
        for past_show in past_shows_query:
            past_shows.append({
                "venue_id": past_show.venue_id,
                "venue_name": past_show.venue_name,
                "venue_image_link": past_show.venue_image_link,
                "start_time": str(past_show.start_time)
            })
        upcoming_shows_query = Show.query.filter(
            artist.id == Show.artist_id, Show.start_time > datetime.now()).all()
        upcoming_shows = []
        for upcoming_show in upcoming_shows_query:
            upcoming_shows.append({
                "venue_id": upcoming_show.venue_id,
                "venue_name": upcoming_show.venue_name,
                "venue_image_link": upcoming_show.venue_image_link,
                "start_time": str(upcoming_show.start_time)
            })

        artist.past_shows_count = len(past_shows)
        artist.upcoming_shows_count = len(upcoming_shows)
        db.session.commit()

        data = {
            "id": artist.id,
            "name": artist.name,
            "genres": artist.genres,
            "city": artist.city,
            "state": artist.state,
            "phone": artist.phone,
            "website": artist.website,
            "facebook_link": artist.facebook_link,
            "seeking_venue": artist.seeking_venue,
            "seeking_description": artist.seeking_description,
            "image_link": artist.image_link,
            "past_shows": past_shows,
            "upcoming_shows": upcoming_shows,
            "past_shows_count": artist.past_shows_count,
            "upcoming_shows_count": artist.upcoming_shows_count
        }
    except:
        db.session.rollback()
        print(sys.exc_info())
    finally:
        db.session.close()

    return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------


@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    form = ArtistForm()
    # TODO: populate form with fields from artist with ID <artist_id>
    artist = Artist.query.filter_by(id=artist_id).first()
    form.name.data = artist.name
    form.genres.data = artist.genres
    form.city.data = artist.city
    form.state.data = artist.state
    form.phone.data = artist.phone
    form.website_link.data = artist.website
    form.facebook_link.data = artist.facebook_link
    form.seeking_venue.data = artist.seeking_venue
    form.seeking_description.data = artist.seeking_description
    form.image_link.data = artist.image_link
    return render_template('forms/edit_artist.html', form=form, artist=artist)


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    # TODO: take values from the form submitted, and update existing
    # artist record with ID <artist_id> using the new attributes
    form = ArtistForm(request.form)
    try:
        artist = Artist.query.filter_by(id=artist_id).first()
        artist.name = form.name.data
        artist.genres = form.genres.data
        artist.city = form.city.data
        artist.state = form.state.data
        artist.phone = form.phone.data
        artist.website = form.website_link.data
        artist.facebook_link = form.facebook_link.data
        artist.seeking_venue = form.seeking_venue.data
        artist.seeking_description = form.seeking_description.data
        artist.image_link = form.image_link.data
        db.session.commit()
    except:
        print(sys.exc_info())
        db.session.rollback()
    finally:
        db.session.close()

    return redirect(url_for('show_artist', artist_id=artist_id))


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    form = VenueForm()
    # TODO: populate form with values from venue with ID <venue_id>
    venue = Venue.query.filter_by(id=venue_id).first()
    form.name.data = venue.name
    form.genres.data = venue.genres
    form.address.data = venue.address
    form.city.data = venue.city
    form.state.data = venue.state
    form.phone.data = venue.phone
    form.website_link.data = venue.website
    form.facebook_link.data = venue.facebook_link
    form.seeking_talent.data = venue.seeking_talent
    form.seeking_description.data = venue.seeking_description
    form.image_link.data = venue.image_link
    return render_template('forms/edit_venue.html', form=form, venue=venue)


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    # TODO: take values from the form submitted, and update existing
    # venue record with ID <venue_id> using the new attributes
    form = VenueForm(request.form)
    try:
        venue = Venue.query.filter_by(id=venue_id).first()
        venue.name = form.name.data
        venue.genres = form.genres.data
        venue.address = form.address.data
        venue.city = form.city.data
        venue.state = form.state.data
        venue.phone = form.phone.data
        venue.website = form.website_link.data
        venue.facebook_link = form.facebook_link.data
        venue.seeking_talent = form.seeking_talent.data
        venue.seeking_description = form.seeking_description.data
        venue.image_link = form.image_link.data
        db.session.commit()
    except:
        print(sys.exc_info())
        db.session.rollback()
    finally:
        db.session.close()

    return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------


@app.route('/artists/create', methods=['GET'])
def create_artist_form():
    form = ArtistForm()
    return render_template('forms/new_artist.html', form=form)


@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
    # called upon submitting the new artist listing form
    # TODO: insert form data as a new Venue record in the db, instead
    # TODO: modify data to be the data object returned from db insertion
    form = ArtistForm(request.form)

    try:
        artist = Artist(name=form.name.data, genres=form.genres.data, city=form.city.data, state=form.state.data, phone=form.phone.data, image_link=form.image_link.data,
                        facebook_link=form.facebook_link.data, website=form.website_link.data, seeking_venue=form.seeking_venue.data, seeking_description=form.seeking_description.data)
        db.session.add(artist)
        db.session.commit()
        # on successful db insert, flash success
        flash('Artist ' + artist.name + ' was successfully listed!')
    except:
        db.session.rollback()
        print(sys.exc_info())
        flash('An error occurred. Artist ' +
              form.name.data + ' could not be listed.')
    finally:
        db.session.close()
    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
    return redirect(url_for('index'))


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
    # displays list of shows at /shows
    # TODO: replace with real venues data.
    data = []
    shows = Show.query.all()
    for show in shows:
        show.start_time = str(show.start_time)
        data.append(show)
    return render_template('pages/shows.html', shows=data)


@app.route('/shows/create')
def create_shows():
    # renders form. do not touch.
    form = ShowForm()
    return render_template('forms/new_show.html', form=form)


@app.route('/shows/create', methods=['POST'])
def create_show_submission():
    # called to create new shows in the db, upon submitting new show listing form
    # TODO: insert form data as a new Show record in the db, instead
    form = ShowForm(request.form)

    # on successful db insert, flash success
    try:
        venue = Venue.query.filter_by(id=form.venue_id.data).first()
        artist = Artist.query.filter_by(id=form.artist_id.data).first()

        show = Show(start_time=form.start_time.data,
                    venue_id=venue.id, venue_name=venue.name, venue_image_link=venue.image_link, artist_id=artist.id, artist_name=artist.name, artist_image_link=artist.image_link)
        if show.start_time > datetime.now():
            venue.upcoming_shows_count += 1
            artist.upcoming_shows_count += 1
        else:
            venue.past_shows_count += 1
            artist.past_shows_count += 1
        db.session.add(show)
        db.session.commit()
        flash('Show was successfully listed!')
    except:
        print(sys.exc_info())
        db.session.rollback()
        flash('An error occurred. Show could not be listed.')
    finally:
        db.session.close()
    # TODO: on unsuccessful db insert, flash an error instead.
    # e.g., flash('An error occurred. Show could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    return redirect(url_for('index'))


@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404


@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.debug = True
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
