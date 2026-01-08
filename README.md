# PHANTOM

### Random shi I made

Just a multi-tools for pentesting.

## Legal Notice

**This tool is for educational and authorized testing purposes only.**

Only use on:

- Your own systems
- Systems with explicit written authorization
- Authorized penetration testing engagements
- Educational lab environments (HTB, THM, etc.)

Unauthorized use is illegal and may result in criminal prosecution.

## Features

### Unified Multi-Tool Interface

Professional menu-driven interface combining all modules in one tool.

### Seven Core Modules

**1. Port Scanner**

- Multi-threaded TCP scanning
- Banner grabbing
- Service identification
- Customizable port ranges

**2. Service Fingerprinting**

- Service version detection
- Banner analysis
- HTTP probing
- Common service signatures

**3. Subdomain Enumeration**

- DNS brute force with built-in wordlist
- Zone transfer testing
- Certificate Transparency logs
- Concurrent DNS lookups

**4. Web Crawler**

- HTTP spider with depth control
- Form discovery
- Email extraction
- Robots.txt parsing
- Sitemap detection

**5. Username Enumeration (OSINT)**

- Check username across 50+ platforms
- Social media presence mapping
- Developer platform checks
- Automated profile discovery

**6. Domain Intelligence (OSINT)**

- WHOIS lookup and registration data
- DNS record enumeration
- IP geolocation
- Web technology detection

**7. DDoS Attack Simulator**

- HTTP Flood attack simulation
- Slowloris connection exhaustion
- Combined multi-method attacks
- Real-time performance monitoring
- **AUTHORIZED INFRASTRUCTURE TESTING ONLY**

## Installation

### Kali Linux (or Ubuntu based)

```bash
# Navigate to project directory
cd phantom

# Run setup script
chmod +x setup.sh
./setup.sh
```

### Manual Installation

```bash
# Install dependencies
pip3 install -r requirements.txt
```

## Output

Results can be saved in JSON format for further analysis:

```json
{
  "target": "example.com",
  "timestamp": "2025-11-23T22:30:00",
  "scans": {
    "port_scan": [...],
    "fingerprinting": [...],
    "subdomains": {...},
    "web_crawl": {...}
  }
}
```

## Requirements

- Python 3.7+
- Linux environment (ParrotOS, Kali, Ubuntu etc)
- Network connectivity
- Proper authorization for target systems

## Security Considerations

**Attack Surface Awareness**

- Every open port is a potential entry point
- Service versions may have known vulnerabilities
- Subdomain discovery reveals hidden infrastructure
- Web forms are common attack vectors

**Defensive Use**

- Audit your own infrastructure
- Identify unnecessary exposed services
- Monitor for reconnaissance attempts
- Keep services updated

## Troubleshooting

**DNS errors in subdomain enumeration**

```bash
# Install/update dnspython
pip3 install --upgrade dnspython
```

**Permission errors**

```bash
# Make sure scripts are executable
chmod +x *.py
```

**Import errors**

```bash
# Ensure all dependencies are installed
pip3 install -r requirements.txt
```

## Contributing

This is an educational project. Feel free to:

- Add new modules
- Improve existing features
- Enhance documentation
- Report bugs

## License

Educational and authorized testing purposes only.

## Author

**Katyusha47**  

---
