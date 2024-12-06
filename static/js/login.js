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
document.getElementById("loginForm").addEventListener("submit", function (event) {
    event.preventDefault(); // Prevent form from refreshing the page

    const email = document.getElementById("email").value.trim();
    const password = document.getElementById("password").value.trim();
    const rememberMe = document.getElementById("rememberMe").checked;

    // Form Validation
    if (!email || !password) {
        showAlert("Please fill in both email and password.", "warning");
        return;
    }

    // Simulate Login Action
    console.log("Logging in with:", { email, password, rememberMe });
    showAlert("Login Successful! Redirecting...", "success");

    // Redirect to Welcome Page
    setTimeout(() => {
        window.location.href = "/welcome";
    }, 2000);
});

// Handle Forgot Password
document.getElementById("forgotPassword").addEventListener("click", function (event) {
    event.preventDefault(); // Prevent default behavior
    showAlert("Redirecting to password recovery page...", "info");

    setTimeout(() => {
        window.location.href = "/forgot-password";
    }, 1000);
});

// Handle Social Login Buttons
document.getElementById("facebookLogin").addEventListener("click", function () {
    showAlert("Facebook login clicked!", "info");
});

document.getElementById("googleLogin").addEventListener("click", function () {
    showAlert("Google login clicked!", "info");
});

// Handle Sign-Up Link
document.getElementById("signupLink").addEventListener("click", function (event) {
    event.preventDefault(); // Prevent default behavior
    showAlert("Redirecting to Sign-Up page...", "info");

    setTimeout(() => {
        window.location.href = "/signup";
    }, 1000);
});
