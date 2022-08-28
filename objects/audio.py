import os
from playsound import playsound

from threading import Thread


def play_track(track):
    if track is None:
        return

    Thread(target=playsound, args=[os.path.join("configs", "tracks", track)], daemon=True).start()
