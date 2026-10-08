# ics_modbus_lab

<p>This lab demonstrates creating a Modbus server with Python, using Kali Linux and Metasploit to attack an industrial control system, and Security Onion as a security solution to monitor and threat hunt. Industrial control systems are the critical, seldomly thought of components to our everyday lives that keep our necessities running, and since availability is a top priority, any type of disruption could cause catastrophic effects to our society. </p>

## Repository Layout
```text
ics-modbus-lab/
├── images/            # screenshots
├── pcaps/             # packet captures
├── src/
│   ├── client.py/     # Modbus client 
│   └── server.py/     # Modbus server
├── Writeup.md/        # write‑ups
├── README.md          # this file
```
## MITRE ATT&CK for ICS Mapping
| Attack Technique         | ID    |
| ------------------------ | ----- |
| Unauthorized Message: Command Message  | T1692.001  |
| Manipulation of Control                | T0831      |

## Purdue Model
![](https://github.com/cjhosea/ics_modbus_lab/blob/main/images/mb_lab_pm.png)

## Network Diagram
![](https://github.com/cjhosea/ics_modbus_lab/blob/main/images/mb_lab_nd.png)
