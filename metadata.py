"""Handle metadata for files"""
from mutagen.id3 import ID3
from mutagen.flac import FLAC
from mutagen.oggvorbis import OggVorbis
import mimetypes

class MusicFile:
    def __init__(self, track):
        self.track = track
        self.suffix = mimetypes.guess_extension(mimetypes.guess_type(track)[0])
        
    def get_album(self):
        if(self.suffix == ".mp3"):
            return ID3(self.track).getall("TALB")[0][0]
        if(self.suffix == ".flac"):
            return FLAC(self.track)["album"][0]
        if(self.suffix == ".ogg"):
            return OggVorbis(self.track)["album"][0]
        