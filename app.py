from flask import Flask, render_template, jsonify, request
from flask_socketio import SocketIO, emit
import threading
import time
import json
import os
from datetime import datetime
from entropy_detector import EntropyDDoSDetector
from packet_simulator import PacketSimulator, PacketGenerator
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'ddos_detection_secret_key')
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# Configuration from environment variables
ENTROPY_THRESHOLD = float(os.environ.get('ENTROPY_THRESHOLD', '2.5'))
WINDOW_SIZE = int(os.environ.get('WINDOW_SIZE', '100'))
PACKET_RATE_THRESHOLD = int(os.environ.get('PACKET_RATE_THRESHOLD', '50'))

# Global objects
detector = EntropyDDoSDetector(window_size=WINDOW_SIZE, threshold=ENTROPY_THRESHOLD)
simulator = PacketSimulator()
monitoring_active = False
simulation_thread = None

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('index.html')

@app.route('/api/status')
def get_status():
    """Get current system status"""
    stats = detector.get_statistics()
    sim_stats = simulator.get_stats()
    
    # Get current detection state
    is_attack, current_entropy, current_accuracy = detector.get_current_state()
    
    return jsonify({
        'detector_stats': stats,
        'simulator_stats': sim_stats,
        'monitoring_active': monitoring_active,
        'current_entropy': current_entropy,
        'current_accuracy': current_accuracy,
        'is_attack': is_attack,
        'packet_count': len(detector.packet_buffer),
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/start_monitoring', methods=['POST'])
def start_monitoring():
    """Start DDoS monitoring"""
    global monitoring_active
    
    if not monitoring_active:
        monitoring_active = True
        # Start monitoring thread
        monitor_thread = threading.Thread(target=monitoring_loop)
        monitor_thread.daemon = True
        monitor_thread.start()
        
        logger.info("DDoS monitoring started")
        return jsonify({'status': 'success', 'message': 'Monitoring started'})
    
    return jsonify({'status': 'warning', 'message': 'Monitoring already active'})

@app.route('/api/stop_monitoring', methods=['POST'])
def stop_monitoring():
    """Stop DDoS monitoring"""
    global monitoring_active
    
    monitoring_active = False
    simulator.stop_simulation()
    
    logger.info("DDoS monitoring stopped")
    return jsonify({'status': 'success', 'message': 'Monitoring stopped'})

@app.route('/api/start_simulation', methods=['POST'])
def start_simulation():
    """Start traffic simulation"""
    global simulation_thread
    
    sim_type = request.json.get('type', 'mixed')
    
    if sim_type == 'normal':
        simulation_thread = threading.Thread(
            target=lambda: simulator.send_normal_traffic(duration=60, rate=20)
        )
    elif sim_type == 'ddos':
        simulation_thread = threading.Thread(
            target=lambda: simulator.send_ddos_traffic(duration=30, rate=500)
        )
    else:  # mixed
        simulation_thread = simulator.start_mixed_simulation(
            callback_func=lambda phase, count: socketio.emit('simulation_phase', {
                'phase': phase, 
                'packet_count': count
            })
        )
    
    if simulation_thread and not simulation_thread.is_alive():
        simulation_thread.start()
    
    return jsonify({'status': 'success', 'message': f'{sim_type} simulation started'})

@app.route('/api/test_detection', methods=['POST'])
def test_detection():
    """Test detection with generated packets"""
    test_type = request.json.get('type', 'normal')
    
    if test_type == 'normal':
        packets = PacketGenerator.generate_normal_packets(100)
    else:
        packets = PacketGenerator.generate_ddos_packets(300, 5)
    
    results = []
    detector.reset_detector()
    
    for packet in packets:
        is_attack, entropy, accuracy = detector.process_packet(
            packet['source_ip'],
            packet['destination_ip'],
            packet['size'],
            packet['timestamp']
        )
        
        if len(detector.packet_buffer) >= 10:  # Only record when we have enough data
            results.append({
                'timestamp': packet['timestamp'],
                'entropy': entropy,
                'accuracy': accuracy,
                'is_attack': is_attack
            })
    
    stats = detector.get_statistics()
    
    return jsonify({
        'status': 'success',
        'test_type': test_type,
        'results': results[-20:],  # Last 20 results
        'final_stats': stats
    })

@app.route('/api/reset', methods=['POST'])
def reset_system():
    """Reset detector and stop all simulations"""
    global monitoring_active
    
    monitoring_active = False
    simulator.stop_simulation()
    detector.reset_detector()
    
    return jsonify({'status': 'success', 'message': 'System reset'})

def monitoring_loop():
    """Main monitoring loop for real-time detection"""
    global monitoring_active
    
    while monitoring_active:
        try:
            # Generate some test packets for demonstration
            if len(detector.packet_buffer) < 50:
                # Generate mixed traffic for demo
                for _ in range(10):
                    if monitoring_active:
                        packet = PacketGenerator.generate_normal_packets(1)[0]
                        is_attack, entropy, accuracy = detector.process_packet(
                            packet['source_ip'],
                            packet['destination_ip'],
                            packet['size']
                        )
            
            # Always get current detection state (even if no new packets)
            is_attack, entropy, accuracy = detector.get_current_state()
            
            # Emit real-time data to frontend
            socketio.emit('detection_update', {
                'timestamp': datetime.now().isoformat(),
                'entropy': entropy,
                'accuracy': accuracy,
                'is_attack': is_attack,
                'packet_count': len(detector.packet_buffer)
            })
            
            # Send statistics update
            stats = detector.get_statistics()
            socketio.emit('stats_update', stats)
            
            time.sleep(1)  # Update every second
            
        except Exception as e:
            logger.error(f"Monitoring loop error: {e}")
            time.sleep(5)

@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    logger.info('Client connected')
    emit('status', {'message': 'Connected to DDoS Detection System'})

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    logger.info('Client disconnected')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    host = os.environ.get('HOST', '0.0.0.0')
    debug = os.environ.get('DEBUG', 'False').lower() == 'true'
    
    logger.info(f"Starting DDoS Detection Web Application on {host}:{port}")
    socketio.run(app, debug=debug, host=host, port=port)
