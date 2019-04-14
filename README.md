# mic2Lifx
Sync connected light bulbs to your music (microphone).<br />
How does it work?<br />
-If iTunes is playing, LIFX is synced with song's BPM (you can calculate BPM thanks to Mixxx app https://www.mixxx.org/).<br />
-If itunes is not playing or no BPM have been detected, This software detect BPMs with your microphone!<br />
You need to have auto Shazam "on";<br />

Requirements:<br />
Tested on a MacOs 10.13.6. and 10.11.6 Python version 2.7.14<br />
Shazam: https://itunes.apple.com/us/app/shazam/id897118787?mt=12<br />
Spotify dev account: https://spotipy.readthedocs.io/en/latest/#installation<br />
##Prerequisites:<br />

Pillow- Screen Grabber https://pypi.python.org/simple/pillow/ <br />
download the wheel (.whl): 5.0 for 10.11.6 and 5.1 for 10.13.4.<br />
pip install (drag&drop downloaded wheel into your terminal to obtain the path)<br />
pip install git+https://github.com/mpapi/lazylights@2.0<br />
pip install colour<br />
pip install requests<br />
pip install spotipy<br />
pip install six<br />

export SPOTIPY_CLIENT_ID='your ID'<br />
export SPOTIPY_CLIENT_SECRET='your password'<br />


