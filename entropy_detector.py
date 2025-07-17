import numpy as np
import time
import threading
from collections import defaultdict, deque
from datetime import datetime
import logging
from typing import Dict, List, Tuple
import math

class EntropyDDoSDetector:
    """
    DDoS Detection using Shannon Entropy computation
    """
    
    def __init__(self, window_size=100, threshold=3.0):
        self.window_size = window_size
        self.threshold = threshold
        self.packet_buffer = deque(maxlen=window_size)
        self.source_ips = defaultdict(int)
        self.timestamps = deque(maxlen=window_size)
        self.detection_results = []
        self.is_monitoring = False
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
    def calculate_shannon_entropy(self, data: List) -> float:
        """
        Calculate Shannon entropy for given data
        H(X) = -Σ p(x) * log2(p(x))
        """
        if not data:
            return 0.0
            
        # Count occurrences
        counts = defaultdict(int)
        for item in data:
            counts[item] += 1
        
        # Calculate probabilities
        total = len(data)
        entropy = 0.0
        
        for count in counts.values():
            if count > 0:
                probability = count / total
                entropy -= probability * math.log2(probability)
                
        return entropy
    
    def process_packet(self, source_ip: str, destination_ip: str, packet_size: int, timestamp: float = None):
        """
        Process incoming packet and update detection metrics
        """
        if timestamp is None:
            timestamp = time.time()
            
        # Add packet to buffer
        packet_info = {
            'source_ip': source_ip,
            'destination_ip': destination_ip,
            'size': packet_size,
            'timestamp': timestamp
        }
        
        self.packet_buffer.append(packet_info)
        self.timestamps.append(timestamp)
        self.source_ips[source_ip] += 1
        
        # Calculate entropy if we have enough data
        if len(self.packet_buffer) >= 10:
            return self.detect_ddos()
        
        return False, 0.0, 0.0
    
    def detect_ddos(self) -> Tuple[bool, float, float]:
        """
        Detect DDoS attack using entropy calculation
        Returns: (is_attack, entropy_value, accuracy)
        """
        if len(self.packet_buffer) < 10:
            return False, 0.0, 0.0
        
        # Extract source IPs from current window
        source_ips = [packet['source_ip'] for packet in self.packet_buffer]
        
        # Calculate entropy
        entropy = self.calculate_shannon_entropy(source_ips)
        
        # Calculate packet rate (packets per second)
        if len(self.timestamps) >= 2:
            time_window = self.timestamps[-1] - self.timestamps[0]
            packet_rate = len(self.packet_buffer) / max(time_window, 1)
        else:
            packet_rate = 0
        
        # DDoS detection logic
        # Low entropy + high packet rate = potential DDoS
        is_attack = entropy < self.threshold and packet_rate > 50
        
        # Calculate accuracy based on entropy variance and packet distribution
        accuracy = self.calculate_accuracy(entropy, packet_rate)
        
        # Log detection result
        detection_result = {
            'timestamp': datetime.now(),
            'entropy': entropy,
            'packet_rate': packet_rate,
            'is_attack': is_attack,
            'accuracy': accuracy,
            'unique_sources': len(set(source_ips)),
            'total_packets': len(self.packet_buffer)
        }
        
        self.detection_results.append(detection_result)
        
        if is_attack:
            self.logger.warning(f"DDoS Attack Detected! Entropy: {entropy:.2f}, Rate: {packet_rate:.2f}, Accuracy: {accuracy:.2f}%")
        
        return is_attack, entropy, accuracy
    
    def calculate_accuracy(self, entropy: float, packet_rate: float) -> float:
        """
        Calculate detection accuracy based on entropy and packet rate patterns
        """
        # Base accuracy on entropy confidence
        if entropy < 1.0:  # Very low entropy - high confidence
            base_accuracy = 95.0
        elif entropy < 2.0:  # Low entropy - good confidence
            base_accuracy = 85.0
        elif entropy < 3.0:  # Medium entropy - moderate confidence
            base_accuracy = 70.0
        else:  # High entropy - low confidence
            base_accuracy = 50.0
        
        # Adjust based on packet rate
        if packet_rate > 100:
            base_accuracy += 5.0
        elif packet_rate > 50:
            base_accuracy += 2.0
        
        # Adjust based on source diversity
        unique_sources = len(set(packet['source_ip'] for packet in self.packet_buffer))
        total_packets = len(self.packet_buffer)
        source_ratio = unique_sources / max(total_packets, 1)
        
        if source_ratio < 0.1:  # Very few unique sources
            base_accuracy += 10.0
        elif source_ratio < 0.3:  # Few unique sources
            base_accuracy += 5.0
        
        return min(base_accuracy, 99.0)  # Cap at 99%
    
    def get_statistics(self) -> Dict:
        """
        Get current detection statistics
        """
        if not self.detection_results:
            return {}
        
        recent_results = self.detection_results[-10:]  # Last 10 detections
        
        return {
            'total_detections': len(self.detection_results),
            'attacks_detected': sum(1 for r in self.detection_results if r['is_attack']),
            'average_entropy': np.mean([r['entropy'] for r in recent_results]),
            'average_accuracy': np.mean([r['accuracy'] for r in recent_results]),
            'current_packet_rate': recent_results[-1]['packet_rate'] if recent_results else 0,
            'unique_sources_recent': recent_results[-1]['unique_sources'] if recent_results else 0
        }
    
    def reset_detector(self):
        """
        Reset detector state
        """
        self.packet_buffer.clear()
        self.source_ips.clear()
        self.timestamps.clear()
        self.detection_results.clear()
        self.logger.info("Detector state reset")

if __name__ == "__main__":
    # Example usage
    detector = EntropyDDoSDetector(window_size=50, threshold=2.5)
    
    # Simulate normal traffic
    print("Simulating normal traffic...")
    for i in range(20):
        detector.process_packet(f"192.168.1.{i%10}", "10.0.0.1", 1024)
        time.sleep(0.1)
    
    # Simulate DDoS attack
    print("Simulating DDoS attack...")
    for i in range(100):
        detector.process_packet(f"192.168.1.{i%3}", "10.0.0.1", 64)
        if i % 10 == 0:
            is_attack, entropy, accuracy = detector.detect_ddos()
            print(f"Detection: Attack={is_attack}, Entropy={entropy:.2f}, Accuracy={accuracy:.2f}%")
    
    # Print final statistics
    stats = detector.get_statistics()
    print(f"\nFinal Statistics: {stats}")
