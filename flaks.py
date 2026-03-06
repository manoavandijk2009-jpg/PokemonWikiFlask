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

    # 1️⃣ Try Gen VIII Brilliant Diamond/Shining Pearl first
    bd_sp_sprite = data["sprites"]["versions"]["generation-viii"]["brilliant-diamond-shining-pearl"]["front_default"]

    # 2️⃣ Official artwork
    artwork_sprite = data["sprites"]["other"]["official-artwork"]["front_default"]

    # 3️⃣ Older versions fallback (Gen I → Gen VII)
    old_generations = []
    for gen in data["sprites"]["versions"]:
        for version in data["sprites"]["versions"][gen]:
            sprite = data["sprites"]["versions"][gen][version].get("front_default")
            if sprite:
                old_generations.append(sprite)

    # 4️⃣ Fallback priority: BD/SP → artwork → oldest available version
    fallback_sprite = bd_sp_sprite or artwork_sprite or (old_generations[0] if old_generations else data["sprites"]["front_default"])

    pokemon_data = {
        "name": data["name"].title(),
        "id": data["id"],
        "base_xp": data["base_experience"],
        "height": height_m,
        "weight": weight_kg,
        "types": ", ".join([t["type"]["name"] for t in data["types"]]),
        "image": fallback_sprite
    }

    return render_template("results.html", pokemon=pokemon_data)

if __name__ == "__main__":
    # Use host 0.0.0.0 and port from environment for Render
    import os
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=True)