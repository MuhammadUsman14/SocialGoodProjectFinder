document.querySelector('form').addEventListener('submit', function (e) {
    e.preventDefault();

    const formData = new FormData(this);
    const data = Object.fromEntries(formData);

    fetch(this.action, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data),
    })
        .then((response) => response.json())
        .then((result) => {
            if (result.success) {
                alert('Thank you for your donation!');
                window.location.href = '/thank-you';
            } else {
                alert('Error processing your donation. Please try again.');
            }
        })
        .catch((error) => console.error('Error:', error));
});
