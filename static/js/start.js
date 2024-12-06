// Handle "Join Now" Button
document.getElementById("joinNow").addEventListener("click", function () {
    alert("Redirecting to the Signup Page...");
    window.location.href = "/signup";
});

// Handle "Sign Up" Button
document.getElementById("signupRedirect").addEventListener("click", function () {
    window.location.href = "/signup";
});

// Handle "Login" Button
document.getElementById("loginRedirect").addEventListener("click", function () {
    window.location.href = "/login";
});

// Redirect to Opportunities Page
document.getElementById("exploreNow").addEventListener("click", function () {
    alert("Redirecting to Contact Page...");
    window.location.href = "/contact";
});
