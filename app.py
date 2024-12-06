from flask import Flask, render_template, redirect, url_for, request, flash, session, jsonify
from routes.auth import create_user, verify_user, update_user_profile, insert_user_skills, get_user_id_from_email, fetch_skills, add_new_skill, get_user_contact_info, get_donation_history, get_recent_contributions, get_monthly_contributions, get_donations_by_program_and_hours, add_donation, is_organization_valid, is_donation_valid, get_user_skills, get_user_profile, fetch_opportunities, get_recommended_opportunities, fetch_opportunities_by_category, fetch_distinct_categories, fetch_total_opportunities, fetch_opportunity_details, express_user_interest # Import authentication functions from auth.py
from datetime import datetime

app = Flask(__name__)
app.secret_key = '3683a25f2a44fc627f33d91ec7cd654151f8696a6fffd057'

# Home Route - displays the login or signup page
@app.route('/')
def home():
    return render_template('start.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/exploreopportunities')
def explore_opportunities():
    return render_template('exploreopportunities.html')

# Signup Route - handles the signup form submission
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    # Get form data
    if request.method == 'POST':
        full_name = request.form['full_name']
        email = request.form['email']
        password = request.form['password']

        # Print out the user input to the terminal
        print(f"User signed up with Full Name: {full_name}, Email: {email}")

        # Call the create_user function from auth.py to insert the user into the database
        error = create_user(full_name, email, password)
        
        if error:
            flash(f"Error: {error}", 'danger')
            return redirect(url_for('signup'))  # Go back to the signup page if there was an error
    
        flash('Account created successfully! Please login.', 'success')
        return redirect(url_for('login'))
    
    return render_template('signup.html')  # Render the sign-up page if GET request


# Login Route - handles both GET (to show the form) and POST (to process the form submission)
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Get the login credentials from the form
        email = request.form['email']
        password = request.form['password']

        # Call the verify_user function from auth.py to check if the credentials are valid
        user_id = verify_user(email, password)  # Now verify_user returns user_id or None if invalid
        if user_id:
            session['user_email'] = email  # Save the email to session
            session['user_id'] = user_id  # Save the user ID to session
            flash('Login successful! Welcome back.', 'success')
            return redirect(url_for('profile_setup'))  # Redirect to the profile setup page on successful login
        else:
            flash('Invalid email or password. Please try again.', 'danger')  # Show error if login fails
            return redirect(url_for('login'))  # Stay on the login page if credentials are incorrect
    # If GET request, render the login page
    return render_template('login.html')  # Render the login form


# Skills API Route for AJAX pagination
@app.route('/skills', methods=['GET'])
def get_skills():
    offset = int(request.args.get('offset', 0))
    skills = fetch_skills(offset=offset)
    return jsonify({'skills': skills})


# Profile Setup Route - handle the profile setup after login
@app.route('/profile_setup', methods=['GET', 'POST'])
def profile_setup():
    # Ensure the user is logged in (i.e., the session contains user_email)
    user_email = session.get('user_email')
    if not user_email:
        flash('Please log in first to access the profile setup.', 'danger')
        return redirect(url_for('login'))  # Redirect to login if not logged in

    # Fetch the user's ID and current profile information
    user_id = session.get('user_id')
    if user_id is None:
        flash('User not found.', 'danger')
        return redirect(url_for('login'))

    # Fetch the user's current profile and skills
    user_profile = get_user_profile(user_id)
    user_skills = get_user_skills(user_id)

    # Check if user has address and phone number
    address_on_file = user_profile.get('address') if user_profile else None
    mobile_number_on_file = user_profile.get('mobile_number') if user_profile else None

    # Check if skip button should be enabled (based on profile completeness)
    skip_enabled = bool(address_on_file and mobile_number_on_file and len(user_skills) >= 3)

    if request.method == 'POST':
        # Collect data from the form
        address = request.form.get('address', '').strip()
        country_code = request.form.get('country_code', '').strip()
        mobile_number = request.form.get('mobile_number', '').strip()
        selected_skills = request.form.getlist('skills')
        new_skill = request.form.get('new_skill', '').strip()
        phone_number = f"{country_code}{mobile_number}"  # Combine country code and phone number

        # Validation for new users (if user profile is empty)
        if not user_profile:
            if not address or len(selected_skills) < 3:
                flash('Please fill out all required fields.', 'danger')
                return redirect(url_for('profile_setup'))

        # Attempt to update the user profile
        error = update_user_profile(user_id, address, phone_number, selected_skills, new_skill)
        if error:
            flash(error, 'danger')
            return redirect(url_for('profile_setup'))

        flash('Profile setup saved successfully!', 'success')
        return redirect(url_for('dashboard'))  # Redirect to the welcome page after successful setup

    # Fetch all available skills for rendering the form
    skills = fetch_skills()

    return render_template(
        'profile_setup.html',
        user_profile=user_profile,
        skills=skills,
        user_skills=user_skills,
        address_on_file=address_on_file,
        mobile_number_on_file=mobile_number_on_file,
        skip_enabled=skip_enabled
    )

@app.route('/dashboard')
def dashboard():
    # Get the user_id from the session
    user_email = session.get('user_email')
    user_id = get_user_id_from_email(user_email)

    if not user_email or not user_id:
        flash('Error: User not found.', 'danger')
        return redirect(url_for('home'))

    # Get user contact information
    contact_info = get_user_contact_info(user_id)

    history = get_donation_history(user_id)
    recent_contributions = get_recent_contributions()
    user_profile = get_user_profile(user_id)

    # Get monthly contributions (donations and hours for chart)
    monthly_contributions = get_monthly_contributions()

    # Structure data for chart
    chart_data = {
        "donations": monthly_contributions['donations'],
        "hours": monthly_contributions['hours']
    }

    # Get donations by program and hours by activity (for pie charts)
    donations_by_program, hours_by_activity = get_donations_by_program_and_hours()

    # Extract next_shift data
    contributions_data = get_recent_contributions()
    next_shift = contributions_data.get('next_shift', {})

    # Pass data to the dashboard template
    return render_template('dashboard.html', 
                           contact_info=contact_info,
                           history=history,
                           recent_contributions=recent_contributions,
                           next_shift=next_shift,
                           user_profile=user_profile,
                           monthly_contributions=monthly_contributions,
                           donations_by_program=donations_by_program,
                           hours_by_activity=hours_by_activity)


# Route for rendering the opportunities page
@app.route('/opportunities', methods=['GET'])
def opportunities():
    user_id = session.get('user_id')

    # Pagination parameters
    page = int(request.args.get('page', 1))  # Current page (default 1)
    limit = 10  # Opportunities per page
    offset = (page - 1) * limit  # Calculate the offset for pagination

    # Fetch total opportunities for calculating pages
    total_opportunities = fetch_total_opportunities()  # New helper function
    total_pages = (total_opportunities + limit - 1) // limit  # Ceiling division

    # Get filter parameters from the request
    location = request.args.get('location', '').strip()
    category = request.args.getlist('category') # Get multiple selected categories
    skills = request.args.get('skills', '').strip()

    print(f"Received Parameters - Location: {location}, Category: {category}, Skills: {skills}, Page: {page}")

    # Parse skills input (if provided) into a list (split by commas if needed)
    skills_list = [skill.strip() for skill in skills.split(',') if skill.strip()] if skills else None
    
    try:
        # Initially fetch general opportunities and recommended ones
        general_opportunities = fetch_opportunities(
            location=location or None, 
            category=category or None, 
            skills=skills_list or None, 
            offset=offset, 
            limit=limit
        )  # First 10 general opportunities

        recommended_opportunities = get_recommended_opportunities(user_id=user_id), # Pass the user_id dynamically
        categories = fetch_distinct_categories(offset=0, limit=5)

    except Exception as e:
        print(f"Error fetching opportunities: {e}")
        general_opportunities = []
        recommended_opportunities = []
        categories = []

    return render_template('opportunities.html', 
                           general_opportunities=general_opportunities, 
                           recommended_opportunities=recommended_opportunities,
                           categories=categories,
                           page=page,
                           total_pages=total_pages,
                           total_opportunities=total_opportunities
    )

@app.route('/opportunity/<int:opportunity_id>')
def opportunity_detail(opportunity_id):
    opportunity = fetch_opportunity_details(opportunity_id)
    if opportunity:
        print(f"Opportunity details in template context: {opportunity}")

        # Processing time commitment
        time_commitment = opportunity['time_commitment']  # Access time_commitment directly
        if time_commitment >= 20:
            commitment = f"{time_commitment} hours per month"
        else:
            commitment = f"{time_commitment} hours per week"
        
        # Make sure organization_id is passed correctly
        organization_id = opportunity['organization_id']  # Accessing it from the opportunity dictionary
        print(f"Organization ID: {opportunity.get('organization_id')}")  # Safely accessing organization_id
        
        return render_template('opportunity_detail.html', opportunity=opportunity, commitment=commitment)
    else:
        return "Opportunity not found", 404


# Route for dynamically loading more categories
@app.route('/categories', methods=['GET'])
def fetch_more_categories():
    offset = int(request.args.get('offset', 0))  # Default offset is 0
    limit = int(request.args.get('limit', 5))   # Default limit is 5

    try:
        categories = fetch_distinct_categories(offset=offset, limit=limit)
        return jsonify({'categories': categories})
    except Exception as e:
        print(f"Error fetching categories: {e}")
        return jsonify({'error': str(e)}), 500


# Route for fetching filtered opportunities based on the user's criteria
@app.route('/filter_opportunities', methods=['POST'])
def filter_opportunities():
    user_id = session.get('user_id')
    location = request.form.get('location')
    category = request.form.get('category')
    skills = request.form.getlist('skills')  # List of selected skills
    
    filtered_opportunities = fetch_opportunities(location=location, category=category, skills=skills, limit=10)
    recommended_opportunities = get_recommended_opportunities(user_id)
    
    return jsonify({
        'filtered_opportunities': filtered_opportunities,
        'recommended_opportunities': recommended_opportunities
    })


# Route for displaying the donation page
@app.route('/donate/<int:organization_id>', methods=['GET', 'POST'])
def donate_form(organization_id):
    print(f"Donate form called with organization_id: {organization_id}")
    if request.method == 'POST':
        user_id = session.get('user_id')
        if not user_id:
            flash('Please log in to donate.', 'danger')
            return redirect(url_for('login'))  # Redirect to login if not logged in

        # Extract donation data from the form
        amount = request.form['amount']
        purpose = request.form['purpose']

        # Ensure donation amount is valid
        try:
            amount = float(amount)
            if amount <= 0:
                raise ValueError
        except ValueError:
            flash('Invalid donation amount. Please enter a valid number.', 'danger')
            return redirect(request.referrer)  # Stay on the donation page

        if not is_donation_valid(amount):  # Call the is_donation_valid function from auth.py
            flash('Donation amount must be between 0 and 100,000.', 'danger')
            return redirect(request.referrer)  # Stay on the donation page
        
        # Call the add_donation function to insert the donation into the database
        message = add_donation(user_id, organization_id, amount, purpose)

        # Flash the result of the donation attempt
        if 'successfully' in message.lower():
            flash('Donation successfully added!', 'success')
        else:
            flash(f'Error: {message}', 'danger')

        # Redirect back to the opportunity details page (or fallback to home if unavailable)
        return redirect(url_for('opportunity_detail', opportunity_id=organization_id))


    # If GET request, render the donation form page
    return render_template('donate.html', organization_id=organization_id)


@app.route('/donation_history')
def donation_history():
    if 'user_id' not in session:
        flash("Please log in to view your donation history.", "error")
        return redirect(url_for('login'))

    user_id = session['user_id']
    history = get_donation_history(user_id)
    
    return render_template('donation_history.html', history=history)

@app.route('/express_interest', methods=['POST'])
def express_interest():
    user_id = session.get('user_id')  # Fetch logged-in user's ID
    if not user_id:
        return jsonify({"status": "error", "message": "User not logged in"}), 403

    # Get data from the JSON body
    data = request.get_json()

    opportunity_id = data.get('opportunity_id')
    comment = data.get('comment', None)

    if not opportunity_id:
        return jsonify({"status": "error", "message": "Missing opportunity ID"}), 400

    # Call the function from auth.py to insert data
    result = express_user_interest(user_id, opportunity_id, comment)

    # Return the result to the front-end
    if result['status'] == 'error':
        return jsonify(result), 400
    return jsonify(result), 200


# Logout Route - clears the session and logs the user out
@app.route('/logout')
def logout():
    session.clear()  # Clear all session data (including user_id)
    flash('You have logged out successfully.', 'success')
    return redirect(url_for('login'))  # Redirect to the login page


# Welcome Route - displays the welcome page after login or signup
@app.route('/welcome')
def welcome():
    return render_template('welcome.html')

if __name__ == '__main__':
    app.run(debug=True)
