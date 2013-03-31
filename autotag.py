#!/usr/bin/python2.7

# Things this program should do
#  Xreplaygain and compress -8
#  Xrename proper (tracknumber-trackname.flac, no wtf chars)
#   use proper metadata (acoustid + musicbrainz)
#   add in album art
#   move, rename cue and log files
#   remove .m3u file, album dir if necessary

import glob
import subprocess
import re
import sys
from musicbrainz2.webservice import Query, TrackFilter, WebServiceError
from mutagen import File
import musicbrainzngs as mb

musicbrainzngs.set_useragent("Autotagger", ".1", "plasmasheep@gmail.com")

tracks = glob.glob("./*.flac"); #All compatible audio files
tracks.extend(glob.glob("./*.mp3"))
tracks.extend(glob.glob("./*.ogg"))
tracks.extend(glob.glob("./*.wav"))

cues = glob.glob("./*.cue") #CUE and log files should also be moved
logs = glob.glob("./*.log")

albums = []; #List of albums for processing cue, log files

def sanitize_name(name):
    return re.sub("[!@#$%^&*()~`]", "", name).lower().replace(" ", "_")

if(len(tracks) == 0):
    print "No compatible audio files found. Please use flac, mp3, or ogg."
    sys.exit()

for track in tracks:
    print "Processing: " + track
    audio = File(track, easy=True)
    
    if(re.search("[a-z0-9\.\-](flac)", track)):
        #subprocess.call(["metaflac", "--set-tag-from-file=DESCRIPTION=info.txt",
        #track])
        print "FLAC file detected"
        suffix = ".flac"
        if(!flacs_normalized):
            print "Processing all FLAC files..."
            subprocess.call(["metaflac",
            "--set-tag-from-file=DESCRIPTION=info.txt", "*.flac"])
            subprocess.check_output(["flac", "-V8f", "--replay-gain",
            "*.flac"])
            flacs_normalized = True;
        
    if(re.search("[a-z0-9\.\-](ogg)", track)):
        print "OGG file detected"
        suffix = ".ogg"
        if(!oggs_normalized):
            print "Processing all OGG files..."
            print subprocess.check_output(["vorbisgain", "*.ogg"])
            oggs_normalized = True
        

    if(re.search("[a-z0-9\.\-](wav)", track)):
        print "WAV file detected";
        #WAV files will become flac files
        newname = track[:-4]
        suffix = ".flac"
        newdir = "./"
        if(!wavs_normalized):
            print "Processing all WAV files...";
            print subprocess.check_output(["flac", "-V8f", "--replay-gain",
            "*.wav"])
            subprocess.call(["metaflac",
            "--set-tag-from-file=DESCRIPTION=info.txt", "*.flac"])
            wavs_normalized = True
                
    '''if(re.search("[a-z0-9\.\-](mp3)", track)):
        print subprocess.check_output(["lame", "--replaygain-accurate", track])
        subprocess.call(["mv", track + ".mp3", track])
        print subprocess.check_output(["id3v2", "-C", track])
        print subprocess.check_output(["id3v2", "--delete-v1", track])
        #trackinfo = subprocess.check_output(["id3v2", "-l", track])
        #trackinfo = trackinfo.splitlines()
        #for line in trackinfo:
        #    
        #    if(line.find("TIT2") == 0):
        #        print "found title";
        #        title = line[43:];
        #    elif(line.find("TRCK") == 0):
        #        num = line[38:];
        suffix = ".mp3";'''

    #This needs to be restructured. newname is set above in some cases.
    #Su3UVJhC
    try:
        title = audio["title"][0]
        num = audio["tracknumber"][0]
        artist = audio["artist"][0]
        album = audio["album"][0]
        newdir = "/home/alyosha/music/" + sanitize_name(artist) + "/" +
        sanitize_name(album) + "/"
        newname = num + "-" + sanitize_name(title) + suffix
        albums.append(album)
        if(len(num) < 2):
            num = "0" + num
    except TypeError:
        print "No metadata readable."
        #title = 
    
    print "Moving " + track + " to " + newname;
    subprocess.call(["mkdir", "-p", newdir])
    subprocess.call(['mv', tracks, newdir + newname])


def main():
    ##

if(__name__ == "__main__"):
    main()