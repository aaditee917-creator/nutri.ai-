import pandas as pd

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


# ==========================================
# LOAD DATASET
# ==========================================

df = pd.read_csv("data/food_data.csv")


# ==========================================
# CREATE FOOD TEXT
# ==========================================

df["food_text"] = (
    df["food_name"].fillna("") + " " +
    df["category"].fillna("") + " " +
    df["meal_type"].fillna("") + " " +
    df["diet"].fillna("")
)


# ==========================================
# TF-IDF
# ==========================================

tfidf = TfidfVectorizer()

tfidf_matrix = tfidf.fit_transform(
    df["food_text"]
)


# ==========================================
# TEST RECOMMENDATION
# ==========================================

def test_profile(diet, meal_type, goal):

    user_text = (
        diet + " " +
        meal_type + " " +
        goal
    )

    user_vector = tfidf.transform(
        [user_text]
    )

    similarity_scores = cosine_similarity(
        user_vector,
        tfidf_matrix
    )[0]

    results = df.copy()

    results["similarity_score"] = similarity_scores

    results = results.sort_values(
        by="similarity_score",
        ascending=False
    )

    return results.head(5)


# ==========================================
# PROFILE A
# ==========================================

print("\n==============================")
print("PROFILE A")
print("==============================")

results_a = test_profile(
    "Vegetarian",
    "Breakfast",
    "Weight Loss"
)

print(
    results_a[
        ["food_name", "similarity_score"]
    ].to_string(index=False)
)


# ==========================================
# PROFILE B
# ==========================================

print("\n==============================")
print("PROFILE B")
print("==============================")

results_b = test_profile(
    "Non-Vegetarian",
    "Lunch",
    "Weight Gain"
)

print(
    results_b[
        ["food_name", "similarity_score"]
    ].to_string(index=False)
)