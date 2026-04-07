from flask import Flask, render_template, request, redirect
import requests
import sqlite3

app = Flask(__name__)

# 🔥 DB INIT
def init_db():
    conn = sqlite3.connect('recipes.db')
    c = conn.cursor()

    c.execute('''
        CREATE TABLE IF NOT EXISTS favorites (
            id TEXT,
            name TEXT,
            image TEXT
        )
    ''')

    conn.commit()
    conn.close()

init_db()


# 🔥 DEFAULT RECIPES
def get_default_recipes():
    url = "https://www.themealdb.com/api/json/v1/1/search.php?s=chicken"
    data = requests.get(url).json()

    recipes = []
    if data['meals']:
        for meal in data['meals'][:6]:
            recipes.append({
                "name": meal['strMeal'],
                "image": meal['strMealThumb'],
                "id": meal['idMeal']
            })
    return recipes


# 🔥 HOME
@app.route('/', methods=['GET', 'POST'])
def home():
    recipes = []
    message = None

    if request.method == 'POST':
        dish = request.form.get('dish', '').strip()

        if not dish:
            return redirect('/')

        url = f"https://www.themealdb.com/api/json/v1/1/search.php?s={dish}"
        data = requests.get(url).json()

        if data['meals']:
            for meal in data['meals']:
                recipes.append({
                    "name": meal['strMeal'],
                    "image": meal['strMealThumb'],
                    "id": meal['idMeal']
                })
        else:
            message = "😢 No recipe found da!"
    else:
        recipes = get_default_recipes()

    return render_template("index.html", recipes=recipes, message=message)


# ❤️ ADD FAVORITE (POST METHOD FIX 🔥)
@app.route('/favorite', methods=['POST'])
def add_favorite():
    id = request.form['id']
    name = request.form['name']
    image = request.form['image']

    conn = sqlite3.connect('recipes.db')
    c = conn.cursor()

    c.execute("INSERT INTO favorites VALUES (?, ?, ?)", (id, name, image))

    conn.commit()
    conn.close()

    return redirect('/')


# ❤️ FAVORITES PAGE
@app.route('/favorites')
def favorites():
    conn = sqlite3.connect('recipes.db')
    c = conn.cursor()

    c.execute("SELECT * FROM favorites")
    data = c.fetchall()

    conn.close()

    return render_template("favorites.html", data=data)


# ❌ DELETE
@app.route('/delete/<id>')
def delete(id):
    conn = sqlite3.connect('recipes.db')
    c = conn.cursor()

    c.execute("DELETE FROM favorites WHERE id=?", (id,))

    conn.commit()
    conn.close()

    return redirect('/favorites')


# 🔥 DETAIL PAGE
@app.route('/recipe/<id>')
def recipe_detail(id):
    url = f"https://www.themealdb.com/api/json/v1/1/lookup.php?i={id}"
    data = requests.get(url).json()

    meal = data['meals'][0]

    raw = meal['strInstructions'].replace('\r', '')
    steps = [s.strip() for s in raw.split('\n') if s.strip()]

    recipe = {
        "name": meal['strMeal'],
        "image": meal['strMealThumb'],
        "steps": steps,
        "ingredients": []
    }

    for i in range(1, 21):
        ing = meal[f"strIngredient{i}"]
        measure = meal[f"strMeasure{i}"]

        if ing and ing.strip():
            recipe["ingredients"].append(f"{ing} - {measure}")

    return render_template("detail.html", recipe=recipe)


# 🔥 RUN (RENDER COMPATIBLE)
import os

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
