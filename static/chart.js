let myChart;
const vehicleColorMap = {};
const presetColors = [
    'rgba(255, 99, 132, 0.8)',
    'rgba(54, 162, 235, 0.8)',
    'rgba(255, 206, 86, 0.8)',
    'rgba(75, 192, 192, 0.8)',
    'rgba(153, 102, 255, 0.8)',
    'rgba(255, 159, 64, 0.8)',
    'rgba(201, 203, 207, 0.8)',
    'rgba(102, 255, 102, 0.8)',
    'rgba(255, 102, 255, 0.8)',
    'rgba(102, 255, 255, 0.8)'
];
let colorIndex = 0;


export function drawChart(chartData) {
    const ctx = document.getElementById('myChart').getContext('2d');
    if (myChart) {
        myChart.destroy();
    }
    myChart = new Chart(ctx, {
        type: 'bar',
        data: chartData,
        options: {
            responsive: true,
            maintainAspectRatio: true,
            scales: {
                x: {
                    stacked: true,
                    title: {
                        display: true,
                        text: '時間帯'
                    }
                },
                y: {
                    stacked: true,
                    title: {
                        display: true,
                        text: 'イベント数'
                    }
                }
            }
        }
    });
}

export function processEvents(events) {
    const hourlyData = {};
    
    // イベントデータを時間帯と車両名ごとに集計
    events.forEach(event => {
        const date = new Date(event.pushed_timestamp);
        const hour = date.getHours();
        const vehicleName = event.name;

        if (!hourlyData[hour]) {
            hourlyData[hour] = {};
        }
        if (!hourlyData[hour][vehicleName]) {
            hourlyData[hour][vehicleName] = 0;
        }
        hourlyData[hour][vehicleName]++;
    });

    // 0時から23時までのすべての時間を配列で固定
    const allHours = Array.from({length: 24}, (_, i) => i);
    const allNames = [...new Set(events.map(e => e.name))].sort();

    const datasets = allNames.map(vehicle => {
        const data = allHours.map(hour => {
            // hourlyDataに該当データがなければ0を返す
            return hourlyData[hour]?.[vehicle] || 0;
        });
        return {
            label: vehicle,
            data: data,
            backgroundColor: getVehicleColor(vehicle)
        };
    });

    const chartData = {
        labels: allHours.map(h => `${h}:00`),
        datasets: datasets
    };

    drawChart(chartData);
}

export function getVehicleColor(vehicle) {
    if (vehicleColorMap[vehicle]) {
        return vehicleColorMap[vehicle];
    }
    const color = presetColors[colorIndex % presetColors.length];
    vehicleColorMap[vehicle] = color;
    colorIndex++;
    return color;
}