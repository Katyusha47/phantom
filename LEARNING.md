# Port Scanner - Learning Guide 🎓

## What You'll Learn

This port scanner teaches you fundamental cybersecurity and networking concepts:

### 1. **How TCP/IP Works**

When you connect to a website, your computer establishes a **TCP connection** with the server. Port scanning works by attempting these connections on different ports to see which ones are listening.

**Key Concept**:

- **Port** = A number (1-65535) that identifies a specific service on a computer
- **Open Port** = Service is listening and accepting connections
- **Closed Port** = Nothing is listening on that port
- **Filtered Port** = Firewall is blocking our connection attempt

### 2. **Socket Programming**

```python
# This is how we create a TCP connection in Python:
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((target_ip, port_number))
```

- `AF_INET` = IPv4 address family
- `SOCK_STREAM` = TCP protocol (vs SOCK_DGRAM for UDP)
- `connect()` = Attempt to establish connection

### 3. **Threading for Performance**

Scanning 1000 ports sequentially would take FOREVER (1000 seconds with 1 sec timeout!).

**Solution**: Multi-threading!

- Scan multiple ports simultaneously
- Our tool uses `ThreadPoolExecutor` with 50 threads by default
- This makes it ~50x faster!

### 4. **Banner Grabbing**

When we connect to a service, many will send us information about themselves:

```
SSH-2.0-OpenSSH_8.2p1 Ubuntu-4ubuntu0.5
220 ProFTPD 1.3.6 Server ready
HTTP/1.1 200 OK\r\nServer: nginx/1.18.0
```

This is called a **banner** and it tells us:

- What service is running (SSH, FTP, HTTP)
- Version numbers (useful for finding known vulnerabilities)
- Operating system hints

## Code Walkthrough

### The Scanning Process

1. **Resolve Target** (`resolve_target()`)

   ```python
   ip = socket.gethostbyname("example.com")  # Convert domain to IP
   ```

2. **Create Socket** (`scan_port()`)

   ```python
   sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
   sock.settimeout(1)  # Don't wait forever
   ```

3. **Attempt Connection**

   ```python
   result = sock.connect_ex((ip, port))
   if result == 0:  # Success! Port is open
       print(f"Port {port} is OPEN")
   ```

4. **Grab Banner** (`grab_banner()`)
   ```python
   banner = sock.recv(1024)  # Read what the service sends us
   ```

### Threading Magic

Instead of:

```python
for port in ports:
    scan_port(port)  # Slow! Takes forever
```

We do:

```python
with ThreadPoolExecutor(max_workers=50) as executor:
    futures = [executor.submit(scan_port, port) for port in ports]
    # All 50 threads scan different ports at the same time!
```

## Practical Examples

### Example 1: Scan Your Local Machine

```bash
# Scan yourself! This is always legal :)
python port_scanner.py -t 127.0.0.1 -v
```

What you might see:

- Port 22: SSH (if you have SSH server running)
- Port 80/443: Web server (if running Apache/nginx)
- Port 3306: MySQL database

### Example 2: Scan a Specific Service

```bash
# Check if a web server is running on common ports
python port_scanner.py -t example.com -p 80,443,8080,8443
```

### Example 3: Fast Network Discovery

```bash
# Scan just the most common 20 ports on your router
python port_scanner.py -t 192.168.1.1 -p 21,22,23,25,53,80,110,143,443,445,3389 -T 100
```

### Example 4: Save Results

```bash
# Scan and save to file for later analysis
python port_scanner.py -t target.com -o scan_results.json
```

## Common Ports Reference

| Port  | Service    | What It Does                          |
| ----- | ---------- | ------------------------------------- |
| 20/21 | FTP        | File Transfer Protocol                |
| 22    | SSH        | Secure Shell (remote access)          |
| 23    | Telnet     | Unencrypted remote access (insecure!) |
| 25    | SMTP       | Email sending                         |
| 53    | DNS        | Domain name resolution                |
| 80    | HTTP       | Web traffic (unencrypted)             |
| 443   | HTTPS      | Web traffic (encrypted with TLS)      |
| 445   | SMB        | Windows file sharing                  |
| 3306  | MySQL      | MySQL database                        |
| 3389  | RDP        | Remote Desktop Protocol (Windows)     |
| 5432  | PostgreSQL | PostgreSQL database                   |
| 6379  | Redis      | Redis in-memory database              |
| 8080  | HTTP-Alt   | Alternative HTTP port (proxies, dev)  |
| 27017 | MongoDB    | MongoDB database                      |

## Security Implications

### Why Port Scanning Matters:

1. **Attack Surface**: Every open port is a potential entry point
2. **Service Discovery**: Knowing what's running helps find vulnerabilities
3. **Defense**: You need to know what YOU have exposed to secure it

### Defensive Perspective:

- **Firewall Rules**: Block unnecessary ports
- **Service Minimization**: Only run services you need
- **Version Updates**: Keep services patched (banners expose versions!)
- **Intrusion Detection**: Monitor for port scans against your network

## Experiments to Try

### 🔬 Experiment 1: Speed Testing

```bash
# Try different thread counts and see the difference
time python port_scanner.py -t 192.168.1.1 -p 1-1000 -T 10
time python port_scanner.py -t 192.168.1.1 -p 1-1000 -T 50
time python port_scanner.py -t 192.168.1.1 -p 1-1000 -T 200
```

Watch how more threads = faster scans (to a point!)

### 🔬 Experiment 2: Banner Analysis

```bash
# Scan yourself and look at the banners
python port_scanner.py -t 127.0.0.1 -v

# Research any version numbers you find:
# "Is OpenSSH 7.4 vulnerable?" (Google this!)
```

### 🔬 Experiment 3: Network Mapping

```bash
# Scan your whole home network (usually 192.168.1.0/24)
for i in {1..254}; do
    python port_scanner.py -t 192.168.1.$i -p 22,80,443 >> network_map.txt
done
```

This finds all devices on your network!

## Next Steps

Once you understand this port scanner, you're ready for:

1. **Service Fingerprinting** - Identify exact versions of services
2. **Vulnerability Scanning** - Check for known CVEs
3. **Network Mapping** - Scan entire subnets
4. **Stealth Techniques** - SYN scans, fragmentation, timing tricks

## Questions to Think About

1. Why do we use TCP for port scanning? Could we use UDP?
2. How could a firewall detect our port scan?
3. How would you make this scanner "stealthier"?
4. What's the difference between a closed port and a filtered port?
5. Why might banner grabbing fail even on open ports?

## Legal Reminder

🚨 **CRITICAL**: Only scan:

- Your own systems
- Systems you have written permission to test
- Lab environments (like TryHackMe, HackTheBox)

Unauthorized scanning can:

- Violate computer fraud laws
- Get your IP banned
- Trigger legal action

**Always get permission first!**

---

Ready to level up? Let's build the service fingerprinting module next! 🚀
