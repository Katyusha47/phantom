#!/usr/bin/env python3
"""
Service Fingerprinting Module
Identifies services and versions from banners and responses
"""

import socket
import re
from typing import Dict, Optional, List

class ServiceFingerprinter:
    """
    Service fingerprinting through banner analysis and probe responses
    """
    
    # Service signatures - regex patterns to identify services
    SIGNATURES = {
        'ssh': [
            (r'SSH-(\d+\.\d+)-OpenSSH[_-](\S+)', 'OpenSSH'),
            (r'SSH-(\d+\.\d+)-(\S+)', 'SSH Server'),
        ],
        'ftp': [
            (r'220.*ProFTPD (\S+)', 'ProFTPD'),
            (r'220.*FileZilla Server (\S+)', 'FileZilla'),
            (r'220.*vsftpd (\S+)', 'vsftpd'),
            (r'220 Microsoft FTP Service', 'Microsoft FTP'),
        ],
        'smtp': [
            (r'220.*ESMTP Postfix', 'Postfix'),
            (r'220.*ESMTP Sendmail (\S+)', 'Sendmail'),
            (r'220.*Microsoft ESMTP MAIL', 'Microsoft Exchange'),
        ],
        'http': [
            (r'Server: nginx/(\S+)', 'nginx'),
            (r'Server: Apache/(\S+)', 'Apache'),
            (r'Server: Microsoft-IIS/(\S+)', 'IIS'),
            (r'Server: lighttpd/(\S+)', 'lighttpd'),
        ],
        'mysql': [
            (r'(\d+\.\d+\.\d+)-MariaDB', 'MariaDB'),
            (r'(\d+\.\d+\.\d+)-MySQL', 'MySQL'),
        ],
        'postgresql': [
            (r'PostgreSQL (\S+)', 'PostgreSQL'),
        ],
        'redis': [
            (r'\$\d+\r\nredis_version:(\S+)', 'Redis'),
        ]
    }
    
    # HTTP probes to send
    HTTP_PROBE = b"HEAD / HTTP/1.0\r\nHost: target\r\n\r\n"
    
    # Generic probe for other services
    GENERIC_PROBE = b"\r\n"
    
    @staticmethod
    def grab_banner(ip: str, port: int, timeout: int = 3) -> Optional[str]:
        """
        Grab banner from service
        
        Args:
            ip: Target IP
            port: Target port
            timeout: Connection timeout
            
        Returns:
            Banner string or None
        """
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            sock.connect((ip, port))
            
            # Wait for automatic banner
            banner = sock.recv(4096).decode('utf-8', errors='ignore').strip()
            
            sock.close()
            return banner if banner else None
            
        except Exception:
            return None
    
    @staticmethod
    def http_probe(ip: str, port: int, timeout: int = 3) -> Optional[str]:
        """
        Send HTTP probe to get server header
        
        Args:
            ip: Target IP
            port: Target port
            timeout: Connection timeout
            
        Returns:
            HTTP response headers or None
        """
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            sock.connect((ip, port))
            
            # Send HTTP HEAD request
            sock.send(ServiceFingerprinter.HTTP_PROBE)
            response = sock.recv(4096).decode('utf-8', errors='ignore')
            
            sock.close()
            return response
            
        except Exception:
            return None
    
    @staticmethod
    def identify_service(port: int, banner: Optional[str] = None) -> Dict[str, str]:
        """
        Identify service based on port and banner
        
        Args:
            port: Port number
            banner: Service banner
            
        Returns:
            Dictionary with service information
        """
        result = {
            'service': 'unknown',
            'version': 'unknown',
            'details': ''
        }
        
        # Port-based identification (fallback)
        port_services = {
            21: 'ftp', 22: 'ssh', 23: 'telnet', 25: 'smtp',
            53: 'dns', 80: 'http', 110: 'pop3', 143: 'imap',
            443: 'https', 445: 'smb', 3306: 'mysql', 3389: 'rdp',
            5432: 'postgresql', 5900: 'vnc', 6379: 'redis',
            8080: 'http-proxy', 8443: 'https-alt', 27017: 'mongodb'
        }
        
        if port in port_services:
            result['service'] = port_services[port]
        
        # Banner-based identification (more accurate)
        if banner:
            result['details'] = banner[:100]
            
            # Try to match against signatures
            for service_type, patterns in ServiceFingerprinter.SIGNATURES.items():
                for pattern, service_name in patterns:
                    match = re.search(pattern, banner, re.IGNORECASE)
                    if match:
                        result['service'] = service_name
                        if match.groups():
                            result['version'] = ' '.join(match.groups())
                        break
        
        return result
    
    @staticmethod
    def fingerprint_port(ip: str, port: int) -> Dict[str, any]:
        """
        Complete fingerprinting of a port
        
        Args:
            ip: Target IP
            port: Target port
            
        Returns:
            Complete fingerprint information
        """
        banner = None
        
        # Special handling for HTTP/HTTPS
        if port in [80, 443, 8080, 8000, 8443]:
            banner = ServiceFingerprinter.http_probe(ip, port)
        else:
            banner = ServiceFingerprinter.grab_banner(ip, port)
        
        service_info = ServiceFingerprinter.identify_service(port, banner)
        
        return {
            'port': port,
            'banner': banner,
            'service': service_info['service'],
            'version': service_info['version'],
            'details': service_info['details']
        }


def fingerprint_target(ip: str, ports: List[int]) -> List[Dict]:
    """
    Fingerprint multiple ports on a target
    
    Args:
        ip: Target IP address
        ports: List of open ports to fingerprint
        
    Returns:
        List of fingerprint results
    """
    results = []
    
    for port in ports:
        result = ServiceFingerprinter.fingerprint_port(ip, port)
        results.append(result)
    
    return results
