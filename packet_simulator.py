import socket
import threading
import time
import random
import ipaddress
from typing import List
import logging

class PacketSimulator:
    """
    Simulate network packets for DDoS testing
    """
    
    def __init__(self, target_ip="127.0.0.1", target_port=8080):
        self.target_ip = target_ip
        self.target_port = target_port
        self.is_running = False
        self.packet_count = 0
        self.threads = []
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    def generate_random_ip(self) -> str:
        """Generate random IP address"""
        return str(ipaddress.IPv4Address(random.randint(1, 0xFFFFFFFF)))
    
    def send_normal_traffic(self, duration: int = 60, rate: int = 10):
        """
        Simulate normal network traffic
        Args:
            duration: How long to send traffic (seconds)
            rate: Packets per second
        """
        self.logger.info(f"Starting normal traffic simulation for {duration}s at {rate} pps")
        
        start_time = time.time()
        packet_interval = 1.0 / rate
        
        while time.time() - start_time < duration and self.is_running:
            try:
                # Generate diverse source IPs for normal traffic
                source_ip = self.generate_random_ip()
                
                # Simulate packet by creating socket connection
                self._simulate_packet(source_ip, random.randint(512, 1500))
                
                time.sleep(packet_interval)
                
            except Exception as e:
                self.logger.error(f"Error in normal traffic: {e}")
    
    def send_ddos_traffic(self, duration: int = 30, rate: int = 1000, source_ips: List[str] = None):
        """
        Simulate DDoS attack traffic
        Args:
            duration: How long to send attack traffic (seconds)
            rate: Packets per second
            source_ips: Limited set of source IPs (simulates botnet)
        """
        if source_ips is None:
            # Simulate botnet with limited IP range
            source_ips = [f"192.168.{random.randint(1,10)}.{random.randint(1,50)}" for _ in range(5)]
        
        self.logger.warning(f"Starting DDoS simulation for {duration}s at {rate} pps from {len(source_ips)} sources")
        
        start_time = time.time()
        packet_interval = 1.0 / rate
        
        while time.time() - start_time < duration and self.is_running:
            try:
                # Use limited source IPs (characteristic of DDoS)
                source_ip = random.choice(source_ips)
                
                # Smaller packet sizes for DDoS
                self._simulate_packet(source_ip, random.randint(64, 512))
                
                time.sleep(packet_interval)
                
            except Exception as e:
                self.logger.error(f"Error in DDoS traffic: {e}")
    
    def _simulate_packet(self, source_ip: str, packet_size: int):
        """
        Simulate a single packet
        """
        try:
            # Create a socket to simulate packet
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(0.1)
            
            # Attempt connection (will likely fail, but simulates traffic)
            try:
                sock.connect((self.target_ip, self.target_port))
                sock.send(b'X' * min(packet_size, 1024))
            except:
                pass  # Expected to fail for simulation
            finally:
                sock.close()
            
            self.packet_count += 1
            
        except Exception as e:
            pass  # Silently handle errors for simulation
    
    def start_mixed_simulation(self, callback_func=None):
        """
        Run a mixed simulation with normal and attack traffic
        """
        self.is_running = True
        self.packet_count = 0
        
        def simulation_sequence():
            try:
                # Phase 1: Normal traffic (30 seconds)
                self.logger.info("Phase 1: Normal traffic")
                self.send_normal_traffic(duration=30, rate=20)
                
                if callback_func:
                    callback_func("normal", self.packet_count)
                
                time.sleep(2)
                
                # Phase 2: DDoS attack (20 seconds)
                self.logger.info("Phase 2: DDoS attack")
                self.send_ddos_traffic(duration=20, rate=500)
                
                if callback_func:
                    callback_func("attack", self.packet_count)
                
                time.sleep(2)
                
                # Phase 3: Return to normal (20 seconds)
                self.logger.info("Phase 3: Back to normal")
                self.send_normal_traffic(duration=20, rate=15)
                
                if callback_func:
                    callback_func("normal", self.packet_count)
                
            except Exception as e:
                self.logger.error(f"Simulation error: {e}")
            finally:
                self.is_running = False
        
        # Run simulation in separate thread
        sim_thread = threading.Thread(target=simulation_sequence)
        sim_thread.start()
        self.threads.append(sim_thread)
        
        return sim_thread
    
    def stop_simulation(self):
        """Stop all traffic simulation"""
        self.is_running = False
        self.logger.info("Stopping traffic simulation")
        
        # Wait for threads to complete
        for thread in self.threads:
            thread.join(timeout=1)
        
        self.threads.clear()
    
    def get_stats(self):
        """Get simulation statistics"""
        return {
            'total_packets': self.packet_count,
            'is_running': self.is_running,
            'active_threads': len([t for t in self.threads if t.is_alive()])
        }

class PacketGenerator:
    """
    Generate packets with specific patterns for testing
    """
    
    @staticmethod
    def generate_normal_packets(count: int = 100):
        """Generate normal traffic packet data"""
        packets = []
        for i in range(count):
            packet = {
                'source_ip': PacketSimulator().generate_random_ip(),
                'destination_ip': '10.0.0.1',
                'size': random.randint(512, 1500),
                'timestamp': time.time() + i * 0.1
            }
            packets.append(packet)
        return packets
    
    @staticmethod
    def generate_ddos_packets(count: int = 500, botnet_size: int = 10):
        """Generate DDoS attack packet data"""
        # Limited source IPs (botnet)
        source_ips = [f"192.168.{random.randint(1,5)}.{random.randint(1,20)}" 
                     for _ in range(botnet_size)]
        
        packets = []
        for i in range(count):
            packet = {
                'source_ip': random.choice(source_ips),
                'destination_ip': '10.0.0.1',
                'size': random.randint(64, 256),  # Smaller packets
                'timestamp': time.time() + i * 0.01  # Higher frequency
            }
            packets.append(packet)
        return packets

if __name__ == "__main__":
    # Test packet simulation
    simulator = PacketSimulator()
    
    print("Testing packet generators...")
    
    # Test normal packet generation
    normal_packets = PacketGenerator.generate_normal_packets(50)
    print(f"Generated {len(normal_packets)} normal packets")
    
    # Test DDoS packet generation
    ddos_packets = PacketGenerator.generate_ddos_packets(200, 5)
    print(f"Generated {len(ddos_packets)} DDoS packets")
    
    # Test unique source count
    normal_sources = len(set(p['source_ip'] for p in normal_packets))
    ddos_sources = len(set(p['source_ip'] for p in ddos_packets))
    
    print(f"Normal traffic: {normal_sources} unique sources")
    print(f"DDoS traffic: {ddos_sources} unique sources")
    print(f"Source diversity ratio - Normal: {normal_sources/len(normal_packets):.2f}, DDoS: {ddos_sources/len(ddos_packets):.2f}")
