#!/bin/bash
mkdir /etc/portscan-detector
cp portscan-detector.py /etc/portscan-detector/portscan-detector.py
chmod 777 /etc/portscan-detector/portscan-detector.py
cp portscan-detector.service /etc/systemd/system/portscan-detector.service
chmod 755 /etc/systemd/system/portscan-detector.service
systemctl daemon-reload
systemctl enable portscan-detector
