from flask import Blueprint, current_app, request, jsonify
from extensions import db
from models import Search
from sqlalchemy import desc
import requests

bp = Blueprint("weather", __name__, url_prefix="/api")

@bp.get("/weather")
def get_weather():
    city = request.args.get("city", "").strip()
    if not city:
        return jsonify({"error": "City parameter is required"}), 400

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

    # Store search in DB (keep last 5)
    try:
        new_search = Search(city_name=city)
        db.session.add(new_search)
        db.session.commit()

        searches = Search.query.order_by(desc(Search.searched_at)).all()
        if len(searches) > 5:
            for s in searches[5:]:
                db.session.delete(s)
            db.session.commit()
    except Exception:
        current_app.logger.exception("DB error while saving search")

    return jsonify(weather)


@bp.get("/last-cities")
def last_cities():
    searches = Search.query.order_by(desc(Search.searched_at)).limit(5).all()
    cities = [s.city_name for s in searches]
    return jsonify(cities)
