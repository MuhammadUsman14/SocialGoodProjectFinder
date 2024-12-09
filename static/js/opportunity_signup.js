document.addEventListener('DOMContentLoaded', () => {
    const form = document.querySelector('form');
    const startDate = document.getElementById('start_date');
    const endDate = document.getElementById('end_date');
    const dayCheckboxes = document.querySelectorAll('input[type="checkbox"]');
    const errorContainer = document.querySelector('.flashes');

    // Function to display error messages
    function displayErrors(messages) {
        errorContainer.innerHTML = ''; // Clear any existing messages
        messages.forEach((message) => {
            const alertDiv = document.createElement('div');
            alertDiv.classList.add('alert', 'danger');
            alertDiv.textContent = message;
            errorContainer.appendChild(alertDiv);
        });
    }

    // Enable or disable time inputs based on checkbox state
    dayCheckboxes.forEach((checkbox) => {
        checkbox.addEventListener('change', () => {
            const startInput = document.querySelector(`#${checkbox.id}-start`);
            const endInput = document.querySelector(`#${checkbox.id}-end`);
            const isChecked = checkbox.checked;

            startInput.disabled = !isChecked;
            endInput.disabled = !isChecked;

            if (!isChecked) {
                startInput.value = ''; // Clear input when disabled
                endInput.value = '';
            }
        });
    });

    // Form validation before submission
    form.addEventListener('submit', (event) => {
        let isValid = true;
        const errorMessages = [];

        // Validate Start Date
        if (!startDate.value) {
            isValid = false;
            errorMessages.push("Start date is required.");
        }

        // Validate End Date
        if (!endDate.value) {
            isValid = false;
            errorMessages.push("End date is required.");
        }

        // Validate availability
        let availabilitySelected = false;
        dayCheckboxes.forEach((checkbox) => {
            if (checkbox.checked) {
                const startTime = document.querySelector(`#${checkbox.id}-start`).value;
                const endTime = document.querySelector(`#${checkbox.id}-end`).value;

                if (!startTime || !endTime) {
                    isValid = false;
                    errorMessages.push(`Please specify both start and end times for ${checkbox.value}.`);
                } else {
                    availabilitySelected = true;
                }
            }
        });

        if (!availabilitySelected) {
            isValid = false;
            errorMessages.push("At least one day of availability is required.");
        }

        // Show errors if validation fails
        if (!isValid) {
            event.preventDefault(); // Prevent form submission
            displayErrors(errorMessages);
        }
    });
});
