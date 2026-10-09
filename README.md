# modbus-detection-lab

<p>This lab demonstrates creating a Modbus server with Python, using Kali Linux and Metasploit to attack an industrial control system, and Security Onion as a security solution to monitor and threat hunt. Industrial control systems are the critical, seldom thought of components to our everyday lives that keep our necessities running, and since availability is a top priority, any type of disruption could cause catastrophic effects to our society. </p>

## Repository Layout
```text
modbus-detection-lab/
├── images/            # screenshots
├── pcaps/             # packet captures
├── src/
│   ├── client.py     # Modbus client 
│   └── server.py     # Modbus server
├── Writeup.md        # write‑up
├── README.md          # this file
```
## MITRE ATT&CK for ICS Mapping
| Attack Technique         | ID    |
| ------------------------ | ----- |
| Unauthorized Message: Command Message  | T1692.001  |
| Manipulation of Control                | T0831      |
| Modify Parameter                       | T0836      |

## MITRE D3FEND for ICS Mapping
| Countermeasures         | ID    |
| ------------------------ | ----- |
| OT Variable Access Restriction  | D3-OVAR  |

## Purdue Model
![](https://github.com/cjhosea/ics_modbus_lab/blob/main/images/mb_lab_pm.png)

As per IEC/ISA 62443, one of the recommended ways to protect an industrial control system environment is to use zones and conduits. Zones are groupings of assets with similar cybersecurity requirements, while conduits are secure communication channels between zones. Zones and conduits can be combined with the Purdue Model, which is a reference model to help properly segment industrial control environments.

- Level 4/5 (Corporate) represents the IT and business side of an organization with assets like web and DNS servers.
- Level 3.5 (iDMZ) represents the secure buffer between the IT and OT networks with assets like historian mirrors (for IT to access) and jump servers. The industrial DMZ is recommended to have two firewalls from two different vendors to reduce the risk of vulnerabilities from one specific vendor. 
- Level 3 (Site Operations) represents the assets for site-wide management, such as patch managers and historians.
- Level 2 (Supervisory Control) represents assets for local control of controllers, such as HMIs and SCADA servers.
- Level 1 (IACS Control) represents controllers to control field devices like PLCs and RTUs.
- Level 0 (Process Instrumentation) represents field devices, which are sensors and actuators.

Because most cyber attacks originate from the OT network and IT depends on OT for business metrics and data, it is recommended that all data flows up from OT and terminates in the DMZ. From the DMZ, IT can get the data they need to keep the business running. Additionally, it is advised to have a unidirectional gateway or data diode for one-way communication between the historian in Level 3 and the historian mirror in Level 3.5. Historians are prime targets for attacks and used frequently for pivoting. Between Levels 2 and 4/5, there are numerous Windows-based systems that have their own vulnerabilities. Historians are usually one of these Windows-based systems and many use SQL, as well, which introduces even more vulnerabilities. If we have OT sending data to IT, but IT can't send data to OT, we reduce the risk of infiltration by a lot. 

For good measure, in my Purdue Model, I put engineering workstations in Level 3 and the Site Operations Zone because of the fact that engineering workstations can directly retrieve and modify a PLC's programming. It would be better if we could have a security measure (i.e. firewall) between these two assets to help mitigate this risk. 

## Network Diagram
![](https://github.com/cjhosea/ics_modbus_lab/blob/main/images/mb_lab_nd.png)

My main computer is my Linux PC at 192.168.86.80. On the host, it runs the 'client.py' script. It has VMWare Workstation installed to have two VMs running, them being Security Onion (with a management interface at 172.16.230.101 and a monitoring interface at 192.168.86.214) and Kali Linux (192.168.86.215). My host PC was plugged in via Ethernet to a router, so that Security Onion could use a NAT interface for management and a bridged interface for monitoring. Security Onion can see the traffic between my host and the Raspberry Pi on its bridged interface through my access point. Lastly, my Raspberry Pi runs the 'server.py' script at 192.168.86.205. 
