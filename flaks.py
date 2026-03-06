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
        return "No Pokémon name provided."

    url = f"https://pokeapi.co/api/v2/pokemon/{name.lower()}"

    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
    except requests.exceptions.HTTPError:
        return "Pokémon not found or spelling mistake D:"
    except requests.exceptions.Timeout:
        return "Request timed out. Please try again."
    except requests.exceptions.RequestException:
        return "Error fetching Pokémon data. Try again later."

    data = response.json()

    height_m = float(data["height"]) / 10
    weight_kg = float(data["weight"]) / 10

    pokemon_data = {
        "name": data["name"].title(),
        "id": data["id"],
        "base_xp": data["base_experience"],
        "height": height_m,
        "weight": weight_kg,
        "types": ", ".join([t["type"]["name"] for t in data["types"]]),
        "image": data["sprites"]["versions"]["generation-viii"]["brilliant-diamond-shining-pearl"]["front_default"]
    }

    return render_template("results.html", pokemon=pokemon_data)

if __name__ == "__main__":
    # Use host 0.0.0.0 and port from environment for Render
    import os
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=True)