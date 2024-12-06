import random
from faker import Faker
import mysql.connector
import geopy
from geopy.geocoders import Nominatim
import time
from geopy.exc import GeocoderTimedOut

fake = Faker()

# Set up geolocator for converting addresses to lat/lon
geolocator = Nominatim(user_agent="social_good_app")

# Connect to MySQL database
conn = mysql.connector.connect(
    host="localhost",
    user="root",  # Replace with your MySQL username
    password="",  # Replace with your MySQL password
    database="social_good"  # Replace with your database name
)

cursor = conn.cursor()

# Function to insert dummy data into Users table
def insert_users():
    print("Inserting Users...")
    for _ in range(100):  # 100 Users
        first_name = fake.first_name()
        last_name = fake.last_name()
        email = fake.email()
        password_hash = fake.sha256()
        mobile_number = fake.phone_number()
        address = fake.address().replace("\n", " ")
        location_lat, location_lon = get_lat_lon(address)
        
        cursor.execute("""
            INSERT IGNORE INTO Users (first_name, last_name, email, password_hash, mobile_number, address, location_lat, location_lon)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (first_name, last_name, email, password_hash, mobile_number, address, location_lat, location_lon))
    
    conn.commit()
    print("Users Insertion Complete.")

# Function to get latitude and longitude from an address
def get_lat_lon(address):
    retries = 3
    for attempt in range(retries):
        try:
            location = geolocator.geocode(address, timeout=10)
            if location:
                return location.latitude, location.longitude
            else:
                return None, None
        except GeocoderTimedOut:
            if attempt < retries - 1:
                time.sleep(2)  # Wait a bit before retrying
                continue
            else:
                raise  # If we exhausted retries, raise the exception

# Function to insert dummy data into Skills table
def insert_skills():
    print("Inserting Skills...")
    skills = [
        "Writing", "Research", "Project Management", "Marketing", "Graphic Design", "Public Speaking", "Event Planning", "Data Analysis", 
        "Teaching", "Social Media", "Fundraising", "Photography", "Customer Service", "Leadership", "Teamwork", "Problem Solving", 
        "Communication", "Organization", "Time Management", "Creativity", "Public Relations", "Accounting", "Budgeting", "Counseling", 
        "Healthcare", "Law", "Technology", "STEM", "Arts", "Music", "Legal", "Volunteer Management", "Sustainability", 
        "Environmental Education", "Policy Advocacy", "Government Relations", "Crisis Management", "Community Outreach", 
        "Grant Writing", "Nonprofit Management", "Board Governance", "Human Resources", "Public Health", "Social Services", 
        "International Relations", "Cultural Sensitivity", "Diversity and Inclusion", "Data Science", "Coding", "App Development", 
        "Website Development", "UX/UI Design", "Database Management", "Business Development", "Communication Strategy", "SEO", 
        "Digital Marketing", "Social Impact", "Risk Management", "Leadership Training"
    ]
    
    for skill in skills:
        cursor.execute("""
            INSERT IGNORE INTO Skills (skill_name) VALUES (%s)
        """, (skill,))
    
    conn.commit()
    print("Skills Insertion Complete.")

# Function to insert dummy data into Organizations table
def insert_organizations():
    print("Inserting Organizations...")
    for _ in range(50):  # 50 Organizations
        name = fake.company()
        contact_name = fake.name()
        contact_email = fake.email()
        contact_phone = fake.phone_number()
        website = fake.url()
        address = fake.address().replace("\n", " ")
        joined_at = fake.date_between(start_date='-50y', end_date='today')
        
        cursor.execute("""
            INSERT IGNORE INTO Organizations (name, contact_name, contact_email, contact_phone, website, address, joined_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (name, contact_name, contact_email, contact_phone, website, address, joined_at))
    
    conn.commit()
    print("Organizations Insertion Complete.")

# Function to insert dummy data into Volunteer_Opportunities table
def insert_volunteer_opportunities():
    print("Inserting Volunteer Opportunities...")
    cursor.execute("SELECT organization_id FROM Organizations")
    organizations = [org[0] for org in cursor.fetchall()]  # Fetching all organization IDs
    
    categories = ["Education", "Health", "Environment", "Legal", "Arts", "Social Impact", "Technology", "Community Outreach", "Fundraising"]
    
    for org_id in organizations:
        for _ in range(20):  # 20 Opportunities per organization
            title = fake.job() + " Volunteer"
            description = fake.paragraph(nb_sentences=5)
            required_skills = random.sample(["Writing", "Research", "Project Management", "Marketing", "Graphic Design", "Public Speaking"], 3)
            required_skills_str = ", ".join(required_skills)
            location_address = fake.address().replace("\n", " ")
            location_lat, location_lon = get_lat_lon(location_address)
            time_commitment = random.randint(5, 30)  # in hours per week
            opportunity_categories = random.sample(categories, random.randint(1, 3))  # Each opportunity can have 1-3 categories
            category_str = ", ".join(opportunity_categories)
            start_date = fake.date_this_year()
            end_date = fake.date_between(start_date=start_date, end_date='+5y')  # End date after start date
            
            cursor.execute("""
                INSERT IGNORE INTO Volunteer_Opportunities (title, description, required_skills, location_address, location_lat, location_lon, time_commitment, category, organization_id, start_date, end_date)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (title, description, required_skills_str, location_address, location_lat, location_lon, time_commitment, category_str, org_id, start_date, end_date))
    
    conn.commit()
    print("Volunteer Opportunities Insertion Complete.")

# Function to insert data into Opportunities_Skills table
def insert_opportunities_skills():
    print("Inserting Opportunities Skills...")
    cursor.execute("SELECT opportunity_id FROM Volunteer_Opportunities")
    opportunities = [opp[0] for opp in cursor.fetchall()]  # Fetching all opportunity IDs
    
    cursor.execute("SELECT skill_id FROM Skills")
    skills = [skill[0] for skill in cursor.fetchall()]  # Fetching all skill IDs
    
    for opportunity_id in opportunities:
        for _ in range(5):  # 5 Skills per opportunity
            skill_id = random.choice(skills)
            cursor.execute("""
                INSERT IGNORE INTO Opportunities_Skills (opportunity_id, skill_id)
                VALUES (%s, %s)
            """, (opportunity_id, skill_id))
    
    conn.commit()
    print("Opportunities Skills Insertion Complete.")

# Function to insert data into UserSkills table
def insert_user_skills():
    print("Inserting User Skills...")
    cursor.execute("SELECT user_id FROM Users")
    users = [user[0] for user in cursor.fetchall()]  # Fetching all user IDs
    
    cursor.execute("SELECT skill_id FROM Skills")
    skills = [skill[0] for skill in cursor.fetchall()]  # Fetching all skill IDs
    
    for user_id in users:
        for _ in range(5):  # 5 Skills per user (skills the user is interested in or has)
            skill_id = random.choice(skills)
            cursor.execute("""
                INSERT IGNORE INTO UserSkills (user_id, skill_id)
                VALUES (%s, %s)
            """, (user_id, skill_id))
    
    conn.commit()
    print("User Skills Insertion Complete.")

# Function to insert data into UserFeedback table
def insert_feedback():
    print("Inserting User Feedback...")
    cursor.execute("SELECT user_id FROM Users")
    users = [user[0] for user in cursor.fetchall()]  # Fetching all user IDs
    
    cursor.execute("SELECT opportunity_id FROM Volunteer_Opportunities")
    opportunities = [opp[0] for opp in cursor.fetchall()]  # Fetching all opportunity IDs
    
    for _ in range(100):  # 100 Feedback entries
        user_id = random.choice(users)
        opportunity_id = random.choice(opportunities)
        rating = random.randint(1, 5)
        comment = fake.paragraph(nb_sentences=random.randint(1, 5))
        
        cursor.execute("""
            INSERT IGNORE INTO UserFeedback (user_id, opportunity_id, rating, comment)
            VALUES (%s, %s, %s, %s)
        """, (user_id, opportunity_id, rating, comment))
    
    conn.commit()
    print("User Feedback Insertion Complete.")

# Function to insert data into VolunteerHours table
def insert_volunteer_hours():
    print("Inserting Volunteer Hours...")
    cursor.execute("SELECT user_id FROM Users")
    users = [user[0] for user in cursor.fetchall()]  # Fetching all user IDs
    
    cursor.execute("SELECT opportunity_id FROM Volunteer_Opportunities")
    opportunities = [opp[0] for opp in cursor.fetchall()]  # Fetching all opportunity IDs
    
    for _ in range(100):  # 100 Volunteer hours entries
        user_id = random.choice(users)
        opportunity_id = random.choice(opportunities)
        hours_volunteered = random.uniform(1, 10)  # Hours between 1 and 10
        date = fake.date_this_year()
        
        cursor.execute("""
            INSERT IGNORE INTO VolunteerHours (user_id, opportunity_id, hours_volunteered, date)
            VALUES (%s, %s, %s, %s)
        """, (user_id, opportunity_id, hours_volunteered, date))
    
    conn.commit()
    print("Volunteer Hours Insertion Complete.")

# Function to insert data into Donations table
def insert_donations():
    print("Inserting Donations...")
    cursor.execute("SELECT user_id FROM Users")
    users = [user[0] for user in cursor.fetchall()]  # Fetching all user IDs
    
    if not users:
        print("No users found. Donations insertion will not proceed.")
        return  # Exit early if no users
    
    for _ in range(100):  # 100 Donations
        user_id = random.choice(users)
        amount = random.randint(5, 17930)  # Donation between $5 and $17930
        purpose = random.choice(["Education Fund", "Medical Aid", "Food Drive", "Disaster Relief", "Environmental Protection", "Community Development"])
        date = fake.date_this_year()
        
        try:
            cursor.execute("""
                INSERT IGNORE INTO Donations (user_id, amount, purpose, date)
                VALUES (%s, %s, %s, %s)
            """, (user_id, amount, purpose, date))
        except Exception as e:
            print(f"Error inserting donation: {e}")
    
    conn.commit()
    print("Donations Insertion Complete.")


# Call all insertion functions
insert_users()
insert_skills()
insert_organizations()
insert_volunteer_opportunities()
insert_opportunities_skills()
insert_user_skills()
insert_feedback()
insert_volunteer_hours()
insert_donations()

# Close the connection
cursor.close()
conn.close()
