document.addEventListener('DOMContentLoaded', function() {
    // Handle sector form submission
    document.getElementById('sectorForm').addEventListener('submit', function(event) {
        event.preventDefault();
        const sector = event.target.sector.value;
        
        fetch('/recommendations_by_sector', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded'
            },
            body: new URLSearchParams({ sector: sector })
        })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                document.getElementById('recommendationsList').innerText = data.error;
                return;
            }
            
            // Clear previous recommendations
            document.getElementById('recommendationsList').innerHTML = '';

            // Display recommendations
            const list = document.createElement('ul');
            data.forEach(item => {
                const listItem = document.createElement('li');
                listItem.innerText = `State: ${item.State}, Combined ESI: ${item['Combined ESI']}`;
                list.appendChild(listItem);
            });
            document.getElementById('recommendationsList').appendChild(list);

            // Update the chart
            const ctx = document.getElementById('recommendationsChart').getContext('2d');
            new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: data.map(item => item.State),
                    datasets: [{
                        label: 'Combined ESI',
                        data: data.map(item => item['Combined ESI']),
                        backgroundColor: 'rgba(75, 192, 192, 0.2)',
                        borderColor: 'rgba(75, 192, 192, 1)',
                        borderWidth: 1
                    }]
                },
                options: {
                    scales: {
                        y: {
                            beginAtZero: true
                        }
                    }
                }
            });
        });
    });
});
