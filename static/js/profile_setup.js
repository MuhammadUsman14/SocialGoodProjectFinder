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
