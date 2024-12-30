from game_recommender import GameRecommender

recommender = GameRecommender('output.csv')

recommender.train_model(n_clusters=8)
# Get recommendations for a specific game
game_title = input("Enter a game: ")

input_game_data = recommender.get_game_data(game_title)

if input_game_data:
    print("\nDetails of the game you entered:")
    print(f"Title: {input_game_data['title']}")
    print(f"Metascore: {input_game_data['metascore']}")
    print(f"Genres: {input_game_data['genres']}")
    print(f"Description: {input_game_data['description']}\n")
else:
    print("\nThe entered game was not found in the database.\n")

recommendations = recommender.get_recommendations(game_title)

# Print the recommendations
for rec in recommendations:
    print(f"\nTitle: {rec['title']}")
    print(f"Similarity Score: {rec['similarity_score']}%")
    print(f"Metascore: {rec['metascore']}")
    print(f"Genres: {rec['genres']}")