#!/usr/bin/python3
import socket
import threading
import logging
import time
import os

MAX_ATTACK_TRIES = 5
UNBAN_TIME = 600
PORTS = range(1,100)

logging.basicConfig(level=logging.DEBUG, filename='portscan-detector.log')

attacker_ips = {}

def iptables_ready():
    if(os.system("iptables -L portscan-bans")==0):
        return True
    else:
        return False

def init_iptables():
    logging.debug("Created iptables chain and added it to INPUT chain.")
    os.system("iptables -N portscan-bans")
    os.system("iptables -A INPUT -j portscan-bans")

def add_iptables_ban(ip):
    logging.debug("Banned "+ip)
    cmd = "iptables -A portscan-bans -p tcp -s "+ip+" -j DROP"
    os.system(cmd)

def flush_bans():
    logging.debug("Flushed all bans.")
    os.system("iptables -F portscan-bans")

def deinit_iptables():
    logging.debug("Removing iptables chain.")
    os.system("iptables -D INPUT -j portscan-bans")
    os.system("iptables -F portscan-bans")
    os.system("iptables -X portscan-bans")

def attack_callback(ip):
    logging.debug("Callback: %s" % ip)
    if ip in attacker_ips:
        attacker_ips[ip] += 1
    else:
        attacker_ips[ip] = 1
    print (attacker_ips)

def socket_factory(port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        s.bind(('0.0.0.0', port))
    except OSError:
        return ''
    s.listen(3)
    logging.debug("Listening on port %d" % port)
    return (s, port)

def socket_thread(socket, port):
    logging.debug("Socket thread started.")
    while True:
        (client, addr) = socket.accept()
        logging.info("Connection attempt at port %d from %s port %d" % (port, addr[0], addr[1]))
        attack_callback(addr[0])
        client.close()

def ban_thread():
    logging.debug("Starting ban thread.")
    while True:
        for attacker in attacker_ips:
            if attacker_ips[attacker] > MAX_ATTACK_TRIES:
                logging.info("Banning "+attacker)
                add_iptables_ban(attacker)
                attacker_ips[attacker] = 0
        time.sleep(1)

def unban_thread():
    logging.debug("Starting unban thread")
    while True:
        time.sleep(UNBAN_TIME)
        logging.info("Unbanning all!")
        flush_bans()

def main():
    print("Created by aol1306. Requires iptables to be installed.")
    # check for root
    if os.geteuid() != 0:
        quit("You need to run this as root.")

    if (iptables_ready() == False):
        init_iptables()

    sockets = []
    # build sockets
    for port in PORTS:
        s = socket_factory(port)
        if (s != ''):
            sockets.append(s)
        else:
            logging.debug("Skipping port "+str(port))

    # start sockets' threads
    for socket in sockets:
        threading.Thread(target=socket_thread, args=(socket[0],socket[1])).start()

    # run ban thread
    threading.Thread(target=ban_thread).start()

    # run unban thread
    threading.Thread(target=unban_thread).start()

if __name__ == "__main__":
    main()
