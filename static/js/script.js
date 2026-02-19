const ctx = document.getElementById('usageChart');

if (ctx) {
    new Chart(ctx, {
        type: 'line',
        data: {
            labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
            datasets: [{
                label: 'Energy Usage (kWh)',
                data: [400, 420, 390, 450, 430, 420],
                borderWidth: 2,
                fill: false
            }]
        }
    });
}
