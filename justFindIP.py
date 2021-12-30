import objc
import lazylights
import time
from PIL import ImageGrab
import os
from colour import Color
import sys
import math
import binascii
import threading
import random
from ScriptingBridge import *
import sqlite3
import spotipy
import spotipy.oauth2 as oauth2
import os
import re
import subprocess #findMacAdress
import xml.etree.ElementTree as ET#findMacAdress
try:
	from Tkinter import *
except ImportError:
	from tkinter import * #graphical interface
import platform #get osx version for Catalina Music app compatibility
mac = ["st","2","3","4","5"]

def find_IP_address_from_MAC(mac_address):
	#mac_address = mac_address #'d0:73:d5:31:ea:4e'
	ip_range='192.168.0.1-60'
	attempt = 0

	
	#print("xml", xml)
	#print (ip_address)
	while attempt < 5:
		try:
			xml = scan_for_hosts(ip_range)
			ip_address = find_ip_address_for_mac_address(xml, mac_address)
		except:
			break
		if ip_address:
			print('Found IP address {} for MAC address {} in IP address range {}.'.format(ip_address, mac_address, ip_range))
			attempt = 0
			return ip_address
		else:
			print('attempt {} for MAC {}.'.format(attempt, mac_address))
			attempt = attempt + 1
			time.sleep(0.4)

def scan_for_hosts(ip_range):
	"""Scan the given IP address range using Nmap and return the result
	in XML format.
	"""
	nmap_args = ['sudo', 'nmap', '-n', '-sP', '-oX', '-', ip_range]
	#nmap_args = ['nmap', '-sn', ip_range]

	return subprocess.check_output(nmap_args)


	mac4='d0:73:d5:31:ea:4e'
def find_ip_address_for_mac_address(xml, mac_address):
	"""Parse Nmap's XML output, find the host element with the given
	MAC address, and return that host's IP address (or `None` if no
	match was found).
	"""
	host_elems = ET.fromstring(xml).iter('host')
	host_elem = find_host_with_mac_address(host_elems, mac_address)
	if host_elem is not None:
		return find_ip_address(host_elem)
def find_host_with_mac_address(host_elems, mac_address):
	"""Return the first host element that contains the MAC address."""
	for host_elem in host_elems:
		if host_has_mac_address(host_elem, mac_address):
			return host_elem


def host_has_mac_address(host_elem, wanted_mac_address):
	"""Return true if the host has the given MAC address."""
	found_mac_address = find_mac_address(host_elem)
	return (
		found_mac_address is not None and
		found_mac_address.lower() == wanted_mac_address.lower()
	)


def find_mac_address(host_elem):
	"""Return the host's MAC address."""
	return find_address_of_type(host_elem, 'mac')


def find_ip_address(host_elem):
	"""Return the host's IP address."""
	return find_address_of_type(host_elem, 'ipv4')


def find_address_of_type(host_elem, type_):
	"""Return the host's address of the given type, or `None` if there
	is no address element of that type.
	"""
	address_elem = host_elem.find('./address[@addrtype="{}"]'.format(type_))
	if address_elem is not None:
		return address_elem.get('addr')

def main():	
	global mac 
	mac[3]=''
	mac[2]=''
	mac[4]=''
	mac[0]=''
	mac[1]=''
	for macX in range (5):
		find_IP_address_from_MAC(mac[macX])

if __name__ == '__main__':
	main()
