document.querySelector('form').addEventListener('submit', function (e) {
    e.preventDefault();  // Prevent default form submission

    const formData = new FormData(this);  // Gather form data
    
    fetch(this.action, {  // Send data via fetch to the server
        method: 'POST',
        body: formData  // Send as form data, not JSON
    })
    .then(response => response.json())  // Parse JSON response
    .then(result => {
        if (result.success) {
            alert(result.message);  // Display success message from the JSON response
            window.location.href = '/dashboard';  // Redirect after successful donation
        } else {
            alert(result.message);  // Display error message from the JSON response
        }
    })
    .catch((error) => console.error('Error:', error));  // Log errors in case of failure
});
