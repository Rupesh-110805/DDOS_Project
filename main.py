#!/usr/bin/env python3
"""
DDoS Detection System Main Application
Complete implementation with entropy computing and accuracy calculation
"""

import sys
import os
import time
import threading
from entropy_detector import EntropyDDoSDetector
from packet_simulator import PacketSimulator, PacketGenerator
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class DDoSDetectionSystem:
    """
    Main DDoS Detection System orchestrator
    """
    
    def __init__(self):
        self.detector = EntropyDDoSDetector(window_size=100, threshold=2.5)
        self.simulator = PacketSimulator()
        self.is_running = False
        self.detection_thread = None
        
    def run_complete_demo(self):
        """
        Run a complete demonstration of the DDoS detection system
        """
        print("="*60)
        print("DDoS DETECTION SYSTEM - ENTROPY COMPUTING DEMO")
        print("="*60)
        
        # Step 1: Test with normal traffic
        print("\n🟢 STEP 1: Testing with Normal Traffic")
        print("-" * 40)
        
        normal_packets = PacketGenerator.generate_normal_packets(100)
        self._process_packets(normal_packets, "Normal Traffic")
        
        # Reset detector for next test
        self.detector.reset_detector()
        time.sleep(1)
        
        # Step 2: Test with DDoS traffic
        print("\n🔴 STEP 2: Testing with DDoS Attack Traffic")
        print("-" * 45)
        
        ddos_packets = PacketGenerator.generate_ddos_packets(300, botnet_size=5)
        self._process_packets(ddos_packets, "DDoS Attack")
        
        # Step 3: Mixed traffic simulation
        print("\n🟡 STEP 3: Mixed Traffic Simulation")
        print("-" * 35)
        
        self._run_mixed_simulation()
        
        # Final results
        self._display_final_results()
        
    def _process_packets(self, packets, traffic_type):
        """Process a batch of packets and display results"""
        results = []
        
        for i, packet in enumerate(packets):
            is_attack, entropy, accuracy = self.detector.process_packet(
                packet['source_ip'],
                packet['destination_ip'],
                packet['size'],
                packet['timestamp']
            )
            
            if len(self.detector.packet_buffer) >= 10 and i % 20 == 0:
                results.append({
                    'packet_num': i + 1,
                    'entropy': entropy,
                    'accuracy': accuracy,
                    'is_attack': is_attack
                })
                
                print(f"Packet {i+1:3d}: Entropy={entropy:5.2f}, Accuracy={accuracy:5.1f}%, Attack={'YES' if is_attack else 'NO'}")
        
        # Display summary
        stats = self.detector.get_statistics()
        print(f"\n📊 {traffic_type} Summary:")
        print(f"   Total packets processed: {len(packets)}")
        print(f"   Attacks detected: {stats.get('attacks_detected', 0)}")
        print(f"   Average entropy: {stats.get('average_entropy', 0):.2f}")
        print(f"   Average accuracy: {stats.get('average_accuracy', 0):.1f}%")
        
        # Calculate accuracy metrics
        if traffic_type == "Normal Traffic":
            false_positives = stats.get('attacks_detected', 0)
            print(f"   False positives: {false_positives}")
        elif traffic_type == "DDoS Attack":
            true_positives = stats.get('attacks_detected', 0)
            total_detections = stats.get('total_detections', 1)
            detection_rate = (true_positives / max(total_detections, 1)) * 100
            print(f"   Detection rate: {detection_rate:.1f}%")
    
    def _run_mixed_simulation(self):
        """Run a mixed simulation with normal and attack traffic"""
        self.detector.reset_detector()
        
        # Phase 1: Normal traffic (30 packets)
        print("   Phase 1: Normal traffic baseline...")
        normal_packets = PacketGenerator.generate_normal_packets(30)
        
        for packet in normal_packets:
            is_attack, entropy, accuracy = self.detector.process_packet(
                packet['source_ip'], packet['destination_ip'], packet['size']
            )
        
        normal_entropy = self.detector.get_statistics().get('average_entropy', 0)
        print(f"   Normal baseline entropy: {normal_entropy:.2f}")
        
        # Phase 2: Gradual attack buildup (50 packets)
        print("   Phase 2: Attack traffic injection...")
        attack_packets = PacketGenerator.generate_ddos_packets(50, botnet_size=3)
        
        attack_detections = 0
        for i, packet in enumerate(attack_packets):
            is_attack, entropy, accuracy = self.detector.process_packet(
                packet['source_ip'], packet['destination_ip'], packet['size']
            )
            
            if is_attack:
                attack_detections += 1
                
            if i % 10 == 0:
                print(f"   Attack packet {i+1:2d}: Entropy={entropy:5.2f}, Detected={'YES' if is_attack else 'NO'}")
        
        final_stats = self.detector.get_statistics()
        print(f"\n   Mixed simulation results:")
        print(f"   Attack detections: {attack_detections}/50")
        print(f"   Final average entropy: {final_stats.get('average_entropy', 0):.2f}")
        print(f"   Overall accuracy: {final_stats.get('average_accuracy', 0):.1f}%")
    
    def _display_final_results(self):
        """Display final system performance results"""
        print("\n" + "="*60)
        print("FINAL SYSTEM PERFORMANCE ANALYSIS")
        print("="*60)
        
        stats = self.detector.get_statistics()
        
        print(f"📈 Detection Performance:")
        print(f"   Total detection cycles: {stats.get('total_detections', 0)}")
        print(f"   Attack patterns detected: {stats.get('attacks_detected', 0)}")
        print(f"   Overall system accuracy: {stats.get('average_accuracy', 0):.1f}%")
        print(f"   Average entropy threshold: {stats.get('average_entropy', 0):.2f}")
        
        print(f"\n🔬 Entropy Analysis:")
        print(f"   Entropy threshold used: {self.detector.threshold}")
        print(f"   Window size: {self.detector.window_size} packets")
        print(f"   Detection algorithm: Shannon Entropy")
        
        print(f"\n✅ Algorithm Effectiveness:")
        if stats.get('average_accuracy', 0) > 90:
            print("   🟢 EXCELLENT - High accuracy detection system")
        elif stats.get('average_accuracy', 0) > 80:
            print("   🟡 GOOD - Reliable detection with room for improvement")
        else:
            print("   🔴 NEEDS TUNING - Consider adjusting parameters")
        
        print(f"\n💡 Recommendations:")
        print(f"   - Fine-tune entropy threshold based on network characteristics")
        print(f"   - Adjust window size for faster/slower detection")
        print(f"   - Implement adaptive thresholds for better accuracy")
        print(f"   - Add additional features like packet size variance")

def main():
    """
    Main function to run the DDoS detection demonstration
    """
    try:
        # Check if web interface is requested
        if len(sys.argv) > 1 and sys.argv[1] == 'web':
            print("Starting web interface...")
            from app import app, socketio
            socketio.run(app, debug=False, host='0.0.0.0', port=5000)
        else:
            # Run console demo
            system = DDoSDetectionSystem()
            system.run_complete_demo()
            
            print("\n" + "="*60)
            print("DEMO COMPLETED")
            print("="*60)
            print("To run the web interface, use: python main.py web")
            print("Then open http://localhost:5000 in your browser")
            
    except KeyboardInterrupt:
        print("\n\nDemo interrupted by user")
    except Exception as e:
        logger.error(f"Error running demo: {e}")
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
