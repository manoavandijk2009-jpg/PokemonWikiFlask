from flask import Flask, render_template, request
import requests
import os

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

    # --- SPRITE LOGIC ---

    # 1️⃣ Official artwork (priority)
    artwork_sprite = data["sprites"]["other"]["official-artwork"].get("front_default")
    artwork_shiny = data["sprites"]["other"]["official-artwork"].get("front_shiny")

    # 2️⃣ Generation VIII BD/SP sprites
    bd_sp_sprite = data["sprites"]["versions"]["generation-viii"]["brilliant-diamond-shining-pearl"].get("front_default")
    bd_sp_shiny = data["sprites"]["versions"]["generation-viii"]["brilliant-diamond-shining-pearl"].get("front_shiny")

    # 3️⃣ Older generations fallback
    old_generations = []
    old_generations_shiny = []
    for gen in data["sprites"]["versions"]:
        for version in data["sprites"]["versions"][gen]:
            v = data["sprites"]["versions"][gen][version]
            sprite = v.get("front_default")
            sprite_shiny = v.get("front_shiny")
            if sprite:
                old_generations.append(sprite)
            if sprite_shiny:
                old_generations_shiny.append(sprite_shiny)

    # 4️⃣ Final fallback: official artwork → BD/SP → old generations → root default
    fallback_sprite = artwork_sprite or bd_sp_sprite or (old_generations[0] if old_generations else data["sprites"].get("front_default"))
    fallback_shiny = artwork_shiny or bd_sp_shiny or (old_generations_shiny[0] if old_generations_shiny else data["sprites"].get("front_shiny"))

    # --- POKEMON DATA ---
    pokemon_data = {
        "name": data["name"].title(),
        "id": data["id"],
        "base_xp": data["base_experience"],
        "height": height_m,
        "weight": weight_kg,
        "types": ", ".join([t["type"]["name"] for t in data["types"]]),
        "image": fallback_sprite,
        "shiny_image": fallback_shiny
    }

    return render_template("results.html", pokemon=pokemon_data)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=True)