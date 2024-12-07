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

    document.body.appendChild(alertDiv);

    setTimeout(() => alertDiv.remove(), 4000);
}

// Handle Signup Form Submission
document.getElementById("signupForm").addEventListener("submit", async function (event) {
    event.preventDefault();

    const fullName = document.getElementById("fullName").value.trim();
    const email = document.getElementById("email").value.trim();
    const countryCode = document.getElementById("countryCode").value.trim();
    const phone = document.getElementById("phone").value.trim();
    const password = document.getElementById("password").value.trim();

    if (!fullName || !email || !phone || !password) {
        showAlert("Please fill in all fields.", "danger");
        return;
    }

    if (!/^\d{10}$/.test(phone)) {
        showAlert("Please enter a valid 10-digit phone number.", "danger");
        return;
    }

    if (password.length < 8) {
        showAlert("Password must be at least 8 characters long.", "danger");
        return;
    }

    const formattedMobileNumber = `${countryCode}${phone}`;

    const formData = {
        fullName,
        email,
        mobileNumber: formattedMobileNumber,
        password,
    };

    try {
        const response = await fetch('/signup', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(formData),
        });

        const data = await response.json();

        if (response.ok && data.success) {
            showAlert(data.message || "Signup successful! Redirecting...", "success");
            setTimeout(() => window.location.href = "/profile_setup", 2000);
        } else {
            showAlert(data.message || "Signup failed. Please try again.", "danger");
        }
    } catch (error) {
        showAlert("An error occurred. Please try again later.", "danger");
        console.error("Error during signup:", error);
    }
});
