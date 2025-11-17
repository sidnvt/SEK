Social Engineering: A Chained, Potent Attack Vector
===================================================

### Capstone Project -- Defensive Security Research

Overview
--------

This repository contains a defensive cybersecurity research project demonstrating how social engineering can trigger a chained, multi-stage attack vector. The project uses a proof-of-concept payload (ProcMon.py) to show how attackers exploit human behavior to gain initial access, deploy a malicious script, establish persistence, capture credentials, exfiltrate data using a cloud-based C2 channel, and remotely wipe evidence.

The purpose of this project is educational. All testing was performed in an isolated, sandboxed environment.

* * * * *

Repository Structure
--------------------

`/Social-Engineering-Chained-Attack/
│
├── ProcMon.py               # Proof-of-concept keylogger + persistence + C2
├── project-report.pdf       # Full project report
└── README.md                # Documentation`

* * * * *

Project Objectives
------------------

1.  Demonstrate how a social engineering lure can deliver a technical payload.

2.  Simulate the full attack chain using a custom Python payload.

3.  Analyze attacker Tactics, Techniques, and Procedures (TTPs).

4.  Document detection opportunities and defensive strategies.

5.  Highlight modern challenges in identifying cloud-based, fileless, and LotL attacks.

* * * * *

Attack Chain Summary
--------------------

| Kill Chain Stage | Implementation in Project |
| --- | --- |
| Reconnaissance | Information gathering and lure preparation |
| Delivery | User executes disguised ProcMon.py script |
| Exploitation | Script runs with user privileges |
| Installation | Persistence added via Startup folder (logger.bat) |
| Command & Control | Firebase Realtime Database used for beaconing and data upload |
| Actions on Objective | Keylogging and credential capture |
| Covering Tracks | Remote kill-switch triggers script and persistence self-deletion |

* * * * *

Proof-of-Concept Payload (ProcMon.py)
-------------------------------------

The payload simulates a realistic chained attack while remaining lightweight and easy to analyze.

### Key Features

**Keylogging**\
Uses the `keyboard` library to capture keystrokes non-blockingly, storing them in a queue.

**Data Exfiltration**\
A background thread periodically pushes buffered keystrokes to a Firebase Realtime Database. Traffic blends with legitimate encrypted HTTPS traffic.

**Persistence Mechanism**\
Adds a batch file named `logger.bat` to:

`%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup`

This ensures continuous execution at every system login.

**Command & Control (C2)**\
Uses Firebase as a "Living off the Land" C2 channel. Processes commands from:

`control/<device_name>/delete`

**Remote Kill-Switch**\
If the C2 signals deletion, the script:

1.  Removes the Startup persistence file

2.  Deletes its own payload file

3.  Terminates immediately

* * * * *

MITRE ATT&CK Mapping
--------------------

| Technique ID | Technique Name | Implementation Context |
| --- | --- | --- |
| T1056 | Input Capture (Keylogging) | Keyboard hook captures all key events |
| T1547.001 | Boot/Logon Autostart (Startup Folder) | Persistence via logger.bat |
| T1071.001 | Application Layer Protocol (Web Protocols) | HTTPS traffic to Firebase |
| T1102 | Web Service for C2 | Firebase Realtime Database |
| T1573 | Encrypted Channel | TLS-encrypted exfiltration |

* * * * *

Defensive Value of This Project
-------------------------------

This project helps understand:

-   How simple tools can bypass traditional signature-based antivirus

-   How cloud services can be abused as covert C2 channels

-   Why behavioral detection (EDR/Sysmon) is essential

-   How chained attacks unfold from initial deception to system compromise

-   How SOC and blue team analysts can detect suspicious activity via telemetry

* * * * *

Detection Opportunities
-----------------------

**1\. Persistence Creation**\
Monitor file creation inside the Startup folder.

**2\. Abnormal Python Behavior**\
Python processes capturing keystrokes or writing to Startup folders are high-risk behaviors.

**3\. Outbound C2 Beaconing**\
Regular, periodic HTTPS connections to Firebase endpoints from a non-browser process.

**4\. Keyboard Hooks**\
Low-level keyboard access from untrusted Python scripts.

* * * * *

Ethical Use Notice
------------------

This project is intended strictly for academic, defensive, and research use in authorized environments.\
Running the payload on systems without explicit permission is illegal and unethical.

* * * * *

Authors
-------

-   Siddhant Tiwari

-   Atharva Barge

-   Neha Varma

Chandigarh University\
B.E. CSE (Hons.) Information Security\
July--December 2025
