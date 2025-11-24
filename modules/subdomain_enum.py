#!/usr/bin/env python3
"""
Subdomain Enumeration Module
DNS-based subdomain discovery through brute force and zone transfers
"""

import socket
import dns.resolver
import dns.zone
import dns.query
import requests
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Set

class SubdomainEnumerator:
    """
    Subdomain enumeration through DNS queries
    """
    
    # Common subdomain wordlist
    COMMON_SUBDOMAINS = [
        'www', 'mail', 'ftp', 'localhost', 'webmail', 'smtp', 'pop', 'ns1', 'webdisk',
        'ns2', 'cpanel', 'whm', 'autodiscover', 'autoconfig', 'm', 'imap', 'test',
        'ns', 'blog', 'pop3', 'dev', 'www2', 'admin', 'forum', 'news', 'vpn', 'ns3',
        'mail2', 'new', 'mysql', 'old', 'lists', 'support', 'mobile', 'mx', 'static',
        'docs', 'beta', 'shop', 'sql', 'secure', 'demo', 'cp', 'calendar', 'wiki',
        'web', 'media', 'email', 'images', 'img', 'www1', 'intranet', 'portal', 'video',
        'sip', 'dns2', 'api', 'cdn', 'stats', 'dns1', 'ns4', 'www3', 'dns', 'search',
        'staging', 'server', 'mx1', 'chat', 'wap', 'my', 'svn', 'mail1', 'sites',
        'proxy', 'ads', 'host', 'crm', 'cms', 'backup', 'mx2', 'lyncdiscover', 'info',
        'apps', 'download', 'remote', 'db', 'forums', 'store', 'relay', 'files',
        'newsletter', 'app', 'live', 'owa', 'en', 'start', 'sms', 'office', 'exchange',
        'ipv4', 'gateway', 'public', 'prod', 'production', 'sandbox', 'alpha'
    ]
    
    def __init__(self, domain: str, wordlist: List[str] = None, threads: int = 20):
        """
        Initialize subdomain enumerator
        
        Args:
            domain: Target domain
            wordlist: Custom subdomain wordlist (uses default if None)
            threads: Number of concurrent threads
        """
        self.domain = domain
        self.wordlist = wordlist if wordlist else self.COMMON_SUBDOMAINS
        self.threads = threads
        self.found_subdomains = set()
    
    def check_subdomain(self, subdomain: str) -> Dict[str, any]:
        """
        Check if a subdomain exists
        
        Args:
            subdomain: Subdomain to check
            
        Returns:
            Dictionary with subdomain info or None
        """
        full_domain = f"{subdomain}.{self.domain}"
        
        try:
            # Try A record lookup
            answers = dns.resolver.resolve(full_domain, 'A', lifetime=2)
            ips = [str(rdata) for rdata in answers]
            
            return {
                'subdomain': full_domain,
                'ips': ips,
                'type': 'A'
            }
            
        except dns.resolver.NXDOMAIN:
            # Domain doesn't exist
            return None
        except dns.resolver.NoAnswer:
            # Try CNAME
            try:
                answers = dns.resolver.resolve(full_domain, 'CNAME', lifetime=2)
                cnames = [str(rdata) for rdata in answers]
                return {
                    'subdomain': full_domain,
                    'cnames': cnames,
                    'type': 'CNAME'
                }
            except:
                return None
        except Exception:
            return None
    
    def brute_force(self) -> List[Dict]:
        """
        Brute force subdomain enumeration
        
        Returns:
            List of found subdomains
        """
        results = []
        
        with ThreadPoolExecutor(max_workers=self.threads) as executor:
            future_to_sub = {
                executor.submit(self.check_subdomain, sub): sub 
                for sub in self.wordlist
            }
            
            for future in as_completed(future_to_sub):
                result = future.result()
                if result:
                    results.append(result)
                    self.found_subdomains.add(result['subdomain'])
        
        return results
    
    def zone_transfer(self) -> List[Dict]:
        """
        Attempt DNS zone transfer
        
        Returns:
            List of records from zone transfer, or empty if failed
        """
        results = []
        
        try:
            # Find nameservers
            ns_records = dns.resolver.resolve(self.domain, 'NS', lifetime=5)
            nameservers = [str(rdata) for rdata in ns_records]
            
            for ns in nameservers:
                try:
                    # Get NS IP
                    ns_ip = str(dns.resolver.resolve(ns, 'A', lifetime=5)[0])
                    
                    # Attempt zone transfer
                    zone = dns.zone.from_xfr(dns.query.xfr(ns_ip, self.domain, timeout=10))
                    
                    # Extract records
                    for name, node in zone.nodes.items():
                        subdomain = str(name) if str(name) != '@' else self.domain
                        full_domain = f"{subdomain}.{self.domain}" if subdomain != self.domain else self.domain
                        
                        results.append({
                            'subdomain': full_domain,
                            'source': 'zone_transfer',
                            'nameserver': ns
                        })
                        
                except Exception:
                    continue
                    
        except Exception:
            pass
        
        return results
    
    def cert_transparency(self) -> List[Dict]:
        """
        Search Certificate Transparency logs for subdomains
        Uses crt.sh API to find SSL certificates issued for the domain
        
        This discovers subdomains beyond the wordlist by checking
        public SSL certificate databases.
        
        Returns:
            List of subdomains found in CT logs
        """
        results = []
        found = set()
        
        try:
            # Query crt.sh API
            url = f"https://crt.sh/?q=%.{self.domain}&output=json"
            response = requests.get(url, timeout=30)
            
            if response.status_code == 200:
                certs = response.json()
                
                for cert in certs:
                    # Extract common name and name values
                    name_value = cert.get('name_value', '')
                    
                    # Split by newlines (multiple domains in one cert)
                    domains = name_value.split('\n')
                    
                    for domain in domains:
                        domain = domain.strip().lower()
                        
                        # Remove wildcard prefix
                        domain = domain.replace('*.', '')
                        
                        # Only include subdomains of our target
                        if domain.endswith(self.domain) and domain not in found:
                            found.add(domain)
                            
                            # Try to resolve it to verify it's active
                            try:
                                answers = dns.resolver.resolve(domain, 'A', lifetime=2)
                                ips = [str(rdata) for rdata in answers]
                                
                                results.append({
                                    'subdomain': domain,
                                    'ips': ips,
                                    'source': 'cert_transparency'
                                })
                                self.found_subdomains.add(domain)
                            except:
                                # Still add it even if not currently resolving
                                results.append({
                                    'subdomain': domain,
                                    'source': 'cert_transparency',
                                    'status': 'not_resolving'
                                })
        
        except Exception as e:
            pass
        
        return results
    
    def enumerate(self, check_zone_transfer: bool = True, check_ct_logs: bool = True) -> Dict[str, any]:
        """
        Run complete subdomain enumeration
        
        Args:
            check_zone_transfer: Whether to attempt zone transfer
            check_ct_logs: Whether to check Certificate Transparency logs
            
        Returns:
            Complete enumeration results
        """
        results = {
            'domain': self.domain,
            'zone_transfer': [],
            'brute_force': [],
            'cert_transparency': [],
            'total_found': 0
        }
        
        # Try zone transfer first (faster if it works)
        if check_zone_transfer:
            zt_results = self.zone_transfer()
            if zt_results:
                results['zone_transfer'] = zt_results
                results['total_found'] += len(zt_results)
        
        # Certificate Transparency lookup (finds subdomains beyond wordlist)
        if check_ct_logs:
            ct_results = self.cert_transparency()
            if ct_results:
                results['cert_transparency'] = ct_results
                results['total_found'] += len(ct_results)
        
        # Brute force enumeration
        bf_results = self.brute_force()
        results['brute_force'] = bf_results
        results['total_found'] += len(bf_results)
        
        return results


def enumerate_subdomains(domain: str, wordlist: List[str] = None, threads: int = 20) -> Dict:
    """
    Enumerate subdomains for a target domain
    
    Args:
        domain: Target domain
        wordlist: Optional custom wordlist
        threads: Number of concurrent threads
        
    Returns:
        Enumeration results
    """
    enumerator = SubdomainEnumerator(domain, wordlist, threads)
    return enumerator.enumerate()
