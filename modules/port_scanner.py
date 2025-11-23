#!/usr/bin/env python3
"""
Port Scanner - Educational Network Reconnaissance Tool
Author: Your Cybersec Mentor :3
Purpose: Learn how port scanners work by building one from scratch

This tool demonstrates:
- TCP socket connections
- Multi-threaded scanning
- Banner grabbing
- Service detection
"""

import socket
import argparse
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
import json

# Color codes for pretty output (works in Linux terminals)
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

# Common ports and their typical services
COMMON_PORTS = {
    20: "FTP-DATA", 21: "FTP", 22: "SSH", 23: "Telnet",
    25: "SMTP", 53: "DNS", 80: "HTTP", 110: "POP3",
    143: "IMAP", 443: "HTTPS", 445: "SMB", 3306: "MySQL",
    3389: "RDP", 5432: "PostgreSQL", 5900: "VNC", 6379: "Redis",
    8080: "HTTP-Proxy", 8443: "HTTPS-Alt", 27017: "MongoDB"
}


def print_banner():
    """Print a cool ASCII banner because why not"""
    banner = f"""
{Colors.OKCYAN}
╔═══════════════════════════════════════════════════════════╗
║           🔍 Network Port Scanner v1.0 🔍                ║
║                 Educational Tool                          ║
║          Use only on authorized systems!                  ║
╚═══════════════════════════════════════════════════════════╝
{Colors.ENDC}
    """
    print(banner)


def resolve_target(target):
    """
    Resolve hostname to IP address
    
    Args:
        target: Hostname or IP address
    
    Returns:
        IP address string
    """
    try:
        ip = socket.gethostbyname(target)
        return ip
    except socket.gaierror:
        print(f"{Colors.FAIL}[!] Error: Cannot resolve hostname '{target}'{Colors.ENDC}")
        sys.exit(1)


def grab_banner(ip, port, timeout=2):
    """
    Attempt to grab service banner from an open port
    
    This is how we identify what service is running!
    We connect and try to read what the service sends us.
    
    Args:
        ip: Target IP address
        port: Target port number
        timeout: Connection timeout in seconds
    
    Returns:
        Banner string or None
    """
    try:
        # Create a socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        sock.connect((ip, port))
        
        # Some services send a banner automatically (like SSH, FTP)
        banner = sock.recv(1024).decode('utf-8', errors='ignore').strip()
        sock.close()
        
        return banner if banner else None
    except:
        return None


def scan_port(ip, port, timeout=1, grab_banners=True):
    """
    Scan a single port on the target
    
    This is the core function! It attempts a TCP connection.
    If it succeeds, the port is open. If it fails, it's closed/filtered.
    
    Args:
        ip: Target IP address
        port: Port number to scan
        timeout: Connection timeout
        grab_banners: Whether to attempt banner grabbing
    
    Returns:
        Dictionary with port info or None if closed
    """
    try:
        # Create a TCP socket (SOCK_STREAM = TCP)
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        
        # Try to connect - this is what actually checks if port is open
        result = sock.connect_ex((ip, port))
        
        if result == 0:  # Port is open!
            service = COMMON_PORTS.get(port, "Unknown")
            banner = None
            
            if grab_banners:
                banner = grab_banner(ip, port)
            
            sock.close()
            
            return {
                'port': port,
                'state': 'open',
                'service': service,
                'banner': banner
            }
        else:
            sock.close()
            return None
            
    except socket.timeout:
        return None
    except socket.error:
        return None
    except KeyboardInterrupt:
        print(f"\n{Colors.WARNING}[!] Scan interrupted by user{Colors.ENDC}")
        sys.exit(0)


def parse_ports(port_string):
    """
    Parse port specification string
    
    Supports formats:
    - Single port: "80"
    - Port list: "80,443,8080"
    - Port range: "1-1000"
    - Mix: "22,80-100,443"
    
    Args:
        port_string: Port specification string
    
    Returns:
        List of port numbers
    """
    ports = set()
    
    for part in port_string.split(','):
        if '-' in part:
            # It's a range like "1-1000"
            start, end = part.split('-')
            ports.update(range(int(start), int(end) + 1))
        else:
            # It's a single port
            ports.add(int(part))
    
    return sorted(list(ports))


def scan_target(target, ports, threads=50, timeout=1, verbose=False):
    """
    Main scanning function - orchestrates the whole scan
    
    This uses ThreadPoolExecutor for concurrent scanning.
    Why? Scanning ports one-by-one is SLOW. Threading makes it fast!
    
    Args:
        target: Target hostname or IP
        ports: List of ports to scan
        threads: Number of concurrent threads
        timeout: Socket timeout
        verbose: Print verbose output
    
    Returns:
        List of open port information
    """
    ip = resolve_target(target)
    
    print(f"{Colors.OKBLUE}[*] Target: {target} ({ip}){Colors.ENDC}")
    print(f"{Colors.OKBLUE}[*] Scanning {len(ports)} ports with {threads} threads{Colors.ENDC}")
    print(f"{Colors.OKBLUE}[*] Scan started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{Colors.ENDC}")
    print(f"{Colors.HEADER}{'='*60}{Colors.ENDC}\n")
    
    open_ports = []
    
    # Use ThreadPoolExecutor for concurrent scanning
    # This is WAY faster than scanning sequentially!
    with ThreadPoolExecutor(max_workers=threads) as executor:
        # Submit all scan jobs
        future_to_port = {
            executor.submit(scan_port, ip, port, timeout): port 
            for port in ports
        }
        
        # Process results as they complete
        for future in as_completed(future_to_port):
            port = future_to_port[future]
            
            try:
                result = future.result()
                
                if result:  # Port is open!
                    open_ports.append(result)
                    
                    # Print the finding
                    banner_info = f" - {result['banner'][:50]}..." if result['banner'] else ""
                    print(f"{Colors.OKGREEN}[+] Port {result['port']}/tcp OPEN - {result['service']}{banner_info}{Colors.ENDC}")
                
                elif verbose:
                    # Only show closed ports in verbose mode
                    print(f"{Colors.FAIL}[-] Port {port}/tcp CLOSED{Colors.ENDC}")
                    
            except Exception as e:
                if verbose:
                    print(f"{Colors.WARNING}[!] Error scanning port {port}: {e}{Colors.ENDC}")
    
    print(f"\n{Colors.HEADER}{'='*60}{Colors.ENDC}")
    print(f"{Colors.OKBLUE}[*] Scan completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{Colors.ENDC}")
    print(f"{Colors.OKGREEN}[*] Found {len(open_ports)} open ports{Colors.ENDC}\n")
    
    return open_ports


def main():
    """Main entry point"""
    print_banner()
    
    # Set up command-line argument parsing
    parser = argparse.ArgumentParser(
        description="Educational TCP Port Scanner",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s -t 192.168.1.1                    # Scan common ports
  %(prog)s -t example.com -p 1-1000          # Scan range
  %(prog)s -t 10.0.0.1 -p 22,80,443 -v       # Scan specific ports verbose
  %(prog)s -t target.com -p 1-65535 -t 100   # Full scan with 100 threads
        """
    )
    
    parser.add_argument('-t', '--target', required=True, help='Target IP address or hostname')
    parser.add_argument('-p', '--ports', default='21,22,23,25,53,80,110,143,443,445,3306,3389,5432,8080',
                        help='Ports to scan (default: common ports). Format: 80,443 or 1-1000')
    parser.add_argument('-T', '--threads', type=int, default=50, 
                        help='Number of threads (default: 50)')
    parser.add_argument('--timeout', type=float, default=1.0,
                        help='Socket timeout in seconds (default: 1.0)')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='Verbose output (show closed ports)')
    parser.add_argument('-o', '--output', help='Output results to JSON file')
    
    args = parser.parse_args()
    
    # Parse port specification
    try:
        ports = parse_ports(args.ports)
    except ValueError:
        print(f"{Colors.FAIL}[!] Error: Invalid port specification{Colors.ENDC}")
        sys.exit(1)
    
    # Run the scan!
    try:
        results = scan_target(
            target=args.target,
            ports=ports,
            threads=args.threads,
            timeout=args.timeout,
            verbose=args.verbose
        )
        
        # Save to JSON if requested
        if args.output:
            output_data = {
                'target': args.target,
                'scan_time': datetime.now().isoformat(),
                'open_ports': results
            }
            
            with open(args.output, 'w') as f:
                json.dump(output_data, f, indent=2)
            
            print(f"{Colors.OKGREEN}[*] Results saved to {args.output}{Colors.ENDC}")
    
    except KeyboardInterrupt:
        print(f"\n{Colors.WARNING}[!] Scan interrupted by user{Colors.ENDC}")
        sys.exit(0)


if __name__ == "__main__":
    main()
