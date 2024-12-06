document.getElementById('apply-filters').addEventListener('click', function() {
    const searchQuery = document.getElementById('search-bar').value;
    const category = document.getElementById('category').value;
    const location = document.getElementById('location').value;
    const skills = document.getElementById('skills').value;

    fetch('/get-opportunities', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            search: searchQuery,
            category: category,
            location: location,
            skills: skills
        })
    })
    .then(response => response.json())
    .then(data => {
        const dashboard = document.getElementById('opportunity-dashboard');
        dashboard.innerHTML = '';
        
        data.forEach(opportunity => {
            const opportunityCard = document.createElement('div');
            opportunityCard.classList.add('opportunity-card');
            
            opportunityCard.innerHTML = `
                <h3>${opportunity.title}</h3>
                <p><strong>Skills:</strong> ${opportunity.skills}</p>
                <p><strong>Location:</strong> ${opportunity.location}</p>
                <p><strong>Category:</strong> ${opportunity.category}</p>
                <p><strong>Description:</strong> ${opportunity.description.substring(0, 100)}...</p>
                <div class="view-details" onclick="viewDetails('${opportunity.id}')">View Details</div>
            `;
            
            dashboard.appendChild(opportunityCard);
        });
    });
});

function viewDetails(opportunityId) {
    window.location.href = `/opportunity/${opportunityId}`;
}
