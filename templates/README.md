# 🥗 NutriAI: Personalized Indian Food Recommendation System

NutriAI is a full-stack web application designed to provide personalized, health-conscious Indian meal recommendations. By calculating the user's Body Mass Index (BMI) and analyzing their specific dietary constraints and fitness goals, NutriAI curates optimized meal choices from a dataset of 100 authentic Indian dishes.

## 🚀 Key Features

* **Intelligent Recommendation Engine:** Filters and ranks meals based on BMI status, fitness goals (weight loss, maintenance, gain), and diet preferences (Veg, Non-Veg, Low-Carb, No Onion/Garlic).
* **Interactive Macro Visualizations:** Features dynamic, responsive Doughnut charts (powered by Chart.js) detailing Protein, Carbohydrates, and Fat breakdowns for every recommended dish.
* **Secure User Authentication:** Implements a robust Two-Factor Authentication (2FA) system utilizing email-based OTPs via Gmail SMTP, complete with a local terminal fallback mechanism.
* **Bulletproof Data Management:** Integrates a self-healing backend script that automatically regenerates the `Healthy_100_Indian_Dishes_Final.csv` dataset if parsing or tokenization errors occur.
* **Seamless Action Integrations:** Direct external deep-linking to YouTube for recipe preparation tutorials, alongside direct ordering pathways via Swiggy and Zomato.

## 💻 Tech Stack

* **Backend:** Python, Flask
* **Database:** SQLite (`nutriai.db`), Pandas (Data processing)
* **Frontend:** HTML5, CSS3, JavaScript
* **Data Visualization:** Chart.js
* **Version Control:** Git & GitHub

## 🛠️ Local Installation & Setup

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/aaditee917-creator/ai-food-recommendation-system.git](https://github.com/aaditee917-creator/ai-food-recommendation-system.git)
   cd ai-food-recommendation-system