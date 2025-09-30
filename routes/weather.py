# # from flask import Blueprint, current_app, request, jsonify
# # from extensions import db
# # from models import Search
# # from sqlalchemy import desc
# # import requests

# # bp = Blueprint("weather", __name__, url_prefix="/api")

# # @bp.get("/weather")
# # def get_weather():
# #     city = request.args.get("city", "").strip()
# #     if not city:
# #         return jsonify({"error": "City parameter is required"}), 400

# #     api_key = current_app.config.get("OPENWEATHER_API_KEY")
# #     url = "http://api.openweathermap.org/data/2.5/weather"
# #     params = {"q": city, "appid": api_key, "units": "metric"}

# #     resp = requests.get(url, params=params)
# #     if resp.status_code != 200:
# #         return jsonify({"error": "City not found"}), resp.status_code

# #     data = resp.json()
# #     weather = {
# #         "city": data.get("name"),
# #         "temperature": data.get("main", {}).get("temp"),
# #         "humidity": data.get("main", {}).get("humidity"),
# #         "condition": (data.get("weather") or [{}])[0].get("main")
# #     }

# #     # Store search in DB (keep last 5)
# #     try:
# #         new_search = Search(city_name=city)
# #         db.session.add(new_search)
# #         db.session.commit()

# #         searches = Search.query.order_by(desc(Search.searched_at)).all()
# #         if len(searches) > 5:
# #             for s in searches[5:]:
# #                 db.session.delete(s)
# #             db.session.commit()
# #     except Exception:
# #         current_app.logger.exception("DB error while saving search")

# #     return jsonify(weather)


# # @bp.get("/last-cities")
# # def last_cities():
# #     searches = Search.query.order_by(desc(Search.searched_at)).limit(5).all()
# #     cities = [s.city_name for s in searches]
# #     return jsonify(cities)
# from flask import Blueprint, current_app, request, jsonify
# from extensions import db
# from models import Search
# from sqlalchemy import desc
# import requests

# bp = Blueprint("weather", __name__, url_prefix="/api")


# @bp.get("/weather")
# def get_weather():
#     city = request.args.get("city", "").strip()
#     if not city:
#         return jsonify({"error": "City parameter is required"}), 400

#     # Fetch weather from OpenWeatherMap
#     api_key = current_app.config.get("OPENWEATHER_API_KEY")
#     url = "http://api.openweathermap.org/data/2.5/weather"
#     params = {"q": city, "appid": api_key, "units": "metric"}

#     try:
#         resp = requests.get(url, params=params)
#         resp.raise_for_status()  # Raise error for bad responses
#         data = resp.json()
#     except requests.RequestException as e:
#         current_app.logger.error(f"Weather API error: {e}")
#         return jsonify({"error": "Failed to fetch weather data"}), 500

#     weather = {
#         "city": data.get("name"),
#         "temperature": data.get("main", {}).get("temp"),
#         "humidity": data.get("main", {}).get("humidity"),
#         "condition": (data.get("weather") or [{}])[0].get("main")
#     }

#     # Store search in DB and keep only last 5
#     try:
#         new_search = Search(city_name=city)
#         db.session.add(new_search)
#         db.session.commit()
#         current_app.logger.info(f"Saved search for city: {city}")

#         # Delete older searches beyond the last 5
#         db.session.query(Search).order_by(desc(Search.searched_at)).offset(5).delete(synchronize_session=False)
#         db.session.commit()
#     except Exception as e:
#         db.session.rollback()
#         current_app.logger.error(f"DB error while saving search: {e}")

#     return jsonify(weather)


# @bp.get("/last-cities")
# def last_cities():
#     try:
#         searches = Search.query.order_by(desc(Search.searched_at)).limit(5).all()
#         cities = [s.city_name for s in searches]
#         return jsonify(cities)
#     except Exception as e:
#         current_app.logger.error(f"DB error fetching last cities: {e}")
#         return jsonify({"error": "Failed to fetch last cities"}), 500
from flask import Blueprint, request, jsonify, current_app
from extensions import db
from models import Search
from sqlalchemy import desc
import requests
from datetime import datetime

bp = Blueprint("weather", __name__, url_prefix="/api")

@bp.get("/weather")
def get_weather():
    city = request.args.get("city", "").strip()
    if not city:
        return jsonify({"error": "City required"}), 400

    api_key = current_app.config.get("OPENWEATHER_API_KEY")
    url = "http://api.openweathermap.org/data/2.5/weather"
    params = {"q": city, "appid": api_key, "units": "metric"}
    resp = requests.get(url, params=params)

    if resp.status_code != 200:
        return jsonify({"error": "City not found"}), resp.status_code

    data = resp.json()
    weather = {
        "city": data.get("name"),
        "temperature": data.get("main", {}).get("temp"),
        "humidity": data.get("main", {}).get("humidity"),
        "condition": (data.get("weather") or [{}])[0].get("main")
    }

    # Add new search
    try:
        new_search = Search(city_name=city, searched_at=datetime.utcnow())
        db.session.add(new_search)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Failed to save search: {e}")

    # Keep only last 5 searches
    try:
        searches = Search.query.order_by(desc(Search.searched_at)).all()
        if len(searches) > 5:
            for s in searches[5:]:
                db.session.delete(s)
            db.session.commit()
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Failed to cleanup old searches: {e}")

    return jsonify(weather)


@bp.get("/last-cities")
def last_cities():
    try:
        searches = Search.query.order_by(desc(Search.searched_at)).limit(5).all()
        cities = [s.city_name for s in searches]
        return jsonify(cities)
    except Exception as e:
        current_app.logger.error(f"Failed to fetch last cities: {e}")
        return jsonify([]), 500
