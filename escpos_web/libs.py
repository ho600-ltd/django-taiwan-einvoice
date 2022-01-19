#! /usr/bin/env python3
# -*- coding:utf-8 -*-
import time, netifaces, urllib.request, datetime


def get_public_ip():
    no_ip = '?.?.?.?'
    i = 0
    while i < 10:
        try:
            external_ip = urllib.request.urlopen('https://ipv4.icanhazip.com').read().strip().decode('utf-8')
        except:
            external_ip = no_ip
        if no_ip == external_ip:
            i += 1
            time.sleep(3)
        else:
            break
    return external_ip


def get_eths():
    eths = []
    for eth in netifaces.interfaces():
        if 'lo' == eth: continue
        i = netifaces.ifaddresses(eth)
        try: ip = netifaces.ifaddresses(eth)[netifaces.AF_INET][0]['addr']
        except: pass
        else: eths.append((eth, ip))
    return eths


def get_boot_seed():
    try:
        seed = open('/var/run/boot_random_seed', 'r').read()[:3].upper()
    except:
        seed = '???'
    return seed


def get_hour_minute():
    return datetime.datetime.now().strftime('%H:%M')
