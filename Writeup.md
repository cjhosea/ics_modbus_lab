# Overview

  Industrial control systems are integral pieces to our society that are taken for granted, but provide us with running water, gas for our vehicles, electricity, and more. Almost everything that we love can be attributed to, in some way, an industrial control system, but what would happen if these unsung heroes were manipulated or disrupted? In this lab, I decided to explore both the defensive and offensive sides of operational technology cybersecurity to see how an attacker could potentially disrupt a system and, at the same time, how a defender could monitor for malicious activity in an industrial network.

# Background

  The protocol that I decided to focus on is Modbus. Modbus dates back to 1979 and is still one of the most widely used fieldbus protocols in use today. Fieldbus protocols are the protocols that allow field controllers (PLCs, RTUs) to communicate with field devices (sensors, actuators). Modbus TCP was introduced in 1999 and enabled Modbus to be used over high-speed Ethernet-connected networks. The reason for Modbus's longevity and ubiquity comes from its simplicity, ease of installation, and cross-platform capabilities. Modbus works via a client-server model, where the client requests a particular action and the server fulfills that request. The server cannot send data without it being requested and these requests usually come in the form of reading or writing to a register/coil. Coils and registers are the names for memory addresses, of which there are 4 with their own (typically) designated memory address ranges:
  1) Coils (00001-09999)
  2) Discrete Input (10001-19999)
  3) Input Registers (30001-39999)
  4) Holding Registers (40001-49999)
  
  Coils are used for reading and writing boolean values, discrete inputs are for read-only boolean values, input registers are for read-only integers, and holding registers are for reading and writing integers. To put that into context, coils usually represent a state, such as a valve being open or close, while holding registers can be used to modify set points. Discrete inputs and input registers are normally used for input data from sensors.
  To make a requests, a client uses function codes, which tells the server what action to perform. These actions could be something like "15: Write Multiple Coils" or "2: Read Discrete Inputs".
  Unfortunately, the simplicity that makes Modbus so great is also what makes it insecure. Modbus has no built-in security or authentication, which can make it easy for a threat actor to carry out their dangerous plans. From the outside attacker perspective, when reading Modbus coils and registers, the values stored without context is meaningless data. But with enough time and reconnaissance, a threat actor can discover what these values mean and execute their goals.
  
  For this lab, I used a Kali Linux VM and Metasploit to carry out an attack and a Security Onion server VM to monitor these alerts. I setup my Raspberry Pi to be the Modbus server and my host PC to be Modbus client. Kali Linux is a popular Linux distribution meant for penetration testing and ethical hacking, while Security Onion is another Linux distribution designed for threat monitoring, hunting, and log management. It has incredibly useful integrations like Suricata, Zeek, and the ELK stack. Finally, Metasploit is a penetration testing framework to help in finding vulnerabilities in countless numbers of software and devices. Additionally, because the default port for Modbus TCP (502) is in the range of privileged ports (under 1024), I used port 5020 for ease of use.  

# Pymodbus

Pymodbus is a Python library that allows you to create Modbus clients and servers, and supports TCP, RTU, and ASCII Modbus communication. 

# Walkthrough

To start off, I first started my Modbus server on Python to listening for any incoming requests.

![](https://github.com/cjhosea/ics_modbus_lab/blob/main/images/server_start.png)

Next, I started my Modbus client to demonstrate what normal Modbus traffic on my network should look like.

![](https://github.com/cjhosea/ics_modbus_lab/blob/main/images/client_start.png)

I also used the command 'sudo tcpdump -i any port 5020 -w ~/Desktop/malicious_mb_traffic.pcap' to get a packet capture. This command just says to capture network traffic on any interface on port 5020 on this device and write it to a file on my Desktop. Also, without sudo, you cannot use promiscuous mode as it is locked behind root privileges (which allows you to sniff traffic on your network). Then, I used Wireshark to investigate this traffic. 

![](https://github.com/cjhosea/ics_modbus_lab/blob/main/images/normal_mb_traffic.png)

Looking at this first image of the normal traffic PCAP, we can see a response coming from the server on the Raspberry Pi at 192.168.86.205 and going to my client on my host computer at 192.168.86.80.

![](https://github.com/cjhosea/ics_modbus_lab/blob/main/images/normal_mb_traffic_2.png)

Opening up packet 24, we can examine a query a little bit more. It has a function code of 16, which is to write to multiple registers. Because Modbus is a layer 7 (application) protocol, we can use the last field on the bottom left pane to see more information, which tells us that we wrote to 4 registers (Word Count: 4), that each hold 2 bytes (Byte Count: 8), and we started at address 40001 (Reference Number: 40001).

