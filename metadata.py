"""Handle metadata for files"""
from mutagen import ID3
import mimetypes

class MusicFile:
    def __init__(self, track):
        self.track = track
        self.suffix = mimetypes.guess_extension(mimetypes.guess_type(track)[0])
        
    def get_album():
        if(self.suffix == ".mp3"):
            return ID3(self.track).getall("TALB")[0][0]