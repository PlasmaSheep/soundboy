#!/usr/bin/python2.7

"""Decide what to do, then run the relevant file."""

import sys
import autotag

def manual():
    print("Soundboy - a program to manage your music. Usage:")
    print("soundboy [command] [flags]")
    print("Commands:")
    print("import - import the files to the music library")
    sys.exit(2)

def main(argv):
    if(argv[0] == "import"):
        print("Importing")
        
    else:
        manual()

if(__name__ == "__main__"):
    main(sys.argv[1:])