#! /usr/bin/python2.7

#Things this program should do
# Convert to format by command line
# Move files to appropriate directory.
# Preserve metadata!

import subprocess;
import mimetypes;

def convert_file(uri, new_type):
    if mimetypes.guess_extension(uri) != "wav":
        print subprocess.check_call(
    if new_type = "flac":
        print subprocess.check_call(["flac", "-