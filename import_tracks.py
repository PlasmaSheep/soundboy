"""Handle importation of files."""

import glob
import argparse
from metadata import MusicFile
import shutil
import os
import re
import filecmp

def sanitize(name):
    """Rename something to something more sensible."""
    return re.sub("[/^[:ascii:]#]", "", name).replace(" ", "_")
    #TODO: make it fix non-ascii characters

def get_files(args):
    files = {}
    root = args["dir"]
    files["tracks"] = glob.glob(root + "/*.flac") #All compatible audio files
    files["tracks"].extend(glob.glob(root + "/*.mp3"))
    files["tracks"].extend(glob.glob(root + "/*.ogg"))
    files["tracks"].extend(glob.glob(root + "/*.wav"))
    files["tracks"].extend(glob.glob(root + "/*.m4a"))
    
    if args["cue"] == True:
        files["cue"] = glob.glob(root + "/*.cue")

    if args["log"] == True:
        files["log"] = glob.glob(root + "/*.log")

    return files

def get_albums(tracks):
    albums = {}
    for track in tracks:
        print track
        info = MusicFile(track)
        if info.get_album() not in albums:
            albums[info.get_album()] = []
        albums[info.get_album()].append(track)
    return albums

def move_track(track, root):
    info = MusicFile(track)
    art = sanitize(info.get_artist())
    alb = sanitize(info.get_album())
    name = sanitize(info.get_title()) + info.suffix
    if not os.path.exists(root + art + "/" + alb):
        os.makedirs(root + art + "/" + alb)
    print "Rename: " + track + " to " + name
    os.rename(track, name)
    try:
        print "Moving " + name + " into " + root + art + "/" + alb
        shutil.move(name, root + art + "/" + alb)
    except shutil.Error:
        print "Looks like that file already exists. Comparing..."
        d = filecmp.cmp(name, root + art + "/" + alb + "/" + name)
        if d:
            print "Files are identical. Deleting this copy..."
            os.remove(name)
        else:
            print "Files are different. Leaving it alone."

def main(args, config):
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
    parser.add_argument("-c", "--cue", action="store_true",
        help="Process cue files (move them, rename tracks if necessary).")
    parser.add_argument("-l", "--log", action="store_true",
        help="Move log files along with tracks (only applies if -m is set).")
    parser.add_argument('dir', action="store", default="./",
        help="Which directory to process (default %(default)s)", nargs="?")
    args = vars(parser.parse_args(args))

    """files = get_files(args)
    print files
    for track in files["tracks"]:
        move_track(track, config["dir"])
    #albs = get_albums(files["tracks"])"""
    