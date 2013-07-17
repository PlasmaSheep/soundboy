"""Handle importation of files."""

import glob
import argparse
from metadata import MusicFile

def get_files(args):
    files = {}
    files["tracks"] = glob.glob("./*.flac") #All compatible audio files
    files["tracks"].extend(glob.glob("./*.mp3"))
    files["tracks"].extend(glob.glob("./*.ogg"))
    files["tracks"].extend(glob.glob("./*.wav"))
    
    if args["cue"] == True:
        files["cue"] = glob.glob("./*.cue")

    if args["log"] == True:
        files["log"] = glob.glob("./*.log")

    return files

def get_albums(tracks):
    albums = {}
    for track in tracks:
        info = MusicFile(track)
        if info.get_album() not in albums:
            albums[info.get_album()] = []
        albums[info.get_album()].append(track)
    return albums
        

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
    args = vars(parser.parse_args(args))

    files = get_files(args)
    albs = get_albums(files["tracks"])
    