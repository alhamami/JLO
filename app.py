#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import FlaskForm
from sqlalchemy.sql.functions import percentile_cont
from forms import *
from flask_migrate import Migrate
import config
from sqlalchemy import func,asc
from flask_cors import CORS
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#
def create_app(test_config=None):
  app = Flask(__name__)
  CORS(app)
  moment = Moment(app)
  app.config.from_object('config')
  db = SQLAlchemy(app)
  migrate = Migrate(app, db)
  app.config['SQLALCHEMY_DATABASE_URI'] = config.SQLALCHEMY_DATABASE_URI



#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

  class Venue(db.Model):
      __tablename__ = 'Venue'

      id = db.Column(db.Integer, primary_key=True)
      name = db.Column(db.String, nullable=False)
      city = db.Column(db.String(120), nullable=False)
      state = db.Column(db.String(120), nullable=False)
      address = db.Column(db.String(120), nullable=False)
      phone = db.Column(db.String(120))
      image_link = db.Column(db.String(150))
      facebook_link = db.Column(db.String(150))
      genres = db.Column("genres", db.ARRAY(db.String()), nullable=False)
      website_link = db.Column(db.String(150))
      seeking_talent = db.Column(db.Boolean, default=True)
      seeking_description = db.Column(db.String(150))
      Show = db.relationship('Show', backref='venue', lazy=True)


  class Artist(db.Model):
      __tablename__ = 'Artist'
      id = db.Column(db.Integer, primary_key=True)
      name = db.Column(db.String, nullable=False)
      city = db.Column(db.String(120), nullable=False)
      state = db.Column(db.String(120), nullable=False)
      phone = db.Column(db.String(120))
      genres = db.Column("genres", db.ARRAY(db.String()), nullable=False)
      image_link = db.Column(db.String(150))
      facebook_link = db.Column(db.String(150))
      website_link = db.Column(db.String(150))
      seeking_venue = db.Column(db.Boolean, default=True)
      seeking_description = db.Column(db.String(150))
      Show = db.relationship('Show', backref='artist', lazy=True)

  class Show(db.Model):
      __tablename__ = 'Show'

      id = db.Column(db.Integer, primary_key=True)
      artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'), nullable=False)
      venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), nullable=False)
      start_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

  #----------------------------------------------------------------------------#
  # Filters.
  #----------------------------------------------------------------------------#


  def format_datetime(value, format='medium'):
    date = dateutil.parser.parse(value)
    if format == 'full':
        format="EEEE MMMM, d, y 'at' h:mma"
    elif format == 'medium':
        format="EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, format)

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
    #       num_shows should be aggregated based on number of upcoming shows per venue.
    city_state_only=db.session.query(Venue.city,Venue.state).group_by(Venue.id,Venue.city,Venue.state).distinct().all()
    data = []
    for place in city_state_only:
      venue_info = Venue.query.filter_by(city=place.city).filter_by(state=place.state).all()
      each_venue = []
      for each in venue_info:
        each_venue.append({"id": each.id,"name": each.name, "num_upcoming_shows": len(db.session.query(Show).filter(Show.venue_id==1).filter(Show.start_time>datetime.now()).all())
        })
      data.append({"city": place.city, "state": place.state, "venues": each_venue})

    return render_template('pages/venues.html', areas=data)

  # search venues
  @app.route('/venues/search', methods=['POST'])
  def search_venues():
    # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
    # seach for Hop should return "The Musical Hop".
    # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
    all = []
    search_term = request.form.get('search_term', '')
    get_search = db.session.query(Venue).filter(Venue.name.ilike(f'%{search_term}%')).all()
    for each in get_search:
      num = len(db.session.query(Show).filter(Show.venue_id == each.id).filter(Show.start_time > datetime.now()).all())
      all.append({"id": each.id,"name": each.name,"num_upcoming_shows": num})
    
    response={
      "count": len(get_search),
      "data": all
    }
    return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))


  @app.route('/venues/<int:venue_id>')  
    # shows the venue page with the given venue_id
    # TODO: replace with real venue data from the venues table, using venue_id
  def show_venue(venue_id):
    lShows = []
    venue = Venue.query.get(venue_id)
    aShows = []
    now = datetime.now()
    shows = db.session.query(Show).join(Artist)
    for each in shows:
      time = str(each.start_time)
      data = {"artist_id": each.artist_id,"artist_name": each.artist.name,"start_time": format_datetime(time),"artist_image_link": each.artist.image_link
          }
      if each.start_time > now:
        aShows.append(data)
      else:
        lShows.append(data)
    data1={
      "id": venue.id,
      "name": venue.name,
      "genres": venue.genres,
      "address": venue.address,
      "city": venue.city,
      "state": venue.state,
      "phone": venue.phone,
      "website": venue.website_link,
      "facebook_link": venue.facebook_link,
      "seeking_talent": venue.seeking_talent,
      "seeking_description":venue.seeking_description,
      "image_link": venue.image_link,
      "past_shows": lShows,
      "upcoming_shows": aShows,
      "past_shows_count": len(lShows),
      "upcoming_shows_count": len(aShows)
    }
    data = list(filter(lambda d: d['id'] == venue_id, [data1]))[0]
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
    
    # on successful db insert, flash success
    info = VenueForm()
    try:
      addone = Venue(name=info.name.data, genres=info.genres.data, address=info.address.data,
      city=info.city.data, state=info.state.data,
      phone=info.phone.data, website_link=info.website_link.data, facebook_link=info.facebook_link.data, 
      seeking_talent=info.seeking_talent.data, image_link=info.image_link.data,
      seeking_description=info.seeking_description.data)
      db.session.add(addone)
      db.session.commit()
      flash('Venue ' + request.form['name'] + ' was successfully listed!')
    except:
      db.session.rollback()
      flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
    finally:
      db.session.close()
    return render_template('pages/home.html')


  @app.route('/venues/<venue_id>', methods=['DELETE'])
  def delete_venue(venue_id):
    # TODO: Complete this endpoint for taking a venue_id, and using
    # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

    try:
      target = Venue.query.get(venue_id)
      db.session.delete(target)
      db.session.commit()
    except:
      db.session.rollback()
    finally:
      db.session.close()
    return redirect(url_for('index'))


  @app.route('/venues/<string:venue_name>', methods=['GET'])
  def delete_venue_bonus(venue_name):

    # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
    # clicking that button delete it from the db then redirect the user to the homepage
  
      try:
          Venue.query.filter_by(name=venue_name).delete()

          db.session.commit()

      except:
          db.session.rollback()
      finally:
          db.session.close()   
          return render_template('pages/home.html')

  #  Artists
  #  ----------------------------------------------------------------
  @app.route('/artists')
  def artists():
    # TODO: replace with real data returned from querying the database
    data = []
    
    all = Artist.query.all()
    for each in all:
      data.append({"id": each.id,"name": each.name})

    return render_template('pages/artists.html', artists=data)

  @app.route('/artists/search', methods=['POST'])
  def search_artists(): 
    # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
    # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
    # search for "band" should return "The Wild Sax Band".
    search_term = request.form.get('search_term', '')
    search_artist = Artist.query.filter(Artist.name.ilike(f'%{search_term}%'))

    response = {'count': search_artist.count(),'data': search_artist}

    return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

  @app.route('/artists/<int:artist_id>')
  def show_artist(artist_id):
    lShow = []
    aShow = []
    all = Artist.query.get(artist_id)
    now = datetime.now()
    each_show = Show.query.filter_by(artist_id=artist_id).all()

    for each in each_show:
      time = str(each.start_time)
      data = {'venue_id': each.venue_id,'venue_name': each.venue.name,'venue_image_link': each.venue.image_link,
      'start_time': format_datetime(time)}
      if each.start_time > now:
        aShow.append(data)
      else:
        lShow.append(data)
    nPs = len(lShow)
    nUp = len(aShow)
    data1 = {
      'id': all.id,
      'name': all.name,
      'genres': all.genres,
      'city': all.city,
      'state': all.state,
      'phone': all.phone,
      'facebook_link': all.facebook_link,
      'image_link': all.image_link,
      'website_link': all.website_link,
      'past_shows': lShow,
      'upcoming_shows': aShow,
      'past_shows_count': nPs,
      'upcoming_shows_count': nUp,
      'seeking_venue' : all.seeking_venue,
      'seeking_description' : all.seeking_description
    }
    data = list(filter(lambda d: d['id'] == artist_id, [data1]))[0]
    return render_template('pages/show_artist.html', artist=data)

  #  Update
  #  ----------------------------------------------------------------
  @app.route('/artists/<int:artist_id>/edit', methods=['GET'])
  def edit_artist(artist_id):
    form_submitted = ArtistForm()
    specific_Artist = Artist.query.get(artist_id)
    edit_Artist={
      "id": specific_Artist.id,
      "name": specific_Artist.name,
      "genres": specific_Artist.genres,
      "city": specific_Artist.city,
      "state": specific_Artist.state,
      "phone": specific_Artist.phone,
      "facebook_link": specific_Artist.facebook_link,
      "image_link": specific_Artist.image_link,
      "seeking_venue" : specific_Artist.seeking_venue,
      "seeking_description" : specific_Artist.seeking_description,
      "website_link": specific_Artist.website_link
    }
    # TODO: populate form with fields from artist with ID <artist_id>
    return render_template('forms/edit_artist.html', form=form_submitted, artist=edit_Artist)

  @app.route('/artists/<int:artist_id>/edit', methods=['POST'])
  def edit_artist_submission(artist_id):
    # TODO: take values from the form submitted, and update existing
    # artist record with ID <artist_id> using the new attributes
    form_submitted = ArtistForm()
    try:
      each_Artist = Artist.query.get(artist_id)
      each_Artist.name = form_submitted.name.data
      each_Artist.phone = form_submitted.phone.data
      each_Artist.genres = form_submitted.genres.data
      each_Artist.state = form_submitted.state.data
      each_Artist.city = form_submitted.city.data
      each_Artist.website_link=form_submitted.website_link.data
      each_Artist.image_link = form_submitted.image_link.data
      each_Artist.facebook_link = form_submitted.facebook_link.data
      each_Artist.seeking_venue=form_submitted.seeking_venue.data
      each_Artist.seeking_description=form_submitted.seeking_description.data

      db.session.commit()
    except:
      db.session.rollback()
    finally:
      db.session.close()
    return redirect(url_for('show_a rtist', artist_id=artist_id))

  @app.route('/venues/<int:venue_id>/edit', methods=['GET'])
  def edit_venue(venue_id):
    form_submitted = VenueForm()

    specific_Venue = Venue.query.get(venue_id)
    edit_Venue = {
      "id": specific_Venue.id,
      "name": specific_Venue.name,
      "genres": specific_Venue.genres,
      "address": specific_Venue.address,
      "city": specific_Venue.city,
      "state": specific_Venue.state,
      "phone": specific_Venue.phone,
      "website_link":specific_Venue.website_link,
      "facebook_link": specific_Venue.facebook_link,
      "seeking_talent": specific_Venue.seeking_talent,
      "seeking_description": specific_Venue.seeking_description,
      "image_link": specific_Venue.image_link
    }  
    return render_template('forms/edit_venue.html', form=form_submitted, venue=edit_Venue)

  @app.route('/venues/<int:venue_id>/edit', methods=['POST'])
  def edit_venue_submission(venue_id):
    # TODO: take values from the form submitted, and update existing
    # venue record with ID <venue_id> using the new attributes
    
    form_submitted = VenueForm()

    try:
      edit_venue = Venue.query.get(venue_id)
      edit_venue.name = form_submitted.name.data
      edit_venue.genres = form_submitted.genres.data
      edit_venue.city = form_submitted.city.data
      edit_venue.state = form_submitted.state.data
      edit_venue.address = form_submitted.address.data
      edit_venue.phone = form_submitted.phone.data
      edit_venue.facebook_link = form_submitted.facebook_link.data
      edit_venue.website_link = form_submitted.website_link.data
      edit_venue.image_link = form_submitted.image_link.data
      edit_venue.seeking_talent = form_submitted.seeking_talent.data
      edit_venue.seeking_description = form_submitted.seeking_description.data

      db.session.commit()
    except:
      db.session.rollback()
    finally:
      db.session.close()
    return redirect(url_for('show_venue', venue_id=venue_id))

  #  Create Artist
  #  ----------------------------------------------------------------

  @app.route('/artists/create', methods=['GET'])
  def create_artist_form():
    form_submitted = ArtistForm()
    return render_template('forms/new_artist.html', form=form_submitted)

  @app.route('/artists/create', methods=['POST'])
  def create_artist_submission():
    # called upon submitting the new artist listing form
    # TODO: insert form data as a new Venue record in the db, instead
    # TODO: modify data to be the data object returned from db insertion
    try:
      form_submitted = ArtistForm()
      addone = Artist(name=form_submitted.name.data, city=form_submitted.city.data, state=form_submitted.state.data,
                      phone=form_submitted.phone.data, genres=form_submitted.genres.data,
                      image_link=form_submitted.image_link.data, facebook_link=form_submitted.facebook_link.data, website_link=form_submitted.website_link.data,
                      seeking_venue=form_submitted.seeking_venue.data, seeking_description=form_submitted.seeking_description.data)
      db.session.add(addone)
      db.session.commit()
      # on successful db insert, flash success
      flash('Artist ' + request.form['name'] + ' was successfully listed!')
    except:
      db.session.rollback()
      flash('An error ocurred, Artist ' + request.form['name'] + ' could not be listed')
    finally:
      db.session.close()
    
    return render_template('pages/home.html')



  #  Shows
  #  ----------------------------------------------------------------

  @app.route('/shows')
  def shows():
    # displays list of shows at /shows
    # TODO: replace with real venues data.
    #       num_shows should be aggregated based on number of upcoming shows per venue.
    
    each_Show = Show.query.order_by(Show.start_time)
    data = []
    for each in each_Show:
      time = str(each.start_time)
      data.append({'venue_id': each.venue_id,'venue_name': each.venue.name,'artist_id': each.artist_id,
        'artist_name': each.artist.name,'artist_image_link': each.artist.image_link,'start_time': format_datetime(time)})
      
    return render_template('pages/shows.html', shows=data)


  @app.route('/shows/create')
  def create_shows():
    # renders form. do not touch.
    form = ShowForm()
    return render_template('forms/new_show.html', form=form)

  @app.route('/shows/create', methods=['POST'])
  def create_show_submission():
    try:
      show_submitting = Show(venue_id=request.form['venue_id'], artist_id=request.form['artist_id'],start_time=request.form['start_time'])
      db.session.add(show_submitting)
      db.session.commit()
      # on successful db insert, flash success
      flash('Show was successfully listed!')
    except:
      db.session.rollback()
      flash('An error occured. show could not be listed')
    finally:
      db.session.close()
    return render_template('pages/home.html')

  @app.errorhandler(404)
  def not_found_error(error):
      return render_template('errors/404.html'), 404

  @app.errorhandler(500)
  def server_error(error):
      return render_template('errors/500.html'), 500


  if not app.debug:
      file_handler = FileHandler('error.log')
      file_handler.setFormatter(
          Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
      )
      app.logger.setLevel(logging.INFO)
      file_handler.setLevel(logging.INFO)
      app.logger.addHandler(file_handler)
      app.logger.info('errors')
  return app
#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#
app = create_app()

if __name__ == '__main__':
    app.run()


# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
