# ----------------------------------------------------------------------------#
# Imports
# ----------------------------------------------------------------------------#

import json
import sys
from typing_extensions import final
import dateutil.parser
import babel
from flask import render_template, request, Response, flash, redirect, url_for
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from werkzeug.wrappers import response
from forms import *
from datetime import datetime as dt
from models import Show, Venue, Artist
from models import app, db

# ----------------------------------------------------------------------------#
# Filters.
# ----------------------------------------------------------------------------#


def format_datetime(value, format="medium"):
    date = dateutil.parser.parse(value)
    if format == "full":
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == "medium":
        format = "EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, format, locale="en")


app.jinja_env.filters["datetime"] = format_datetime

# ----------------------------------------------------------------------------#
# Controllers.
# ----------------------------------------------------------------------------#


@app.route("/")
def index():
    return render_template("pages/home.html")


#  Venues
#  ----------------------------------------------------------------


@app.route("/venues")
def venues():
    # TODO: replace with real venues data.
    #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue.

    data = []

    for location in db.session.query(Venue.city, Venue.state).distinct().all():
        venue_query = (
            db.session.query(Venue.id, Venue.name)
            .filter(Venue.state == location[1])
            .filter(Venue.city == location[0])
            .all()
        )
        temp = {
            "city": location[0],
            "state": location[1],
            "venues": [
                {
                    "id": venue[0],
                    "name": venue[1],
                    "num_upcoming_shows": db.session.query(db.func.count(Show.id))
                    .join(Venue.shows)
                    .filter(Show.start_time > dt.now())
                    .filter(Venue.id == venue[0])
                    .first()[0],
                }
                for venue in venue_query
            ],
        }
        print(temp)
        data.append(temp)

    return render_template("pages/venues.html", areas=data)


@app.route("/venues/search", methods=["POST"])
def search_venues():
    # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
    # seach for Hop should return "The Musical Hop".
    # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
    search_term = request.form.get("search_term", "")
    searched_venues = Venue.query.filter(
        Venue.name.ilike("%" + search_term + "%")
    ).all()

    response = {
        "count": len(searched_venues),
        "data": [
            {
                "id": venue.id,
                "name": venue.name,
                "num_upcoming_shows": db.session.query(db.func.count(Show.id))
                .join(Venue.shows)
                .filter(Show.start_time > dt.now())
                .filter(Venue.id == venue.id)
                .first()[0],
            }
            for venue in searched_venues
        ],
    }

    return render_template(
        "pages/search_venues.html",
        results=response,
        search_term=search_term,
    )


@app.route("/venues/<int:venue_id>")
def show_venue(venue_id):
    # shows the venue page with the given venue_id
    # TODO: replace with real venue data from the venues table, using venue_id

    venue = Venue.query.get(venue_id)
    past_shows = [show for show in venue.shows if show.start_time < dt.now()]
    upcoming_shows = [show for show in venue.shows if show.start_time >= dt.now()]

    data = {
        "id": venue.id,
        "name": venue.name,
        "genres": venue.genres.strip("{").strip("}").split(","),
        "address": venue.address,
        "city": venue.city,
        "state": venue.state,
        "phone": venue.phone,
        "website": venue.website,
        "facebook_link": venue.facebook_link,
        "seeking_talent": venue.seeking_talent,
        "seeking_description": venue.seeking_description,
        "image_link": venue.image_link,
        "past_shows": [
            {
                "artist_id": show.artist_id,
                "artist_name": show.artist.name,
                "artist_image_link": show.artist.image_link,
                "start_time": str(show.start_time),
            }
            for show in past_shows
        ],
        "upcoming_shows": [
            {
                "artist_id": show.artist_id,
                "artist_name": show.artist.name,
                "artist_image_link": show.artist.image_link,
                "start_time": str(show.start_time),
            }
            for show in upcoming_shows
        ],
        "past_shows_count": len(past_shows),
        "upcoming_shows_count": len(upcoming_shows),
    }

    return render_template("pages/show_venue.html", venue=data)


#  Create Venue
#  ----------------------------------------------------------------


@app.route("/venues/create", methods=["GET"])
def create_venue_form():
    form = VenueForm()
    return render_template("forms/new_venue.html", form=form)


@app.route("/venues/create", methods=["POST"])
def create_venue_submission():
    # TODO: insert form data as a new Venue record in the db, instead
    # TODO: modify data to be the data object returned from db insertion

    form = VenueForm(request.form)

    try:
        venue = Venue(
            name=form.name.data,
            city=form.city.data,
            state=form.state.data,
            address=form.address.data,
            phone=form.phone.data,
            genres=form.genres.data,
            facebook_link=form.facebook_link.data,
            image_link=form.image_link.data,
            seeking_talent=form.seeking_talent.data,
            seeking_description=form.seeking_description.data,
        )
        db.session.add(venue)
        db.session.commit()
        # on successful db insert, flash success
        flash("Venue " + form.name.data + " was successfully listed!")
    except:
        print("ERROR: ", sys.exc_info())
        db.session.rollback()
        # TODO: on unsuccessful db insert, flash an error instead.
        flash("An error occurred. Venue " + form.name.data + " could not be listed.")
    finally:
        db.session.close()

    return render_template("pages/home.html")


@app.route("/venues/<venue_id>", methods=["DELETE"])
def delete_venue(venue_id):
    # TODO: Complete this endpoint for taking a venue_id, and using
    # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

    # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
    # clicking that button delete it from the db then redirect the user to the homepage
    return None


#  Artists
#  ----------------------------------------------------------------
@app.route("/artists")
def artists():
    # TODO: replace with real data returned from querying the database

    data = [{"id": artist.id, "name": artist.name} for artist in Artist.query.all()]

    return render_template("pages/artists.html", artists=data)


@app.route("/artists/search", methods=["POST"])
def search_artists():
    # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
    # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
    # search for "band" should return "The Wild Sax Band".

    search_term = request.form.get("search_term", "")
    searched_artists = Artist.query.filter(
        Artist.name.ilike("%" + search_term + "%")
    ).all()

    response = {
        "count": len(searched_artists),
        "data": [
            {
                "id": artist.id,
                "name": artist.name,
                "num_upcoming_shows": db.session.query(db.func.count(Show.id))
                .join(Artist.shows)
                .filter(Show.start_time > dt.now())
                .filter(Artist.id == artist.id)
                .first()[0],
            }
            for artist in searched_artists
        ],
    }
    return render_template(
        "pages/search_artists.html",
        results=response,
        search_term=search_term,
    )


@app.route("/artists/<int:artist_id>")
def show_artist(artist_id):
    # shows the artist page with the given artist_id
    # TODO: replace with real artist data from the artist table, using artist_id

    artist = Artist.query.get(artist_id)

    past_shows = [show for show in artist.shows if show.start_time < dt.now()]
    upcoming_shows = [show for show in artist.shows if show.start_time >= dt.now()]

    data = {
        "id": artist.id,
        "name": artist.name,
        "genres": artist.genres.strip("{").strip("}").strip('"').split(","),
        "city": artist.city,
        "state": artist.state,
        "phone": artist.phone,
        "website": artist.website,
        "facebook_link": artist.facebook_link,
        "seeking_venue": artist.seeking_venue,
        "seeking_description": artist.seeking_description,
        "image_link": artist.image_link,
        "past_shows": [
            {
                "venue_id": show.venue_id,
                "venue_name": show.venue.name,
                "venue_image_link": show.venue.image_link,
                "start_time": str(show.start_time),
            }
            for show in past_shows
        ],
        "upcoming_shows": [
            {
                "venue_id": show.venue_id,
                "venue_name": show.venue.name,
                "venue_image_link": show.venue.image_link,
                "start_time": str(show.start_time),
            }
            for show in upcoming_shows
        ],
        "past_shows_count": len(past_shows),
        "upcoming_shows_count": len(upcoming_shows),
    }
    return render_template("pages/show_artist.html", artist=data)


#  Update
#  ----------------------------------------------------------------
@app.route("/artists/<int:artist_id>/edit", methods=["GET"])
def edit_artist(artist_id):
    artist_query = Artist.query.get(artist_id)
    form = ArtistForm(obj=artist_query)
    # TODO: populate form with fields from artist with ID <artist_id>
    return render_template("forms/edit_artist.html", form=form, artist=artist_query)


@app.route("/artists/<int:artist_id>/edit", methods=["POST"])
def edit_artist_submission(artist_id):
    # TODO: take values from the form submitted, and update existing
    # artist record with ID <artist_id> using the new attributes

    artist = Artist.query.get(artist_id)
    form = ArtistForm(request.form)

    try:
        artist.name = form.name.data
        artist.city = form.city.data
        artist.state = form.state.data
        artist.phone = form.phone.data
        artist.facebook_link = form.facebook_link.data
        artist.image_link = form.image_link.data
        artist.website = form.website_link.data
        artist.seeking_venue = form.seeking_venue.data
        artist.seeking_description = form.seeking_description.data
        db.session.commit()
        flash("Artist " + form.name.data + " was successfully edited")
    except:
        print("ERROR")
        db.session.rollback()
        flash("Error in editing Artist " + form.name.data)
    finally:
        db.session.close()

    return redirect(url_for("show_artist", artist_id=artist_id))


@app.route("/venues/<int:venue_id>/edit", methods=["GET"])
def edit_venue(venue_id):
    # TODO: populate form with values from venue with ID <venue_id>
    venue_query = Venue.query.get(venue_id)
    form = VenueForm(obj=venue_query)
    return render_template("forms/edit_venue.html", form=form, venue=venue_query)


@app.route("/venues/<int:venue_id>/edit", methods=["POST"])
def edit_venue_submission(venue_id):
    # TODO: take values from the form submitted, and update existing
    # venue record with ID <venue_id> using the new attributes

    venue = Venue.query.get(venue_id)
    form = VenueForm(request.form)
    try:
        venue.name = form.name.data
        venue.city = form.city.data
        venue.state = form.state.data
        venue.phone = form.phone.data
        venue.address = form.address.data
        venue.genres = form.genres.data
        venue.facebook_link = form.facebook_link.data
        venue.image_link = form.image_link.data
        venue.website = form.website_link.data
        venue.seeking_talent = form.seeking_talent.data
        venue.seeking_description = form.seeking_description.data
        db.session.commit()
        flash("Venue " + form.name.data + " was successfully edited")
    except ValueError as e:
        print("ERROR: ", e)
        db.session.rollback()
        flash("Error in editing Venue " + form.name.data)
    finally:
        db.session.close()

    return redirect(url_for("show_venue", venue_id=venue_id))


#  Create Artist
#  ----------------------------------------------------------------


@app.route("/artists/create", methods=["GET"])
def create_artist_form():
    form = ArtistForm()
    return render_template("forms/new_artist.html", form=form)


@app.route("/artists/create", methods=["POST"])
def create_artist_submission():
    # called upon submitting the new artist listing form
    # TODO: insert form data as a new Venue record in the db, instead
    # TODO: modify data to be the data object returned from db insertion

    form = ArtistForm(request.form)

    try:
        artist = Artist(
            name=form.name.data,
            city=form.city.data,
            state=form.state.data,
            phone=form.phone.data,
            genres=form.genres.data,
            facebook_link=form.facebook_link.data,
            image_link=form.image_link.data,
            website=form.website_link.data,
            seeking_venue=form.seeking_venue.data,
            seeking_description=form.seeking_description.data,
        )
        print(artist)
        db.session.add(artist)
        db.session.commit()
        # on successful db insert, flash success
        flash("Artist " + form.name.data + " was successfully listed!")
    except:
        print("ERROR: ", sys.exc_info())
        db.session.rollback()
        # TODO: on unsuccessful db insert, flash an error instead.
        flash("An error occurred. Artist " + form.name.data + " could not be listed.")
    finally:
        db.session.close()

    return render_template("pages/home.html")


#  Shows
#  ----------------------------------------------------------------


@app.route("/shows")
def shows():
    # displays list of shows at /shows
    # TODO: replace with real venues data.

    data = [
        {
            "venue_id": show.venue_id,
            "venue_name": show.venue.name,
            "artist_id": show.artist_id,
            "artist_name": show.artist.name,
            "artist_image_link": show.artist.image_link,
            "start_time": str(show.start_time),
        }
        for show in Show.query.all()
    ]

    return render_template("pages/shows.html", shows=data)


@app.route("/shows/create")
def create_shows():
    # renders form. do not touch.
    form = ShowForm()
    return render_template("forms/new_show.html", form=form)


@app.route("/shows/create", methods=["POST"])
def create_show_submission():
    # called to create new shows in the db, upon submitting new show listing form
    # TODO: insert form data as a new Show record in the db, instead

    form = ShowForm(request.form)

    try:
        show = Show(
            artist_id=form.artist_id.data,
            venue_id=form.venue_id.data,
            start_time=form.start_time.data,
        )
        db.session.add(show)
        db.session.commit()
        # on successful db insert, flash success
        flash("Show was successfully listed!")
    except:
        print("ERROR: ", sys.exc_info())
        db.session.rollback()
        # TODO: on unsuccessful db insert, flash an error instead.
        flash("An error occurred. Show could not be listed.")
    finally:
        db.session.close()

    return render_template("pages/home.html")


@app.errorhandler(404)
def not_found_error(error):
    return render_template("errors/404.html"), 404


@app.errorhandler(500)
def server_error(error):
    return render_template("errors/500.html"), 500


if not app.debug:
    file_handler = FileHandler("error.log")
    file_handler.setFormatter(
        Formatter("%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]")
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info("errors")

# ----------------------------------------------------------------------------#
# Launch.
# ----------------------------------------------------------------------------#

# Default port:
if __name__ == "__main__":
    app.run()

# Or specify port manually:
"""
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
"""
