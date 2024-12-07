// Helper Function to Display Alerts
function showAlert(message, type = 'info') {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type}`;
    alertDiv.textContent = message;

    // Append Alert to Body
    document.body.appendChild(alertDiv);

    // Remove Alert After 3 Seconds
    setTimeout(() => {
        alertDiv.remove();
    }, 3000);
}

// Handle Login Form Submission
document.getElementById("loginForm").addEventListener("submit", async function (event) {
    event.preventDefault(); // Prevent form from refreshing the page

    const email = document.getElementById("email").value.trim();
    const password = document.getElementById("password").value.trim();

    // Form Validation
    if (!email || !password) {
        showAlert("Please fill in both email and password.", "warning");
        return;
    }

    try {
        // Send login data to the backend
        const response = await fetch('/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ email, password }),
        });

        const data = await response.json();

        if (response.ok) {
            showAlert(data.message || "Login Successful! Redirecting...", "success");
            setTimeout(() => {
                window.location.href = "/dashboard"; // Redirect to dashboard
            }, 2000);
        } else {
            showAlert(data.message || "Login failed. Please try again.", "danger");
        }
    } catch (error) {
        console.error("Error during login:", error);
        showAlert("An error occurred. Please try again later.", "danger");
    }
});
