from flask import Flask, render_template, request
import requests

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/pokemon")
def pokemon():
    name = request.args.get("name")

    if not name:
        return "No Pokemon name provided"

    url = f"https://pokeapi.co/api/v2/pokemon/{name.lower()}"
    response = requests.get(url)

    if response.status_code != 200:
        return "Pokemon not found"

    data = response.json()

    pokemon_data = {
        "name": data["name"].title(),
        "height": data["height"],
        "weight": data["weight"],
        "types": ", ".join([t["type"]["name"] for t in data["types"]]),
        "image": data["sprites"]["front_default"]
    }

    return render_template("results.html", pokemon=pokemon_data)

if __name__ == "__main__":
    app.run(debug=True)
