import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Load dataset
data = pd.read_csv("data/food_data.csv")

print("Dataset loaded successfully!")
print("Total foods:", len(data))

# Combine important food features
data["features"] = (
    data["category"].astype(str) + " " +
    data["meal_type"].astype(str) + " " +
    data["diet"].astype(str)
)

# Convert text features into numerical vectors
vectorizer = TfidfVectorizer()
feature_vectors = vectorizer.fit_transform(data["features"])

# Calculate similarity between foods
similarity = cosine_similarity(feature_vectors)


def recommend_food(food_name, number_of_recommendations=5):

    matches = data[
        data["food_name"].str.lower() == food_name.lower()
    ]

    if matches.empty:
        print("Food not found!")
        return

    food_index = matches.index[0]

    similarity_scores = list(
        enumerate(similarity[food_index])
    )

    similarity_scores = sorted(
        similarity_scores,
        key=lambda x: x[1],
        reverse=True
    )

    print("\nRecommended foods for:", food_name)
    print("--------------------------------")

    count = 0

    for index, score in similarity_scores:

        if index == food_index:
            continue

        print(
            data.iloc[index]["food_name"],
            "| Similarity:",
            round(score, 2)
        )

        count += 1

        if count == number_of_recommendations:
            break


# Test the AI recommendation system
recommend_food("Oats Banana Bowl")