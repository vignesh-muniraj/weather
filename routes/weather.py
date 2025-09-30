
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

    try:
        new_search = Search(city_name=city, searched_at=datetime.utcnow())
        db.session.add(new_search)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Failed to save search: {e}")

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
