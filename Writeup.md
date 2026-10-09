# Overview

  Industrial control systems are integral pieces to our society that are taken for granted, but provide us with running water, gas for our vehicles, electricity, and more. Almost everything that we love can be attributed to, in some way, an industrial control system, but what would happen if these unsung heroes were manipulated or disrupted? In this lab, I decided to explore both the defensive and offensive sides of operational technology cybersecurity to see how an attacker could potentially disrupt a system and, at the same time, how a defender could monitor for malicious activity in an industrial network.

# Background

  The protocol that I decided to focus on is Modbus. Modbus dates back to 1979 and is still one of the most widely used fieldbus protocols in use today. Fieldbus protocols are the protocols that allow field controllers (PLCs, RTUs) to communicate with field devices (sensors, actuators). Modbus TCP was introduced in 1999 and enabled Modbus to be used over high-speed Ethernet-connected networks. The reason for Modbus's longevity and ubiquity comes from its simplicity, ease of installation, and cross-platform capabilities. Modbus works via a client-server model, where the client requests a particular action and the server fulfills that request. The server cannot send data without it being requested and these requests usually come in the form of reading or writing to a register/coil. Coils and registers are the names for memory addresses, of which there are 4 with their own (typically) designated memory address ranges:
  1) Coils (00001-09999)
  2) Discrete Inputs (10001-19999)
  3) Input Registers (30001-39999)
  4) Holding Registers (40001-49999)
  
  Coils are used for reading and writing boolean values, discrete inputs are for read-only boolean values, input registers are for read-only integers, and holding registers are for reading and writing integers. To put that into context, coils usually represent a state, such as a valve being open or closed, while holding registers can be used to modify set points. Discrete inputs and input registers are normally used for input data from sensors.
  To make a request, a client uses function codes, which tells the server what action to perform. These actions could be something like "15: Write Multiple Coils" or "2: Read Discrete Inputs".
  Unfortunately, the simplicity that makes Modbus so great is also what makes it insecure. Modbus has no built-in security or authentication, which can make it easy for a threat actor to carry out their dangerous plans. From the outside attacker perspective, when reading Modbus coils and registers, the values stored without context are meaningless data. But with enough time and reconnaissance, a threat actor can discover what these values mean and execute their goals.
  
  For this lab, I used a Kali Linux VM and Metasploit to carry out an attack and a Security Onion server VM to monitor these alerts. I setup my Raspberry Pi to be the Modbus server and my host PC to be Modbus client. Kali Linux is a popular Linux distribution meant for penetration testing and ethical hacking, while Security Onion is another Linux distribution designed for threat monitoring, hunting, and log management. It has incredibly useful integrations like Suricata, Zeek, and the ELK stack. Finally, Metasploit is a penetration testing framework to help in finding vulnerabilities in countless numbers of software and devices. Additionally, because the default port for Modbus TCP (502) is in the range of privileged ports (under 1024), I used port 5020 for ease of use.  

# Pymodbus

Pymodbus is a Python library that allows you to create Modbus clients and servers, and supports TCP, RTU, and ASCII Modbus communication. 

# Walkthrough

To start off, I first started my Modbus server on Python to listen for any incoming requests.

![](https://github.com/cjhosea/ics_modbus_lab/blob/main/images/server_start.png)

Next, I started my Modbus client to demonstrate what normal Modbus traffic on my network should look like.

![](https://github.com/cjhosea/ics_modbus_lab/blob/main/images/client_start.png)

I also used the command 'sudo tcpdump -i wlp10s0 port 5020 -n -w normal_mb_traffic.pcap' to get a packet capture. This command just says to capture network traffic on the wlp10s0 interface, on port 5020, on this device, don't resolve any names, and write it to a file called 'normal_mb_traffic.pcap'. Also, without sudo, you cannot use promiscuous mode as it is locked behind root privileges (which allows you to sniff traffic on your network). Then, I used Wireshark to investigate this traffic. 

![](https://github.com/cjhosea/ics_modbus_lab/blob/main/images/tcpdump_cap.png)

![](https://github.com/cjhosea/ics_modbus_lab/blob/main/images/normal_mb_traffic.png)

Looking at this first image of the normal traffic PCAP, we can see a response coming from the server on the Raspberry Pi at 192.168.86.205 and going to my client on my host computer at 192.168.86.80.

![](https://github.com/cjhosea/ics_modbus_lab/blob/main/images/normal_mb_traffic_2.png)

Opening up packet 24, we can examine a query a little bit more. It has a function code of 16, which is to write to multiple registers. Because Modbus is a layer 7 (application) protocol, we can use the last field on the bottom left pane to see more information, which tells us that we wrote to 4 registers (Word Count: 4), that each hold 2 bytes (Byte Count: 8), and we started at address 40001 (Reference Number: 40001).

After that, I installed a Security Onion VM on my host and, after lots of trials and tribulations, I got the server to work. Some of the main problems I had with Security Onion were that it wouldn't install all of its agents properly or it wouldn't properly alert me based on my Suricata rules.

![](https://github.com/cjhosea/ics_modbus_lab/blob/main/images/sonion_status.png)


Through our web browser, we can use the web interface by entering in our server's IP address (mine being 172.16.230.101). In configuration, we can set our Suricata variables. For traditional Suricata, the 'suricata.yaml' file allows us to edit our configuration. This is also where you can add 5020 to our list of Modbus ports. 

![](https://github.com/cjhosea/ics_modbus_lab/blob/main/images/sonion_suricata_config.png)
![](https://github.com/cjhosea/ics_modbus_lab/blob/main/images/suricata_yaml.png)

Normally, we can add Suricata rules by using our own local ruleset, but in Security Onion, we can add them under 'Detections'. 

![](https://github.com/cjhosea/ics_modbus_lab/blob/main/images/suricata_rules.png)
![](https://github.com/cjhosea/ics_modbus_lab/blob/main/images/suricata_detection_screen.png)
![](https://github.com/cjhosea/ics_modbus_lab/blob/main/images/suricata_add_detection.png)

If we look at the Suricata rules, we can see they follow a particular format. That being:
(what action when activated) (what protocol) (source of traffic) (source port) (direction of traffic) (destination of traffic) (destination port) followed by what options we choose. 

What the first rule is saying is "alert us if any Modbus traffic is being sent from any client that is NOT (!) one of our designated Modbus clients and being sent to our Modbus server on a Modbus port (being 5020)". Inside the parentheses, we add our options, which are "alert message is 'Malicious Modbus Write Coil Request', the data is flowing to the server, search specifically for Modbus function code 05 (Write Coil), classification is bad-unknown (Potentially Bad Traffic), and give a signature ID of 100". 

Switching to our Kali Linux attacker VM, we can start our attack. Typing 'msfconsole' into the terminal lets us start Metasploit. From there, we can search for modules pertaining to Modbus. Typing 'use 1' allows us to use the 'Modbus Banner Grabbing' module and typing 'use 2' allows us to use the 'Modbus Client Utility' module. 

![](https://github.com/cjhosea/ics_modbus_lab/blob/main/images/msfconsole_start_and_search.png)
![](https://github.com/cjhosea/ics_modbus_lab/blob/main/images/msfconsole_banner_grabbing.png)

For the Modbus Banner Grabbing module, we can set our RPORT to 5020 and our RHOSTS to 192.168.86.205 (server). After running it, we get useful data about the server, which we can potentially use to find more vulnerabilities. 

Going back to the Modbus Client Utility, we can use 'show options' and 'show actions' to see what things we can do in this module. Setting our DATA_ADDRESS to 3 lets us use the coil address of 3. If we set our DATA to 1, we can assume we are setting whatever is at data address 3 to True. Setting our RPORT to 5020 and our RHOSTS to 192.168.86.205 again lets us attack the server. Then, we can set our action to WRITE_COIL and then execute our command using 'run'. As we can see in the output, we successfully overwrote the DATA at 3 to be True (1). We can then set our action to be 'READ_COILS' and we can read what we just inputted to the address. 

![](https://github.com/cjhosea/ics_modbus_lab/blob/main/images/msfconsole_banner_grabbing.png)
![](https://github.com/cjhosea/ics_modbus_lab/blob/main/images/msf_console_run_first_write_coil.png)
![](https://github.com/cjhosea/ics_modbus_lab/blob/main/images/msfconsole_read_coils.png)

We can repeat this for the holding registers and read and write to multiple registers at the same time.

![](https://github.com/cjhosea/ics_modbus_lab/blob/main/images/msfconsole_write_registers.png)
![](https://github.com/cjhosea/ics_modbus_lab/blob/main/images/msfconsole_read_multiple_registers.png)

Going back to Security Onion, we can see that Suricata fired off some alerts based on these malicious activities and view the details for these alerts.

![](https://github.com/cjhosea/ics_modbus_lab/blob/main/images/sonion_all_alerts.png)
![](https://github.com/cjhosea/ics_modbus_lab/blob/main/images/sonion_alert_details.png)

We can additionally capture the traffic from the attacker as a PCAP and import it into Security Onion, where it produces Zeek logs. In the 'Hunt' section, we can examine the details from the Zeek conn.log file and see that 192.168.86.215 (Kali Linux) is a "VMWare, Inc" host (VM). 

![](https://github.com/cjhosea/ics_modbus_lab/blob/main/images/sonion_all_alerts.png)
![](https://github.com/cjhosea/ics_modbus_lab/blob/main/images/sonion_pcap_link.png)
![](https://github.com/cjhosea/ics_modbus_lab/blob/main/images/sonion_zeek_hunt.png)

Now, moving over to the ELK Stack offered by Security Onion, which we can use as our SIEM solution. ELK Stack is a solution comprising of multiple projects that, when combined, can make up a SIEM similar to Splunk. It uses Elasticsearch as its search engine and storage unit. Logstash is to collect and parse logs. Kibana is its visualization tool for Elasticsearch. Furthermore, Beats, which are the agents that collect and forward data, are used to send data typically to Logstash. Using ELK Stack, we can search for our attacker's IP address, the rules they triggered, and visualize their attacks and attack timeline.


![](https://github.com/cjhosea/ics_modbus_lab/blob/main/images/elk_search_attacker_ip.png)
![](https://github.com/cjhosea/ics_modbus_lab/blob/main/images/elk_%20search_write_multiple_registers.png)

Lastly, Security Onion contains a MITRE ATT&CK navigator that enables us to see the TTPs correlated with alerts that Suricata detected. This can be a very powerful tool to bolster your defenses alongside other frameworks like MITRE D3FEND.

![](https://github.com/cjhosea/ics_modbus_lab/blob/main/images/sonion_suricata_attck.png)

# Discussion

Although the exact attack vectors or methodologies used in this lab may not be 100% accurate, the tools very much are and I enjoyed learning more about them. Security Onion, in particular, is a grand security solution with a lot more features than I expected. Additionally, the Auxiliary modules in Metasploit usually aren't for exploiting a target, but it was still a great exercise for seeing how both the Modbus protocol and Metasploit can work. Moreover, the Suricata variables I used are able to be spoofed and would not work well against an attacker pivoting through a network. Even so, it was good practice to set up these rules and see how they would work in an environment using Modbus. 

Furthermore, mapping this attack to MITRE ATT&CK for ICS, we can identify three techniques:
- Unauthorized Message: Command Message
- Modify Parameter 
- Manipulation of Control

'Unauthorized Message: Command Message' and 'Modify Parameter' both fall under the 'Impair Process Control' tactic, while 'Manipulation of Control' falls under the 'Impact' tactic. On any of these techniques' pages, you can view recommended the mitigations and detection strategies. For example, for 'Modify Parameter', it is recommended that "all field controllers should restrict the modification of parameter values to only certain users," which is M0800: 'Authorization Enforcement'. But another thing we can also do is use MITRE D3FEND framework (https://d3fend.mitre.org/domain/ot/), in which we can see a different countermeasure being D3-OVAR. D3-OVAR is 'OT Variable Access Restriction', where we "assign read/write access controls on designated registers or data tags to prevent unauthorized writes." The related offensive techniques also map to certain D3FEND countermeasures, in which you can see below. 

![](https://github.com/cjhosea/ics_modbus_lab/blob/main/images/mitre_d3fend_ovar.png)

Better yet, we look up specific devices on MITRE D3FEND to see their descriptions, relationships with other devices, recommended countermeasures, and associated ATT&CK TTPs.

![](https://github.com/cjhosea/ics_modbus_lab/blob/main/images/d3fend_control_server.png)
![](https://github.com/cjhosea/ics_modbus_lab/blob/main/images/d3fend_control_server_2.png)

Treating my Raspberry Pi like the control server or PLC, we can use these recommended countermeasures jointly with ATT&CK mitigations and the Purdue Model to create a robust defense-in-depth approach for not only this asset, but all assets and our network. 

Furthermore, the reason I opted to use Suricata as an IDS instead of an IPS is because of the critical nature of industrial control systems. In an industrial control system, every second matters and availability and safety is of utmost importance. Latency is a problem that we should keep to a minimum, but it can be accounted for and adjusted. On the other hand, in-line monitoring not only comes with latency, but also jitter, which can cause massive issues. 

While traditional IT networks and systems can have latency and jitter and be unpredictable, industrial control systems should be deterministic and very predictable. Industrial networks use assets that have a lot longer lifespans than IT and can last for 10-20 years. This means there isn't as much plug and play as IT, so we need to secure the systems we have right now in the best way we can. Industrial cybersecurity has to make sure that the backbones of our country's infrastructure not only run as intended, but that these systems are also durable to cyber attacks. On top of that, compensating controls are incredibly important for industrial cybersecurity because downtime can be huge costs to safety and the business. We cannot just take systems down all the time to patch them. Making these systems resilient can be the difference of having running water for a shower in the morning and not being able to start your hygienic routine or having clean water to drink.  


