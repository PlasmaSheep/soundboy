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

import pprint

''''
cues = glob.glob("./*.cue") #CUE and log files should also be moved
logs = glob.glob("./*.log")

albums = []; #List of albums for processing cue, log files'''

args = {"rename":False, "move":False, "albumart":False,
    "descriptionfile":"info.txt", "normalize":False }

def sanitize_name(name):
    return re.sub("[!@#$%^&*()~`]", "", name).lower().replace(" ", "_")

def convert_process_flacs(mask):
    """Convert all files matching mask to flac and process at once."""
    global args
    if args["normalize"]:
        print(subprocess.check_output("flac -V8f --replay-gain " + mask,
            shell = True))
    try:
        subprocess.check_output("metaflac --set-tag-from-file=DESCRIPTION=" +
            args["descriptionfile"] + " *.flac", shell = True)
    except subprocess.CalledProcessError:
        pass #no big deal

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

    if args["albumart"]:
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
        
        if suffix == ".flac":
            print("FLAC file detected")
            if flacs_normalized is False:
                print("Processing all FLAC files...")
                convert_process_flacs("*.flac")
                flacs_normalized = True;
            else:
                print("FLACs already processed")
            
        if suffix == ".ogg":
            print("OGG file detected")
            if oggs_normalized is False:
                print("Processing all OGG files...")
                print(subprocess.check_output("vorbisgain *.ogg", shell = True))
                oggs_normalized = True
            else:
                print("OGGs already processed")

        if suffix == ".wav":
            print("WAV file detected")
            if wavs_normalized is False:
                print("Processing all WAV files...")
                convert_process_flacs("*.wav")
                wavs_normalized = True
            else:
                print("WAVs already processed")
            #WAV files will become flac files, update track accordingly
            track = track[:-4] + ".flac"
        
        if suffix == ".mp3":
            #First convert all tags into a dict
            tags = {}
            keys = audio.keys()
            for key in keys:
                tags[key] = audio[key][0]

            if args["normalize"]: #TODO: this does not handle album norm
                print(subprocess.check_output(["lame", "--replaygain-accurate",
                track]))
                subprocess.call(["mv", track + ".mp3", track])
                audio = File(track)
                for tag, value in tags.iteritems():
                    #audio = File(track)
                    audio[tag] = value
                    audio.save()
                    #Set file's tags, save it
            #print subprocess.check_output(["id3v2", "-C", track])
            #print subprocess.check_output(["id3v2", "--delete-v1", track])

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
        
def main(argv): #Maybe make this take a list of files?
    global args
    parser = argparse.ArgumentParser(
        description = "Import files in the current directory.")
    parser.add_argument("-r", "--rename", action="store_true",
        help="Rename the files.")
    parser.add_argument("-m", "--move", action="store_true",
        help="Move the files to the music directory.")
    parser.add_argument("-a", "--albumart", action="store_true",
        help="Set album art as metadata.")
    parser.add_argument("-n", "--normalize", action="store_true",
        help="Normalize tracks with ReplayGain.")
    parser.add_argument("-d", "--descriptionfile", action="store_true",
        default="info.txt", help="Which file to use for the DESCRIPTION tag.")
    args = vars(parser.parse_args(argv))
    
    process()


if(__name__ == "__main__"):
    main(sys.argv[1:])