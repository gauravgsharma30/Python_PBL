from flask import Flask, request, redirect

app = Flask(__name__)


food_db = [
    {"name": "Apple", "calories": 95},
    {"name": "Banana", "calories": 105},
    {"name": "Egg", "calories": 78}
]

daily_intake = []
daily_goal = 2000

def generate_home_html():
    total_calories = sum(item.get('calories', 0) for item in daily_intake)
    remaining = max(daily_goal - total_calories, 0)
    progress = min(int((total_calories / daily_goal) * 100), 100) if daily_goal > 0 else 0

    
    intake_list = ""
    for idx, food in enumerate(daily_intake):
        intake_list += f"""
        <li>{food['name']} - {food['calories']} cal
            <form action="/remove_food" method="POST" style="display:inline;">
                <input type="hidden" name="index" value="{idx}">
                <button type="submit">Remove</button>
            </form>
        </li>"""
    if not daily_intake:
        intake_list = "<li>No food added yet.</li>"

   
    food_items_html = ""
    for food in food_db:
        food_items_html += f"""
        <li onclick="consumeFood('{food['name']}')">{food['name']} ({food['calories']} cal)</li>
        """

    
    if total_calories < daily_goal * 0.8:
        bar_color = "green"
    elif total_calories < daily_goal:
        bar_color = "orange"
    else:
        bar_color = "red"

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Calorie Counter</title>
        <link rel="stylesheet" href="/static/style.css">
        <script src="/static/script.js"></script>
    </head>
    <body>
        <div class="container">
            <h1>Calorie Counter</h1>

            <div class="goal">
                <form action="/set_goal" method="POST">
                    <label>Set Daily Goal:</label>
                    <input type="number" name="goal" value="{daily_goal}">
                    <button type="submit">Set</button>
                </form>

                <p style="color:{'red' if total_calories > daily_goal else 'black'}">
                    Total Calories Consumed: {total_calories} / {daily_goal}
                </p>
                <p>Calories Remaining: {remaining}</p>

                <div class="progress-bar">
                    <div class="progress" style="width:{progress}%; background-color:{bar_color};"></div>
                </div>

                <form action="/reset_intake" method="POST">
                    <button type="submit">Reset Daily Intake</button>
                </form>
            </div>

            <h2>Food Database</h2>
            <input type="text" id="search" placeholder="Search food..." onkeyup="filterFood()">
            <ul id="food_list">
                {food_items_html}
            </ul>
            <form action="/add_food" method="GET">
                <button type="submit">Add New Food</button>
            </form>

            <h2>Today's Intake ({len(daily_intake)} items)</h2>
            <ul>
                {intake_list}
            </ul>
        </div>
    </body>
    </html>
    """
    return html

def generate_add_food_html():
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Add Food</title>
        <link rel="stylesheet" href="/static/style.css">
    </head>
    <body>
        <div class="container">
            <h1>Add New Food</h1>
            <form action="/add_food" method="POST">
                <label>Food Name:</label>
                <input type="text" name="name" required><br>
                <label>Calories:</label>
                <input type="number" name="calories" required><br>
                <button type="submit">Add</button>
            </form>
            <form action="/" method="GET">
                <button type="submit">Back to Home</button>
            </form>
        </div>
    </body>
    </html>
    """
    return html


@app.route('/')
def home():
    return generate_home_html()

@app.route('/add_food', methods=['GET', 'POST'])
def add_food():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        calories = request.form.get('calories', 0)
        try:
            calories = int(calories)
            if name and calories >= 0:
                food_db.append({"name": name, "calories": calories})
        except:
            pass
        return redirect('/')
    return generate_add_food_html()

@app.route('/consume_food', methods=['POST'])
def consume_food():
    food_name = request.form.get('food_name', '')
    for food in food_db:
        if food.get('name') == food_name:
            daily_intake.append(food)
            break
    return redirect('/')

@app.route('/remove_food', methods=['POST'])
def remove_food():
    index = int(request.form.get('index', -1))
    if 0 <= index < len(daily_intake):
        daily_intake.pop(index)
    return redirect('/')

@app.route('/reset_intake', methods=['POST'])
def reset_intake():
    daily_intake.clear()
    return redirect('/')

@app.route('/set_goal', methods=['POST'])
def set_goal():
    global daily_goal
    try:
        new_goal = int(request.form.get('goal', daily_goal))
        if new_goal > 0:
            daily_goal = new_goal
    except:
        pass
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)
