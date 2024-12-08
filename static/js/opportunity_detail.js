document.getElementById('express-interest-form').addEventListener('submit', function (e) {
    e.preventDefault();

    fetch('{{ url_for("express_interest") }}', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ opportunity_id: this.opportunity_id.value }),
    })
        .then((response) => response.json())
        .then((data) => {
            if (data.success) {
                alert('Your interest has been recorded!');
            } else {
                alert('An error occurred. Please try again.');
            }
        })
        .catch((error) => console.error('Error:', error));
});
