document.addEventListener('DOMContentLoaded', function () {
  const form = document.querySelector('form');
  const startDate = document.getElementById('start_date');
  const endDate = document.getElementById('end_date');
  
  // Get the correct checkboxes based on their ids, and make sure to check each for change
  const dayCheckboxes = document.querySelectorAll('input[type="checkbox"]');
  
  // Form Validation before submission
  form.addEventListener('submit', function (event) {
      let isValid = true;
      let errorMessages = [];

      // Start Date Validation
      if (!startDate.value) {
          isValid = false;
          errorMessages.push("Start date is required.");
      }

      // End Date Validation
      if (!endDate.value) {
          isValid = false;
          errorMessages.push("End date is required.");
      }

      // Availability Validation
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

      // Display error messages
      if (!isValid) {
          event.preventDefault(); // Prevent form submission
          const errorContainer = document.querySelector('.flashes');
          errorContainer.innerHTML = ''; // Clear any previous messages
          errorMessages.forEach((message) => {
              const alertDiv = document.createElement('div');
              alertDiv.classList.add('alert', 'danger');
              alertDiv.textContent = message;
              errorContainer.appendChild(alertDiv);
          });
      }
  });

  // Enable/Disable time inputs based on checkbox state
  dayCheckboxes.forEach((checkbox) => {
      checkbox.addEventListener('change', function () {
          // Adjust the time inputs based on checkbox selection
          const startInput = document.querySelector(`#${checkbox.id}-start`);
          const endInput = document.querySelector(`#${checkbox.id}-end`);
          if (checkbox.checked) {
              startInput.disabled = false; // Enable the start time input
              endInput.disabled = false; // Enable the end time input
          } else {
              startInput.disabled = true; // Disable the start time input
              endInput.disabled = true; // Disable the end time input
              startInput.value = ''; // Clear the value if unchecked
              endInput.value = ''; // Clear the value if unchecked
          }
      });
  });
});
