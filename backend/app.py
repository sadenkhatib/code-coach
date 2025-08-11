from flask import Flask, request, jsonify
from flask_cors import CORS
from workouts import generate_plan

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes and origins by default

@app.route('/generate-plan', methods=['POST'])
def generate_workout():
    data = request.get_json()
    goal = data.get('goal')
    days = data.get('days')

    if not goal or not days:
        return jsonify({"error": "Missing goal or days"}), 400

    try:
        result = generate_plan(goal, int(days))
        return jsonify(result)
    except Exception as e:
        print(f"ERROR in generate_plan(): {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5050)
