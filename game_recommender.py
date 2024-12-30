import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.metrics.pairwise import cosine_similarity
import re

class GameRecommender:
    def __init__(self, csv_path):
        self.df = pd.read_csv(csv_path)
        self.preprocessed_data = None
        self.kmeans_model = None
        self.n_clusters = None
        self.feature_matrix = None
        
    def preprocess_data(self):
        # Convert scores to numerical values
        self.df['Metascore'] = pd.to_numeric(self.df['Metascore'], errors='coerce')
        self.df['User Score'] = pd.to_numeric(self.df['User Score'], errors='coerce')
        
        # Process release dates
        self.df['Release Year'] = pd.to_datetime(self.df['Release Date'], errors='coerce').dt.year
        
        # Create genre features using one-hot encoding
        genres = self.df['Genres'].str.get_dummies(sep=', ')
        
        # Create platform features using one-hot encoding
        platforms = self.df['Platforms'].str.get_dummies(sep=', ')
        
        # Combine numerical and categorical features
        numerical_features = self.df[['Metascore', 'User Score', 'Release Year']].fillna(0)
        
        # Standardize numerical features
        scaler = StandardScaler()
        scaled_numerical = scaler.fit_transform(numerical_features)
        scaled_numerical_df = pd.DataFrame(
            scaled_numerical,
            columns=numerical_features.columns
        )
        
        # Combine all features
        self.feature_matrix = pd.concat(
            [scaled_numerical_df, genres, platforms],
            axis=1
        )
        
        return self.feature_matrix
    
    def train_model(self, n_clusters=8):
        if self.feature_matrix is None:
            self.preprocess_data()
            
        self.n_clusters = n_clusters
        self.kmeans_model = KMeans(
            n_clusters=n_clusters,
            random_state=42,
            n_init=10
        )
        
        # Fit the model and add cluster labels to the dataframe
        self.df['Cluster'] = self.kmeans_model.fit_predict(self.feature_matrix)
        
    def get_recommendations(self, game_title, n_recommendations=5):
        # Find the game in our dataset
        game_idx = self.df[self.df['Title'].str.contains(game_title, case=False, na=False)].index
        
        if len(game_idx) == 0:
            return
            
        game_idx = game_idx[0]
        game_cluster = self.df.loc[game_idx, 'Cluster']
        
        # Get games from the same cluster
        cluster_games = self.df[self.df['Cluster'] == game_cluster]
        
        # Calculate similarity scores within the cluster
        game_features = self.feature_matrix.iloc[game_idx].values.reshape(1, -1)
        cluster_features = self.feature_matrix.iloc[cluster_games.index]
        
        similarities = cosine_similarity(game_features, cluster_features)[0]
        
        # Get top N similar games
        similar_game_indices = similarities.argsort()[::-1][1:n_recommendations+1]
        
        recommendations = []
        for idx, similarity in zip(similar_game_indices, similarities[similar_game_indices]):
            recommendations.append({
                'title': self.df.iloc[cluster_games.index[idx]]['Title'],
                'similarity_score': round(similarity * 100, 2),
                'metascore': self.df.iloc[cluster_games.index[idx]]['Metascore'],
                'genres': self.df.iloc[cluster_games.index[idx]]['Genres']
            })
            
        return recommendations
    
    def analyze_clusters(self):
        cluster_analysis = {}
        
        for cluster in range(self.n_clusters):
            cluster_games = self.df[self.df['Cluster'] == cluster]
            
            # Calculate cluster statistics
            cluster_analysis[f'Cluster {cluster}'] = {
                'size': len(cluster_games),
                'avg_metascore': cluster_games['Metascore'].mean(),
                'avg_user_score': cluster_games['User Score'].mean(),
                'common_genres': self._get_most_common(cluster_games['Genres']),
                'common_platforms': self._get_most_common(cluster_games['Platforms']),
                'avg_year': cluster_games['Release Year'].mean()
            }
            
        return cluster_analysis
    
    def _get_most_common(self, series, top_n=3):
        all_items = []
        for items in series.dropna():
            all_items.extend([item.strip() for item in items.split(',')])
            
        from collections import Counter
        return Counter(all_items).most_common(top_n)

if __name__ == "__main__":
    # Initialize and train the recommender
    recommender = GameRecommender("output.csv")
    recommender.train_model(n_clusters=8)
    
    # Get recommendations for a specific game
    recommendations = recommender.get_recommendations("The Legend of Zelda")
    
    # Print recommendations
    print("\nRecommended Games:")
    for rec in recommendations:
        print(f"\nTitle: {rec['title']}")
        print(f"Similarity Score: {rec['similarity_score']}%")
        print(f"Metascore: {rec['metascore']}")
        print(f"Genres: {rec['genres']}")
    
    # Analyze clusters
    cluster_analysis = recommender.analyze_clusters()
    
    # Print cluster analysis
    print("\nCluster Analysis:")
    for cluster, stats in cluster_analysis.items():
        print(f"\n{cluster}:")
        print(f"Size: {stats['size']} games")
        print(f"Average Metascore: {stats['avg_metascore']:.2f}")
        print(f"Most Common Genres: {stats['common_genres']}")