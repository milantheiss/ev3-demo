EV3 Demo Project
=================

Das Projekt demonstriert den LEGO Mindstorm EV3 Roboter.  
Auf dem Roboter läuft ev3dev-stretch.  
Aller Quellcode in diesem Repository wurde in Python verfasst  
und benutzt die [ev3dev2 Python Library](https://github.com/ev3dev/ev3dev-lang-python).

---
Mitgewirkt an diesem Projekt haben:  
- [Milan Theiß](https://github.com/milantheiss) - EV3 Programmierung, Backend, Discord Bot
- [Noah Yannik Alps](https://github.com/Noah-Alps) - Radar Application, Bau
- [Max Meinel](https://github.com/Max-Meinel) - Discord Bot, Bau
- [Leonhard Wegers](https://github.com/leonhard2004) - Bau
---
Für die Steuerung des EV3 mit einem XBox Controller wurde Quellcode von Github User [hugbug](https://github.com/hugbug/ev3/tree/master/gidd3) adaptiert.  
Für die Server und Clients wurde Quellcode von [RealPython](https://realpython.com/python-sockets/)

---
### Getting Started  
Die einzelnen Unterordner gehören jeweils zu einem Gerät.  
Nutze diese Befehle, um die Script auf dem Gerät im Terminal zu starten.  
Für Windows:  
`python *.py`  
Für Linux:  
`python3 *.py`  
Ersetze * mit dem vollen Python Script Name.  

Jeweils die ... _control Scripte steuern die Prozesse.

---
Um die Scripte ausführen zu können, installiere die Dependencies aus `requirements.txt`  
Nutze `pip install -r requirements.txt`

---
Um den Discord Bot starten zu können, musst du dir einen eigenen Bot erstellen  
und in einer .env Datei den Bot Token abzuspeichern.  
Der Token muss in der .env Datei unter `DISCORD_TOKEN` abgespeichert werden 

