// custom.js for PVLogger Dashboard
// Generate last 12 months for dropdown
function getLast12Months() {
    const months = [];
    const now = new Date();
    for (let i = 0; i < 12; i++) {
        const d = new Date(now.getFullYear(), now.getMonth() - i, 1);
        months.push({
            month: d.getMonth() + 1,
            year: d.getFullYear(),
            label: d.toLocaleString('default', { month: 'long', year: 'numeric' })
        });
    }
    return months;
}

// Populate dropdown
document.addEventListener('DOMContentLoaded', function () {
    const menu = document.getElementById('monthYearMenu');
    if (!menu) return;
    getLast12Months().forEach(({ month, year, label }) => {
        const li = document.createElement('li');
        const a = document.createElement('a');
        a.className = 'dropdown-item';
        a.href = '#';
        a.textContent = label;
        a.dataset.month = month;
        a.dataset.year = year;
        li.appendChild(a);
        menu.appendChild(li);
    });

    // Handle dropdown selection
    menu.addEventListener('click', function (e) {
        if (e.target.matches('.dropdown-item')) {
            e.preventDefault();
            const month = e.target.dataset.month;
            const year = e.target.dataset.year;
            document.getElementById('monthDropdown').textContent = e.target.textContent;
            fetchMonthlyData(month, year);
        }
    });
});

function fetchMonthlyData(month, year) {
    fetch(`/monthly-data/?month=${month}&year=${year}`)
        .then(res => res.json())
        .then(data => {
            if (data.dates && data.generation_values && data.consumption_values) {
                showMonthlyChart(data);
            }
        });
}

function showMonthlyChart(data) {
    document.getElementById('monthlyChartContainer').style.display = '';
    // Format dates to show only the date part (YYYY-MM-DD)
    const formattedDates = data.dates.map(dateStr => dateStr.split('T')[0]);
    const trace1 = {
        x: formattedDates,
        y: data.generation_values,
        name: 'Generation (kWh)',
        mode: 'lines+markers',
        type: 'scatter',
        marker: { color: '#0d6efd' }
    };
    const trace2 = {
        x: formattedDates,
        y: data.consumption_values,
        name: 'Consumption (kWh)',
        mode: 'lines+markers',
        type: 'scatter',
        marker: { color: '#ffc107' }
    };
    const maxY = Math.max(
        ...data.generation_values,
        ...data.consumption_values
    ) + 3;
    const layout = {
        xaxis: { title: 'Date' },
        yaxis: {
            title: 'Energy (kWh)',
            titlefont: { color: '#333' },
            tickfont: { color: '#333' },
            range: [0, maxY]
        },
        legend: { orientation: 'h', x: 0.5, xanchor: 'center', y: 1.1 }
    };
    Plotly.newPlot('monthlyChart', [trace1, trace2], layout, { responsive: true });
}
