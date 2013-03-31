#!/usr/bin/python2.7

# Things this program should do
#   use proper metadata (acoustid + musicbrainz)
#   add in album art
#   move, rename cue and log files
#   remove .m3u file, album dir if necessary
#   custom music directory

import glob
import subprocess
import re
import sys
import getopt
from musicbrainz2.webservice import Query, TrackFilter, WebServiceError
from mutagen import File
import musicbrainzngs as mb
import mimetypes

''''
musicbrainzngs.set_useragent("Autotagger", ".1", "plasmasheep@gmail.com")
cues = glob.glob("./*.cue") #CUE and log files should also be moved
logs = glob.glob("./*.log")

albums = []; #List of albums for processing cue, log files'''

def sanitize_name(name):
    return re.sub("[!@#$%^&*()~`]", "", name).lower().replace(" ", "_")

def process_flacs():
    try:
        subprocess.check_output(
            "metaflac --set-tag-from-file=DESCRIPTION=info.txt *.flac",
            shell = True)
    except CalledProcessError:
        print "Info file for DESCRIPTION tag not found."
        
    print subprocess.check_output("flac -V8f --replay-gain *.flac",
        shell = True)

def process_wavs():
    print subprocess.check_output("flac -V8f --replay-gain *.wav",
        shell = True)
    try:
        subprocess.check_output(
            "metaflac --set-tag-from-file=DESCRIPTION=info.txt *.flac",
            shell = True)
    except CalledProcessError:
        print "Info file for DESCRIPTION tag not found."

def process(rename, move):
    tracks = glob.glob("./*.flac"); #All compatible audio files
    tracks.extend(glob.glob("./*.mp3"))
    tracks.extend(glob.glob("./*.ogg"))
    tracks.extend(glob.glob("./*.wav"))

    flacs_normalized = False;
    wavs_normalized = False;
    oggs_normalized = False;
    
    if(len(tracks) == 0):
        print "No compatible audio files found. Please use flac, mp3, or ogg."
        sys.exit()
    
    for track in tracks:
        print "Processing: " + track
        audio = File(track, easy=True)
        filetype = mimetypes.guess_type(track)[0]
        suffix = mimetypes.guess_extension(filetype)
        
        if filetype.find("flac") != -1:
            print "FLAC file detected"
            if flacs_normalized is False:
                print "Processing all FLAC files..."
                process_flacs()
                flacs_normalized = True;
            else:
                print "FLACs already processed"
            
        if filetype.find("ogg") != -1:
            print "OGG file detected"
            if oggs_normalized is False:
                print "Processing all OGG files..."
                print subprocess.check_output("vorbisgain *.ogg", shell = True)
                oggs_normalized = True
            else:
                print "OGGs already processed"

        if filetype.find("wav") != -1:
            print "WAV file detected";
            if wavs_normalized is False:
                print "Processing all WAV files...";
                process_wavs()
                wavs_normalized = True
            else:
                print "WAVs already processed"
            #WAV files will become flac files
            track = track[:-4] + ".flac"
        
                
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

        if rename:
            try:
                newname = '{:0>2}'.format(audio["tracknumber"][0]) + "-" + \
                    sanitize_name(audio["title"][0])
                print "Moving " + track + " to " + newname + suffix;
                subprocess.call(['mv', track, newname + suffix])
                track = newname + suffix
            except TypeError:
                print "No metadata readable, cannot rename with track info."
                subprocess.call(["mv", track, sanitize_name(track)])
                track = sanitize_name(track)
            
        if move:
            try:
                newdir = "/home/alyosha/music/" + \
                    sanitize_name(audio["artist"][0]) + "/" + \
                    sanitize_name(album) + "/"
                subprocess.call(["mkdir", "-p", newdir])
                subprocess.call(['mv', track, newdir + track])
            except TypeError:
                print "No metadata readable, cannot move."

        print "----"

def manual():
    print "autotag <options> <directory>" #TODO: real help
    sys.exit(2)

def main(argv):
    rename = False;
    move = False
    try:
        opts, args = getopt.getopt(argv, "hnm", ["help", "rename", "move"])
    except getopt.GetoptError:
        manual()
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            manual()
        elif opt in ("-n", "--rename"):
            rename = True
        elif opt in ("-m", "--move"):
            move = True
    process(rename, move)


if(__name__ == "__main__"):
    main(sys.argv[1:])