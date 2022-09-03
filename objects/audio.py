from playsound import playsound

from threading import Thread

from path import path_to


def play_track(track):
    if track is None:
        return

    Thread(target=playsound, args=[path_to("configs", "tracks", track)], daemon=True).start()
