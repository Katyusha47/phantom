#!/usr/bin/env python3
"""
PHANTOM - Invisible Network Reconnaissance Framework
Advanced penetration testing toolkit for authorized security operations
Author: Katyusha47

LEGAL NOTICE:
This tool is for educational and authorized testing purposes only.
Unauthorized use is illegal.
"""

import os
import sys
import json
from datetime import datetime
import argparse

# Import our modules from modules package
from modules.port_scanner import scan_target, resolve_target, parse_ports
from modules.service_fingerprint import fingerprint_target
from modules.subdomain_enum import enumerate_subdomains
from modules.web_crawler import crawl_website
from modules.username_enum import check_username
from modules.domain_intel import domain_intelligence

class Colors:
    """ANSI color codes for terminal output - Cyberpunk theme"""
    PURPLE = '\033[95m'      # Main title, branding
    CYAN = '\033[96m'        # Menu items, borders  
    NEON = '\033[38;5;51m'   # Accent, active status
    GREEN = '\033[92m'       # Success messages
    YELLOW = '\033[93m'      # Warnings, info
    RED = '\033[91m'         # Errors, critical
    BLUE = '\033[94m'        # Secondary info
    MAGENTA = '\033[95m'     # Highlights
    WHITE = '\033[97m'       # Standard text
    GRAY = '\033[90m'        # Subdued text
    BOLD = '\033[1m'         # Bold text
    ENDC = '\033[0m'         # Reset color


def clear_screen():
    """Clear terminal screen"""
    os.system('clear' if os.name != 'nt' else 'cls')


def print_banner():
    """Display main ASCII banner"""
    banner = f"""{Colors.PURPLE}{Colors.BOLD}
╔══════════════════════════════════════════════════════════════════╗
║                                                                  ║
║   ██████╗ ██╗  ██╗ █████╗ ███╗   ██╗████████╗ ██████╗ ███╗   ███╗
║   ██╔══██╗██║  ██║██╔══██╗████╗  ██║╚══██╔══╝██╔═══██╗████╗ ████║
║   ██████╔╝███████║███████║██╔██╗ ██║   ██║   ██║   ██║██╔████╔██║
║   ██╔═══╝ ██╔══██║██╔══██║██║╚██╗██║   ██║   ██║   ██║██║╚██╔╝██║
║   ██║     ██║  ██║██║  ██║██║ ╚████║   ██║   ╚██████╔╝██║ ╚═╝ ██║
║   ╚═╝     ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═══╝   ╚═╝    ╚═════╝ ╚═╝     ╚═╝
║                                                                  ║
║            {Colors.CYAN}「 INVISIBLE RECONNAISSANCE FRAMEWORK 」{Colors.PURPLE}             ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝
{Colors.ENDC}
{Colors.GRAY}┌────────────────────────────────────────────────────────────────┐{Colors.ENDC}
{Colors.PURPLE}│ AUTHOR  {Colors.GRAY}│{Colors.ENDC} {Colors.WHITE}Katyusha47{Colors.ENDC}
{Colors.PURPLE}│ VERSION {Colors.GRAY}│{Colors.ENDC} {Colors.NEON}1.0.0{Colors.ENDC}
{Colors.PURPLE}│ PURPOSE {Colors.GRAY}│{Colors.ENDC} {Colors.CYAN}Authorized Security Operations Only{Colors.ENDC}
{Colors.GRAY}└────────────────────────────────────────────────────────────────┘{Colors.ENDC}

{Colors.RED}{Colors.BOLD}⚠  WARNING:{Colors.ENDC} {Colors.YELLOW}Unauthorized use of this tool is illegal.{Colors.ENDC}
{Colors.GRAY}   Only test systems you own or have explicit permission to scan.{Colors.ENDC}
"""
    print(banner)


def print_menu():
    """Display main menu"""
    print(f"\n{Colors.PURPLE}{'═'*68}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.PURPLE}                      {Colors.CYAN}◈  OPERATION MENU  ◈{Colors.ENDC}")
    print(f"{Colors.PURPLE}{'═'*68}{Colors.ENDC}\n")
    
    menu_items = [
        ("PORT SCANNER", "Scan target for open ports", Colors.CYAN),
        ("SERVICE FINGERPRINT", "Identify services and versions", Colors.CYAN),
        ("SUBDOMAIN ENUMERATION", "Discover subdomains", Colors.CYAN),
        ("WEB CRAWLER", "Spider websites for intelligence", Colors.CYAN),
        ("USERNAME ENUMERATION", "Check username across platforms (OSINT)", Colors.PURPLE),
        ("DOMAIN INTELLIGENCE", "WHOIS and domain reconnaissance (OSINT)", Colors.PURPLE),
        ("FULL RECONNAISSANCE", "Run all modules sequentially", Colors.NEON),
        ("SETTINGS", "Configure scan parameters", Colors.GRAY),
        ("EXIT", "Exit the program", Colors.RED),
    ]
    
    for idx, (name, desc, color) in enumerate(menu_items, 1):
        status = f"{Colors.NEON}[◉ ACTIVE]{Colors.ENDC}"
        print(f"{Colors.GRAY}{idx:02d}.{Colors.ENDC} {color}{name:<30}{Colors.ENDC} {status}")
        print(f"    {Colors.GRAY}└─{Colors.ENDC} {Colors.WHITE}{desc}{Colors.ENDC}")
        if idx < len(menu_items):
            print()
    
    print(f"\n{Colors.PURPLE}{'═'*68}{Colors.ENDC}")


def get_user_input(prompt, input_type=str, default=None):
    """
    Get validated user input
    
    Args:
        prompt: Prompt message
        input_type: Expected type (str, int, etc.)
        default: Default value if user presses enter
        
    Returns:
        User input of specified type
    """
    while True:
        try:
            default_text = f" [default: {default}]" if default else ""
            user_input = input(f"{Colors.YELLOW}[INPUT]{Colors.ENDC} {prompt}{default_text}: ").strip()
            
            if not user_input and default is not None:
                return default
            
            if input_type == int:
                return int(user_input)
            elif input_type == bool:
                return user_input.lower() in ['y', 'yes', 'true', '1']
            else:
                return user_input
                
        except ValueError:
            print(f"{Colors.RED}[ERROR]{Colors.ENDC} Invalid input type. Please try again.")
        except KeyboardInterrupt:
            print(f"\n{Colors.YELLOW}[INFO]{Colors.ENDC} Operation cancelled.")
            return None


def save_results(results, filename=None, module_name=None):
    """
    Save results to JSON file
    
    Args:
        results: Results dictionary
        filename: Output filename (auto-generated if None)
        module_name: Name of module for auto-generated filename
    """
    if not filename:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        if module_name:
            filename = f"{module_name}_{timestamp}.json"
        else:
            filename = f"recon_results_{timestamp}.json"
    
    try:
        with open(filename, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"{Colors.GREEN}[SUCCESS]{Colors.ENDC} Results saved to {filename}")
    except Exception as e:
        print(f"{Colors.RED}[ERROR]{Colors.ENDC} Failed to save results: {e}")


def module_port_scanner():
    """Port scanner module interface"""
    clear_screen()
    print(f"\n{Colors.PURPLE}{'═'*68}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.CYAN}◈ PORT SCANNER MODULE{Colors.ENDC}")
    print(f"{Colors.PURPLE}{'═'*68}{Colors.ENDC}\n")
    
    target = get_user_input("Target IP/Hostname", str)
    if not target:
        return
    
    port_range = get_user_input("Port range (e.g., 1-1000 or 80,443)", str, "21,22,23,25,53,80,110,143,443,3306,8080")
    threads = get_user_input("Thread count", int, 50)
    
    print(f"\n{Colors.YELLOW}[INFO]{Colors.ENDC} Starting port scan...")
    print(f"{Colors.YELLOW}[INFO]{Colors.ENDC} Target: {target}")
    print(f"{Colors.YELLOW}[INFO]{Colors.ENDC} Ports: {port_range}")
    print(f"{Colors.CYAN}{'='*60}{Colors.ENDC}\n")
    
    # Parse ports
    from modules.port_scanner import parse_ports
    ports = parse_ports(port_range)
    
    # Run scan
    results = scan_target(target, ports, threads=threads, timeout=1, verbose=False)
    
    print(f"\n{Colors.GREEN}[COMPLETE]{Colors.ENDC} Found {len(results)} open ports")
    
    # Ask to save
    if results and get_user_input("Save results to file? (y/n)", bool, False):
        save_results({'scan_type': 'port_scan', 'target': target, 'results': results}, module_name='port_scan')
    
    input(f"\n{Colors.YELLOW}Press Enter to continue...{Colors.ENDC}")


def module_service_fingerprint():
    """Service fingerprinting module interface"""
    clear_screen()
    print(f"\n{Colors.PURPLE}{'═'*68}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.CYAN}◈ SERVICE FINGERPRINTING MODULE{Colors.ENDC}")
    print(f"{Colors.PURPLE}{'═'*68}{Colors.ENDC}\n")
    
    target = get_user_input("Target IP/Hostname", str)
    if not target:
        return
    
    ports_input = get_user_input("Ports to fingerprint (comma-separated)", str, "80,443,22,21")
    
    # Resolve target
    ip = resolve_target(target)
    
    # Parse ports
    ports = [int(p.strip()) for p in ports_input.split(',')]
    
    print(f"\n{Colors.YELLOW}[INFO]{Colors.ENDC} Fingerprinting services on {target} ({ip})...")
    print(f"{Colors.CYAN}{'='*60}{Colors.ENDC}\n")
    
    # Run fingerprinting
    results = fingerprint_target(ip, ports)
    
    # Display results
    for result in results:
        print(f"{Colors.GREEN}[+]{Colors.ENDC} Port {result['port']}: {result['service']}")
        if result['version'] != 'unknown':
            print(f"    Version: {result['version']}")
        if result['details']:
            print(f"    Details: {result['details'][:80]}...")
        print()
    
    # Ask to save
    if results and get_user_input("Save results to file? (y/n)", bool, False):
        save_results({'scan_type': 'service_fingerprint', 'target': target, 'results': results}, module_name='service_fingerprint')
    
    input(f"\n{Colors.YELLOW}Press Enter to continue...{Colors.ENDC}")


def module_subdomain_enum():
    """Subdomain enumeration module interface"""
    clear_screen()
    print(f"\n{Colors.PURPLE}{'═'*68}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.CYAN}◈ SUBDOMAIN ENUMERATION MODULE{Colors.ENDC}")
    print(f"{Colors.PURPLE}{'═'*68}{Colors.ENDC}\n")
    
    domain = get_user_input("Target domain (e.g., example.com)", str)
    if not domain:
        return
    
    threads = get_user_input("Thread count", int, 20)
    
    print(f"\n{Colors.YELLOW}[INFO]{Colors.ENDC} Enumerating subdomains for {domain}...")
    print(f"{Colors.YELLOW}[INFO]{Colors.ENDC} This may take a few minutes...")
    print(f"{Colors.CYAN}{'='*60}{Colors.ENDC}\n")
    
    # Run enumeration
    results = enumerate_subdomains(domain, threads=threads)
    
    # Display results
    print(f"{Colors.GREEN}[COMPLETE]{Colors.ENDC} Found {results['total_found']} subdomains\n")
    
    if results['zone_transfer']:
        print(f"{Colors.YELLOW}[ZONE TRANSFER]{Colors.ENDC} Successful! Found {len(results['zone_transfer'])} records")
    
    if results['cert_transparency']:
        print(f"{Colors.PURPLE}[CERT TRANSPARENCY]{Colors.ENDC} Found {len(results['cert_transparency'])} from SSL certificates")
    
    if results['brute_force']:
        print(f"\n{Colors.CYAN}Discovered Subdomains:{Colors.ENDC}")
        
        # Combine all sources for display
        all_subs = []
        all_subs.extend(results['brute_force'])
        all_subs.extend(results.get('cert_transparency', []))
        
        for item in all_subs[:20]:  # Show first 20
            source_tag = f"[CT]" if item.get('source') == 'cert_transparency' else ""
            if 'ips' in item:
                print(f"  {Colors.GREEN}[+]{Colors.ENDC} {source_tag} {item['subdomain']} -> {', '.join(item['ips'])}")
            elif 'cnames' in item:
                print(f"  {Colors.GREEN}[+]{Colors.ENDC} {source_tag} {item['subdomain']} -> CNAME: {', '.join(item['cnames'])}")
            elif item.get('status') == 'not_resolving':
                print(f"  {Colors.GRAY}[+]{Colors.ENDC} {source_tag} {item['subdomain']} (not resolving)")
        
        if len(all_subs) > 20:
            print(f"  ... and {len(all_subs) - 20} more")
    
    # Ask to save
    if results['total_found'] > 0 and get_user_input("\nSave results to file? (y/n)", bool, False):
        save_results(results, module_name='subdomain_enum')
    
    input(f"\n{Colors.YELLOW}Press Enter to continue...{Colors.ENDC}")


def module_web_crawler():
    """Web crawler module interface"""
    clear_screen()
    print(f"\n{Colors.PURPLE}{'═'*68}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.CYAN}◈ WEB CRAWLER MODULE{Colors.ENDC}")
    print(f"{Colors.PURPLE}{'═'*68}{Colors.ENDC}\n")
    
    url = get_user_input("Target URL (e.g., https://example.com)", str)
    if not url:
        return
    
    max_depth = get_user_input("Maximum crawl depth", int, 3)
    max_pages = get_user_input("Maximum pages to crawl", int, 50)
    
    print(f"\n{Colors.YELLOW}[INFO]{Colors.ENDC} Crawling {url}...")
    print(f"{Colors.YELLOW}[INFO]{Colors.ENDC} Max depth: {max_depth}, Max pages: {max_pages}")
    print(f"{Colors.CYAN}{'='*60}{Colors.ENDC}\n")
    
    # Run crawler
    results = crawl_website(url, max_depth=max_depth, max_pages=max_pages)
    
    # Display results
    print(f"{Colors.GREEN}[COMPLETE]{Colors.ENDC} Crawl finished\n")
    print(f"  Pages crawled: {len(results['pages'])}")
    print(f"  Forms found: {len(results['forms'])}")
    print(f"  External links: {len(results['external_links'])}")
    print(f"  Emails found: {len(results['emails'])}")
    print(f"  Robots.txt: {'Found' if results['robots_txt'] else 'Not found'}")
    print(f"  Sitemap: {'Found' if results['sitemap'] else 'Not found'}")
    
    # Show sample results
    if results['forms']:
        print(f"\n{Colors.CYAN}Forms discovered:{Colors.ENDC}")
        for form in results['forms'][:5]:
            print(f"  {Colors.GREEN}[+]{Colors.ENDC} {form['method']} {form['action']}")
    
    if results['emails']:
        print(f"\n{Colors.CYAN}Emails found:{Colors.ENDC}")
        for email in list(results['emails'])[:10]:
            print(f"  {Colors.GREEN}[+]{Colors.ENDC} {email}")
    
    # Ask to save
    if get_user_input("\nSave results to file? (y/n)", bool, False):
        save_results(results, module_name='web_crawler')
    
    input(f"\n{Colors.YELLOW}Press Enter to continue...{Colors.ENDC}")


def module_username_enum():
    """Username enumeration OSINT module"""
    clear_screen()
    print(f"\n{Colors.PURPLE}{'═'*68}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.PURPLE}◈ USERNAME ENUMERATION MODULE [OSINT]{Colors.ENDC}")
    print(f"{Colors.PURPLE}{'═'*68}{Colors.ENDC}\n")
    
    username = get_user_input("Username to check", str)
    if not username:
        return
    
    print(f"\n{Colors.YELLOW}[INFO]{Colors.ENDC} Checking username '{username}' across 50+ platforms...")
    print(f"{Colors.YELLOW}[INFO]{Colors.ENDC} This may take a moment...")
    print(f"{Colors.CYAN}{'='*60}{Colors.ENDC}\n")
    
    # Run check
    results = check_username(username)
    
    # Display results
    print(f"{Colors.GREEN}[COMPLETE]{Colors.ENDC} Scan finished\n")
    print(f"  Total platforms checked: {results['total_checked']}")
    print(f"  {Colors.GREEN}Found: {len(results['found'])}{Colors.ENDC}")
    print(f"  {Colors.RED}Not found: {len(results['not_found'])}{Colors.ENDC}")
    print(f"  {Colors.GRAY}Unknown/Error: {len(results['unknown'])}{Colors.ENDC}")
    
    # Show found profiles
    if results['found']:
        print(f"\n{Colors.PURPLE}═══ FOUND PROFILES ═══{Colors.ENDC}\n")
        for item in results['found']:
            print(f"{Colors.GREEN}[✓]{Colors.ENDC} {Colors.CYAN}{item['platform']:<20}{Colors.ENDC} {Colors.GRAY}{item['url']}{Colors.ENDC}")
    
    # Show sample of not found (first 10)
    if results['not_found']:
        print(f"\n{Colors.GRAY}═══ NOT FOUND (sample) ═══{Colors.ENDC}\n")
        for item in results['not_found'][:10]:
            print(f"{Colors.RED}[✗]{Colors.ENDC} {Colors.GRAY}{item['platform']}{Colors.ENDC}")
    
    # Ask to save
    if get_user_input("\nSave results to file? (y/n)", bool, False):
        save_results(results, module_name='username_enum')
    
    input(f"\n{Colors.YELLOW}Press Enter to continue...{Colors.ENDC}")


def module_domain_intel():
    """Domain intelligence OSINT module"""
    clear_screen()
    print(f"\n{Colors.PURPLE}{'═'*68}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.PURPLE}◈ DOMAIN INTELLIGENCE MODULE [OSINT]{Colors.ENDC}")
    print(f"{Colors.PURPLE}{'═'*68}{Colors.ENDC}\n")
    
    domain = get_user_input("Domain to investigate (e.g., example.com)", str)
    if not domain:
        return
    
    print(f"\n{Colors.YELLOW}[INFO]{Colors.ENDC} Gathering intelligence on '{domain}'...")
    print(f"{Colors.CYAN}{'='*60}{Colors.ENDC}\n")
    
    # Run intelligence gathering
    results = domain_intelligence(domain)
    
    # Display WHOIS info
    print(f"{Colors.PURPLE}═══ WHOIS INFORMATION ═══{Colors.ENDC}\n")
    if 'error' not in results['whois']:
        whois = results['whois']
        if whois.get('registrar'):
            print(f"{Colors.CYAN}Registrar:{Colors.ENDC} {whois['registrar']}")
        if whois.get('creation_date'):
            print(f"{Colors.CYAN}Created:{Colors.ENDC} {whois['creation_date']}")
        if whois.get('expiration_date'):
            print(f"{Colors.CYAN}Expires:{Colors.ENDC} {whois['expiration_date']}")
        if whois.get('org'):
            print(f"{Colors.CYAN}Organization:{Colors.ENDC} {whois['org']}")
        if whois.get('country'):
            print(f"{Colors.CYAN}Country:{Colors.ENDC} {whois['country']}")
        if whois.get('emails'):
            emails = whois['emails'] if isinstance(whois['emails'], list) else [whois['emails']]
            print(f"{Colors.CYAN}Contact Emails:{Colors.ENDC} {', '.join(emails)}")
    else:
        print(f"{Colors.YELLOW}{results['whois']['error']}{Colors.ENDC}")
    
    # Display IP info
    print(f"\n{Colors.PURPLE}═══ IP & LOCATION ═══{Colors.ENDC}\n")
    if 'error' not in results['ip_info']:
        ip_info = results['ip_info']
        print(f"{Colors.CYAN}IP Address:{Colors.ENDC} {ip_info.get('ip', 'N/A')}")
        if ip_info.get('country'):
            print(f"{Colors.CYAN}Country:{Colors.ENDC} {ip_info['country']}")
        if ip_info.get('city'):
            print(f"{Colors.CYAN}City:{Colors.ENDC} {ip_info['city']}")
        if ip_info.get('isp'):
            print(f"{Colors.CYAN}ISP:{Colors.ENDC} {ip_info['isp']}")
    else:
        print(f"{Colors.YELLOW}{results['ip_info']['error']}{Colors.ENDC}")
    
    # Display DNS records
    print(f"\n{Colors.PURPLE}═══ DNS RECORDS ═══{Colors.ENDC}\n")
    dns = results['dns']
    if dns.get('A'):
        print(f"{Colors.CYAN}A Records:{Colors.ENDC} {', '.join(dns['A'])}")
    if dns.get('MX'):
        print(f"{Colors.CYAN}MX Records:{Colors.ENDC} {', '.join(dns['MX'])}")
    if dns.get('NS'):
        print(f"{Colors.CYAN}Nameservers:{Colors.ENDC} {', '.join(dns['NS'])}")
    
    # Display web technologies
    print(f"\n{Colors.PURPLE}═══ WEB TECHNOLOGIES ═══{Colors.ENDC}\n")
    if 'error' not in results['web_tech']:
        tech = results['web_tech']
        print(f"{Colors.CYAN}Server:{Colors.ENDC} {tech.get('server', 'Unknown')}")
        if tech.get('technologies'):
            print(f"{Colors.CYAN}Technologies:{Colors.ENDC} {', '.join(tech['technologies'])}")
    else:
        print(f"{Colors.YELLOW}{results['web_tech']['error']}{Colors.ENDC}")
    
    # Ask to save
    if get_user_input("\nSave results to file? (y/n)", bool, False):
        save_results(results, module_name='domain_intel')
    
    input(f"\n{Colors.YELLOW}Press Enter to continue...{Colors.ENDC}")


def module_full_recon():
    """Run all reconnaissance modules"""
    clear_screen()
    print(f"\n{Colors.PURPLE}{'═'*68}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.PURPLE}◈◈◈ {Colors.CYAN}FULL RECONNAISSANCE SUITE {Colors.PURPLE}◈◈◈{Colors.ENDC}")
    print(f"{Colors.PURPLE}{'═'*68}{Colors.ENDC}\n")
    
    target = get_user_input("Target (IP/hostname for network scan, domain for DNS)", str)
    if not target:
        return
    
    print(f"\n{Colors.YELLOW}[INFO]{Colors.ENDC} Starting full reconnaissance on {target}...")
    print(f"{Colors.YELLOW}[INFO]{Colors.ENDC} This will run all modules sequentially")
    print(f"{Colors.CYAN}{'='*60}{Colors.ENDC}\n")
    
    full_results = {
        'target': target,
        'timestamp': datetime.now().isoformat(),
        'scans': {}
    }
    
    # 1. Port Scan
    print(f"{Colors.BLUE}[1/4]{Colors.ENDC} Running port scan...")
    from modules.port_scanner import parse_ports
    ports = parse_ports("1-1000")
    port_results = scan_target(target, ports, threads=100, timeout=1, verbose=False)
    full_results['scans']['port_scan'] = port_results
    print(f"{Colors.GREEN}[DONE]{Colors.ENDC} Found {len(port_results)} open ports\n")
    
    # 2. Service Fingerprinting
    if port_results:
        print(f"{Colors.BLUE}[2/4]{Colors.ENDC} Fingerprinting services...")
        ip = resolve_target(target)
        open_ports = [p['port'] for p in port_results]
        fp_results = fingerprint_target(ip, open_ports[:20])  # Limit to first 20
        full_results['scans']['fingerprinting'] = fp_results
        print(f"{Colors.GREEN}[DONE]{Colors.ENDC} Identified {len(fp_results)} services\n")
    
    # 3. Subdomain Enumeration
    print(f"{Colors.BLUE}[3/4]{Colors.ENDC} Enumerating subdomains...")
    try:
        subdomain_results = enumerate_subdomains(target, threads=30)
        full_results['scans']['subdomains'] = subdomain_results
        print(f"{Colors.GREEN}[DONE]{Colors.ENDC} Found {subdomain_results['total_found']} subdomains\n")
    except:
        print(f"{Colors.YELLOW}[SKIP]{Colors.ENDC} Subdomain enumeration failed\n")
    
    # 4. Web Crawl
    print(f"{Colors.BLUE}[4/4]{Colors.ENDC} Crawling web presence...")
    try:
        url = f"http://{target}"
        crawl_results = crawl_website(url, max_depth=2, max_pages=30)
        full_results['scans']['web_crawl'] = crawl_results
        print(f"{Colors.GREEN}[DONE]{Colors.ENDC} Crawled {len(crawl_results['pages'])} pages\n")
    except:
        print(f"{Colors.YELLOW}[SKIP]{Colors.ENDC} Web crawling failed\n")
    
    print(f"{Colors.CYAN}{'='*60}{Colors.ENDC}")
    print(f"{Colors.GREEN}[COMPLETE]{Colors.ENDC} Full reconnaissance finished")
    print(f"{Colors.CYAN}{'='*60}{Colors.ENDC}\n")
    
    # Auto-save full recon results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"full_recon_{target.replace('.', '_')}_{timestamp}.json"
    save_results(full_results, filename)
    
    input(f"\n{Colors.YELLOW}Press Enter to continue...{Colors.ENDC}")


def main():
    """Main program loop"""
    
    while True:
        clear_screen()
        print_banner()
        print_menu()
        
        choice = get_user_input("\nSelect option", str)
        
        if choice == '1':
            module_port_scanner()
        elif choice == '2':
            module_service_fingerprint()
        elif choice == '3':
            module_subdomain_enum()
        elif choice == '4':
            module_web_crawler()
        elif choice == '5':
            module_username_enum()
        elif choice == '6':
            module_domain_intel()
        elif choice == '7':
            module_full_recon()
        elif choice == '8':
            print(f"{Colors.YELLOW}[INFO]{Colors.ENDC} Settings module coming soon...")
            input(f"\n{Colors.YELLOW}Press Enter to continue...{Colors.ENDC}")
        elif choice == '9' or choice.lower() in ['exit', 'quit', 'q']:
            print(f"\n{Colors.PURPLE}{'═'*68}{Colors.ENDC}")
            print(f"{Colors.CYAN}[◈]{Colors.ENDC} {Colors.PURPLE}PHANTOM shutting down...{Colors.ENDC}")
            print(f"{Colors.GRAY}Remember: Stay invisible. Only test authorized systems.{Colors.ENDC}")
            print(f"{Colors.PURPLE}{'═'*68}{Colors.ENDC}\n")
            sys.exit(0)
        else:
            print(f"{Colors.RED}[!]{Colors.ENDC} Invalid option. Please try again.")
            input(f"\n{Colors.YELLOW}Press Enter to continue...{Colors.ENDC}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}[!]{Colors.ENDC} {Colors.PURPLE}PHANTOM interrupted{Colors.ENDC}")
        print(f"{Colors.GRAY}Vanishing...{Colors.ENDC}\n")
        sys.exit(0)
