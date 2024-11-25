// static/js/script.js

function toggleForm() {
    // Get references to the login and signup forms
    const signupForm = document.getElementById('signup-form');
    const loginForm = document.getElementById('login-form');

    // Toggle the visibility of the forms
    signupForm.classList.toggle('hidden');
    loginForm.classList.toggle('hidden');
}
