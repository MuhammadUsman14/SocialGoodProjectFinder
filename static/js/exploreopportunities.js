document.addEventListener('DOMContentLoaded', () => {
    const filterInputs = document.querySelectorAll('.filter-input');
    const modal = document.getElementById('login-modal');
    const closeBtn = document.querySelector('.close-btn');

    // Add click event to filter inputs
    filterInputs.forEach(input => {
        input.addEventListener('change', () => {
            // Show the modal
            modal.style.display = 'flex';
        });
    });

    // Close the modal
    closeBtn.addEventListener('click', () => {
        modal.style.display = 'none';
    });

    // Close modal on clicking outside
    window.addEventListener('click', (e) => {
        if (e.target === modal) {
            modal.style.display = 'none';
        }
    });
});
