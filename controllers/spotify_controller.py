"""
==========================================================
spotify_controller.py

Spotify Controller

Supports:

• Windows Media Keys
• Spotify Desktop
• Future Spotify API integration

==========================================================
"""

from __future__ import annotations

import keyboard

from vision.gesture import GestureType


class SpotifyController:

    def __init__(self):

        self.enabled = True

    # ##########################################################
    # # Play
    # ##########################################################

    def play(self):

        keyboard.send("play/pause media")

    ##########################################################
    # Pause
    ##########################################################

    def pause(self):

        keyboard.send("play/pause media")

    ##########################################################
    # Toggle
    ##########################################################

    def toggle(self):

        keyboard.send("play/pause media")

    ##########################################################
    # Next
    ##########################################################

    def next_track(self):

        keyboard.send("next track")

    ##########################################################
    # Previous
    ##########################################################

    def previous_track(self):

        keyboard.send("previous track")

    ##########################################################
    # Stop
    ##########################################################

    def stop(self):

        keyboard.send("stop media")
        ##########################################################
    # Execute Action
    ##########################################################

    def execute(self, gesture: GestureType):

        if not self.enabled:
            return

        if gesture == GestureType.PLAY:

            self.play()

        elif gesture == GestureType.PAUSE:

            self.pause()

        elif gesture == GestureType.TOGGLE_PLAY_PAUSE:

            self.toggle()

        elif gesture == GestureType.NEXT_TRACK:

            self.next_track()

        elif gesture == GestureType.PREVIOUS_TRACK:

            self.previous_track()

        elif gesture == GestureType.STOP:

            self.stop()
        ##########################################################
    # Enable
    ##########################################################

    def enable(self):

        self.enabled = True

    ##########################################################
    # Disable
    ##########################################################

    def disable(self):

        self.enabled = False

    ##########################################################
    # Status
    ##########################################################

    def is_enabled(self):

        return self.enabled

    ##########################################################
    # String
    ##########################################################

    def __str__(self):

        return f"SpotifyController(enabled={self.enabled})"
    