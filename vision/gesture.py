from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import List
import time


# ============================================================
# Gesture Enum
# ============================================================

class GestureType(Enum):

    # --------------------------------------------------------
    # No Gesture
    # --------------------------------------------------------

    NONE = auto()

    # --------------------------------------------------------
    # Playback
    # --------------------------------------------------------

    PLAY = auto()

    PAUSE = auto()

    TOGGLE_PLAY_PAUSE = auto()

    NEXT_TRACK = auto()

    PREVIOUS_TRACK = auto()

    STOP = auto()

    # --------------------------------------------------------
    # Volume
    # --------------------------------------------------------

    VOLUME_UP = auto()

    VOLUME_DOWN = auto()

    PINCH = auto()

    MUTE = auto()

    # --------------------------------------------------------
    # Static Hand Gestures
    # --------------------------------------------------------

    OPEN_PALM = auto()

    CLOSED_FIST = auto()

    PEACE = auto()

    THREE_FINGERS = auto()

    POINT = auto()

    THUMBS_UP = auto()

    THUMBS_DOWN = auto()

    ROCK = auto()

    OK = auto()

    # --------------------------------------------------------
    # Motion Gestures
    # --------------------------------------------------------

    SWIPE_LEFT = auto()

    SWIPE_RIGHT = auto()

    SWIPE_UP = auto()

    SWIPE_DOWN = auto()

    ROTATE_CLOCKWISE = auto()

    ROTATE_COUNTERCLOCKWISE = auto()

    HOLD = auto()

    # --------------------------------------------------------
    # Spotify Specific
    # --------------------------------------------------------

    LIKE_TRACK = auto()

    SHUFFLE = auto()

    REPEAT = auto()
    # ============================================================
# Gesture Result
# ============================================================

@dataclass(slots=True)
class GestureResult:

    # Final detected gesture
    gesture: GestureType = GestureType.NONE

    # Confidence (0-1)
    confidence: float = 0.0

    # Left / Right
    hand: str = ""

    # [Thumb,Index,Middle,Ring,Pinky]
    fingers: List[bool] = field(default_factory=list)

    finger_count: int = 0

    # Distance between thumb/index normalized by palm width
    pinch_ratio: float = 0.0

    # Raw pinch distance in pixels
    pinch_distance: float = 0.0

    # Bounding box
    bbox: tuple = (0, 0, 0, 0)

    # Palm center
    center: tuple = (0, 0)

    # Is this gesture stable?
    stable: bool = False

    # Timestamp
    timestamp: float = field(default_factory=time.time)

    ##########################################################

    def is_valid(self):

        return self.gesture != GestureType.NONE

    ##########################################################

    def reset(self):

        self.gesture = GestureType.NONE
        self.confidence = 0
        self.stable = False
    # ============================================================
# Helper Functions
# ============================================================

def gesture_name(gesture: GestureType):

    return gesture.name.replace("_", " ").title()


def gesture_icon(gesture: GestureType):

    icons = {

        GestureType.NONE: "",

        GestureType.PLAY: "▶",

        GestureType.PAUSE: "⏸",

        GestureType.NEXT_TRACK: "⏭",

        GestureType.PREVIOUS_TRACK: "⏮",

        GestureType.VOLUME_UP: "🔊",

        GestureType.VOLUME_DOWN: "🔉",

        GestureType.PINCH: "🤏",

        GestureType.OPEN_PALM: "🖐",

        GestureType.CLOSED_FIST: "✊",

        GestureType.PEACE: "✌",

        GestureType.THREE_FINGERS: "🖖",

        GestureType.THUMBS_UP: "👍",

        GestureType.THUMBS_DOWN: "👎",

        GestureType.ROCK: "🤘",

        GestureType.OK: "👌",

        GestureType.POINT: "☝"

    }

    return icons.get(gesture, "")
# ============================================================
# Debug String
# ============================================================

def gesture_description(result: GestureResult):

    return (

        f"{gesture_icon(result.gesture)} "

        f"{gesture_name(result.gesture)} | "

        f"Confidence={result.confidence:.2f} | "

        f"Hand={result.hand} | "

        f"Fingers={result.finger_count} | "

        f"Pinch={result.pinch_ratio:.2f}"

    )
