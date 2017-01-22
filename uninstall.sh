#!/bin/bash
rm -rfv /etc/portscan-detector
systemctl stop portscan-detector
systemctl disable portscan-detector
rm /etc/systemd/system/portscan-detector.service
systemctl daemon-reload
