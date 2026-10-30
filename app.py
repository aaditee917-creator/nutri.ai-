import random
import smtplib
from email.mime.text import MIMEText

from flask import Flask, render_template, request, redirect, url_for, session
import pandas as pd
import sqlite3
import os
import re
from werkzeug.security import generate_password_hash, check_password_hash

# =========================================================
# FLASK APPLICATION
# =========================================================
app = Flask(__name__)
app.secret_key = "nutriai_secret_key_2026"

DATABASE_FOLDER = "database"
DATABASE_NAME = os.path.join(DATABASE_FOLDER, "nutriai.db")
os.makedirs(DATABASE_FOLDER, exist_ok=True)

def get_db_connection():
    connection = sqlite3.connect(DATABASE_NAME)
    connection.row_factory = sqlite3.Row
    return connection

# =========================================================
# INITIALIZE DATABASE 
# =========================================================
def init_database():
    connection = get_db_connection()
    connection.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            age INTEGER,
            gender TEXT,
            height REAL,
            weight REAL,
            diet TEXT,
            goal TEXT,
            allergies TEXT
        )
    ''')
    connection.commit()
    connection.close()

init_database()

# =========================================================
# LOAD & CLEAN DATASET (BULLETPROOF VERSION)
# =========================================================
DATASET_PATH = "Healthy_100_Indian_Dishes_Final.csv"

def generate_perfect_dataset():
    dishes = [
        # Cereals
        ("Whole Wheat Roti", "Cereal", "No Garlic and Onion", "Lunch/Dinner", 297, 12.0, 61.2, 1.7, 10.5, 0.5, 3.5, 34),
        ("Bajra Roti", "Cereal", "No Garlic and Onion", "Lunch/Dinner", 361, 11.6, 67.5, 5.0, 11.5, 0.0, 8.0, 42),
        ("Jowar Roti", "Cereal", "No Garlic and Onion", "Lunch/Dinner", 349, 10.4, 72.6, 1.9, 9.7, 0.0, 4.1, 28),
        ("Ragi Roti", "Cereal", "No Garlic and Onion", "Breakfast/Lunch", 328, 7.3, 72.0, 1.3, 11.2, 0.0, 3.9, 344),
        ("Makki Roti", "Cereal", "No Garlic and Onion", "Lunch/Dinner", 365, 9.4, 74.3, 4.7, 7.3, 0.0, 2.7, 10),
        ("Multigrain Roti", "Cereal", "Veg", "Lunch/Dinner", 310, 13.5, 60.0, 2.5, 12.0, 0.5, 4.5, 45),
        ("Missi Roti", "Cereal", "Veg", "Lunch/Dinner", 330, 15.0, 55.0, 4.0, 10.0, 0.5, 5.0, 50),
        ("White Rice (Cooked)", "Cereal", "No Garlic and Onion", "Lunch/Dinner", 130, 2.7, 28.0, 0.3, 0.4, 0.1, 0.2, 10),
        ("Brown Rice (Cooked)", "Cereal", "No Garlic and Onion", "Lunch/Dinner", 111, 2.6, 23.0, 0.9, 1.8, 0.4, 0.4, 10),
        ("Quinoa Pulao", "Cereal", "Veg", "Lunch/Dinner", 120, 4.4, 21.3, 1.9, 2.8, 0.9, 1.5, 17),
        ("Daliya (Broken Wheat)", "Cereal", "No Garlic and Onion", "Breakfast", 150, 4.5, 32.0, 0.5, 4.0, 0.5, 1.5, 15),
        ("Oats Porridge", "Cereal", "Veg", "Breakfast", 389, 16.9, 66.3, 6.9, 10.6, 1.0, 4.7, 54),
        ("Poha", "Cereal", "Veg", "Breakfast", 250, 5.0, 45.0, 5.0, 3.0, 2.0, 2.5, 20),
        ("Upma", "Cereal", "Veg", "Breakfast", 220, 6.0, 38.0, 4.0, 4.0, 2.0, 1.5, 15),
        ("Millet Khichdi", "Cereal", "No Garlic and Onion", "Lunch/Dinner", 210, 7.5, 35.0, 3.5, 6.0, 0.5, 2.5, 40),
        ("Sabudana Khichdi", "Cereal", "No Garlic and Onion", "Breakfast", 320, 4.0, 55.0, 10.0, 3.0, 1.0, 1.0, 20),
        ("Lemon Rice", "Cereal", "No Garlic and Onion", "Lunch", 180, 3.5, 30.0, 5.0, 1.5, 0.5, 1.2, 12),
        ("Jeera Rice", "Cereal", "No Garlic and Onion", "Lunch/Dinner", 150, 3.0, 29.0, 3.0, 1.0, 0.1, 0.5, 15),
        ("Vegetable Pulao", "Cereal", "Veg", "Lunch/Dinner", 170, 4.0, 32.0, 3.5, 3.0, 1.0, 1.0, 25),
        ("Besan Chilla", "Cereal", "Veg", "Breakfast", 240, 10.0, 35.0, 6.0, 5.0, 2.0, 3.0, 30),
        
        # Pulses
        ("Toor Dal (Cooked)", "Pulse", "No Garlic and Onion", "Lunch/Dinner", 110, 7.0, 18.0, 1.0, 5.0, 0.5, 1.5, 25),
        ("Moong Dal (Cooked)", "Pulse", "No Garlic and Onion", "Lunch/Dinner", 105, 7.5, 17.0, 0.5, 5.5, 0.5, 1.8, 27),
        ("Chana Dal (Cooked)", "Pulse", "Veg", "Lunch/Dinner", 120, 8.0, 20.0, 1.2, 6.0, 1.0, 2.0, 30),
        ("Urad Dal (Cooked)", "Pulse", "No Garlic and Onion", "Lunch/Dinner", 130, 8.5, 21.0, 1.0, 5.5, 0.5, 2.2, 35),
        ("Masoor Dal (Cooked)", "Pulse", "Veg", "Lunch/Dinner", 115, 8.0, 19.0, 0.5, 5.0, 0.5, 2.5, 20),
        ("Rajma (Cooked)", "Pulse", "Veg", "Lunch/Dinner", 140, 9.0, 22.0, 1.0, 7.0, 1.5, 3.0, 40),
        ("Chole (Cooked)", "Pulse", "Veg", "Lunch/Dinner", 160, 8.5, 25.0, 2.5, 7.5, 2.0, 2.8, 45),
        ("Lobia (Black-eyed Peas)", "Pulse", "No Garlic and Onion", "Lunch/Dinner", 110, 8.0, 20.0, 0.5, 6.0, 1.0, 2.5, 24),
        ("Black Chickpeas (Kala Chana)", "Pulse", "Veg", "Lunch/Dinner", 150, 9.0, 24.0, 2.0, 8.0, 1.5, 3.5, 50),
        ("Green Gram (Whole Moong)", "Pulse", "No Garlic and Onion", "Lunch/Dinner", 120, 8.5, 21.0, 0.8, 7.0, 1.0, 2.5, 35),
        ("Kulthi Dal (Horse Gram)", "Pulse", "No Garlic and Onion", "Lunch/Dinner", 135, 9.0, 22.0, 1.0, 8.0, 0.5, 3.8, 60),
        ("Panchmel Dal", "Pulse", "Veg", "Lunch/Dinner", 125, 8.5, 20.0, 1.5, 6.0, 1.0, 2.2, 32),
        ("Dal Makhani (Low Fat)", "Pulse", "Veg", "Lunch/Dinner", 180, 9.0, 22.0, 6.0, 7.0, 1.5, 2.5, 55),
        ("Soya Chunks Curry", "Pulse", "Veg", "Lunch/Dinner", 145, 18.0, 12.0, 2.0, 5.0, 1.0, 4.0, 120),
        ("Tofu Curry", "Pulse", "Veg", "Lunch/Dinner", 130, 12.0, 6.0, 7.0, 2.0, 1.0, 2.5, 200),
        
        # Veg
        ("Palak Paneer", "Vegetable", "No Garlic and Onion", "Lunch/Dinner", 185, 9.5, 4.2, 14.5, 1.5, 1.0, 1.8, 180),
        ("Matar Paneer", "Vegetable", "Veg", "Lunch/Dinner", 210, 10.0, 12.0, 13.0, 4.0, 3.0, 1.5, 160),
        ("Bhindi Masala", "Vegetable", "Veg", "Lunch/Dinner", 120, 2.5, 10.0, 8.0, 4.0, 2.0, 1.0, 50),
        ("Baingan Bharta", "Vegetable", "Veg", "Lunch/Dinner", 95, 2.0, 8.0, 6.0, 4.0, 3.0, 0.8, 30),
        ("Aloo Gobi", "Vegetable", "Veg", "Lunch/Dinner", 110, 3.0, 15.0, 5.0, 4.0, 2.5, 1.2, 40),
        ("Mix Veg Curry", "Vegetable", "Veg", "Lunch/Dinner", 130, 3.5, 14.0, 6.0, 5.0, 3.5, 1.5, 55),
        ("Lauki Sabzi", "Vegetable", "No Garlic and Onion", "Lunch/Dinner", 75, 1.5, 6.0, 5.0, 2.5, 2.0, 0.5, 25),
        ("Torai Sabzi (Ridge Gourd)", "Vegetable", "No Garlic and Onion", "Lunch/Dinner", 65, 1.2, 5.0, 4.5, 2.0, 1.5, 0.6, 20),
        ("Karela Sabzi (Bitter Gourd)", "Vegetable", "Veg", "Lunch/Dinner", 90, 2.0, 8.0, 6.0, 3.5, 1.0, 1.0, 35),
        ("Cabbage Thoran", "Vegetable", "No Garlic and Onion", "Lunch/Dinner", 100, 2.5, 7.0, 7.0, 3.5, 2.0, 0.8, 45),
        ("Beans Poriyal", "Vegetable", "No Garlic and Onion", "Lunch/Dinner", 115, 3.5, 9.0, 7.5, 4.0, 1.5, 1.2, 50),
        ("Mushroom Masala", "Vegetable", "Veg", "Lunch/Dinner", 125, 4.0, 8.0, 8.0, 2.5, 2.0, 1.5, 20),
        ("Capsicum Besan", "Vegetable", "No Garlic and Onion", "Lunch/Dinner", 140, 5.0, 12.0, 8.0, 3.0, 2.5, 1.5, 30),
        ("Pumpkin Sabzi", "Vegetable", "No Garlic and Onion", "Lunch/Dinner", 85, 1.5, 9.0, 5.0, 2.5, 3.5, 0.7, 25),
        ("Gajar Matar", "Vegetable", "Veg", "Lunch/Dinner", 105, 3.0, 14.0, 4.0, 5.0, 6.0, 1.0, 40),
        ("Methi Malai Matar (Low Fat)", "Vegetable", "Veg", "Lunch/Dinner", 150, 5.0, 12.0, 9.0, 4.0, 3.0, 1.5, 80),
        ("Cauliflower Curry", "Vegetable", "Veg", "Lunch/Dinner", 95, 2.5, 8.0, 6.0, 3.5, 2.0, 0.9, 35),
        ("Beetroot Poriyal", "Vegetable", "No Garlic and Onion", "Lunch/Dinner", 110, 2.5, 12.0, 6.0, 4.0, 7.0, 1.2, 30),
        ("Raw Banana Curry", "Vegetable", "No Garlic and Onion", "Lunch/Dinner", 130, 2.0, 20.0, 5.0, 3.5, 1.5, 1.0, 25),
        ("Jackfruit Sabzi (Kathal)", "Vegetable", "Veg", "Lunch/Dinner", 145, 3.5, 18.0, 6.5, 6.0, 3.0, 1.5, 40),

        # Meat
        ("Chicken Curry (Lean)", "Meat", "Non-Veg", "Lunch/Dinner", 165, 22.0, 5.0, 6.0, 1.0, 1.0, 1.5, 25),
        ("Chicken Tikka", "Meat", "Low-Carb", "Dinner/Snack", 175, 24.5, 2.5, 7.5, 0.5, 1.0, 1.2, 30),
        ("Egg Curry", "Meat", "Non-Veg", "Lunch/Dinner", 180, 12.0, 6.0, 12.0, 1.0, 1.5, 1.8, 60),
        ("Boiled Egg", "Meat", "Low-Carb", "Breakfast/Snack", 155, 12.6, 1.1, 10.6, 0.0, 1.1, 1.2, 50),
        ("Masala Omelette", "Meat", "Low-Carb", "Breakfast", 190, 13.0, 3.0, 14.0, 0.5, 1.0, 1.5, 55),
        ("Fish Curry (Rohu)", "Meat", "Non-Veg", "Lunch/Dinner", 140, 16.0, 4.0, 6.5, 1.0, 0.5, 1.5, 300),
        ("Prawn Masala", "Meat", "Non-Veg", "Lunch/Dinner", 155, 18.0, 5.0, 7.0, 1.0, 1.0, 2.0, 60),
        ("Mutton Rogan Josh (Lean)", "Meat", "Non-Veg", "Lunch/Dinner", 210, 20.0, 6.0, 12.0, 1.5, 1.0, 3.0, 40),
        ("Chicken Seekh Kebab", "Meat", "Low-Carb", "Snack/Dinner", 185, 21.0, 3.0, 9.0, 1.0, 0.5, 1.8, 35),
        ("Egg Bhurji", "Meat", "Low-Carb", "Breakfast", 200, 13.5, 4.0, 15.0, 1.0, 1.5, 1.9, 65),
        ("Tandoori Chicken", "Meat", "Low-Carb", "Dinner/Snack", 160, 23.0, 2.0, 6.5, 0.5, 0.5, 1.2, 25),
        ("Fish Fry (Shallow)", "Meat", "Non-Veg", "Lunch/Dinner", 190, 18.0, 4.0, 11.0, 0.5, 0.5, 1.0, 250),
        ("Murg Saagwala", "Meat", "Non-Veg", "Lunch/Dinner", 170, 22.0, 6.0, 7.0, 2.5, 1.0, 2.5, 120),
        ("Chicken Korma", "Meat", "Non-Veg", "Lunch/Dinner", 220, 20.0, 8.0, 12.0, 1.5, 2.0, 1.5, 50),
        ("Fish Tikka", "Meat", "Low-Carb", "Snack/Dinner", 150, 19.0, 2.0, 7.0, 0.5, 0.5, 1.0, 220),

        # Snacks & Sides
        ("Idli", "Dish", "No Garlic and Onion", "Breakfast", 150, 4.5, 32.0, 0.5, 2.0, 0.5, 1.0, 15),
        ("Masala Dosa", "Dish", "Veg", "Breakfast", 210, 5.5, 32.0, 7.0, 2.5, 1.5, 1.2, 25),
        ("Uttappam", "Dish", "Veg", "Breakfast", 180, 5.0, 28.0, 5.5, 3.0, 1.5, 1.5, 20),
        ("Dhokla (Besan)", "Dish", "No Garlic and Onion", "Breakfast/Snack", 160, 6.0, 25.0, 4.0, 3.0, 4.0, 1.8, 25),
        ("Khandvi", "Dish", "No Garlic and Onion", "Snack", 180, 6.0, 20.0, 8.0, 4.0, 3.0, 1.5, 30),
        ("Pesarattu (Moong Dosa)", "Dish", "Veg", "Breakfast", 190, 8.0, 30.0, 4.0, 4.5, 1.0, 2.5, 40),
        ("Roasted Makhana", "Dish", "No Garlic and Onion", "Snack", 350, 9.7, 77.0, 0.1, 14.5, 0.0, 1.4, 60),
        ("Chana Chaat", "Dish", "Veg", "Snack", 140, 7.0, 22.0, 3.0, 6.0, 2.5, 2.5, 45),
        ("Sprout Salad", "Dish", "No Garlic and Onion", "Snack", 115, 8.5, 18.0, 0.5, 4.5, 1.2, 2.0, 35),
        ("Peanut Salad", "Dish", "No Garlic and Onion", "Snack", 310, 12.0, 15.0, 24.0, 5.0, 2.0, 2.2, 50),
        ("Bhel Puri (No Sev)", "Dish", "Veg", "Snack", 150, 3.5, 30.0, 2.0, 3.0, 3.0, 1.5, 20),
        ("Baked Panipuri", "Dish", "Veg", "Snack", 120, 3.0, 24.0, 1.5, 3.0, 1.5, 1.0, 15),
        ("Muthia", "Dish", "No Garlic and Onion", "Snack", 170, 5.0, 25.0, 5.0, 4.0, 2.0, 2.0, 40),
        ("Patra", "Dish", "No Garlic and Onion", "Snack", 185, 4.5, 28.0, 6.0, 5.0, 3.0, 2.5, 80),
        ("Roasted Chana", "Dish", "No Garlic and Onion", "Snack", 360, 18.5, 60.0, 5.0, 15.0, 1.0, 6.0, 105),

        # Soups, Dairy, Chutneys, Desserts
        ("Rasam", "Dish", "No Garlic and Onion", "Soup/Side", 60, 2.0, 10.0, 1.5, 2.0, 2.0, 1.0, 15),
        ("Tomato Soup (Indian Style)", "Dish", "Veg", "Soup", 75, 1.5, 12.0, 2.5, 3.0, 6.0, 0.8, 20),
        ("Sweet Corn Soup", "Dish", "Veg", "Soup", 90, 2.5, 18.0, 1.5, 2.0, 4.0, 0.5, 10),
        ("Spinach Soup", "Dish", "No Garlic and Onion", "Soup", 85, 3.0, 8.0, 4.5, 2.5, 2.0, 2.0, 90),
        ("Cucumber Raita", "Dairy", "No Garlic and Onion", "Side", 70, 3.0, 5.0, 4.0, 0.5, 4.0, 0.2, 110),
        ("Plain Curd", "Dairy", "No Garlic and Onion", "Side", 98, 3.3, 4.7, 4.3, 0.0, 4.7, 0.1, 121),
        ("Paneer Tikka", "Dairy", "Low-Carb", "Snack/Dinner", 260, 17.0, 5.0, 19.0, 1.0, 2.0, 1.0, 200),
        ("Chaas (Buttermilk)", "Dairy", "No Garlic and Onion", "Drink", 40, 2.0, 3.0, 2.0, 0.0, 2.5, 0.1, 80),
        ("Plain Lassi (No Sugar)", "Dairy", "No Garlic and Onion", "Drink", 110, 4.0, 6.0, 7.0, 0.0, 5.5, 0.1, 150),
        ("Sambar", "Dish", "Veg", "Side", 110, 4.5, 18.0, 2.5, 4.0, 3.0, 1.5, 40),
        ("Coconut Chutney", "Dish", "No Garlic and Onion", "Side", 180, 2.0, 6.0, 17.0, 4.0, 2.0, 1.0, 15),
        ("Mint Coriander Chutney", "Dish", "Veg", "Side", 50, 2.0, 8.0, 1.0, 3.0, 2.0, 1.5, 40),
        ("Tomato Chutney", "Dish", "Veg", "Side", 65, 1.5, 10.0, 2.0, 2.5, 5.0, 0.8, 20),
        ("Carrot Halwa (Low Sugar)", "Dish", "No Garlic and Onion", "Dessert", 190, 4.0, 25.0, 8.0, 3.0, 12.0, 1.0, 100),
        ("Phirni (Sugar Free)", "Dish", "No Garlic and Onion", "Dessert", 140, 5.0, 20.0, 4.5, 1.0, 5.0, 0.5, 130)
    ]
    df = pd.DataFrame(dishes, columns=["name", "category", "diet", "meal_type", "calories", "protein", "carbs", "fat", "fiber", "sugar", "iron", "calcium"])
    df.to_csv(DATASET_PATH, index=False)
    print("✅ GENERATED FRESH 100-DISH DATASET SUCCESSFULLY!")
    return df

# Try to load the CSV safely, if it fails, delete it and regenerate it
try:
    if not os.path.exists(DATASET_PATH):
        df = generate_perfect_dataset()
    else:
        df = pd.read_csv(DATASET_PATH)
        
    # Test if it's corrupted
    if len(df.columns) < 5 or "calories" not in df.columns:
        raise ValueError("File is corrupted or has wrong columns.")
        
except Exception as e:
    print(f"⚠️ Dataset '{DATASET_PATH}' was missing or corrupted. Fixing automatically...")
    if os.path.exists(DATASET_PATH):
        os.remove(DATASET_PATH)
    df = generate_perfect_dataset()

# Clean up columns
df.columns = df.columns.str.strip().str.lower()
required_columns = ["name", "category", "diet", "meal_type", "calories", "protein", "carbs", "fat", "fiber", "sugar", "iron", "calcium"]
for column in required_columns:
    if column not in df.columns:
        df[column] = 0

numeric_columns = ["calories", "protein", "carbs", "fat", "fiber", "sugar", "iron", "calcium"]
for column in numeric_columns:
    df[column] = pd.to_numeric(df[column], errors="coerce").fillna(0)

df = df.dropna(subset=["name"])
df = df.drop_duplicates(subset=["name"])

print("="*50)
print(f"✅ SUCCESSFULLY LOADED {len(df)} DISHES FROM THE DATABASE!")
print("="*50)

# =========================================================
# BMI LOGIC
# =========================================================
def calculate_bmi(weight, height):
    if height <= 0: return 0
    height_m = height / 100
    bmi = weight / (height_m ** 2)
    return round(bmi, 1)

def bmi_category(bmi):
    if bmi < 18.5: return "Underweight"
    elif bmi < 25: return "Normal"
    elif bmi < 30: return "Overweight"
    else: return "Obese"

# =========================================================
# FOOD RECOMMENDATION ENGINE
# =========================================================
def recommend_foods(diet, meal_type, goal, bmi, allergies="", top_n=10):
    results = df.copy()

    # 1. FILTER OUT ALLERGIES FIRST
    if allergies:
        # Ignore words like 'none', 'no', 'na', 'nothing' which users often type
        ignore_words = ['none', 'no', 'na', 'nothing', 'n/a', 'nil']
        allergy_list = [a.strip().lower() for a in allergies.split(",")]
        
        for allergy in allergy_list:
            if allergy and allergy not in ignore_words:
                results = results[~results["name"].str.lower().str.contains(allergy)]
                
    if results.empty:
        return results

    diet_input = str(diet).strip().lower()
    meal_input = str(meal_type).strip().lower()
    goal_input = str(goal).strip().lower()

    # Fix: Use 'contains' for meal types since some are 'Lunch/Dinner'
    results["diet_score"] = (results["diet"].astype(str).str.strip().str.lower() == diet_input).astype(float)
    results["meal_score"] = (results["meal_type"].astype(str).str.strip().str.lower().str.contains(meal_input)).astype(float)

    max_calories = results["calories"].max()
    min_calories = results["calories"].min()
    calorie_range = max_calories - min_calories if (max_calories - min_calories) > 0 else 1

    if goal_input == "weight loss":
        results["calorie_score"] = (max_calories - results["calories"]) / calorie_range
    elif goal_input == "weight gain":
        results["calorie_score"] = (results["calories"] - min_calories) / calorie_range
    else:
        target_calories = (min_calories + max_calories) / 2
        results["calorie_score"] = (1 - (abs(results["calories"] - target_calories) / calorie_range))

    max_protein = results["protein"].max() if results["protein"].max() > 0 else 1
    results["protein_score"] = (results["protein"] / max_protein)

    max_fiber = results["fiber"].max() if results["fiber"].max() > 0 else 1
    results["fiber_score"] = (results["fiber"] / max_fiber)

    max_sugar = results["sugar"].max() if results["sugar"].max() > 0 else 1
    results["sugar_score"] = (1 - (results["sugar"] / max_sugar))
    
    # Adding Iron and Calcium for RDA Capping mechanism
    max_iron = results["iron"].max() if results["iron"].max() > 0 else 1
    results["iron_score"] = (results["iron"] / max_iron)

    max_calcium = results["calcium"].max() if results["calcium"].max() > 0 else 1
    results["calcium_score"] = (results["calcium"] / max_calcium)

    if bmi < 18.5:
        results["bmi_score"] = (results["protein_score"] * 0.45 + results["calorie_score"] * 0.35 + results["fiber_score"] * 0.20)
    elif bmi < 25:
        results["bmi_score"] = (results["protein_score"] * 0.35 + results["calorie_score"] * 0.35 + results["fiber_score"] * 0.20 + results["sugar_score"] * 0.10)
    elif bmi < 30:
        results["bmi_score"] = (results["calorie_score"] * 0.45 + results["protein_score"] * 0.25 + results["fiber_score"] * 0.20 + results["sugar_score"] * 0.10)
    else:
        results["bmi_score"] = (results["calorie_score"] * 0.50 + results["protein_score"] * 0.20 + results["fiber_score"] * 0.20 + results["sugar_score"] * 0.10)

    # Updated Final Score
    results["final_score"] = (
        results["diet_score"] * 0.20 + results["meal_score"] * 0.20 + results["calorie_score"] * 0.15 +
        results["protein_score"] * 0.10 + results["fiber_score"] * 0.10 + results["sugar_score"] * 0.05 + 
        results["bmi_score"] * 0.10 + results["iron_score"] * 0.05 + results["calcium_score"] * 0.05
    )

    results = results.sort_values(by="final_score", ascending=False)
    return results.head(top_n)

# =========================================================
# EMAIL OTP FUNCTION FOR 2FA
# =========================================================
def send_otp_email(user_email, otp_code):
    # Your project's sender email credentials
    sender_email = "YOUR_EMAIL@gmail.com"  # <--- REPLACE THIS WITH YOUR GMAIL ADDRESS
    sender_password = "ljymycasizenxujz" # App Password (spaces removed)
    
    # FAIL-SAFE: Always print to terminal so you never get locked out during testing!
    print("\n========================================")
    print(f"🔑 YOUR NUTRIAI 2FA OTP IS: {otp_code}")
    print("========================================\n")

    msg = MIMEText(f"Hello!\n\nYour NutriAI login verification code is: {otp_code}\n\nDo not share this with anyone.")
    msg['Subject'] = 'NutriAI 2-Step Verification Code'
    msg['From'] = sender_email
    msg['To'] = user_email

    try:
        # Using port 587 (TLS) to fix the "Connection unexpectedly closed" error
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.ehlo()
            server.starttls() # Secure the connection
            server.login(sender_email, sender_password)
            server.send_message(msg)
            print(f"✅ Real email successfully sent to {user_email}")
    except Exception as e:
        print("❌ Email sending failed:", e)
        print("⚠️ NOTE: You can still log in using the OTP printed above!")

# =========================================================
# ROUTES
# =========================================================
@app.route("/")
def home():
    return render_template("home.html", user=session.get("user"))

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        if not name or not email or not password:
            return render_template("signup.html", error="Please fill all fields.")
            
        email_pattern = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"
        if not re.match(email_pattern, email):
            return render_template("signup.html", error="Invalid email address.")
        if len(password) < 6:
            return render_template("signup.html", error="Password must be at least 6 characters.")

        connection = get_db_connection()
        if connection.execute("SELECT id FROM users WHERE email = ?", (email,)).fetchone():
            connection.close()
            return render_template("signup.html", error="Email already exists.")

        hashed_password = generate_password_hash(password)
        connection.execute("INSERT INTO users (name, email, password) VALUES (?, ?, ?)", (name, email, hashed_password))
        connection.commit()
        connection.close()
        return redirect(url_for("login", success="Account created! Please login."))
    return render_template("signup.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    success = request.args.get("success")
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        
        connection = get_db_connection()
        user = connection.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
        connection.close()

        if user is None or not check_password_hash(user["password"], password):
            return render_template("login.html", error="Invalid credentials.", success=success)

        # ---> START 2FA INSTEAD OF LOGGING IN DIRECTLY <---
        otp = str(random.randint(100000, 999999))
        session['pending_user'] = {"id": user["id"], "name": user["name"], "email": user["email"]}
        session['otp'] = otp
        
        # Trigger the terminal print/email
        send_otp_email(email, otp)
        
        return redirect(url_for('verify_2fa'))
        
    return render_template("login.html", success=success)

@app.route("/verify_2fa", methods=["GET", "POST"])
def verify_2fa():
    if 'pending_user' not in session:
        return redirect(url_for('login'))
        
    if request.method == 'POST':
        user_entered_otp = request.form.get('otp', '').strip()
        
        if user_entered_otp == session.get('otp'):
            # 2FA SUCCESSFUL! 
            session['user'] = session['pending_user']
            session.pop('pending_user', None)
            session.pop('otp', None)
            return redirect(url_for('recommend'))
        else:
            return render_template('verify_2fa.html', error="Invalid verification code. Please try again.", email=session.get('pending_user', {}).get('email'))
            
    return render_template('verify_2fa.html', email=session.get('pending_user', {}).get('email'))

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))

@app.route("/recommend", methods=["GET", "POST"])
def recommend():
    if "user" not in session:
        return redirect(url_for("login"))

    connection = get_db_connection()
    user_profile = connection.execute("SELECT * FROM users WHERE id = ?", (session["user"]["id"],)).fetchone()
    
    recommendations, bmi, bmi_status, error = None, None, None, None

    if request.method == "POST":
        try:
            age = int(request.form.get("age", 0))
            gender = request.form.get("gender", "").strip()
            height = float(request.form.get("height", 0))
            weight = float(request.form.get("weight", 0))
            diet = request.form.get("diet", "").strip()
            meal_type = request.form.get("meal_type", "").strip()
            goal = request.form.get("goal", "").strip()
            allergies = request.form.get("allergies", "").strip()
        except ValueError:
            return render_template("index.html", user=session.get("user"), user_profile=user_profile, error="Invalid input.")

        connection.execute('''
            UPDATE users SET age=?, gender=?, height=?, weight=?, diet=?, goal=?, allergies=? WHERE id=?
        ''', (age, gender, height, weight, diet, goal, allergies, session["user"]["id"]))
        connection.commit()

        user_profile = connection.execute("SELECT * FROM users WHERE id = ?", (session["user"]["id"],)).fetchone()

        bmi = calculate_bmi(weight, height)
        bmi_status = bmi_category(bmi)
        
        recommendation_df = recommend_foods(diet, meal_type, goal, bmi, allergies, top_n=10)
        
        if recommendation_df.empty:
            error = "No foods found matching your criteria and allergies. Try adjusting your filters."
        else:
            # === NEW: IMAGE CATEGORY MAPPING ===
            category_images = {
                "Cereal": "https://images.unsplash.com/photo-1505253716362-afaea1d3d1af?auto=format&fit=crop&w=400&q=80",
                "Pulse": "https://images.unsplash.com/photo-1546833999-b9f581a1996d?auto=format&fit=crop&w=400&q=80",
                "Vegetable": "https://images.unsplash.com/photo-1565557623262-b51c2513a641?auto=format&fit=crop&w=400&q=80",
                "Meat": "https://images.unsplash.com/photo-1604908176997-125f25cc6f3d?auto=format&fit=crop&w=400&q=80",
                "Dairy": "https://images.unsplash.com/photo-1550583724-b2692b85b150?auto=format&fit=crop&w=400&q=80",
                "Dish": "https://images.unsplash.com/photo-1601050690597-df0568f70950?auto=format&fit=crop&w=400&q=80"
            }

            recommendations = recommendation_df.to_dict(orient="records")
            for food in recommendations:
                food["ai_score"] = round(float(food["final_score"]) * 100, 0)
                # Assign the image URL based on the category
                food["image_url"] = category_images.get(food.get("category", "Dish"), category_images["Dish"])
                
    connection.close()
    return render_template("index.html", recommendations=recommendations, bmi=bmi, bmi_status=bmi_status, user=session.get("user"), user_profile=user_profile, error=error)

if __name__ == "__main__":
    app.run(debug=True)