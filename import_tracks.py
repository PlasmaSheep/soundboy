"""Handle importation of music files."""

import glob
import argparse

def get_files(args):
    files = {}
    files["tracks"] = glob.glob("./*.flac") #All compatible audio files
    files["tracks"].extend(glob.glob("./*.mp3"))
    files["tracks"].extend(glob.glob("./*.ogg"))
    files["tracks"].extend(glob.glob("./*.wav"))

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
    args = vars(parser.parse_args(args))

    files = get_files(args)
    