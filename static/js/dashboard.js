const ctx = document.getElementById('contributionChart').getContext('2d');
const chartData = {
    labels: ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"],
    datasets: [
        {
            label: 'Hours',
            data: {{ monthly_contributions['hours'] | tojson }},
            backgroundColor: 'rgba(54, 162, 235, 0.2)',
            borderColor: 'rgba(54, 162, 235, 1)',
            borderWidth: 1
        },

        {
            label: 'Donations',
            data: {{ monthly_contributions['donations'] | tojson }},
            backgroundColor: 'rgba(255, 159, 64, 0.2)',
            borderColor: 'rgba(255, 159, 64, 1)',
            borderWidth: 1
        }
    ]
};

const contributionChart = new Chart(ctx, {
    type: 'bar',
    data: chartData,
    options: {
        responsive: true,
        scales: {
            x: { beginAtZero: true },
            y: { beginAtZero: true }
        }
    }
});
