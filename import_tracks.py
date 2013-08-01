"""Handle importation of files."""

import glob
import argparse
from metadata import MusicFile
import shutil
import os
import re
import filecmp
from unidecode import unidecode

conf = {}
args = {}

def sanitize(name):
    """Rename something to something more sensible."""
    name = unidecode(name) #Unicode filenames are such a bad idea
    print conf["rename-mask"]
    return re.sub("[/^[:ascii:]#]", "", name).replace(" ", "_")
    #TODO: make it fix non-ascii characters

def get_files():
    files = {}
    root = args["dir"]
    files["tracks"] = glob.glob(root + u"/*.flac") #All compatible audio files
    files["tracks"].extend(glob.glob(root + u"/*.mp3"))
    files["tracks"].extend(glob.glob(root + u"/*.ogg"))
    files["tracks"].extend(glob.glob(root + u"/*.wav"))
    files["tracks"].extend(glob.glob(root + u"/*.m4a"))
    
    if args["cue"] == True:
        files["cue"] = glob.glob(root + u"/*.cue")

    if args["log"] == True:
        files["log"] = glob.glob(root + u"/*.log")

    return files

def get_path(track):
    """Get the artist/album format path for this particular track"""
    info = MusicFile(track)
    art = sanitize(info.get_artist())
    alb = sanitize(info.get_album())
    return art + "/" + alb

def get_albums(tracks):
    """Associate each album with a path leading to the directory with the
    tracks in the album."""
    albums = {}
    for track in tracks:
        print track
        info = MusicFile(track)
        if info.get_album() not in albums:
            albums[info.get_album()] = []
            albums[info.get_album()] = get_path(track)
    return albums

def move_track(track):
    info = MusicFile(track)
    path = get_path(track)
    name = sanitize(info.get_title()) + info.suffix
    if not os.path.exists(root + path):
        os.makedirs(root + path)
    print "Rename: " + track + " to " + name
    os.rename(track, name)
    try:
        print "Moving " + name + " into " + root + path
        shutil.move(name, root + path)
    except shutil.Error:
        print "Looks like that file already exists. Comparing..."
        d = filecmp.cmp(name, root + art + "/" + path)
        if d:
            print "Files are identical. Deleting this copy..."
            os.remove(name)
        else:
            print "Files are different. Leaving it alone."

def main(argv, config):
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
    argv = vars(parser.parse_args(argv))

    global conf, args
    conf = config
    args = argv

    files = get_files()
    albums = get_albums(files["tracks"])

    #for track in files["tracks"]:
        #We temporarily organize tracks into a hierarchy at the present
        #directory so that we can have proper album replay data.
        #move_track(track)
    
    print albums
    """print files
    for track in files["tracks"]:
        move_track(track, config["dir"])
    #albs = get_albums(files["tracks"])"""
    