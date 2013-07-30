"""Handle metadata for files"""
from mutagen.id3 import ID3
from mutagen.flac import FLAC
from mutagen.oggvorbis import OggVorbis
from mutagen.mp4 import MP4
import mimetypes

class MusicFile:
    def __init__(self, track):
        self.track = track
        self.suffix = mimetypes.guess_extension(mimetypes.guess_type(track)[0])
        self.suffix = track[-4:] #HACK
        
    def get_album(self):
        if self.suffix == ".mp3" and len(ID3(self.track).getall("TALB")) > 0:
            return ID3(self.track).getall("TALB")[0][0]
        elif self.suffix == ".flac" and len(FLAC(self.track)["album"]) > 0:
            return FLAC(self.track)["album"][0]
        elif self.suffix == ".ogg" and len(OggVorbis(self.track)["album"]) > 0:
            return OggVorbis(self.track)["album"][0]
        elif self.suffix == ".m4a" and len(MP4(self.track)["\xa9alb"]) > 0:
            return MP4(self.track)["\xa9alb"][0] #ewwww
        else:
            return "Unknown"

    def get_artist(self):
        if self.suffix == ".mp3" and len(ID3(self.track).getall("TPE1")) > 0:
            return ID3(self.track).getall("TPE1")[0][0]
        elif self.suffix == ".flac" and len(FLAC(self.track)["artist"]) > 0:
            return FLAC(self.track)["artist"][0]
        elif self.suffix == ".ogg" and len(OggVorbis(self.track)["artist"]) > 0:
            return OggVorbis(self.track)["artist"][0]
        elif self.suffix == ".m4a" and len(MP4(self.track)["\xa9ART"]):
            return MP4(self.track)["\xa9ART"][0] #ewwww
        else:
            return "Unknown"

    def get_title(self):
        if self.suffix == ".mp3" and len(ID3(self.track).getall("TIT2")) > 0:
            return ID3(self.track).getall("TIT2")[0][0]
        elif self.suffix == ".flac" and len(FLAC(self.track)["artist"]) > 0:
            return FLAC(self.track)["artist"][0]
        elif self.suffix == ".ogg" and len(OggVorbis(self.track)["artist"]) > 0:
            return OggVorbis(self.track)["artist"][0]
        elif self.suffix == ".m4a" and len(MP4(self.track)["\xa9nam"]):
            return MP4(self.track)["\xa9nam"][0] #ewwww
        else:
            return "Unknown"