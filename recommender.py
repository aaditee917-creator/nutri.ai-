import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


# ==========================================
# 1. LOAD FOOD DATASET
# ==========================================

df = pd.read_csv("data/food_data.csv")

print("Dataset loaded successfully!")
print("Total foods:", len(df))


# ==========================================
# 2. CREATE TEXT FEATURES
# ==========================================

df["features"] = (
    df["category"].fillna("") + " " +
    df["meal_type"].fillna("") + " " +
    df["diet"].fillna("")
)


# ==========================================
# 3. CONVERT TEXT INTO TF-IDF VECTORS
# ==========================================

vectorizer = TfidfVectorizer()

feature_matrix = vectorizer.fit_transform(df["features"])


# ==========================================
# 4. CALCULATE SIMILARITY
# ==========================================

similarity_matrix = cosine_similarity(feature_matrix)


# ==========================================
# 5. PERSONALIZED RECOMMENDATION FUNCTION
# ==========================================

def recommend_foods(diet, meal_type, goal, top_n=5):

    # Make a copy so we can calculate scores
    results = df.copy()

    # --------------------------------------
    # Diet matching
    # --------------------------------------

    results["diet_score"] = (
        results["diet"].str.lower() == diet.lower()
    ).astype(int)

    # --------------------------------------
    # Meal type matching
    # --------------------------------------

    results["meal_score"] = (
        results["meal_type"].str.lower() == meal_type.lower()
    ).astype(int)

    # --------------------------------------
    # Goal scoring
    # --------------------------------------

    if goal.lower() == "weight loss":

        # Prefer foods with lower calories
        calorie_score = 1 - (
            results["calories"] / results["calories"].max()
        )

    elif goal.lower() == "weight gain":

        # Prefer foods with higher calories
        calorie_score = (
            results["calories"] / results["calories"].max()
        )

    else:

        # For maintenance
        calorie_score = 0.5

    results["calorie_score"] = calorie_score

    # --------------------------------------
    # Protein score
    # --------------------------------------

    protein_score = (
        results["protein"] / results["protein"].max()
    )

    results["protein_score"] = protein_score

    # --------------------------------------
    # FINAL SCORE
    # --------------------------------------

    results["final_score"] = (
        results["diet_score"] * 0.40 +
        results["meal_score"] * 0.30 +
        results["calorie_score"] * 0.20 +
        results["protein_score"] * 0.10
    )

    # --------------------------------------
    # Sort recommendations
    # --------------------------------------

    results = results.sort_values(
        by="final_score",
        ascending=False
    )

    return results.head(top_n)


# ==========================================
# 6. GET USER INFORMATION
# ==========================================

print("\n")
print("==========================================")
print("       AI FOOD RECOMMENDATION SYSTEM")
print("==========================================")

diet = input(
    "Enter your diet (Vegetarian/Non-Vegetarian): "
)

meal_type = input(
    "Enter meal type (Breakfast/Lunch/Dinner): "
)

goal = input(
    "Enter your goal (Weight Loss/Weight Gain/Maintain): "
)


# ==========================================
# 7. GENERATE RECOMMENDATIONS
# ==========================================

recommendations = recommend_foods(
    diet,
    meal_type,
    goal
)


# ==========================================
# 8. DISPLAY RESULTS
# ==========================================

print("\n")
print("Recommended foods for you:")
print("------------------------------------------")

for _, food in recommendations.iterrows():

    print(
        f"{food['food_name']} | "
        f"Calories: {food['calories']} kcal | "
        f"Protein: {food['protein']} g | "
        f"Score: {food['final_score']:.2f}"
    )
    