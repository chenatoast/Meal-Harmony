import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.linear_model import LinearRegression

# Load data
df = pd.read_csv("Food survey.csv")

# Extract dish ratings
dishes = df.iloc[:, 1:].copy()
dish_names = dishes.columns.values

# Simulated user IDs
users = {i: str(i) for i in range(36)}

# Calculate dish similarity
dish_similarity = cosine_similarity(dishes.T)

# Dictionary to track recently selected dishes for each user
recently_selected = {}

def item_similarity(interaction_matrix):
    item_interaction_matrix = interaction_matrix.T
    similarity_matrix = cosine_similarity(item_interaction_matrix)
    return similarity_matrix

def select_neighborhood(similarity_matrix, item_id, neighborhood_size):
    item_similarity_scores = similarity_matrix[item_id]
    sorted_indices = np.argsort(item_similarity_scores)[::-1]
    neighborhood = sorted_indices[1:neighborhood_size+1]  # Exclude the item itself
    return neighborhood

def update_data(user_id, selected_dish, neighborhood_size=5):
    hood = select_neighborhood(dish_similarity, selected_dish, neighborhood_size)

    for i in hood:
        adjustment = 0.5 if dish_similarity[selected_dish][i] < 0.5 else -0.7
        dish_similarity[selected_dish][i] += adjustment
        dishes.iloc[user_id][i] = np.clip(dishes.iloc[user_id][i] + adjustment, 1, 5)

    # Track the recently selected dish
    if user_id not in recently_selected:
        recently_selected[user_id] = []
    recently_selected[user_id].append(selected_dish)

    # Limit the number of tracked recent dishes (e.g., 3)
    if len(recently_selected[user_id]) > 3:
        recently_selected[user_id].pop(0)

# Train a linear regression model to predict ratings for new users
x = np.array(df.iloc[:, 1:])
y = np.array(df.iloc[:, 0]).reshape(-1, 1)
model = LinearRegression().fit(y, x)

def add_user(user_id, name):
    new_data = model.predict([[user_id]])
    dishes.loc[len(dishes)] = np.clip(new_data[0], 1, 5)
    users[user_id] = name
    print(f"Account created successfully! Welcome, {name}.")

def validate_user(user_id):
    return user_id in dishes.index

def get_recommendations(user_id, num_recommendations=5):
    user_ratings = dishes.iloc[user_id].values
    unrated_dishes = [(i, user_ratings[i]) for i in range(len(user_ratings)) if user_ratings[i] < 3]
    sorted_unrated = sorted(unrated_dishes, key=lambda x: x[1], reverse=True)
    
    # Exclude recently selected dishes from recommendations
    recommendations = [(i, score) for i, score in sorted_unrated if i not in recently_selected.get(user_id, [])]
    
    return recommendations[:num_recommendations]

def interact(user_id):
    print(f"Welcome, {users[user_id]}")
    while True:
        print("\nWhat would you like to do?")
        print("1: Get Recommendations")
        print("2: Select a Dish")
        print("3: View Recently Selected Dishes")
        print("99: Exit\n")

        choice = input("Enter your choice: ")

        if choice == "99":
            print("Thank you for using the Food Recommendation System. Goodbye!")
            break
        elif choice == "1":
            recommendations = get_recommendations(user_id)

            print("We recommend the following dishes:")
            for i, _ in recommendations:
                print(f"{i}: {dish_names[i]}")

            selection = int(input("\nEnter the number of your selected dish: "))
            update_data(user_id, selection)
            
            print("Your selection has been saved. Enjoy your meal!")
        elif choice == "2":
            print("Please enter the number of the dish you want to select:")
            for i, dish in enumerate(dish_names):
                print(f"{i}: {dish}")

            selection = int(input("\nEnter the number of your selected dish: "))
            update_data(user_id, selection)

            print("Your selection has been saved. Enjoy your meal!")
        elif choice == "3":
            print("Your recently selected dishes are:")
            for dish_id in recently_selected.get(user_id, []):
                print(dish_names[dish_id])
        else:
            print("Invalid choice. Please try again.")

# Main loop
while True:
    user_id = int(input("Enter your ID: "))
    if not validate_user(user_id):
        print("User doesn't exist, creating account...")
        name = input("Please enter your username: ")
        add_user(user_id, name)
    else:
        interact(user_id)
        break
