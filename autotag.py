#!/usr/bin/python2.7

# Things this program should do
#   use proper metadata (acoustid + musicbrainz)
#   add in album art (guess from file names?)
#   move, rename cue and log files
#   remove .m3u file, album dir if necessary
#   custom music directory

import acoustid
import argparse
import glob
import mimetypes
import musicbrainzngs as mb
from mutagen import File
import re
import subprocess
import sys

''''
cues = glob.glob("./*.cue") #CUE and log files should also be moved
logs = glob.glob("./*.log")

albums = []; #List of albums for processing cue, log files'''

args = {"rename": False, "move": False, "addart": False}

def sanitize_name(name):
    return re.sub("[!@#$%^&*()~`]", "", name).lower().replace(" ", "_")

def process_flacs():
    """Process all flac files at once."""
    try:
        subprocess.check_output(
            "metaflac --set-tag-from-file=DESCRIPTION=info.txt *.flac",
            shell = True)
    except subprocess.CalledProcessError:
        print("Info file for DESCRIPTION tag not found.")
        
    print(subprocess.check_output("flac -V8f --replay-gain *.flac",
        shell = True))

def process_wavs():
    """Process all wav files at once, and convert to flac."""
    print(subprocess.check_output("flac -V8f --replay-gain *.wav",
        shell = True))
    try:
        subprocess.check_output(
            "metaflac --set-tag-from-file=DESCRIPTION=info.txt *.flac",
            shell = True)
    except subprocess.CalledProcessError:
        print("Info file for DESCRIPTION tag not found.")

def process():
    global args
    """Process all tracks in the current directory.

    Keyword arguments:
    rename - If true, rename the tracks.
    move - If true, move the tracks to the music directory.
    addart - If true, try to guess and add album art to files.
    """
    tracks = glob.glob("./*.flac") #All compatible audio files
    tracks.extend(glob.glob("./*.mp3"))
    tracks.extend(glob.glob("./*.ogg"))
    tracks.extend(glob.glob("./*.wav"))

    flacs_normalized = False;
    wavs_normalized = False;
    oggs_normalized = False;

    if args["addart"]:
        pics = glob.glob("./*.png") #Image files
        pics.extend(glob.glob("./*.jpg"))
        pics.extend(glob.glob("./*.jpeg"))
        pics.extend(glob.glob("./*.gif"))

    if False:
        mb.set_useragent("Autotagger", ".1", "plasmasheep@gmail.com")
    
    if(len(tracks) == 0):
        print("No compatible audio files found. Please use flac, mp3, or ogg.")
        sys.exit()
    
    for track in tracks:
        print("Processing: " + track)
        audio = File(track, easy=True)
        filetype = mimetypes.guess_type(track)[0]
        suffix = mimetypes.guess_extension(filetype)
        
        if filetype.find("flac") != -1:
            print("FLAC file detected")
            if flacs_normalized is False:
                print("Processing all FLAC files...")
                process_flacs()
                flacs_normalized = True;
            else:
                print("FLACs already processed")
            
        if filetype.find("ogg") != -1:
            print("OGG file detected")
            if oggs_normalized is False:
                print("Processing all OGG files...")
                print(subprocess.check_output("vorbisgain *.ogg", shell = True))
                oggs_normalized = True
            else:
                print("OGGs already processed")

        if filetype.find("wav") != -1:
            print("WAV file detected")
            if wavs_normalized is False:
                print("Processing all WAV files...")
                process_wavs()
                wavs_normalized = True
            else:
                print("WAVs already processed")
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
        
        '''if grabmeta:
            fingerprint = acoustid.fingerprint_file(track)
            result = acoustid.lookup("ZKTsCHXl", fingerprint[1], fingerprint[0])
            look = mb.get_release_by_id(result["results"][0]["recordings"][0]["id"])'''

        if args["rename"]:
            try:
                newname = '{:0>2}'.format(audio["tracknumber"][0]) + "-" + \
                    sanitize_name(audio["title"][0])
                print(subprocess.check_output(['mv', "-v", track,
                    newname + suffix]))
                track = newname + suffix
            except TypeError:
                print("No metadata readable, cannot rename with track info.")
                print(subprocess.check_output(["mv", "-v", track,
                    sanitize_name(track)]))
                track = sanitize_name(track)
            
        if args["move"]:
            try:
                newdir = "/home/user/music/" + \
                    sanitize_name(audio["artist"][0]) + "/" + \
                    sanitize_name(audio["album"][0]) + "/"
                subprocess.call(["mkdir", "-p", newdir])
                print(subprocess.check_output(['mv', "-v", track,
                    newdir + track]))
            except TypeError:
                print("No metadata readable, cannot move.")

        print("----")

def manual():
    """Give the user help."""
    print("autotag <options> <directory>") #TODO: real help)
    sys.exit(2)

def main(argv): #Maybe make this take a list of files?
    global args
    parser = ArgumentParser(
        description = "Import files in the current directory.")
    parser.add_argument("-r", "--rename", action="store_true")
    parser.add_argument("-m", "--move", action="store_true")
    parser.add_argument("-a", "--albumart", action="store_true")
    
    """try:
        opts, args = getopt.getopt(argv, "hnma", ["help", "rename", "move",
            "albumart"])
    except getopt.GetoptError:
        manual()
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            manual()
        elif opt in ("-n", "--rename"):
            args["rename"] = True
        elif opt in ("-m", "--move"):
            args["move"] = True
        elif opt in ("-a", "--albumart"):
            args["addart"] = True"""
    
    process()


if(__name__ == "__main__"):
    main(sys.argv[1:])