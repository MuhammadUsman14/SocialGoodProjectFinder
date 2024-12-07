let offset = 5; // Initial offset

function loadMoreSkills() {
    fetch(`/skills?offset=${offset}`)
        .then(response => response.json())
        .then(data => {
            const skillsList = document.getElementById('skills-list');
            data.skills.forEach(skill => {
                const skillItem = document.createElement('div');
                skillItem.className = 'skill-item';
                skillItem.innerHTML = `
                    <label>
                        <input type="checkbox" name="skills" value="${skill}"> ${skill}
                    </label>`;
                skillsList.appendChild(skillItem);
            });
            if (data.skills.length === 0) {
                alert("No more skills to load.");
            } else {
                offset += 5; // Increment offset for the next batch
            }
        })
        .catch(error => console.error('Error fetching more skills:', error));
}

// Live character counter for bio
const bioInput = document.getElementById('bio');
const bioCounter = document.getElementById('bioCounter');

bioInput.addEventListener('input', () => {
    const length = bioInput.value.length;
    bioCounter.textContent = `${length}/300`;
    if (length > 300) {
        bioCounter.style.color = 'red';
    } else {
        bioCounter.style.color = '#666';
    }
});

document.getElementById("profileForm").addEventListener("submit", function (event) {
    const countryCode = document.getElementById("countryCode").value.trim();
    const phone = document.getElementById("mobileNumber").value.trim();

    // Validate the phone number
    if (!/^\d{10}$/.test(phone)) {
        alert("Please enter a valid 10-digit phone number.");
        event.preventDefault();
        return;
    }

    const formattedNumber = `${countryCode} ${phone}`;
    console.log("Formatted Phone Number:", formattedNumber);
});
