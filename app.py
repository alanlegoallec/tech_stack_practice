# # app.py

import os
from flask import Flask, request, jsonify
from backend import db, multiply_with_random

# Read variables from environment
db_user = os.environ.get("POSTGRES_USER")
db_password = os.environ.get("POSTGRES_PASSWORD")
db_name = os.environ.get("POSTGRES_DB")
db_host = os.environ.get("DB_HOST", "db")  # default to 'db'
db_port = os.environ.get("DB_PORT", 5432)
flask_port = int(os.environ.get("FLASK_PORT", 5001))

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = (
    f'postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}'
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

@app.route("/multiply", methods=["POST"])
def multiply():
    data = request.get_json()
    number = data.get("number")
    if number is None:
        return jsonify({"error": "Missing 'number' in request"}), 400
    # Ensure we are in app context for DB access
    with app.app_context():
        try:
            result, multiplier, explanation = multiply_with_random(number)
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    return jsonify({"result": result, "multiplier": multiplier, "explanation": explanation})

if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=flask_port)
