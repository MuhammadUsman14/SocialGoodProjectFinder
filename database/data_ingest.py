import random
from faker import Faker
import mysql.connector

fake = Faker()

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
    for _ in range(100):  # 100 Users
        first_name = fake.first_name()
        last_name = fake.last_name()
        email = fake.email()
        password_hash = fake.sha256()
        address = fake.address().replace("\n", " ")
        location_lat = round(random.uniform(-90, 90), 6)
        location_lon = round(random.uniform(-180, 180), 6)
        
        cursor.execute("""
            INSERT IGNORE INTO Users (first_name, last_name, email, password_hash, address, location_lat, location_lon)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (first_name, last_name, email, password_hash, address, location_lat, location_lon))
    
    conn.commit()

# Function to insert dummy data into Skills table
def insert_skills():
    skills = [
        "Writing", "Research", "Project Management", "Marketing", "Graphic Design",
        "Public Speaking", "Event Planning", "Data Analysis", "Teaching", "Social Media",
        "Fundraising", "Photography", "Customer Service", "Leadership", "Teamwork",
        "Problem Solving", "Communication", "Organization", "Time Management", "Creativity",
        "Public Relations", "Accounting", "Budgeting", "Counseling", "Healthcare", "Law",
        "Technology", "STEM", "Arts", "Music", "Legal", "Volunteer Management", "Sustainability",
        "Environmental Education", "Policy Advocacy", "Government Relations", "Crisis Management", 
        "Community Outreach", "Fundraising Campaigns", "Grant Writing", "Nonprofit Management", 
        "Board Governance", "Human Resources", "Public Health", "Social Services", "International Relations",
        "Cultural Sensitivity", "Diversity and Inclusion", "Data Science", "Coding", "App Development",
        "Website Development", "Research and Analysis", "Writing for Digital Media"
    ]
    
    for skill in skills:
        cursor.execute("""
            INSERT IGNORE INTO Skills (skill_name) VALUES (%s)
        """, (skill,))
    
    conn.commit()

# Function to insert dummy data into Organizations table
def insert_organizations():
    for _ in range(50):  # 50 Organizations
        name = fake.company()
        contact_name = fake.name()
        contact_email = fake.email()
        contact_phone = fake.phone_number()
        website = fake.url()
        address = fake.address().replace("\n", " ")
        
        cursor.execute("""
            INSERT IGNORE INTO Organizations (name, contact_name, contact_email, contact_phone, website, address)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (name, contact_name, contact_email, contact_phone, website, address))
    
    conn.commit()

# Function to insert dummy data into Volunteer_Opportunities table
def insert_volunteer_opportunities():
    cursor.execute("SELECT organization_id FROM Organizations")
    organizations = [org[0] for org in cursor.fetchall()]  # Fetching all organization IDs
    
    for org_id in organizations:
        for _ in range(20):  # 20 Opportunities per organization
            title = fake.bs()
            description = fake.paragraph(nb_sentences=5)
            required_skills = random.sample(["Writing", "Research", "Project Management", "Marketing", "Graphic Design", "Public Speaking"], 3)
            required_skills_str = ", ".join(required_skills)
            location_address = fake.address().replace("\n", " ")
            location_lat = round(random.uniform(-90, 90), 6)
            location_lon = round(random.uniform(-180, 180), 6)
            time_commitment = random.randint(5, 30)  # in hours per week
            category = random.choice(["Education", "Health", "Environment", "Legal", "Arts", "Social Impact"])
            start_date = fake.date_this_year()
            end_date = fake.date_this_decade()

            cursor.execute("""
                INSERT IGNORE INTO Volunteer_Opportunities (title, description, required_skills, location_address, location_lat, location_lon, time_commitment, category, organization_id, start_date, end_date)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (title, description, required_skills_str, location_address, location_lat, location_lon, time_commitment, category, org_id, start_date, end_date))
    
    conn.commit()

# Function to insert data into Opportunities_Skills table
def insert_opportunities_skills():
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

# Function to insert data into UserSkills table
def insert_user_skills():
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

# Function to insert data into UserFeedback table
def insert_feedback():
    cursor.execute("SELECT user_id FROM Users")
    users = [user[0] for user in cursor.fetchall()]  # Fetching all user IDs
    
    cursor.execute("SELECT opportunity_id FROM Volunteer_Opportunities")
    opportunities = [opp[0] for opp in cursor.fetchall()]  # Fetching all opportunity IDs
    
    for _ in range(100):  # 100 Feedback entries
        user_id = random.choice(users)
        opportunity_id = random.choice(opportunities)
        rating = random.randint(1, 5)
        comment = random.choice([
            "This was an amazing experience, I learned so much!",
            "The opportunity was great, but I would have liked more guidance.",
            "It was okay, but I felt there was a lack of support.",
            "I didn't find it engaging enough, would appreciate more hands-on tasks.",
            "Fantastic! I'd love to participate again next time."
        ])
        
        cursor.execute("""
            INSERT IGNORE INTO UserFeedback (user_id, opportunity_id, rating, comment)
            VALUES (%s, %s, %s, %s)
        """, (user_id, opportunity_id, rating, comment))
    
    conn.commit()

# Function to insert data into VolunteerHours table
def insert_volunteer_hours():
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

# Function to insert data into Donations table
def insert_donations():
    cursor.execute("SELECT user_id FROM Users")
    users = [user[0] for user in cursor.fetchall()]  # Fetching all user IDs
    
    cursor.execute("SELECT organization_id FROM Organizations")
    organizations = [org[0] for org in cursor.fetchall()]  # Fetching all organization IDs
    
    for _ in range(50):  # 50 Donations entries
        user_id = random.choice(users)
        organization_id = random.choice(organizations)
        amount = round(random.uniform(10, 500), 2)  # Donation amount between $10 and $500
        date = fake.date_this_year()
        purpose = fake.sentence(nb_words=6)
        
        cursor.execute("""
            INSERT IGNORE INTO Donations (user_id, organization_id, amount, date, purpose)
            VALUES (%s, %s, %s, %s, %s)
        """, (user_id, organization_id, amount, date, purpose))
    
    conn.commit()

# Call all functions to insert data
insert_users()
insert_skills()
insert_organizations()
insert_volunteer_opportunities()
insert_opportunities_skills()
insert_user_skills()
insert_feedback()
insert_volunteer_hours()
insert_donations()

# Close connection
cursor.close()
conn.close()
