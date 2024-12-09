from flask import Flask, render_template, request, redirect, session, flash, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
import mysql.connector
import re
from datetime import datetime, timedelta
from geopy.geocoders import Nominatim
import calendar

app = Flask(__name__)
app.secret_key = '3683a25f2a44fc627f33d91ec7cd654151f8696a6fffd057'  # Replace with a secure secret key for sessions

# Function to establish a connection to the database
def connect_db():
    return mysql.connector.connect(
        host="localhost",  # e.g., localhost or IP
        user="root",   # MySQL username
        password="@MySeniorProJecT21",  # MySQL password
        database="social_good"  # Database name
    )


# Function to check if an email is already registered
def email_exists(email):
    db = connect_db()
    cursor = db.cursor()
    cursor.execute("SELECT COUNT(*) FROM Users WHERE email = %s", (email,))
    result = cursor.fetchone()
    cursor.close()
    db.close()
    
    return result[0] > 0  # Returns True if the email exists, False otherwise


# Function to create a new user and store it in the database
def create_user(full_name, email, password, mobile_number):
    if email_exists(email):
        return "Error: Email already registered."  # Error if email is already registered
    
    hashed_password = generate_password_hash(password)  # Hash the password before storing
    
    # Split the full name into first name and last name
    name_parts = full_name.split(' ')
    first_name = name_parts[0]
    last_name = ' '.join(name_parts[1:])

    db = connect_db()
    cursor = db.cursor()
    
    try:
        # Insert the user's data into the Users table
        cursor.execute(
            "INSERT INTO Users (first_name, last_name, email, password_hash, mobile_number) VALUES (%s, %s, %s, %s, %s)",
            (first_name, last_name, email, hashed_password, mobile_number)
        )
        db.commit()  # Commit the transaction
        print(f"User {first_name} {last_name} inserted into the database.")
    
    except mysql.connector.Error as err:
        db.rollback()
        print(f"Error: {err}")  # Print the error to the terminal
        return f"Error: {err}"  # Return the error message if something goes wrong
    finally:
        cursor.close()
        db.close()

# Function to verify the user's credentials during login
def verify_user(email, password):
    db = connect_db()
    cursor = db.cursor()

    # Fetch the user record based on the email address
    cursor.execute("SELECT user_id, password_hash FROM Users WHERE email = %s", (email,))
    user = cursor.fetchone()

    cursor.close()
    db.close()

    # Check if a user was found and if the password matches
    if user and check_password_hash(user[1], password):  
        return user[0]  # Return user_id on successful login
    return None  # If no match, login fails


# Function to get user_id based on email
def get_user_id_from_email(email):
    db = connect_db()
    cursor = db.cursor()
    cursor.execute("SELECT user_id FROM Users WHERE email = %s", (email,))
    result = cursor.fetchone()
    cursor.close()
    db.close()
    if result:
        return result[0]  # Return the user_id
    return None


# Function to update the user profile with address, location, and skills
def update_user_profile(user_id, address, phone_number, selected_skills, new_skill):
    geolocator = Nominatim(user_agent="SocialGoodFinder")
    
    # Geocode address if provided
    location_lat = location_lon = None
    if address: 
        try:
            location = geolocator.geocode(address)
            print(location.address)
            if location:
                location_lat = location.latitude
                location_lon = location.longitude
            else:
                return "Invalid address. Could not geocode."
        except Exception as e:
            return f"Geocoding error: {e}"

    db = connect_db()
    cursor = db.cursor()

    try:
        # Update Address and Location if provided
        if address:
            cursor.execute("""
                UPDATE Users
                SET address = %s, location_lat = %s, location_lon = %s
                WHERE user_id = %s
            """, (address, location_lat, location_lon, user_id))
        
        if phone_number:
            cursor.execute("""
                UPDATE Users
                SET mobile_number = %s
                WHERE user_id = %s
            """, (phone_number, user_id))

        # Get current skills for the user
        cursor.execute("""
            SELECT skill_name FROM Skills
            INNER JOIN UserSkills ON Skills.skill_id = UserSkills.skill_id
            WHERE UserSkills.user_id = %s
        """, (user_id,))
        current_skills = {row[0] for row in cursor.fetchall()}  # Set of current skills

        # Determine skills to add and remove
        selected_skills = set(selected_skills or [])  # Ensure selected_skills is a set
        skills_to_remove = current_skills - selected_skills
        skills_to_add = selected_skills - current_skills

        # Remove unchecked skills
        for skill in skills_to_remove:
            cursor.execute("""
                DELETE FROM UserSkills WHERE user_id = %s AND skill_id = (
                    SELECT skill_id FROM Skills WHERE skill_name = %s
                )
            """, (user_id, skill))

        # Add newly checked skills
        for skill in selected_skills:
            cursor.execute("""
                INSERT INTO UserSkills (user_id, skill_id)
                SELECT %s, skill_id FROM Skills WHERE skill_name = %s
            """, (user_id, skill))

        # Add new skill if provided and associate with user
        if new_skill:
            # Check if skill already exists
            cursor.execute("SELECT skill_id FROM Skills WHERE skill_name = %s", (new_skill,))
            result = cursor.fetchone()
            if result:
                new_skill_id = result[0]
            else:
                # Insert the new skill
                cursor.execute("INSERT INTO Skills (skill_name) VALUES (%s)", (new_skill,))
                cursor.execute("SELECT LAST_INSERT_ID()")  # Get the new skill_id
                new_skill_id = cursor.fetchone()[0]

            # Associate the new skill with the user
            cursor.execute("""
                INSERT INTO UserSkills (user_id, skill_id) VALUES (%s, %s)
            """, (user_id, new_skill_id))   

        db.commit()  # Commit the transaction
    except mysql.connector.Error as err:
        db.rollback()
        return f"Database Error: {err}"
    finally:
        cursor.close()
        db.close()
    
    return None  # If no errors, return None


# Function to insert skills into UserSkills table
def insert_user_skills(user_id, skills):
    db = connect_db()
    cursor = db.cursor()

    try:
        for skill in skills:
            cursor.execute("""
                INSERT INTO UserSkills (user_id, skill_id)
                VALUES (%s, (SELECT skill_id FROM Skills WHERE skill_name = %s))
            """, (user_id, skill))
        db.commit()
    except mysql.connector.Error as err:
        db.rollback()
        return f"Error: {err}"
    finally:
        cursor.close()
        db.close()
    
    return None  # Return None if successful


# Function to fetch skills from the database with pagination
def fetch_skills(offset=0, limit=5):
    db = connect_db()
    cursor = db.cursor()
    try:
        cursor.execute("""
            SELECT skill_name FROM Skills 
            LIMIT %s OFFSET %s
        """, (limit, offset))
        result = cursor.fetchall()
    finally:
        cursor.close()
        db.close()
    return [row[0] for row in result]

# Function to add a new skill to the Skills table
def add_new_skill(skill_name):
    db = connect_db()
    cursor = db.cursor()
    try:
        cursor.execute("INSERT INTO Skills (skill_name) VALUES (%s)", (skill_name,))
        db.commit()
    except mysql.connector.Error as err:
        db.rollback()
        return f"Error: {err}"
    finally:
        cursor.close()
        db.close()
    return None  # Return None if successful

def get_user_profile(user_id):
    db = connect_db()  
    cursor = db.cursor(dictionary=True)  # Using dictionary cursor for easier data access

    try:
        # Query to fetch the user's profile
        cursor.execute("""
            SELECT
                user_id,
                first_name,
                last_name,
                email,
                address,
                mobile_number,
                location_lat,
                location_lon
            FROM Users
            WHERE user_id = %s
        """, (user_id,))
        
        # Fetch one record (assuming user_id is unique)
        profile = cursor.fetchone()
        return profile  # Return the profile as a dictionary, or None if not found
    except mysql.connector.Error as err:
        print(f"Database error: {err}")
        return None
    finally:
        cursor.close()
        db.close()


# Function to get current skills of a user
def get_user_skills(user_id):
    db = connect_db()
    cursor = db.cursor()
    
    try:
        cursor.execute("""
            SELECT skill_name FROM Skills
            INNER JOIN UserSkills ON Skills.skill_id = UserSkills.skill_id
            WHERE UserSkills.user_id = %s
        """, (user_id,))
        result = cursor.fetchall()
        # Return a list of skill names
        return [row[0] for row in result]
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return []  # Return an empty list if there's an error
    finally:
        cursor.close()
        db.close()


# Function to get user contact information
def get_user_contact_info(user_id):
    db = connect_db()
    cursor = db.cursor()
    cursor.execute("SELECT email, mobile_number FROM Users WHERE user_id = %s", (user_id,))
    result = cursor.fetchone()
    cursor.close()
    db.close()
    return result  # Returns (email, mobile_number)

# Function to get donation history
def get_donation_history(user_id):
    db = connect_db()
    cursor = db.cursor()
    
    # Initialize default values
    donations_this_year = 0
    lifetime_donations = 0
    first_donation_date = None
    volunteer_hours_this_year = 0
    lifetime_volunteer_hours = 0
    first_volunteer_date = None

    # Fetch total donations this year and lifetime donations
    cursor.execute("""
        SELECT SUM(amount), YEAR(date) AS donation_year
        FROM Donations
        WHERE user_id = %s
        GROUP BY donation_year
    """, (user_id,))
    donation_results = cursor.fetchall()

    for row in donation_results:
        total_amount, donation_year = row  # Unpack the tuple
        if donation_year == datetime.now().year:
            donations_this_year = total_amount or 0
        lifetime_donations += total_amount or 0
        if not first_donation_date:
            first_donation_date = donation_year  # Store the year of the first donation

    # Get total volunteer hours this year and lifetime volunteer hours
    cursor.execute("""
        SELECT SUM(hours_volunteered), YEAR(date) AS volunteer_year
        FROM VolunteerHours
        WHERE user_id = %s
        GROUP BY volunteer_year
    """, (user_id,))
    volunteer_results = cursor.fetchall()

    for row in volunteer_results:
        total_hours, volunteer_year = row  # Unpack the tuple
        if volunteer_year == datetime.now().year:
            volunteer_hours_this_year = total_hours or 0
        lifetime_volunteer_hours += total_hours or 0
        if not first_volunteer_date:
            first_volunteer_date = volunteer_year  # Store the year of the first volunteer

    # Get the user's first donation and volunteer dates
    cursor.execute("""
        SELECT MIN(date) 
        FROM Donations 
        WHERE user_id = %s
    """, (user_id,))
    first_donation_date_row = cursor.fetchone()
    first_donation_date = first_donation_date_row[0] if first_donation_date_row else None
    
    cursor.execute("""
        SELECT MIN(date) 
        FROM VolunteerHours 
        WHERE user_id = %s
    """, (user_id,))
    first_volunteer_date_row = cursor.fetchone()
    first_volunteer_date = first_volunteer_date_row[0] if first_volunteer_date_row else None

    cursor.close()
    db.close()

    # Format data for template
    return {
        'this_year': f"{donations_this_year:.2f}, {volunteer_hours_this_year}",
        'lifetime': f"{lifetime_donations:.2f}, {lifetime_volunteer_hours}",
        'first_donation': first_donation_date.strftime('%Y-%m-%d') if first_donation_date else 'N/A',
        'first_volunteer': first_volunteer_date.strftime('%Y-%m-%d') if first_volunteer_date else 'N/A'
    }

# Function to get recent donations and shifts
def get_recent_contributions():
    user_id = session.get('user_id')
    if not user_id:
        raise ValueError('User not logged in')
    
    db = connect_db()
    cursor = db.cursor()

    # Get recent donations
    cursor.execute("""
        SELECT O.name, D.amount, D.date, D.purpose
        FROM Donations D
        JOIN Organizations O ON D.organization_id = O.organization_id
        WHERE D.user_id = %s
        ORDER BY D.date DESC
        LIMIT 5
    """, (user_id,))

    recent_donations = cursor.fetchall()

    # Get the next volunteer shift
    cursor.execute("""
        SELECT V.title, V.start_date, V.location_address
        FROM Volunteer_Opportunities V
        WHERE V.opportunity_id = (
            SELECT opportunity_id
            FROM VolunteerHours
            WHERE user_id = %s AND date > NOW()
            ORDER BY date ASC
            LIMIT 1)
    """, (user_id,))
    next_shift = cursor.fetchone()

    cursor.close()
    db.close()

    return {
        'recent_donations': recent_donations,
        'next_shift': next_shift
    }

# Function to get monthly contributions (for chart)
def get_monthly_contributions():
    user_id = session.get('user_id')
    if not user_id:
        raise ValueError('User not logged in')
    
    db = connect_db()
    cursor = db.cursor()
    
    # Get donations and hours contributed by month
    cursor.execute("""
        SELECT MONTH(date) AS month, COALESCE(SUM(amount), 0) AS donations
        FROM Donations
        WHERE user_id = %s
        GROUP BY MONTH(date)
    """, (user_id,))
    donation_data = cursor.fetchall()

    # Fetch hours volunteered grouped by month
    cursor.execute("""
        SELECT MONTH(date) AS month, COALESCE(SUM(hours_volunteered), 0) AS hours
        FROM VolunteerHours
        WHERE user_id = %s
        GROUP BY MONTH(date)
    """, (user_id,))
    volunteer_data = cursor.fetchall()

    cursor.close()
    db.close()
    
    # Process data into a unified structure for charting
    months = list(range(1, 13))  # Months from January (1) to December (12)
    monthly_contributions = {
        'donations': [0] * 12,  # Initialize with zeros for all months
        'hours': [0] * 12
    }

    # Map donations to months
    for row in donation_data:
        month, donations = row
        monthly_contributions['donations'][month - 1] = float(donations)

    # Map hours to months
    for row in volunteer_data:
        month, hours = row
        monthly_contributions['hours'][month - 1] = int(hours)
    return monthly_contributions

# Function to get program-wise donations and activity-wise hours (for pie charts)
def get_donations_by_program_and_hours():
    user_id = session.get('user_id')
    if not user_id:
        raise ValueError('User not logged in')
    
    db = connect_db()
    cursor = db.cursor()

    # Donations by program (example: for Exhibits for Youth, Restorations, etc.)
    cursor.execute("""
        SELECT V.category, SUM(D.amount)
        FROM Donations D
        JOIN Volunteer_Opportunities V ON D.organization_id = V.organization_id
        WHERE D.user_id = %s
        GROUP BY V.category
    """, (user_id,))
    donations_by_program = cursor.fetchall()

    # Hours by activity
    cursor.execute("""
        SELECT V.category, SUM(VH.hours_volunteered)
        FROM VolunteerHours VH
        JOIN Volunteer_Opportunities V ON VH.opportunity_id = V.opportunity_id
        WHERE VH.user_id = %s
        GROUP BY V.category
    """, (user_id,))
    hours_by_activity = cursor.fetchall()

    cursor.close()
    db.close()

    return donations_by_program, hours_by_activity


def is_organization_valid(organization_id):
    print(f"Checking if organization with ID {organization_id} is valid.")
    db = connect_db()
    cursor = db.cursor()
    cursor.execute("SELECT COUNT(*) FROM Organizations WHERE organization_id = %s", (organization_id,))
    result = cursor.fetchone()
    cursor.close()
    db.close()

    print(f"Organization with ID {organization_id} exists: {result[0] > 0}")  # Debugging line
    return result[0] > 0


def is_donation_valid(amount):
    return amount > 0 and amount < 100000


def add_donation(user_id, organization_id, amount, purpose):
    if not is_organization_valid(organization_id):
        return "Organization not found."
    if not is_donation_valid(amount):
        return "Donation amount is invalid."
    
    db = connect_db()
    cursor = db.cursor()

    try:
        # Insert the donation record into the Donations table
        cursor.execute("""
            INSERT INTO Donations (user_id, organization_id, amount, date, purpose)
            VALUES (%s, %s, %s, NOW(), %s)
        """, (user_id, organization_id, amount, purpose))
        db.commit()  # Commit the transaction
        print(f"Donation of {amount} added for user {user_id} to organization {organization_id}.")
    
    except mysql.connector.Error as err:
        db.rollback()  # Rollback if there's an error
        print(f"Error: {err}")
        return f"Error: {err}"
    finally:
        cursor.close()
        db.close()
    
    return "Donation successfully added."  # Return success message if donation was added


from datetime import datetime, timedelta
import calendar

def record_volunteer_hours(user_id, opportunity_id, start_date, end_date, availability):
    if not user_id:  # Check if user_id is None or empty
        return {"success": False, "error": "User ID is required"}

    if not availability or len(availability) == 0:
        return {"success": False, "error": "Availability is required"}

    # Check if start_date or end_date is None
    if not start_date or not end_date:
        return {"success": False, "error": "Start date and End date are required"}

    try:
        # Convert start_date and end_date to datetime objects
        start_date = datetime.strptime(start_date, '%Y-%m-%d')
        end_date = datetime.strptime(end_date, '%Y-%m-%d')
    except ValueError:
        return {"success": False, "error": "Invalid date format. Please use YYYY-MM-DD."}

    # Connect to database
    db = connect_db()
    cursor = db.cursor()

    try:
        # Loop through the availability and calculate hours
        for day, start_time, end_time in availability:
            # Parse start_time and end_time to datetime objects
            start_time_obj = datetime.strptime(start_time, '%H:%M')
            end_time_obj = datetime.strptime(end_time, '%H:%M')

            # Calculate the difference between start and end time (in hours)
            duration = (end_time_obj - start_time_obj).total_seconds() / 3600.0

            # Get all occurrences of the selected day within the date range
            current_date = start_date
            while current_date <= end_date:
                # Check if the current_date is the selected day
                if current_date.weekday() == calendar.day_name.index(day):
                    # Insert into VolunteerHours table (using current_date for 'date')
                    cursor.execute("""
                        INSERT INTO VolunteerHours (user_id, opportunity_id, hours_volunteered, date)
                        VALUES (%s, %s, %s, %s)
                    """, (user_id, opportunity_id, duration, current_date.date()))

                    db.commit()

                # Move to the next week
                current_date += timedelta(days=7)

        return {"success": True, "message": "Successfully signed up", "total_hours": len(availability)}

    except Exception as e:
        db.rollback()
        print(f"Error while inserting volunteer hours: {e}")
        return {"success": False, "error": str(e)}
    finally:
        cursor.close()
        db.close()



# Function to fetch distinct categories from the Volunteer_Opportunities table
def fetch_distinct_categories(offset=0, limit=5):
    db = connect_db()
    cursor = db.cursor()

    try:
        # Query to get distinct categories
        cursor.execute("SELECT DISTINCT category FROM Volunteer_Opportunities LIMIT %s OFFSET %s", (limit, offset))
        categories = cursor.fetchall()
        return [category[0] for category in categories]  # Return list of distinct categories
    
    except mysql.connector.Error as err:
        print(f"Error fetching categories: {err}")
        return []  # Return an empty list if there's an error
    finally:
        cursor.close()
        db.close()


def parse_location(user_input):
    # Match city, state (with optional comma)
    pattern = r"([a-zA-Z\s]+),?\s*([a-zA-Z\s]+)"
    match = re.match(pattern, user_input.strip())
    
    if match:
        city = match.group(1).strip()
        state = match.group(2).strip()
        return city, state
    return None, None



# Function to fetch volunteer opportunities with optional filters (location, category, skills, etc.)
def fetch_opportunities(location=None, category=None, skills=None, offset=0, limit=10):
    db = connect_db()
    cursor = db.cursor(dictionary=True)

    # Start building the query
    query = """
        SELECT V.opportunity_id, V.title, V.location_address, V.category, V.required_skills, V.start_date, V.end_date, O.name AS organization_name 
        FROM Volunteer_Opportunities V
        JOIN Organizations O ON V.organization_id = O.organization_id
        WHERE 1=1
    """

    # Apply filters if provided
    params = []
    if location:
        city, state = parse_location(location)

        if city and state:
            query += """
                AND LOWER(SUBSTRING_INDEX(SUBSTRING_INDEX(V.location_address, ',', 1), ' ', -1)) = LOWER(%s)
                AND LOWER(SUBSTRING_INDEX(SUBSTRING_INDEX(V.location_address, ',', -1), ' ', 1)) = LOWER(%s)
            """
            params.extend([city, state])

        else:
            query += " AND LOWER(V.location_address) LIKE LOWER(%s)"
            params.append(f"%{location}%")
    
    if category:
        query += " AND LOWER(V.category) = LOWER(%s)"
        params.append(category)
    
    if skills:
        # Match opportunities with required skills
        #skill_placeholders = ','.join(['%s'] * len(skills))
        query += """ 
            AND EXISTS (
                SELECT 1 
                FROM Opportunities_Skills OS 
                JOIN Skills S ON OS.skill_id = S.skill_id 
                WHERE OS.opportunity_id = V.opportunity_id AND S.skill_name IN ({})
            )
        """.format(','.join(['%s'] * len(skills)))
        params.extend(skills)  # Convert list of skills to a comma-separated string
    
    # Apply ORDER BY and pagination
    query += " ORDER BY V.end_date DESC LIMIT %s OFFSET %s"
    params.extend([limit, offset])

    try:
        # Debugging: Print the final query and parameters
        print(f"Final Query: {query}")
        print(f"Parameters: {params}")

        cursor.execute(query, params)
        opportunities = cursor.fetchall()
        return opportunities
    except mysql.connector.Error as err:
        print(f"Error fetching opportunities: {err}")
        return []
    finally:
        cursor.close()
        db.close()


def fetch_opportunity_by_id(opportunity_id):
    print(f"Fetching opportunity with ID: {opportunity_id}")
    db = connect_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("""
        SELECT V.opportunity_id, V.title, V.location_address, V.category, V.required_skills, V.start_date, V.end_date, V.organization_id, O.name AS organization_name
        FROM Volunteer_Opportunities V
        JOIN Organizations O ON V.organization_id = O.organization_id
        WHERE V.opportunity_id = %s
    """, (opportunity_id,))
    opportunity = cursor.fetchone()
    cursor.close()
    db.close()

    print(f"Fetched Opportunity: {opportunity}")  # Debugging line
    return opportunity


def fetch_opportunity_by_id(opportunity_id):
    print(f"Fetching opportunity with ID: {opportunity_id}")
    db = connect_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("""
        SELECT V.opportunity_id, V.title, V.location_address, V.category, V.required_skills, V.start_date, V.end_date, V.organization_id, O.name AS organization_name
        FROM Volunteer_Opportunities V
        JOIN Organizations O ON V.organization_id = O.organization_id
        WHERE V.opportunity_id = %s
    """, (opportunity_id,))
    opportunity = cursor.fetchone()
    cursor.close()
    db.close()

    print(f"Fetched Opportunity: {opportunity}")  # Debugging line
    return opportunity


def fetch_opportunity_details(opportunity_id):
    db = connect_db()
    cursor = db.cursor(dictionary=True)
    
    query = """
        SELECT O.organization_id, O.name AS organization_name, V.opportunity_id, V.title, V.description AS role_description, V.category, V.required_skills, V.location_address,  
               V.start_date, V.end_date, V.time_commitment  
        FROM Volunteer_Opportunities V
        JOIN Organizations O ON V.organization_id = O.organization_id
        WHERE V.opportunity_id = %s
    """
    
    try:
        cursor.execute(query, (opportunity_id,))
        opportunity = cursor.fetchone()
        print(f"Fetched opportunity: {opportunity}")
        return opportunity
    except mysql.connector.Error as err:
        print(f"Error fetching opportunity details: {err}")
        return None
    finally:
        cursor.close()
        db.close()


def fetch_total_opportunities():
    try:
        db = connect_db()
        cursor = db.cursor()

        # Query to count total opportunities
        cursor.execute("SELECT COUNT(*) FROM Volunteer_Opportunities")
        result = cursor.fetchone()
        
        if result is not None:
            return result[0]  # Access the count from the tuple
        else:
            return 0  # No opportunities in the table
    
    except Exception as e:
        print(f"An error occurred while fetching total opportunities: {e}")    # Log the error
        return None
    
    finally:
        if cursor:
            cursor.close()
        if db:
            db.close()


# Function to fetch recommended opportunities for a user based on their skills and past activities
def get_recommended_opportunities(user_id):
    user_skills = get_user_skills(user_id)
    
    # If the user has no skills, we recommend all opportunities
    if not user_skills:
        print("User has no skills. Fetching general opportunities...")
        return fetch_opportunities(limit=5)

    # If the user has skills, filter opportunities that require those skills
    print(f"User skills: {user_skills}. Fetching matching opportunities...")
    recommended_opportunities = fetch_opportunities(skills=user_skills, limit=6)

    print(f"Matching opportunities: {recommended_opportunities}")  # Debug log to verify query results

    if not recommended_opportunities:
        print("No opportunities found matching user skills.")
        return fetch_opportunities(limit=3)  # Fallback to general opportunities if none found

    return recommended_opportunities


# Function to get opportunities based on the user's location and preferences
def get_filtered_opportunities(user_id, location=None, category=None):
    # Fetch user’s location or use the provided filter
    user_location = get_user_profile(user_id).get('location', None) if not location else location

    # Fetch opportunities based on filters and location
    return fetch_opportunities(location=user_location, category=category)

# Function to fetch all opportunities in a specific category
def fetch_opportunities_by_category(category, offset=0, limit=5):
    return fetch_opportunities(category=category, offset=offset, limit=limit)


# Function to recommend volunteer opportunities based on a user's profile (skills, previous volunteer work)
def recommend_opportunities(user_id):
    # Fetch user skills
    user_skills = get_user_skills(user_id)

    # Fetch opportunities with matching skills
    recommended_opportunities = fetch_opportunities(skills=user_skills)

    return recommended_opportunities



def express_user_interest(user_id, opportunity_id, comment=None):
    """
    Insert a new record in the User_Opportunities table.
    """
    try:
        db = connect_db()
        cursor = db.cursor()

        # Check if user and opportunity exist
        user_check_query = "SELECT COUNT(*) FROM Users WHERE user_id = %s"
        opportunity_check_query = "SELECT COUNT(*) FROM Volunteer_Opportunities WHERE opportunity_id = %s"

        cursor.execute(user_check_query, (user_id,))
        user_exists = cursor.fetchone()[0]

        cursor.execute(opportunity_check_query, (opportunity_id,))
        opportunity_exists = cursor.fetchone()[0]

        if not user_exists or not opportunity_exists:
            return {"status": "error", "message": "Invalid user or opportunity ID"}

        # Insert the record
        insert_query = """
        INSERT INTO User_Opportunities (user_id, opportunity_id, comment)
        VALUES (%s, %s, %s)
        """
        cursor.execute(insert_query, (user_id, opportunity_id, comment))
        db.commit()

        return {"status": "success", "message": "Interest expressed successfully!"}
    except mysql.connector.Error as err:
        return {"status": "error", "message": f"Database error: {err}"}
    finally:
        cursor.close()
        db.close







