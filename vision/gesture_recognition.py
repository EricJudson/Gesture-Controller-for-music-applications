"""
==========================================================
gesture_recognition.py

Professional Gesture Recognition Engine

Receives:
    Hand

Returns:
    GestureResult

Author:
    Emmanuel Judson + ChatGPT
==========================================================
"""

from __future__ import annotations

import time

from collections import deque

from vision.hand import Hand
from vision.gesture import GestureType
from vision.gesture import GestureResult

ACTION_MAP = {

    GestureType.OPEN_PALM: GestureType.PLAY,

    GestureType.CLOSED_FIST: GestureType.PAUSE,

    GestureType.PEACE: GestureType.NEXT_TRACK,

    GestureType.THREE_FINGERS: GestureType.PREVIOUS_TRACK,

    GestureType.THUMBS_UP: GestureType.VOLUME_UP,

    GestureType.THUMBS_DOWN: GestureType.VOLUME_DOWN,

    GestureType.PINCH: GestureType.PINCH

}

class GestureRecognizer:

    """
    Main gesture recognition engine.
    """

    ##########################################################
    # Constructor
    ##########################################################

    def __init__(

        self,

        history_size=7,

        cooldown=0.75,

        confidence_threshold=0.65

    ):

        # ------------------------------
        # Settings
        # ------------------------------

        self.history_size = history_size

        self.cooldown = cooldown

        self.confidence_threshold = confidence_threshold

        # ------------------------------
        # Runtime
        # ------------------------------

        self.history = deque(maxlen=history_size)

        self.last_gesture = GestureType.NONE

        self.last_time = 0

        self.last_result = GestureResult()

        self.frame_counter = 0

        self.current_result = GestureResult()
        ##########################################################
    # Main Detection
    ##########################################################

    ##########################################################
# Map Pose -> Action
##########################################################

    def _map_action(self, result: GestureResult):

        if result.gesture in ACTION_MAP:

            result.gesture = ACTION_MAP[result.gesture]

        return result

    def detect(self, hand: Hand) -> GestureResult:

        """
        Main recognition pipeline.
        """

        self.frame_counter += 1

        candidates = []

        ######################################################
        # Gesture Detectors
        ######################################################

        detectors = [

            self._detect_pinch,

            self._detect_open_palm,

            self._detect_closed_fist,

            self._detect_peace,

            self._detect_three,

            self._detect_point,

            self._detect_rock,

            self._detect_ok,

            self._detect_thumb_up,

            self._detect_thumb_down

        ]

        ######################################################
        # Evaluate all detectors
        ######################################################

        for detector in detectors:

            result = detector(hand)

            if result is not None:

                candidates.append(result)

        ######################################################
        # Nothing detected
        ######################################################

        if len(candidates) == 0:

            return GestureResult()

        ######################################################
        # Pick best confidence
        ######################################################

        best = max(

            candidates,

            key=lambda r: r.confidence

        )

        ######################################################
        # Below threshold
        ######################################################

        if best.confidence < self.confidence_threshold:

            return GestureResult()

        ######################################################
        # Copy hand information
        ######################################################

        best.hand = hand.handedness

        best.fingers = hand.fingers_up

        best.finger_count = sum(hand.fingers_up)

        best.pinch_ratio = hand.pinch_ratio

        best.pinch_distance = hand.pinch_distance

        best.center = hand.center

        best.bbox = hand.bbox

        ######################################################
        # Stabilize
        ######################################################

        best = self._stabilize(best)

        if not self._cooldown(best):
            return GestureResult()

        best = self._map_action(best)

        self.last_result = best

        return best
        ##########################################################
    # Utility
    ##########################################################

    def _result(

        self,

        gesture,

        confidence

    ):

        result = GestureResult()

        result.gesture = gesture

        result.confidence = confidence

        return result
    ##########################################################
# Utility
##########################################################

    def _finger_match(
        self,
        hand: Hand,
        pattern: list[bool]
    ) -> float:
        """
        Compares current finger state against a pattern.

        Returns
        -------
        confidence : float (0.0 - 1.0)
        """

        score = 0

        for actual, expected in zip(hand.fingers_up, pattern):

            if actual == expected:
                score += 1

        return score / 5.0
    ##########################################################
# Open Palm
##########################################################

    def _detect_open_palm(
        self,
        hand: Hand
    ):

        confidence = self._finger_match(

            hand,

            [True, True, True, True, True]

        )

        if confidence < 0.80:
            return None

        return self._result(

            GestureType.OPEN_PALM,

            confidence

        )
        ##########################################################
    # Closed Fist
    ##########################################################

    def _detect_closed_fist(
        self,
        hand: Hand
    ):

        confidence = self._finger_match(

            hand,

            [False, False, False, False, False]

        )

        if confidence < 0.80:
            return None

        return self._result(

            GestureType.CLOSED_FIST,

            confidence

        )
    ##########################################################
# Peace Sign
##########################################################

    def _detect_peace(
        self,
        hand: Hand
    ):

        confidence = self._finger_match(

            hand,

            [False, True, True, False, False]

        )

        if confidence < 0.80:
            return None

        return self._result(

            GestureType.PEACE,

            confidence

        )
    ##########################################################
# Three Fingers
##########################################################

    def _detect_three(
        self,
        hand: Hand
    ):

        confidence = self._finger_match(

            hand,

            [False, True, True, True, False]

        )

        if confidence < 0.80:
            return None

        return self._result(

            GestureType.THREE_FINGERS,

            confidence

        )
    ##########################################################
# Finger Count
##########################################################

    def finger_count(
        self,
        hand: Hand
    ):

        return sum(hand.fingers_up)
    ##########################################################
# Pinch
##########################################################

    def _detect_pinch(
        self,
        hand: Hand
    ):

        ratio = hand.pinch_ratio

        if ratio > 0.35:
            return None

        confidence = 1.0 - (ratio / 0.35)

        confidence = max(0.0, min(confidence, 1.0))

        return self._result(

            GestureType.PINCH,

            confidence

        )
    ##########################################################
# Thumb Up
##########################################################

    def _detect_thumb_up(
        self,
        hand: Hand
    ):

        if hand.fingers_up != [True, False, False, False, False]:
            return None

        thumb = hand.landmark(4)

        wrist = hand.landmark(0)

        if thumb.y > wrist.y:
            return None

        return self._result(

            GestureType.THUMBS_UP,

            0.90

        )
    ##########################################################
# Thumb Down
##########################################################

    def _detect_thumb_down(
        self,
        hand: Hand
    ):

        if hand.fingers_up != [True, False, False, False, False]:
            return None

        thumb = hand.landmark(4)

        wrist = hand.landmark(0)

        if thumb.y < wrist.y:
            return None

        return self._result(

            GestureType.THUMBS_DOWN,

            0.90

        )
    ##########################################################
# Point
##########################################################

    def _detect_point(
        self,
        hand: Hand
    ):

        confidence = self._finger_match(

            hand,

            [False, True, False, False, False]

        )

        if confidence < 0.80:
            return None

        return self._result(

            GestureType.POINT,

            confidence

        )
    ##########################################################
    # Rock
    ##########################################################

    def _detect_rock(
        self,
        hand: Hand
    ):

        confidence = self._finger_match(

            hand,

            [False, True, False, False, True]

        )

        if confidence < 0.80:
            return None

        return self._result(

            GestureType.ROCK,

            confidence

        )
    ##########################################################
    # OK
    ##########################################################

    def _detect_ok(
        self,
        hand: Hand
    ):

        if hand.distance(4, 8) > 35:
            return None

        if hand.fingers_up[2:] != [True, True, True]:
            return None

        return self._result(

            GestureType.OK,

            0.95

        )
    ##########################################################
# Stabilization
##########################################################

    def _stabilize(
        self,
        result: GestureResult
    ):

        self.history.append(result)

        if len(self.history) < self.history_size:

            result.stable = False
            return result

        ######################################################
        # Check whether all gestures match
        ######################################################

        gesture = self.history[0].gesture

        for item in self.history:

            if item.gesture != gesture:

                result.stable = False
                return result

        ######################################################
        # Average confidence
        ######################################################

        avg_conf = sum(

            item.confidence

            for item in self.history

        ) / len(self.history)

        stable = GestureResult(

            gesture=result.gesture,

            confidence=avg_conf,

            hand=result.hand,

            fingers=result.fingers,

            finger_count=result.finger_count,

            pinch_ratio=result.pinch_ratio,

            pinch_distance=result.pinch_distance,

            bbox=result.bbox,

            center=result.center,

            stable=True

        )

        return stable
    ##########################################################
    # Cooldown
    ##########################################################

    def _cooldown(
        self,
        result: GestureResult
    ):

        if not result.stable:

            return False

        now = time.time()

        ######################################################
        # Same gesture still inside cooldown
        ######################################################

        if (

            result.gesture == self.last_gesture

            and

            now - self.last_time < self.cooldown

        ):

            return False

        ######################################################
        # Update timer
        ######################################################

        self.last_time = now

        self.last_gesture = result.gesture

        return True
    ##########################################################
    # Reset
    ##########################################################

    def reset(self):

        self.history.clear()

        self.last_gesture = GestureType.NONE

        self.last_result = GestureResult()

        self.frame_counter = 0

        self.current_result = GestureResult()

        self.last_time = 0
        def last(self):

            return self.last_result
    ##########################################################
    # Debug
    ##########################################################

    def debug(self):

        result = self.last_result

        print()

        print("-----------------------------")

        print("Gesture :", result.gesture.name)

        print("Confidence :", round(result.confidence,2))

        print("Stable :", result.stable)

        print("Hand :", result.hand)

        print("Finger Count :", result.finger_count)

        print("Pinch :", round(result.pinch_ratio,2))

        print("-----------------------------")
    ##########################################################
    # String
    ##########################################################

    def __str__(self):

        return (

            f"GestureRecognizer("

            f"history={len(self.history)}, "

            f"last={self.last_gesture.name})"

        )


