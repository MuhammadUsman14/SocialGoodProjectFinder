document.addEventListener('DOMContentLoaded', () => {
    const ctx = document.getElementById('contributionChart').getContext('2d');

    // Placeholder data for hours and donations
    const hoursData = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12];
    const donationsData = [1,2,3,4,5];

    // Chart configuration
    const chartData = {
        labels: ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"],
        datasets: [
            {
                label: 'Hours',
                data: hoursData,
                backgroundColor: 'rgba(54, 162, 235, 0.2)',
                borderColor: 'rgba(54, 162, 235, 1)',
                borderWidth: 1,
                hoverBackgroundColor: 'rgba(54, 162, 235, 0.5)',
                hoverBorderColor: 'rgba(54, 162, 235, 1)'
            },
            {
                label: 'Donations',
                data: donationsData,
                backgroundColor: 'rgba(255, 159, 64, 0.2)',
                borderColor: 'rgba(255, 159, 64, 1)',
                borderWidth: 1,
                hoverBackgroundColor: 'rgba(255, 159, 64, 0.5)',
                hoverBorderColor: 'rgba(255, 159, 64, 1)'
            }
        ]
    };

    const chartOptions = {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: {
                display: true,
                position: 'top'
            },
            tooltip: {
                enabled: true,
                mode: 'index',
                intersect: false
            }
        },
        scales: {
            x: {
                beginAtZero: true,
                title: {
                    display: true,
                    text: 'Months'
                }
            },
            y: {
                beginAtZero: true,
                title: {
                    display: true,
                    text: 'Contributions'
                }
            }
        }
    };

    // Render the chart
    new Chart(ctx, {
        type: 'bar',
        data: chartData,
        options: chartOptions
    });
});
