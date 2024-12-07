// Helper Function to Display Alerts
function showAlert(message, type = 'info') {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type}`;
    alertDiv.style = `
        position: fixed;
        top: 20px;
        right: 20px;
        background-color: ${type === 'success' ? '#d4edda' : '#f8d7da'};
        color: ${type === 'success' ? '#155724' : '#721c24'};
        border: 1px solid ${type === 'success' ? '#c3e6cb' : '#f5c6cb'};
        padding: 15px 20px;
        border-radius: 5px;
        z-index: 1000;
        box-shadow: 0px 2px 10px rgba(0, 0, 0, 0.1);
    `;
    alertDiv.textContent = message;

    // Append Alert to Body
    document.body.appendChild(alertDiv);

    // Remove Alert After 4 Seconds
    setTimeout(() => {
        alertDiv.remove();
    }, 4000);
}

// Handle Signup Form Submission
document.getElementById("signupForm").addEventListener("submit", function (event) {
    event.preventDefault(); // Prevent form from refreshing the page

    const fullName = document.getElementById("fullName").value.trim();
    const email = document.getElementById("email").value.trim();
    const countryCode = document.getElementById("countryCode").value.trim();
    const phone = document.getElementById("phone").value.trim();
    const password = document.getElementById("password").value.trim();

    // Validate Inputs
    if (!fullName || !email || !phone || !password) {
        showAlert("Please fill in all fields.", "danger");
        return;
    }

    // Prepare data to be sent to the backend
    const formData = {
        fullName,
        email,
        mobileNumber: countryCode + phone, // Combine the country code and phone number
        password
    };

    // Send the form data to the backend using fetch
    fetch('/signup', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showAlert("Signup Successful! Redirecting...", "success");
            setTimeout(() => {
                window.location.href = "/login"; // Redirect to login page
            }, 2000);
        } else {
            showAlert(data.message || "Signup failed. Please try again.", "danger");
        }
    })
    .catch(error => {
        showAlert("An error occurred. Please try again.", "danger");
        console.error("Error during signup:", error);
    });
});
