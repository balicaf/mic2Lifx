#Todo: Change global var with getter and setter function (OOP)
#Todo: make the code nicer with Pep8 & pylint
#to run it, if you have a foundation not found (and pip pyobjc is not working) ...
#... try /usr/bin/python ~/Documents/GitHub/mic2Lifx/mic2Lifx.py
#brew install nmap

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

KELVIN = 0  # 0 nothing applied i.e. 6500K. [2000 to 8000], where 2000 is the warmest and 8000 is the coolest
INTENSITY = 1 #Amplitude of the light, 1 is the max 0 the min
DURATION = 3000  # The time over which to change the colour of the lights in ms. Use 100 for faster transitions
SLOW_DOWN = 1  # integer to decrease stroboscopic effect
bpmTrack = 0  # bpm output of Itunes

qSpotify_last = ""  #it stores the last shazam ong identified
shazamChangedTime = 0  # to know if it's been more than 4 minutes than the song has begun to play

#18.7.0 --> Mojave
#19.2.0 --> catalina
if  int(platform.release()[0:2])<19:
	iTunes = SBApplication.applicationWithBundleIdentifier_("com.apple.iTunes")
else:
	iTunes = SBApplication.applicationWithBundleIdentifier_("com.apple.Music")
previousSong = iTunes.currentTrack().name()  #intialisation
bpm = iTunes.currentTrack().bpm()#0  # bpm that will be the input of LIFX #initialization
pathSQL = os.path.expanduser("~/Library/Group Containers/4GWDBCF5A4.group.com.shazam/com.shazam.mac.Shazam/ShazamDataModel.sqlite")
#cd ~/Library/Group\ Containers/4GWDBCF5A4.group.com.shazam/com.shazam.mac.Shaza
sliderValue = 0  # graphical interface

"""
# I use this to manually create a bulb using IP and MAC address.
def createBulb(ip, macString, port=56700):
	return lazylights.Bulb(b'LIFXV2', binascii.unhexlify(macString.replace(':', '')), (ip, port))
"""
def main():
	print("hello world")
	graphInterfaceInit() # slidder to mannualy control the begging of the beats
	BPMCalculator() #output music bpm
	lightChanger() #loop to change light according to bpms

def scan_for_hosts(ip_range):
	"""Scan the given IP address range using Nmap and return the result
	in XML format.
	"""
	nmap_args = ['nmap', '-n', '-sP', '-oX', '-', ip_range]
	#nmap_args = ['nmap', '-sn', ip_range]
	return subprocess.check_output(nmap_args)


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

#https://homework.nwsnet.de/releases/9577/
def find_IP_address_from_MAC(mac_address):
	#mac_address = mac_address #'d0:73:d5:31:ea:4e'
	ip_range = '192.168.0.1-60'

	xml = scan_for_hosts(ip_range)
	ip_address = find_ip_address_for_mac_address(xml, mac_address)

	if ip_address:
		print('Found IP address {} for MAC address {} in IP address range {}.'
			  .format(ip_address, mac_address, ip_range))
		return ip_address
	else:
		print('No IP address found for MAC address {} in IP address range {}.'
			  .format(mac_address, ip_range))

def graphInterfaceInit():
	global w, w2
	master = Tk()
	w = Scale(master, from_=0, to=100,length=600, label='shift one beat per -50- ')
	w.pack()
	w2 = Scale(master, from_=1, to=16,length=600,tickinterval=1, orient=HORIZONTAL, label='-4- normal, -2- blinks twice faster, -8- slower')
	w2.set(4)
	w2.pack()

def graphInterfaceUpdate():
	global w, w2
	global sliderValue
	global SLOW_DOWN
	w.update()
	sliderValue = w.get()
	w2.update()
	SLOW_DOWN = (w2.get())/4.0

def getShazamSong():
	global pathSQL
	connection = sqlite3.connect(pathSQL)
	cursor = connection.cursor()
	results = cursor.execute(
		'''
		SELECT artist.ZNAME, tag.ZTRACKNAME
		FROM ZSHARTISTMO artist, ZSHTAGRESULTMO tag
		WHERE artist.ZTAGRESULT = tag.Z_PK
		ORDER BY tag.ZDATE
		DESC LIMIT 1
		'''
	)
	for result in results:
		artistSpotify = re.sub(r'\([^)]*\)', '', result[0])
		artistSpotify = artistSpotify.replace('&',' ')
		artistSpotify = artistSpotify.replace('.',' ')
		trackSpotify = re.sub(r'\([^)]*\)', '', result[1])
		trackSpotify = trackSpotify.replace('&',' ')
		trackSpotify = trackSpotify.replace('.',' ')
		qSpotify = " ".join(artistSpotify.split()[:2]) + ", " + " ".join(trackSpotify.split()[:3])#just the 2 first words
	connection.close()
	print("shazam info to spotify: ", qSpotify)
	return qSpotify

def getSpotifyBPM():
	global sliderValue
	global beginBPM
	global bpm
	qSpotify = getShazamSong()
	credentials = oauth2.SpotifyClientCredentials(
			client_id=os.environ['SPOTIPY_CLIENT_ID'],
			client_secret=os.environ['SPOTIPY_CLIENT_SECRET'])
	token = credentials.get_access_token()
	sp = spotipy.Spotify(auth=token)#if not t['name']:
	results = sp.search(q=qSpotify, limit=1)
	for i, t in enumerate(results['tracks']['items']):
		idTrack = t['id']
		features = sp.audio_features([idTrack])
	try:
		print("BPM spotify: ",features[0]['tempo'])
		print("w1.get()", sliderValue)
		print("beginBPMSlidder", beginBPMSlidder)
	except:
		print("features not get from spotify?")	
	try:	
		return (features[0]['tempo']) #(features['tempo'] not dict, 10th place
	except:
		return (bpm) #standart bpm
def shazamChanged():
		global qSpotify_last
		global shazamChangedTime
		qSpotify_cur = getShazamSong()
		if qSpotify_cur != qSpotify_last:
			print("modified")
			qSpotify_last = qSpotify_cur
			shazamChanged = True
			shazamChangedTime = time.time()
		else:
			shazamChanged = False

def spotify2BPM():
	global bpm
	global shazamChanged
	global shazamChangedTime
	shazamChanged()
	if shazamChanged:
		bpm = getSpotifyBPM()
	elif time.time() - shazamChangedTime > 240:  #it's been too long since the last music, switch to colorWheel
		bpm = 0

def BPMCalculator():
	threading.Timer(8.0, BPMCalculator).start()
	global previousSong
	global bpm
#	while True:
#	time.sleep(2)
	#print(iTunes.playerState())
	notPlaying = (iTunes.playerState() == 1800426352)# or iTunes.playerState() == MusicEPlSPaused) #https://github.com/kyleneideck/BackgroundMusic/blob/master/BGMApp/BGMApp/Music%20Players/BGMMusic.m
	if notPlaying:# if Itunes is not playing music	#MusicEPlSPaused
		spotify2BPM()
		print("not playing", notPlaying)
	elif bpm == 0:
		print("bpm", bpm)
		# if it is playing but no BPMs
		spotify2BPM()  # run shazam
	elif iTunes.currentTrack().name() != previousSong:  #playing next_track: #i.e. iTunes.currentTrack().name not equal
		previousSong = iTunes.currentTrack().name()
		bpmTrack = iTunes.currentTrack().bpm()
		print("this track BPM is: ", bpmTrack)
		# if it's playing and there is an associated BPM
		#bpmTrack != 0:
		bpm = bpmTrack
def createBulb(ip, macString, port = 56700):        
	return lazylights.Bulb(b'LIFXV2', binascii.unhexlify(macString.replace(':', '')), (ip,port))
def lightChanger():
	global sliderValue
	global bpm
	global beginBPMSlidder
	# Scan for 2 bulbs
	#bulbs = lazylights.find_bulbs(expected_bulbs=4, timeout=4)
	#bulb0 = list(bulbs)[0]
	#print(len(bulbs))
	#myBulb1 = createBulb('\xd0s\xd51\xeaN')  
	#myBulb2 = createBulb('\xd0s\xd5$mE')  
	mac1='d0:73:d5:31:ea:4e'
	mac2='d0:73:d5:2c:ba:d1'
	mac3='d0:73:d5:53:ff:a2'
	mac4='02:0F:B5:24:6D:45'

	ip1 = find_IP_address_from_MAC(mac1)
	ip2 = find_IP_address_from_MAC(mac2)
	ip3 = find_IP_address_from_MAC(mac3)
	#mac4 = find_IP_address_from_MAC('d0:73:d5:2c:ba:d1')

	myBulb1 = createBulb(ip1,mac1)   
	myBulb2 = createBulb(ip2,mac2) 
	myBulb3 = createBulb(ip3,mac3) 
	#myBulb4 = createBulb(mac2,'d0:73:d5:2c:ba:d1')   

	#d0:73:d5:31:ea:4e
	#d0:73:d5:2c:ba:d1
	#d0:73:d5:53:ff:a2
	#02:0F:B5:24:6D:45 wtf?

	#myBulb3 = createBulb('192.168.1.x','xx:xx:xx:xx:xx:xx')
	# Bulb(gateway_mac='LIFXV2', mac='\xd0s\xd51\xeaN', addr=('192.168.0.12', 56700)),
	# Bulb(gateway_mac='LIFXV2', mac='\xd0s\xd5$mE'   , addr=('192.168.0.14', 56700))  
	bulbs=[myBulb1, myBulb2, myBulb3]
	# now bulbs can be called by their names
	bulbs_by_name = {state.label.strip(" \x00"): state.bulb
					 for state in lazylights.get_state(bulbs)}
	if (len(bulbs) == 0):
		print ("No LIFX bulbs found. Make sure you're on the same WiFi network and try again")
		sys.exit(1)
	# turn on
	lazylights.set_power(bulbs, True)
	# do nothing during a tenth of a second
	time.sleep(0.1)
	# init counters/accumulators
	red = 0
	green = 0
	blue = 0
	redReg = 0
	greenReg = 0
	blueReg = 0
	begin1 = time.time()
	beatLenghtReg = DURATION + 1  # to force it to a state beatLenghtReg not equal to beatLenght
	beginBPM = time.time()
	countBeat = 1
	cReg = Color(rgb=(1, 0, 0))
	global cHue
	cHue = cReg.hue
	sliderValueReg = sliderValue
	# the music changed
	while True:
		graphInterfaceUpdate()
		if bpm != 0:
			beatLenght = SLOW_DOWN * 60000.0 / bpm
		else:
			beatLenght = DURATION

		if beatLenghtReg != beatLenght:
			beginBPM = time.time()
			countBeat = 0
			beatLenghtReg = beatLenght 
			print ("music changed BPM is now: ", bpm)
		# no music is playing (e.g. pause or just only watching youtube music)
		elif (beatLenght == DURATION):  #i.e. bpm == 0

			cHue += 0.01
			time.sleep(0.2)  # 20 wifi commands per seconds, can be increased if no checking
			lazylights.set_state(bulbs, (cHue + 0.5) * 360, 1, 1, KELVIN, 200, False)
			# LIFX 246D45
			lazylights.set_state(bulbs, cHue * 360, 1, 1, KELVIN, 200, False)
			print(cHue)
		# 31ea4e
		# while music is playing
		else:
			#if sliderValue != sliderValueReg
			beginBPMSlidder = beginBPM + 2 * sliderValue * beatLenght / 100000  #slider value is 0->100 
			#print("beginBPMSlidder", beginBPMSlidder)

				#sliderValueReg = sliderValueReg
			# this is the same music
			a = (beatLenght / 1000) - (time.time() - beginBPMSlidder) % (beatLenght / 1000.0)
			a = max(0, a)
			time.sleep(a)  # should not sleep if 0
			countBeat += 1
			red = random.uniform(0, 1)
			#find RGB that is not looking the same as the previous RGB
			while abs(red - redReg) < 0.15:
				red = random.uniform(0, 1)
			while abs(blue - blueReg) < 0.15:
				blue = random.uniform(0, 1)
			while abs(green - greenReg) < 0.15:
				green = random.uniform(0, 1)

			c = Color(rgb=(red, green, blue))  # display a random color but sufficently different from the previous one

			# on even numbers, first lifx is light on
			if countBeat % 2 == 0:
				lazylights.set_state(bulbs, cReg.hue * 360, cReg.saturation, INTENSITY, KELVIN, 0, False)
			# on odd numbers it is the other one
			else:
				cReg = c
				redReg = red  # save each previous color
				blueReg = blue
				greenReg = green
				lazylights.set_state(bulbs, c.hue * 360, c.saturation, INTENSITY, KELVIN, 0, False)
		# lazylights.set_state(bulbs,c.hue*360,(2+c.saturation)/3,1,KELVIN,(DURATION),False)#c.luminance

if __name__ == '__main__':
	main()

