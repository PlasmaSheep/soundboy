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
#import musicbrainzngs as mb
from mutagen import File
import re
import subprocess
import sys

import pprint

''''
cues = glob.glob("./*.cue") #CUE and log files should also be moved
logs = glob.glob("./*.log")
'''

args = {"rename": False, "move": False, "albumart": False,
    "descriptionfile": "info.txt", "normalize": False }

def sanitize_name(name):
    """Rename something to something more sensible."""
    return re.sub("[!@#$%^&*()~`]", "", name).lower().replace(" ", "_")

def convert_process_flacs(mask="*.flac"):
    """Convert all files matching mask to flac and process at once.
    mask - the string that matches the files (default: *.flac)"""
    global args
    if args["normalize"]:
        print(subprocess.check_output("flac -V8f --replay-gain " + mask,
            shell = True))
    try:
        subprocess.check_output("metaflac --set-tag-from-file=DESCRIPTION=" +
            args["descriptionfile"] + " *.flac", shell = True)
    except subprocess.CalledProcessError:
        pass #no big deal

def ranged_input(min, max):
    input = raw_input()
    while input > max or input < min:
        print("Input error: must be between " + str(min) + " and " + str(max)
            + " inclusive")
        input = int(raw_input())
    return input

def get_cover_and_code(albums, img): #this is not so bad atm
    codes = ["Other", "32x32 pixels 'file icon' (PNG only)", "Other file icon",
        "Cover (front)", "Cover (back)", "Leaflet page",
        "Media (e.g. label side of CD)", "Lead artist/lead performer/soloist",
        "Artist/performer", "Conductor", "Band/Orchestra", "Composer",
        "Lyricist/text writer", "Recording Location", "During recording",
        "During performance", "Movie/video screen capture",
        "A bright coloured fish", "Illustration", "Band/artist logotype",
        "Publisher/Studio logotype"]
    for index, item in enumerate(albums):
        print(str(index) + ": " + item)
    print("Enter number of album with cover {0} (-1 for none):".format(img))
    album = ranged_input(-1, albums - 1)
    if(cover > -1):
        for index, item in enumerate(codes):
            print(str(index) + ": " + item)
        print("Enter description code: ")
        code = ranged_input(0, len(codes) - 1)
    return [album, code]

def add_art(imgcode, img, albums):
    """Associate img with the tracks associated with that album as shown by
    albums according to the rules in imgcode."""
        

def process():
    """Process all tracks in the current directory."""
    global args
    
    tracks = glob.glob("./*.flac") #All compatible audio files
    tracks.extend(glob.glob("./*.mp3"))
    tracks.extend(glob.glob("./*.ogg"))
    tracks.extend(glob.glob("./*.wav"))
    albums = {}

    flacs_normalized = False;
    wavs_normalized = False;
    oggs_normalized = False;

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
        try:
            if audio["album"][0] not in albums:
                albums[audio["album"][0]] = []
                print("Detected new album: " + audio["album"][0])
            albums[audio["album"][0]].append(track)
        except KeyError:
            print("This file has no album.")
        
        if suffix == ".flac":
            print("FLAC file detected")
            if flacs_normalized is False:
                print("Processing all FLAC files...")
                convert_process_flacs()
                flacs_normalized = True;
            else:
                print("FLACs already processed")
            
        if suffix == ".ogg":
            print("OGG file detected")
            if oggs_normalized is False:
                print("Processing all OGG files...")
                print(subprocess.check_output("vorbisgain -a *.ogg",
                    shell = True))
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
            print("MP3 file detected")
            if args["normalize"]: #TODO: this does not handle album norm
                print(subprocess.check_output(["lame", "--replaygain-accurate",
                track]))
                subprocess.call(["mv", track + ".mp3", track])
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

        print("")

    if args["albumart"]:
        pics = glob.glob("./*.png") #Image files
        pics.extend(glob.glob("./*.jpg"))
        pics.extend(glob.glob("./*.jpeg"))
        pics.extend(glob.glob("./*.gif"))
        print(str(len(pics)) + " images found.")
        if(len(pics) > 0):
            #Convert albums into a more useful format:
            #{"album1":["track1", "track2"], "album2":["track3"]} --->
            #[{"album1":["track1", "track2"]}, {"album2":["track3"]}]
            #We can access albums by numbers this way
            albumlist = []
            for album, tracks in albums.iteritems():
                albumlist.append({album: tracks})
            for pic in pics:
                #For each pic, associate with an album, associate with a type,
                #then tag all files with that album
                print("Image: " + pic)
                arts = get_cover_and_code(albumlist, pic)
                add_album_art(arts, pic, albums)
                
        else:
            print("No images found, cannot add album art.") #TODO: online art
        
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
    parser.add_argument("-d", "--descriptionfile", action="store",
        default="info.txt", help="Which file to use for the DESCRIPTION tag.")
    args = vars(parser.parse_args(argv))
    process()

if(__name__ == "__main__"):
    main(sys.argv[1:])