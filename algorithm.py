import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from geopy.distance import geodesic
import mysql.connector
import re

# Database connection
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="password",
    database="social_good"
)

cursor = conn.cursor()

# State coordinates (for simplicity, we use abbreviations as keys)
state_coordinates = {
    "AL": (32.806671, -86.791130), "AK": (61.370716, -152.404419), "AZ": (33.729759, -111.431221),
    "AR": (34.969704, -92.373123), "CA": (36.116203, -119.681564), "CO": (39.059811, -105.311104),
    "CT": (41.597782, -72.755371), "DE": (39.318523, -75.507141), "FL": (27.766279, -81.686783),
    "GA": (33.040619, -83.643074), "HI": (21.094318, -157.498337), "ID": (44.240459, -114.478828),
    "IL": (40.349457, -88.986137), "IN": (39.849426, -86.258278), "IA": (42.011539, -93.210526),
    "KS": (38.526600, -96.726486), "KY": (37.668140, -84.670067), "LA": (31.169546, -91.867805),
    "ME": (44.693947, -69.381927), "MD": (39.063946, -76.802101), "MA": (42.230171, -71.530106),
    "MI": (43.326618, -84.536095), "MN": (45.694454, -93.900192), "MS": (32.741646, -89.678696),
    "MO": (38.456085, -92.288368), "MT": (46.921925, -110.454353), "NE": (41.125370, -98.268082),
    "NV": (38.313515, -117.055374), "NH": (43.452492, -71.563896), "NJ": (40.298904, -74.521011),
    "NM": (34.840515, -106.248482), "NY": (42.165726, -74.948051), "NC": (35.630066, -79.806419),
    "ND": (47.528912, -99.784012), "OH": (40.388783, -82.764915), "OK": (35.565342, -96.928917),
    "OR": (44.572021, -122.070938), "PA": (40.590752, -77.209755), "RI": (41.680893, -71.511780),
    "SC": (33.856892, -80.945007), "SD": (44.299782, -99.438828), "TN": (35.747845, -86.692345),
    "TX": (31.054487, -97.563461), "UT": (40.150032, -111.862434), "VT": (44.045876, -72.710686),
    "VA": (37.769337, -78.169968), "WA": (47.400902, -121.490494), "WV": (38.491226, -80.954456),
    "WI": (44.268543, -89.616508), "WY": (42.755966, -107.302490)
}

def fetch_opportunities_from_db(limit=None):
    """Fetch volunteer opportunities from the database."""
    query = """
    SELECT 
        o.title, o.description, o.required_skills, o.location_address, o.category, 
        o.location_lat, o.location_lon, org.name AS organization_name 
    FROM Volunteer_Opportunities o
    INNER JOIN Organizations org ON o.organization_id = org.organization_id
    """
    if limit:
        query += f" LIMIT {limit}"  # Add the LIMIT clause to the query
    
    cursor.execute(query)
    results = cursor.fetchall()

    # Convert results to a DataFrame
    opportunities = pd.DataFrame(results, columns=[
        'title', 'description', 'required_skills', 'location_address', 'category',  
        'location_lat', 'location_lon', 'organization_name'
    ])
    return opportunities

def extract_opportunity_state(location_address):
    """
    Extract the state from a full address.
    Assumes the state is a two-letter code after the last comma.
    """
    match = re.search(r',\s*([A-Z]{2})\s', location_address)
    if match:
        state = match.group(1)  # Return the state code
        return state
    return None  # Return None if no state is found

def extract_user_state(location):
    """
    Extract the state from a location string.
    Assume the state is the last part of the input after a comma.
    """
    match = re.search(r',\s*([A-Z]{2})\s', location)
    if match:
        state = match.group(1)  # Return the state code
        return state
    return None  # Return None if no state is found

def calculate_distance(user_state, opportunity_state):
    """Calculate the distance between the user's state and the opportunity's state."""
    user_coords = state_coordinates.get(user_state)
    opportunity_coords = state_coordinates.get(opportunity_state)
    if user_coords and opportunity_coords:
        return geodesic(user_coords, opportunity_coords).miles
    return float('inf')  # Return a large distance if the state is not found

def get_user_with_highest_id():
    """Fetch the user with the highest user_id."""
    query = "SELECT * FROM users ORDER BY user_id DESC LIMIT 1"
    cursor.execute(query)
    user_data = cursor.fetchone()
    return user_data

def get_user_skills(user_id):
    """Fetch skills for the user with the provided user_id."""
    query = f"""
    SELECT s.skill_name 
    FROM userskills us
    INNER JOIN skills s ON us.skill_id = s.skill_id
    WHERE us.user_id = {user_id}
    """
    cursor.execute(query)
    skills = cursor.fetchall()
    return [skill[0] for skill in skills]  # Extract skill names from the result

def recommend_opportunities(category_filter=None):
    """Recommend opportunities based on the user with the highest user_id."""
    # Get the user with the highest user_id
    user_data = get_user_with_highest_id()

    # Extract user's location and skills
    user_location = user_data[6]  # Assuming user_location is the 3rd column
    user_skills = get_user_skills(user_data[0])  # Assuming user_id is the 1st column
   
    #Print statements to check accurate extraction of data
    # print(f"User Location: {user_location}")
    # print(f"User Skills: {user_skills}")
   
    # Create the user's profile
    user_profile = {
        'skills': ", ".join(user_skills),
        'location': user_location
    }

    # Fetch opportunities from the database
    opportunities = fetch_opportunities_from_db()

    # Filter opportunities by the desired category if provided
    if category_filter:
        opportunities = opportunities[opportunities['category'].str.contains(category_filter, case=False, na=False)]

    # Add a new column for the state extracted from the opportunity's location
    opportunities['state'] = opportunities['location_address'].apply(extract_opportunity_state)

    # Vectorize skills using TF-IDF
    vectorizer = TfidfVectorizer()
    opportunity_skills = vectorizer.fit_transform(opportunities['required_skills'])
    user_skills_vectorized = vectorizer.transform([user_profile['skills']])
    
    # Compute similarity scores
    similarities = cosine_similarity(user_skills_vectorized, opportunity_skills).flatten()
    opportunities['similarity'] = similarities

    # Calculate distances based on state-level information
    user_state = extract_user_state(user_profile['location'])
    opportunities['distance'] = opportunities['state'].apply(lambda opp_state: calculate_distance(user_state, opp_state))
    
    # Normalize and invert distances
    max_distance = opportunities['distance'].max()
    opportunities['distance_normalized'] = opportunities['distance'] / max_distance
    opportunities['distance_inverted'] = 1 - opportunities['distance_normalized']

    # Compute final weighted score
    opportunities['score'] = opportunities['similarity'] * 0.8 + opportunities['distance_inverted'] * 0.2
    
    # Convert score to percentage
    opportunities['score'] = opportunities['score'] * 100

    # Remove rows with NaN in the score column
    opportunities = opportunities.dropna(subset=['score'])
    
    # Sort opportunities by score
    recommendations = opportunities.sort_values(by='score', ascending=False)
   
    # Format the score as a percentage
    recommendations['score'] = recommendations['score'].apply(lambda x: f"{x:.2f}%")
   
    # Limit to the top 100 results
    recommendations = recommendations.head(100)
   
    return recommendations[['title', 'organization_name', 'score']]

if __name__ == "__main__":
    # print("Welcome to the Volunteer Matching Program!")

    # Get recommendations
    results = recommend_opportunities()
    
    # Display recommendations
    print("\nRecommended Opportunities:")
    print(results.to_string(index=False, header=["Title", "Organization", "Score"]))
