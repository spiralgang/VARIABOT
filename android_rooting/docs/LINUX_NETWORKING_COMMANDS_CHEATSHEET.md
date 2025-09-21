# Linux Networking Commands Cheatsheet

## Overview

This comprehensive cheatsheet covers essential Linux networking commands for Android rooting, privilege escalation, and network penetration testing. Specifically tailored for Kali Linux, Termux, and Android environments.

## Table of Contents

1. [Network Interface Management](#network-interface-management)
2. [IP Address and Routing](#ip-address-and-routing)
3. [Network Scanning and Discovery](#network-scanning-and-discovery)
4. [DNS Operations](#dns-operations)
5. [Network Monitoring](#network-monitoring)
6. [Firewall and Security](#firewall-and-security)
7. [Wireless Networking](#wireless-networking)
8. [Privilege Escalation via Network](#privilege-escalation-via-network)
9. [Android-Specific Networking](#android-specific-networking)
10. [Troubleshooting Commands](#troubleshooting-commands)

## Network Interface Management

### Basic Interface Commands

```bash
# List all network interfaces
ip link show
ifconfig -a
ls /sys/class/net/

# Show active interfaces only
ip link show up
ifconfig | grep -E "^[a-z]"

# Bring interface up/down
ip link set eth0 up
ip link set eth0 down
ifconfig eth0 up
ifconfig eth0 down

# Show interface statistics
ip -s link show eth0
cat /proc/net/dev
```

### Interface Configuration

```bash
# Set IP address
ip addr add 192.168.1.100/24 dev eth0
ifconfig eth0 192.168.1.100 netmask 255.255.255.0

# Remove IP address
ip addr del 192.168.1.100/24 dev eth0

# Set MAC address
ip link set dev eth0 address 00:11:22:33:44:55
ifconfig eth0 hw ether 00:11:22:33:44:55

# Set MTU
ip link set dev eth0 mtu 1500
ifconfig eth0 mtu 1500
```

### Virtual Interfaces

```bash
# Create virtual interface
ip link add link eth0 name eth0.100 type vlan id 100

# Create bridge
ip link add name br0 type bridge
ip link set dev br0 up

# Create tunnel
ip tunnel add gre1 mode gre remote 10.0.0.1 local 10.0.0.2
ip link set gre1 up
```

## IP Address and Routing

### IP Address Management

```bash
# Show IP addresses
ip addr show
ip a
hostname -I

# Show specific interface
ip addr show eth0
ifconfig eth0

# Add multiple IPs to same interface
ip addr add 192.168.1.100/24 dev eth0
ip addr add 192.168.1.101/24 dev eth0

# Show IP addresses in CIDR format
ip -4 addr show | grep -oP '(?<=inet\s)\d+(\.\d+){3}/\d+'
```

### Routing Commands

```bash
# Show routing table
ip route show
route -n
netstat -rn

# Add default gateway
ip route add default via 192.168.1.1
route add default gw 192.168.1.1

# Add specific route
ip route add 10.0.0.0/8 via 192.168.1.254
route add -net 10.0.0.0/8 gw 192.168.1.254

# Delete route
ip route del 10.0.0.0/8
route del -net 10.0.0.0/8

# Show route to specific destination
ip route get 8.8.8.8
traceroute 8.8.8.8
```

### Advanced Routing

```bash
# Policy-based routing
ip rule add from 192.168.1.100 table 100
ip route add default via 192.168.1.1 table 100

# Multiple routing tables
echo "100 custom" >> /etc/iproute2/rt_tables
ip route show table custom

# Load balancing
ip route add default scope global \
    nexthop via 192.168.1.1 weight 1 \
    nexthop via 192.168.1.2 weight 1
```

## Network Scanning and Discovery

### Port Scanning

```bash
# Nmap basic scans
nmap -sn 192.168.1.0/24          # Ping scan
nmap -sS 192.168.1.1             # SYN scan
nmap -sT 192.168.1.1             # TCP connect scan
nmap -sU 192.168.1.1             # UDP scan
nmap -sA 192.168.1.1             # ACK scan

# Comprehensive scan
nmap -A -T4 192.168.1.1          # Aggressive scan
nmap -sC -sV 192.168.1.1         # Script and version detection

# Specific port ranges
nmap -p 1-1000 192.168.1.1       # Port range
nmap -p 80,443,22 192.168.1.1    # Specific ports
nmap -p- 192.168.1.1             # All ports

# Fast scan techniques
nmap -T5 --min-rate 1000 192.168.1.1
nmap --top-ports 1000 192.168.1.1
```

### Network Discovery

```bash
# ARP scanning
arp-scan -l
arp-scan 192.168.1.0/24
nmap -PR 192.168.1.0/24

# Netdiscover
netdiscover -r 192.168.1.0/24
netdiscover -p

# Masscan (fast port scanner)
masscan -p1-65535 192.168.1.0/24 --rate=1000

# Zmap (Internet-wide scanning)
zmap -p 80 -o results.txt
```

### Service Detection

```bash
# Banner grabbing
nc -nv 192.168.1.1 80
telnet 192.168.1.1 22
curl -I http://192.168.1.1

# Nmap service detection
nmap -sV -p 1-1000 192.168.1.1
nmap --script banner 192.168.1.1

# Amap (application mapper)
amap -A 192.168.1.1 80
amap -bqv 192.168.1.1 1-1000
```

## DNS Operations

### DNS Lookup Commands

```bash
# Basic DNS lookup
nslookup google.com
host google.com
dig google.com

# Specific record types
dig google.com MX
dig google.com NS
dig google.com TXT
dig google.com AAAA

# Reverse DNS lookup
dig -x 8.8.8.8
host 8.8.8.8
nslookup 8.8.8.8

# DNS server specification
dig @8.8.8.8 google.com
nslookup google.com 1.1.1.1
```

### DNS Enumeration

```bash
# Zone transfer
dig @ns1.example.com example.com AXFR
host -l example.com ns1.example.com

# Subdomain enumeration
dnsrecon -d example.com -t std
dnsmap example.com
sublist3r -d example.com

# DNS bruteforcing
gobuster dns -d example.com -w wordlist.txt
dnsenum example.com
fierce -dns example.com
```

### DNS Configuration

```bash
# View DNS configuration
cat /etc/resolv.conf
systemd-resolve --status

# Change DNS servers
echo "nameserver 8.8.8.8" > /etc/resolv.conf
echo "nameserver 1.1.1.1" >> /etc/resolv.conf

# Flush DNS cache
systemd-resolve --flush-caches
sudo /etc/init.d/nscd restart

# DNS over HTTPS/TLS
dig @1.1.1.1 google.com +https
```

## Network Monitoring

### Traffic Monitoring

```bash
# Real-time traffic monitoring
iftop
iftop -i eth0
iftop -n -P -B

# Bandwidth usage
vnstat
vnstat -i eth0
vnstat -l -i eth0

# Network statistics
ss -tuln
netstat -tuln
ss -s

# Active connections
ss -ant
netstat -ant
lsof -i
```

### Packet Capture

```bash
# Tcpdump basic usage
tcpdump -i eth0
tcpdump -i any
tcpdump -i eth0 -w capture.pcap

# Specific protocols
tcpdump -i eth0 tcp
tcpdump -i eth0 udp port 53
tcpdump -i eth0 icmp

# Advanced filters
tcpdump -i eth0 host 192.168.1.1
tcpdump -i eth0 net 192.168.1.0/24
tcpdump -i eth0 port 80 or port 443

# Wireshark (GUI)
wireshark &
tshark -i eth0 -w capture.pcap
```

### Network Analysis

```bash
# Protocol analysis
tshark -r capture.pcap -q -z conv,ip
tshark -r capture.pcap -q -z io,stat,1

# Extract files from pcap
tcpick -r capture.pcap -wR

# Network baselining
ntopng
cacti
nagios
```

## Firewall and Security

### Iptables Commands

```bash
# List rules
iptables -L
iptables -L -n -v
iptables -t nat -L

# Basic rules
iptables -A INPUT -p tcp --dport 22 -j ACCEPT
iptables -A INPUT -j DROP
iptables -D INPUT 1

# NAT rules
iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE
iptables -t nat -A PREROUTING -p tcp --dport 80 -j REDIRECT --to-port 8080

# Save/restore rules
iptables-save > iptables.rules
iptables-restore < iptables.rules
```

### UFW (Uncomplicated Firewall)

```bash
# Enable/disable UFW
ufw enable
ufw disable
ufw status

# Basic rules
ufw allow 22
ufw allow ssh
ufw deny 80
ufw allow from 192.168.1.0/24

# Advanced rules
ufw allow from 192.168.1.100 to any port 22
ufw allow out 53
```

### Network Security Tools

```bash
# Port security
fail2ban-client status
fail2ban-client status ssh

# Intrusion detection
aide --check
rkhunter --check
chkrootkit

# Network intrusion detection
snort -A console -q -c /etc/snort/snort.conf -i eth0
suricata -c /etc/suricata/suricata.yaml -i eth0
```

## Wireless Networking

### WiFi Interface Management

```bash
# List wireless interfaces
iwconfig
iw dev

# Scan for networks
iwlist scan
iw scan

# Connect to network
iwconfig wlan0 essid "NetworkName"
iwconfig wlan0 key s:password

# Using wpa_supplicant
wpa_supplicant -B -i wlan0 -c wpa_supplicant.conf
dhclient wlan0
```

### WiFi Security Testing

```bash
# Monitor mode
airmon-ng start wlan0
iwconfig wlan0 mode monitor

# Capture handshakes
airodump-ng wlan0mon
airodump-ng -c 6 --bssid AA:BB:CC:DD:EE:FF -w capture wlan0mon

# Deauthentication attack
aireplay-ng -0 5 -a AA:BB:CC:DD:EE:FF wlan0mon

# Crack WPA/WPA2
aircrack-ng -w wordlist.txt capture-01.cap
hashcat -m 2500 capture.hccapx wordlist.txt
```

### Bluetooth

```bash
# Bluetooth scanning
hcitool scan
bluetoothctl scan on

# Device information
hciconfig -a
bluetoothctl info XX:XX:XX:XX:XX:XX

# Bluetooth attacks
btscanner
bluelog
redfang
```

## Privilege Escalation via Network

### Network-based Privilege Escalation

```bash
# Check for SUID network binaries
find / -perm -u=s -type f 2>/dev/null | grep -E "(nc|ncat|socat|ssh)"

# Abuse SUID binaries
# If /usr/bin/ncat has SUID bit
ncat -l -p 1234 -e /bin/sh

# SSH key abuse
cat ~/.ssh/id_rsa
ssh-keygen -y -f ~/.ssh/id_rsa

# Network service exploitation
# Check for vulnerable services
netstat -tulpn | grep LISTEN
ss -tulpn | grep LISTEN
```

### Lateral Movement

```bash
# SSH tunneling
ssh -L 8080:localhost:80 user@remote
ssh -R 8080:localhost:22 user@remote
ssh -D 8080 user@remote

# ProxyChains
proxychains nmap -sT 10.0.0.1
proxychains firefox

# Pivoting with Metasploit
# meterpreter> run autoroute -s 10.0.0.0/24
# meterpreter> portfwd add -l 8080 -p 80 -r 10.0.0.1
```

### Credential Harvesting

```bash
# Network credential sniffing
ettercap -T -M arp:remote /192.168.1.1// /192.168.1.100//
dsniff -i eth0

# MITM attacks
mitmdump -s script.py
bettercap -iface eth0

# WiFi credential capture
hostapd-wpe hostapd-wpe.conf
freeradius-wpe
```

## Android-Specific Networking

### Android Network Commands

```bash
# Android property commands
getprop | grep net
setprop net.dns1 8.8.8.8
setprop net.dns2 8.8.4.4

# Interface management
netcfg
ip route show table all

# Android-specific tools
netstat -i
cat /proc/net/dev
cat /proc/net/route

# WiFi management
wpa_cli scan
wpa_cli scan_results
wpa_cli list_networks
```

### Termux Networking

```bash
# Install network tools in Termux
pkg install nmap
pkg install netcat-openbsd
pkg install openssh
pkg install curl wget

# Termux-specific networking
termux-wifi-connectioninfo
termux-wifi-scaninfo
termux-telephony-cellinfo

# Port forwarding in Termux
ssh -L 8080:localhost:80 user@server
```

### Android Network Security

```bash
# Check for open ports
netstat -tulpn
ss -tulpn

# Monitor network connections
netstat -ant | grep ESTABLISHED
ss -o state established

# Network traffic analysis
tcpdump -i any -w /sdcard/capture.pcap
```

## Troubleshooting Commands

### Connectivity Testing

```bash
# Basic connectivity
ping google.com
ping -c 4 8.8.8.8
ping6 google.com

# Advanced ping
ping -f google.com           # Flood ping
ping -s 1472 google.com      # Large packet size
ping -R google.com           # Record route

# Traceroute
traceroute google.com
tracepath google.com
mtr google.com               # My traceroute
```

### DNS Troubleshooting

```bash
# DNS resolution test
nslookup google.com
dig google.com +trace
host google.com

# Check DNS server response time
dig @8.8.8.8 google.com | grep "Query time"
dig @1.1.1.1 google.com | grep "Query time"

# DNS cache issues
systemd-resolve --flush-caches
sudo service nscd restart
```

### Network Interface Issues

```bash
# Check interface status
ip link show
ethtool eth0
mii-tool eth0

# Check for packet loss
ip -s link show eth0
cat /proc/net/dev

# Reset network interface
ip link set eth0 down
ip link set eth0 up
systemctl restart networking
```

### Performance Testing

```bash
# Bandwidth testing
iperf3 -s                    # Server mode
iperf3 -c server_ip          # Client mode
speedtest-cli

# Network latency
ping -c 100 google.com | tail -1
hping3 -S -p 80 google.com

# Throughput testing
nc -l -p 12345 > /dev/null   # Server
nc target_ip 12345 < /dev/zero  # Client
```

### Log Analysis

```bash
# System network logs
journalctl -u networking
tail -f /var/log/syslog | grep network
dmesg | grep -i network

# Connection tracking
cat /proc/net/nf_conntrack
conntrack -L

# Network statistics
cat /proc/net/netstat
cat /proc/net/snmp
ss -s
```

## Advanced Network Commands

### Network Namespaces

```bash
# Create network namespace
ip netns add test
ip netns exec test ip link show

# Move interface to namespace
ip link set eth0 netns test

# Execute commands in namespace
ip netns exec test ping google.com
```

### Traffic Control

```bash
# Bandwidth limiting
tc qdisc add dev eth0 root handle 1: htb default 30
tc class add dev eth0 parent 1: classid 1:1 htb rate 100mbit

# Packet delay
tc qdisc add dev eth0 root netem delay 100ms

# Packet loss simulation
tc qdisc add dev eth0 root netem loss 1%
```

### Network Bonding

```bash
# Create bond interface
modprobe bonding
echo +bond0 > /sys/class/net/bonding_masters

# Configure bonding
echo 0 > /sys/class/net/bond0/bonding/mode
echo 100 > /sys/class/net/bond0/bonding/miimon

# Add slaves
echo +eth0 > /sys/class/net/bond0/bonding/slaves
echo +eth1 > /sys/class/net/bond0/bonding/slaves
```

## Security Best Practices

### Network Hardening

```bash
# Disable unnecessary services
systemctl disable telnet
systemctl disable rsh
systemctl disable rlogin

# Secure SSH configuration
# Edit /etc/ssh/sshd_config
# PermitRootLogin no
# PasswordAuthentication no
# AllowUsers specific_user

# Network parameter tuning
echo 1 > /proc/sys/net/ipv4/tcp_syncookies
echo 0 > /proc/sys/net/ipv4/ip_forward
echo 1 > /proc/sys/net/ipv4/icmp_echo_ignore_broadcasts
```

### Monitoring and Alerting

```bash
# Real-time monitoring
watch -n 1 'netstat -i'
watch -n 1 'ss -s'

# Automated monitoring scripts
#!/bin/bash
while true; do
    netstat -i | grep -v lo | awk 'NR>2 {print $1, $3, $7}'
    sleep 5
done
```

## References and Resources

### Official Documentation
- [Linux Networking Documentation](https://www.kernel.org/doc/Documentation/networking/)
- [iproute2 Manual](https://man7.org/linux/man-pages/man8/ip.8.html)
- [Android Networking](https://source.android.com/devices/tech/connect/)

### Security Resources
- [OWASP Mobile Security](https://owasp.org/www-project-mobile-security-testing-guide/)
- [Kali Linux Network Tools](https://www.kali.org/tools/)
- [Penetration Testing Framework](http://www.vulnerabilityassessment.co.uk/Penetration%20Test.html)

### Learning Resources
- [Linux Network Administration](https://www.tldp.org/LDP/nag2/index.html)
- [TCP/IP Illustrated](https://www.pearson.com/store/p/tcp-ip-illustrated-volume-1-the-protocols/P100000148515)
- [Network Security Tools](https://nmap.org/book/)

---

**Note**: This cheatsheet provides commands for educational and authorized testing purposes only. Always ensure you have proper authorization before performing network scanning, penetration testing, or security assessments. Use these commands responsibly and in compliance with applicable laws and organizational policies.

**Last Updated**: $(date -Iseconds)
**Compatibility**: Linux, Kali Linux, Android/Termux, Network Security Testing