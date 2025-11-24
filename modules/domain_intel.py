#!/usr/bin/env python3
"""
Domain Intelligence Module - OSINT
WHOIS lookup and domain reconnaissance
"""

import socket
import dns.resolver
import requests
from typing import Dict, List, Optional
from datetime import datetime

class DomainIntel:
    """
    Domain and website intelligence gathering
    """
    
    def __init__(self, domain: str):
        """
        Initialize domain intelligence
        
        Args:
            domain: Target domain (without http://)
        """
        self.domain = domain.replace('http://', '').replace('https://', '').split('/')[0]
    
    def whois_lookup(self) -> Dict:
        """
        Perform WHOIS lookup
        
        Returns:
            WHOIS information
        """
        def safe_extract(value):
            """Safely extract value from whois data"""
            if value is None:
                return None
            # Handle lists (whois sometimes returns lists)
            if isinstance(value, list):
                if len(value) > 0:
                    return str(value[0])
                return None
            # Convert to string
            return str(value)
        
        try:
            import whois
            
            w = whois.whois(self.domain)
            
            # Extract relevant info with safe extraction
            info = {
                'domain': self.domain,
                'registrar': safe_extract(getattr(w, 'registrar', None)),
                'creation_date': safe_extract(getattr(w, 'creation_date', None)),
                'expiration_date': safe_extract(getattr(w, 'expiration_date', None)),
                'updated_date': safe_extract(getattr(w, 'updated_date', None)),
                'name_servers': getattr(w, 'name_servers', []) or [],
                'status': safe_extract(getattr(w, 'status', None)),
                'emails': getattr(w, 'emails', []) or [],
                'org': safe_extract(getattr(w, 'org', None)),
                'country': safe_extract(getattr(w, 'country', None)),
            }
            
            return info
            
        except ImportError:
            return {
                'error': 'python-whois not installed. Run: pip install python-whois'
            }
        except Exception as e:
            return {
                'error': f'WHOIS lookup failed: {str(e)}'
            }
    
    def dns_records(self) -> Dict:
        """
        Get DNS records
        
        Returns:
            Dictionary of DNS records
        """
        records = {
            'domain': self.domain,
            'A': [],
            'AAAA': [],
            'MX': [],
            'NS': [],
            'TXT': [],
            'CNAME': []
        }
        
        record_types = ['A', 'AAAA', 'MX', 'NS', 'TXT', 'CNAME']
        
        for record_type in record_types:
            try:
                answers = dns.resolver.resolve(self.domain, record_type, lifetime=5)
                records[record_type] = [str(rdata) for rdata in answers]
            except dns.resolver.NoAnswer:
                records[record_type] = []
            except dns.resolver.NXDOMAIN:
                records['error'] = 'Domain does not exist'
                break
            except Exception:
                records[record_type] = []
        
        return records
    
    def get_ip_info(self) -> Dict:
        """
        Get IP address and geolocation info
        
        Returns:
            IP and location information
        """
        try:
            # Get IP
            ip = socket.gethostbyname(self.domain)
            
            # Try to get geolocation (using free API)
            geo_info = {'ip': ip}
            
            try:
                response = requests.get(f'http://ip-api.com/json/{ip}', timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    geo_info.update({
                        'country': data.get('country'),
                        'region': data.get('regionName'),
                        'city': data.get('city'),
                        'isp': data.get('isp'),
                        'org': data.get('org'),
                        'timezone': data.get('timezone')
                    })
            except:
                pass
            
            return geo_info
            
        except socket.gaierror:
            return {'error': 'Could not resolve domain to IP'}
        except Exception as e:
            return {'error': str(e)}
    
    def check_web_technologies(self) -> Dict:
        """
        Detect web technologies used
        
        Returns:
            Dictionary of detected technologies
        """
        try:
            url = f"http://{self.domain}"
            response = requests.get(url, timeout=10, allow_redirects=True)
            
            tech = {
                'url': response.url,
                'status_code': response.status_code,
                'server': response.headers.get('Server', 'Unknown'),
                'powered_by': response.headers.get('X-Powered-By', 'Unknown'),
                'technologies': []
            }
            
            # Check for common tech indicators in headers
            headers = response.headers
            content = response.text.lower()
            
            # Server detection
            if 'nginx' in tech['server'].lower():
                tech['technologies'].append('Nginx')
            if 'apache' in tech['server'].lower():
                tech['technologies'].append('Apache')
            if 'cloudflare' in str(headers).lower():
                tech['technologies'].append('Cloudflare')
            
            # CMS detection
            if 'wp-content' in content or 'wordpress' in content:
                tech['technologies'].append('WordPress')
            if 'joomla' in content:
                tech['technologies'].append('Joomla')
            if 'drupal' in content:
                tech['technologies'].append('Drupal')
            
            # Framework detection
            if 'react' in content:
                tech['technologies'].append('React')
            if 'angular' in content:
                tech['technologies'].append('Angular')
            if 'vue' in content:
                tech['technologies'].append('Vue.js')
            
            return tech
            
        except Exception as e:
            return {'error': str(e)}
    
    def full_intel(self) -> Dict:
        """
        Gather all intelligence on domain
        
        Returns:
            Complete domain intelligence report
        """
        report = {
            'domain': self.domain,
            'timestamp': datetime.now().isoformat(),
            'whois': self.whois_lookup(),
            'dns': self.dns_records(),
            'ip_info': self.get_ip_info(),
            'web_tech': self.check_web_technologies()
        }
        
        return report


def domain_intelligence(domain: str) -> Dict:
    """
    Gather intelligence on a domain
    
    Args:
        domain: Target domain
        
    Returns:
        Intelligence report
    """
    intel = DomainIntel(domain)
    return intel.full_intel()
