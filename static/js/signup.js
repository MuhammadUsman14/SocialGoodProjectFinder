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

// Handle Signup Form Submission
document.getElementById("signupForm").addEventListener("submit", function (event) {
    event.preventDefault(); // Prevent form from refreshing the page

    const email = document.getElementById("email").value.trim();
    const mobile = document.getElementById("mobile").value.trim();
    const password = document.getElementById("password").value;
    const termsAccepted = document.getElementById("terms").checked;

    // Form Validation
    if (!email || !mobile || !password) {
        showAlert("Please fill in all the required fields.", "warning");
        return;
    }

    if (!termsAccepted) {
        showAlert("You must agree to the terms and conditions.", "danger");
        return;
    }

    // Simulate Signup Action
    console.log("Signing up with:", { email, mobile, password });
    showAlert("Signup Successful! Redirecting to login page...", "success");

    // Redirect to Login Page
    setTimeout(() => {
        window.location.href = "/login";
    }, 2000);
});

// Handle Social Signup Buttons
document.getElementById("facebookSignup").addEventListener("click", function () {
    showAlert("Facebook signup clicked!", "info");
});

document.getElementById("googleSignup").addEventListener("click", function () {
    showAlert("Google signup clicked!", "info");
});

// Handle Login Link
document.getElementById("loginLink").addEventListener("click", function (event) {
    event.preventDefault(); // Prevent default behavior
    showAlert("Redirecting to login page...", "info");

    setTimeout(() => {
        window.location.href = "/login";
    }, 1000);
});
