import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.linear_model import LinearRegression

# Load data
df = pd.read_csv("Food survey.csv")

# Set UserID as index and extract dish ratings
df.set_index('UserID', inplace=True)
dishes = df.copy()
dish_names = dishes.columns.values

# Simulate user IDs from the CSV file
users = {user_id: str(user_id) for user_id in df.index}

# Calculate dish similarity
dish_similarity = cosine_similarity(dishes.T)

# Dictionary to track recently selected dishes for each user
recently_selected = {}

def select_neighborhood(similarity_matrix, item_id, neighborhood_size):
    item_similarity_scores = similarity_matrix[item_id]
    sorted_indices = np.argsort(item_similarity_scores)[::-1]
    neighborhood = sorted_indices[1:neighborhood_size+1]  # Exclude the item itself
    return neighborhood

def update_data(user_id, selected_dish, neighborhood_size=5):
    hood = select_neighborhood(dish_similarity, selected_dish, neighborhood_size)

    for i in hood:
        current_rating = dishes.loc[user_id, dish_names[i]]
        if dish_similarity[selected_dish][i] < 0.5:
            adjustment = 0.1  # smaller positive adjustment
        else:
            # Only apply negative adjustment if the current rating is well above 1.0
            adjustment = -0.2 if current_rating > 1.2 else 0
        dish_similarity[selected_dish][i] += adjustment

        dish_name = dish_names[i] 
        # print(f"Updating user {user_id}, dish {dish_name}. Current rating: {dishes.loc[user_id, dish_name]}")

        new_rating = np.clip(dishes.loc[user_id, dish_name] + adjustment, 1, 5)
        new_rating = round(new_rating, 1)
        dishes.loc[user_id, dish_name] = new_rating

        # print(f"New rating: {new_rating}")

    # Track the recently selected dish
    if user_id not in recently_selected:
        recently_selected[user_id] = []
    recently_selected[user_id].append(selected_dish)

    # Limit the number of tracked recent dishes (e.g., 3)
    if len(recently_selected[user_id]) > 3:
        recently_selected[user_id].pop(0)

    # Save the updated data to CSV
    df.loc[user_id] = dishes.loc[user_id]
    df.to_csv("Food survey.csv")

# Train a linear regression model to predict ratings for new users
x = np.array(df)
y = np.arange(len(df)).reshape(-1, 1) 
model = LinearRegression().fit(y, x)

def add_user(user_id, name):
    global dishes

    new_data = model.predict([[user_id]])
    new_ratings = np.clip(new_data[0], 1, 5)
    new_ratings = np.round(new_ratings, 1)

    new_user_data = pd.Series(new_ratings, index=dishes.columns, name=user_id)
    dishes = pd.concat([dishes, new_user_data.to_frame().T])

    df.loc[user_id] = new_ratings
    df.to_csv("Food survey.csv")

    users[user_id] = name
    
    print(f"Account created successfully! Welcome, {name}.\n")

def validate_user(user_id):
    return user_id in dishes.index

def get_recommendations(user_id, num_recommendations=5):
    user_ratings = dishes.loc[user_id].values
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
        name = input("\nPlease enter your username: ")
        add_user(user_id, name)
    else:
        interact(user_id)
        break
