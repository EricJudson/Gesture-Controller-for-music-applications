"""
=========================================================
Gesture Spotify Controller
Configuration File

Modify these values to tune the application's behaviour.
=========================================================
"""

# --------------------------------------------------------
# CAMERA SETTINGS
# --------------------------------------------------------

CAMERA_INDEX = 0

FRAME_WIDTH = 1280
FRAME_HEIGHT = 720

FLIP_CAMERA = True


# --------------------------------------------------------
# MEDIAPIPE SETTINGS
# --------------------------------------------------------

MAX_NUM_HANDS = 1

DETECTION_CONFIDENCE = 0.75

TRACKING_CONFIDENCE = 0.75


# --------------------------------------------------------
# GESTURE SETTINGS
# --------------------------------------------------------

# Time (seconds) before another gesture can be executed
GESTURE_COOLDOWN = 1.0

# Number of frames required before confirming a gesture
GESTURE_STABILITY_FRAMES = 8


# --------------------------------------------------------
# PINCH VOLUME CONTROL
# --------------------------------------------------------

# Distance (pixels) between thumb and index finger

PINCH_MIN_DISTANCE = 25

PINCH_MAX_DISTANCE = 220

SMOOTHING_FACTOR = 5


# --------------------------------------------------------
# UI SETTINGS
# --------------------------------------------------------

SHOW_FPS = True

SHOW_LANDMARKS = True

SHOW_GESTURE_NAME = True

SHOW_VOLUME_BAR = True

FONT_SCALE = 1

FONT_THICKNESS = 2


# --------------------------------------------------------
# COLORS (BGR)
# --------------------------------------------------------

GREEN = (0, 255, 0)

RED = (0, 0, 255)

BLUE = (255, 0, 0)

WHITE = (255, 255, 255)

YELLOW = (0, 255, 255)

CYAN = (255, 255, 0)

MAGENTA = (255, 0, 255)

BLACK = (0, 0, 0)


# --------------------------------------------------------
# VOLUME BAR
# --------------------------------------------------------

BAR_X = 50

BAR_Y = 150

BAR_WIDTH = 30

BAR_HEIGHT = 300


# --------------------------------------------------------
# WINDOW
# --------------------------------------------------------

WINDOW_NAME = "Gesture Spotify Controller"


# --------------------------------------------------------
# GESTURE LABELS
# --------------------------------------------------------

GESTURES = {
    "PLAY": "▶ PLAY",
    "PAUSE": "⏸ PAUSE",
    "NEXT": "⏭ NEXT",
    "PREVIOUS": "⏮ PREVIOUS",
    "VOLUME": "🔊 VOLUME",
    "NONE": ""
}