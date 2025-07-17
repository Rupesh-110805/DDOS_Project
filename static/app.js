// DDoS Detection System Frontend JavaScript
let socket;
let entropyChart;
let accuracyChart;
let entropyData = [];
let accuracyData = [];
let timeLabels = [];
let maxDataPoints = 20;

// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
    initializeSocket();
    initializeCharts();
    updateStatus();
    
    // Update status every 5 seconds
    setInterval(updateStatus, 5000);
});

// Initialize Socket.IO connection
function initializeSocket() {
    socket = io();
    
    socket.on('connect', function() {
        console.log('Connected to server');
        showAlert('Connected to DDoS Detection System', 'success');
    });
    
    socket.on('disconnect', function() {
        console.log('Disconnected from server');
        showAlert('Disconnected from server', 'danger');
    });
    
    socket.on('detection_update', function(data) {
        updateRealtimeData(data);
    });
    
    socket.on('stats_update', function(stats) {
        updateStatistics(stats);
    });
    
    socket.on('simulation_phase', function(data) {
        showAlert(`Simulation phase: ${data.phase} (${data.packet_count} packets)`, 'info');
    });
}

// Initialize Chart.js charts
function initializeCharts() {
    // Entropy Chart
    const entropyCtx = document.getElementById('entropyChart').getContext('2d');
    entropyChart = new Chart(entropyCtx, {
        type: 'line',
        data: {
            labels: timeLabels,
            datasets: [{
                label: 'Entropy Value',
                data: entropyData,
                borderColor: 'rgba(75, 192, 192, 1)',
                backgroundColor: 'rgba(75, 192, 192, 0.2)',
                tension: 0.4,
                fill: true
            }, {
                label: 'DDoS Threshold',
                data: Array(maxDataPoints).fill(2.5),
                borderColor: 'rgba(255, 99, 132, 1)',
                backgroundColor: 'rgba(255, 99, 132, 0.1)',
                borderDash: [5, 5],
                fill: false
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    labels: { color: 'white' }
                }
            },
            scales: {
                x: {
                    ticks: { color: 'white' },
                    grid: { color: 'rgba(255, 255, 255, 0.1)' }
                },
                y: {
                    ticks: { color: 'white' },
                    grid: { color: 'rgba(255, 255, 255, 0.1)' },
                    min: 0,
                    max: 6
                }
            }
        }
    });
    
    // Accuracy Chart
    const accuracyCtx = document.getElementById('accuracyChart').getContext('2d');
    accuracyChart = new Chart(accuracyCtx, {
        type: 'bar',
        data: {
            labels: timeLabels,
            datasets: [{
                label: 'Detection Accuracy (%)',
                data: accuracyData,
                backgroundColor: 'rgba(54, 162, 235, 0.6)',
                borderColor: 'rgba(54, 162, 235, 1)',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    labels: { color: 'white' }
                }
            },
            scales: {
                x: {
                    ticks: { color: 'white' },
                    grid: { color: 'rgba(255, 255, 255, 0.1)' }
                },
                y: {
                    ticks: { color: 'white' },
                    grid: { color: 'rgba(255, 255, 255, 0.1)' },
                    min: 0,
                    max: 100
                }
            }
        }
    });
}

// Update real-time detection data
function updateRealtimeData(data) {
    const timestamp = new Date(data.timestamp).toLocaleTimeString();
    
    // Add new data point
    timeLabels.push(timestamp);
    entropyData.push(data.entropy);
    accuracyData.push(data.accuracy);
    
    // Remove old data points
    if (timeLabels.length > maxDataPoints) {
        timeLabels.shift();
        entropyData.shift();
        accuracyData.shift();
    }
    
    // Update charts
    entropyChart.update('none');
    accuracyChart.update('none');
    
    // Update current values
    document.getElementById('entropy-value').textContent = data.entropy.toFixed(2);
    document.getElementById('accuracy-value').textContent = data.accuracy.toFixed(2) + '%';
    
    // Update system status
    const statusIndicator = document.querySelector('.status-indicator');
    const statusText = document.getElementById('status-text');
    
    if (data.is_attack) {
        statusIndicator.className = 'status-indicator status-attack';
        statusText.textContent = 'DDoS ATTACK DETECTED!';
        showAlert(`DDoS Attack Detected! Entropy: ${data.entropy.toFixed(2)}, Accuracy: ${data.accuracy.toFixed(2)}%`, 'danger');
    } else {
        statusIndicator.className = 'status-indicator status-active';
        statusText.textContent = 'Monitoring Active';
    }
}

// Update statistics display
function updateStatistics(stats) {
    if (stats.total_detections !== undefined) {
        document.getElementById('total-detections').textContent = stats.total_detections;
    }
    if (stats.attacks_detected !== undefined) {
        document.getElementById('attacks-detected').textContent = stats.attacks_detected;
    }
    if (stats.average_entropy !== undefined) {
        document.getElementById('avg-entropy').textContent = stats.average_entropy.toFixed(2);
    }
    if (stats.average_accuracy !== undefined) {
        document.getElementById('avg-accuracy').textContent = stats.average_accuracy.toFixed(2) + '%';
    }
    if (stats.current_packet_rate !== undefined) {
        document.getElementById('packet-rate').textContent = Math.round(stats.current_packet_rate) + ' pps';
    }
    if (stats.unique_sources_recent !== undefined) {
        document.getElementById('unique-sources').textContent = stats.unique_sources_recent;
    }
}

// API Functions
async function makeAPICall(endpoint, method = 'GET', data = null) {
    try {
        const options = {
            method: method,
            headers: {
                'Content-Type': 'application/json',
            }
        };
        
        if (data) {
            options.body = JSON.stringify(data);
        }
        
        const response = await fetch(endpoint, options);
        const result = await response.json();
        
        if (result.status === 'success') {
            showAlert(result.message, 'success');
        } else {
            showAlert(result.message, result.status || 'warning');
        }
        
        return result;
    } catch (error) {
        console.error('API call failed:', error);
        showAlert('API call failed: ' + error.message, 'danger');
        return null;
    }
}

// Control Functions
async function startMonitoring() {
    const result = await makeAPICall('/api/start_monitoring', 'POST');
    if (result && result.status === 'success') {
        const statusIndicator = document.querySelector('.status-indicator');
        const statusText = document.getElementById('status-text');
        statusIndicator.className = 'status-indicator status-active';
        statusText.textContent = 'Monitoring Active';
    }
}

async function stopMonitoring() {
    const result = await makeAPICall('/api/stop_monitoring', 'POST');
    if (result && result.status === 'success') {
        const statusIndicator = document.querySelector('.status-indicator');
        const statusText = document.getElementById('status-text');
        statusIndicator.className = 'status-indicator status-inactive';
        statusText.textContent = 'Monitoring Stopped';
    }
}

async function resetSystem() {
    const result = await makeAPICall('/api/reset', 'POST');
    if (result && result.status === 'success') {
        // Clear charts
        entropyData.length = 0;
        accuracyData.length = 0;
        timeLabels.length = 0;
        entropyChart.update();
        accuracyChart.update();
        
        // Reset displays
        document.getElementById('entropy-value').textContent = '0.00';
        document.getElementById('accuracy-value').textContent = '0.00%';
        document.getElementById('packet-rate').textContent = '0 pps';
        
        // Reset status
        const statusIndicator = document.querySelector('.status-indicator');
        const statusText = document.getElementById('status-text');
        statusIndicator.className = 'status-indicator status-inactive';
        statusText.textContent = 'System Reset';
        
        // Clear statistics
        document.getElementById('total-detections').textContent = '0';
        document.getElementById('attacks-detected').textContent = '0';
        document.getElementById('avg-entropy').textContent = '0.00';
        document.getElementById('avg-accuracy').textContent = '0.00%';
        document.getElementById('unique-sources').textContent = '0';
    }
}

async function startSimulation(type) {
    await makeAPICall('/api/start_simulation', 'POST', { type: type });
}

async function testDetection(type) {
    showAlert(`Running ${type} traffic test...`, 'info');
    
    const result = await makeAPICall('/api/test_detection', 'POST', { type: type });
    
    if (result && result.status === 'success') {
        const stats = result.final_stats;
        const testResults = result.results;
        
        showAlert(`Test completed: ${testResults.length} detection cycles, ${stats.attacks_detected || 0} attacks detected`, 'success');
        
        // Update charts with test results
        if (testResults && testResults.length > 0) {
            // Clear existing data
            entropyData.length = 0;
            accuracyData.length = 0;
            timeLabels.length = 0;
            
            // Add test results
            testResults.forEach((result, index) => {
                timeLabels.push(`T${index + 1}`);
                entropyData.push(result.entropy);
                accuracyData.push(result.accuracy);
            });
            
            entropyChart.update();
            accuracyChart.update();
        }
        
        // Update statistics
        updateStatistics(stats);
    }
}

// Update system status
async function updateStatus() {
    try {
        const response = await fetch('/api/status');
        const data = await response.json();
        
        if (data.detector_stats) {
            updateStatistics(data.detector_stats);
        }
        
        // Update current values from API if available
        if (data.current_entropy !== undefined) {
            document.getElementById('entropy-value').textContent = data.current_entropy.toFixed(2);
        }
        
        if (data.current_accuracy !== undefined) {
            document.getElementById('accuracy-value').textContent = data.current_accuracy.toFixed(2) + '%';
        }
        
        // Update buffer size
        if (data.packet_count !== undefined) {
            document.getElementById('buffer-size').textContent = data.packet_count;
        }
        
        // Update monitoring status
        const statusIndicator = document.querySelector('.status-indicator');
        const statusText = document.getElementById('status-text');
        
        if (data.monitoring_active) {
            if (data.is_attack) {
                statusIndicator.className = 'status-indicator status-attack';
                statusText.textContent = 'DDoS ATTACK DETECTED!';
            } else {
                statusIndicator.className = 'status-indicator status-active';
                statusText.textContent = 'Monitoring Active';
            }
        } else {
            statusIndicator.className = 'status-indicator status-inactive';
            statusText.textContent = 'Monitoring Inactive';
        }
        
    } catch (error) {
        console.error('Status update failed:', error);
    }
}

// Utility function to show alerts
function showAlert(message, type) {
    const alertContainer = document.getElementById('alert-container');
    
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.innerHTML = `
        <strong>${type.charAt(0).toUpperCase() + type.slice(1)}:</strong> ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    alertContainer.appendChild(alertDiv);
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        if (alertDiv && alertDiv.parentNode) {
            alertDiv.remove();
        }
    }, 5000);
}

// Add some demo data on load
function loadDemoData() {
    const demoTimes = ['10:00', '10:01', '10:02', '10:03', '10:04'];
    const demoEntropy = [4.2, 3.8, 2.1, 1.5, 3.9];
    const demoAccuracy = [75, 82, 94, 97, 78];
    
    timeLabels.push(...demoTimes);
    entropyData.push(...demoEntropy);
    accuracyData.push(...demoAccuracy);
    
    entropyChart.update();
    accuracyChart.update();
}

// Load demo data after a short delay
setTimeout(loadDemoData, 1000);
