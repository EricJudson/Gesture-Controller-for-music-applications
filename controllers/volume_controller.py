"""
==========================================================
volume_controller.py

Windows Volume Controller

Uses:
    pycaw

Supports:
    • Get volume
    • Set volume
    • Volume %
    • Mute
    • Pinch Volume

==========================================================
"""

from __future__ import annotations

from ctypes import POINTER, cast

from comtypes import CLSCTX_ALL

from pycaw.pycaw import AudioUtilities
from pycaw.pycaw import IAudioEndpointVolume

from vision.gesture import GestureType


class VolumeController:

    ##########################################################
    # Constructor
    ##########################################################

    def __init__(self):

        self.enabled = True

        ######################################################
        # Get Speakers
        ######################################################

        devices = AudioUtilities.GetSpeakers()

        interface = devices.Activate(

            IAudioEndpointVolume._iid_,

            CLSCTX_ALL,

            None

        )

        self.volume = cast(

            interface,

            POINTER(IAudioEndpointVolume)

        )

        ######################################################
        # Volume Range
        ######################################################

        self.min_db, self.max_db, self.step = (

            self.volume.GetVolumeRange()

        )

        ######################################################
        # Cache
        ######################################################

        self.last_percent = self.get_volume_percent()
        ##########################################################
    # Get Raw dB
    ##########################################################

    def get_volume_db(self):

        return self.volume.GetMasterVolumeLevel()

    ##########################################################
    # Set Raw dB
    ##########################################################

    def set_volume_db(self, db):

        db = max(

            self.min_db,

            min(

                self.max_db,

                db

            )

        )

        self.volume.SetMasterVolumeLevel(

            db,

            None

        )

        self.last_percent = self.get_volume_percent()
        ##########################################################
    # Get Volume Percentage
    ##########################################################

    def get_volume_percent(self):

        db = self.get_volume_db()

        percent = (

            (db - self.min_db)

            /

            (self.max_db - self.min_db)

        )

        return int(percent * 100)

    ##########################################################
    # Set Volume Percentage
    ##########################################################

    def set_volume_percent(

        self,

        percent

    ):

        percent = max(

            0,

            min(

                100,

                percent

            )

        )

        db = (

            self.min_db

            +

            (

                percent / 100

            )

            *

            (

                self.max_db

                -

                self.min_db

            )

        )

        self.set_volume_db(db)
        ##########################################################
    # Minimum
    ##########################################################

    def minimum(self):

        self.set_volume_db(

            self.min_db

        )

    ##########################################################
    # Maximum
    ##########################################################

    def maximum(self):

        self.set_volume_db(

            self.max_db

        )

    ##########################################################
    # Current Volume
    ##########################################################

    @property
    def percent(self):

        return self.get_volume_percent()
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
    # Enabled?
    ##########################################################

    def is_enabled(self):

        return self.enabled
        ##########################################################
    # Increase Volume
    ##########################################################

    def increase(self, step=5):

        if not self.enabled:
            return

        self.set_volume_percent(

            self.percent + step

        )

    ##########################################################
    # Decrease Volume
    ##########################################################

    def decrease(self, step=5):

        if not self.enabled:
            return

        self.set_volume_percent(

            self.percent - step

        )
        ##########################################################
    # Mute
    ##########################################################

    def mute(self):

        self.volume.SetMute(

            1,

            None

        )

    ##########################################################
    # Unmute
    ##########################################################

    def unmute(self):

        self.volume.SetMute(

            0,

            None

        )

    ##########################################################
    # Toggle Mute
    ##########################################################

    def toggle_mute(self):

        muted = self.volume.GetMute()

        self.volume.SetMute(

            int(not muted),

            None

        )

    ##########################################################
    # Is Muted
    ##########################################################

    def is_muted(self):

        return bool(

            self.volume.GetMute()

        )
        ##########################################################
    # Pinch To Volume
    ##########################################################

    def pinch_to_volume(

        self,

        pinch_ratio,

        minimum=0.15,

        maximum=0.80

    ):

        if not self.enabled:
            return

        pinch_ratio = max(

            minimum,

            min(

                maximum,

                pinch_ratio

            )

        )

        # Convert pinch ratio to a target volume percentage
        target_percent = (
            (pinch_ratio - minimum)
            /
            (maximum - minimum)
        ) * 100

        # Clamp to valid range
        target_percent = max(0, min(100, target_percent))

        # Current system volume
        current_percent = self.percent

        # Exponential smoothing (0.2 = smoothing factor)
        smoothed_percent = current_percent + (
            target_percent - current_percent
        ) * 0.2

        self.set_volume_percent(int(smoothed_percent))
        ##########################################################
    # Execute Gesture
    ##########################################################

    def execute(

        self,

        gesture,

        pinch_ratio=None

    ):

        if not self.enabled:
            return

        if gesture == GestureType.VOLUME_UP:

            self.increase()

        elif gesture == GestureType.VOLUME_DOWN:

            self.decrease()

        elif gesture == GestureType.MUTE:

            self.toggle_mute()

        elif gesture == GestureType.PINCH:

            if pinch_ratio is not None:

                self.pinch_to_volume(

                    pinch_ratio

                )