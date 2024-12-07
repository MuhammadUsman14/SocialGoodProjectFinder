import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from geopy.geocoders import Nominatim
from geopy.distance import geodesic

# Sample dataset of volunteer opportunities
opportunities = pd.DataFrame({
    'name': ['Community Arts Program', 'Park Cleanup', 'Web Development for Nonprofit'],
    'skills': ['graphic design, painting, teaching', 'manual labor, organizing', 'web development, coding, backend'],
    'location': ['New York, NY', 'Brooklyn, NY', 'New York, NY']
})

# Initialize the geolocator
geolocator = Nominatim(user_agent="volunteer_matching")

def calculate_distance(user_location, opportunity_location):
    """Calculate the distance between the user and the opportunity."""
    user_coords = geolocator.geocode(user_location)
    opportunity_coords = geolocator.geocode(opportunity_location)
    if user_coords and opportunity_coords:
        return geodesic((user_coords.latitude, user_coords.longitude), 
                        (opportunity_coords.latitude, opportunity_coords.longitude)).miles
    return float('inf')  # Return a large distance if geocoding fails

def recommend_opportunities(user):
    """Recommend volunteer opportunities for the given user."""
    # Vectorize skills using TF-IDF
    vectorizer = TfidfVectorizer()
    opportunity_skills = vectorizer.fit_transform(opportunities['skills'])
    user_skills = vectorizer.transform([user['skills']])
    
    # Compute similarity scores
    similarities = cosine_similarity(user_skills, opportunity_skills).flatten()
    opportunities['similarity'] = similarities
    
    # Calculate distances for location filtering
    opportunities['distance'] = opportunities['location'].apply(lambda loc: calculate_distance(user['location'], loc))
    
    # Normalize and invert distances
    max_distance = opportunities['distance'].max()
    opportunities['distance_normalized'] = opportunities['distance'] / max_distance
    opportunities['distance_inverted'] = 1 - opportunities['distance_normalized']
    
    # Compute a weighted score (higher similarity, closer distance is better)
    opportunities['score'] = opportunities['similarity'] * 0.8 + opportunities['distance_inverted'] * 0.2
    
    # Convert score to percentage
    opportunities['score_percentage'] = (opportunities['score'] * 100).round(2)
    
    # Sort opportunities by score in descending order
    recommendations = opportunities.sort_values(by='score', ascending=False)
    return recommendations[['name', 'score_percentage']]


if __name__ == "__main__":
    print("Welcome to the Volunteer Matching Program!")
    
    # Prompt the user for their skills
    user_skills = input("Please enter your skills (comma-separated): ").strip()
    
    # Prompt the user for their location
    user_location = input("Please enter your location (City, State): ").strip()
    
    # Create the user's profile
    user_profile = {
        'skills': user_skills,
        'location': user_location
    }

    # Get recommendations
    results = recommend_opportunities(user_profile)

    # Convert the score to percentage
    results['score_percentage'] = (results['score_percentage']).round(2)

    # Print recommendations
    print("\nRecommended Opportunities (with Scores as Percentages):")
    print(results.to_string(index=False, header=["Name", "Score (%)"]))
