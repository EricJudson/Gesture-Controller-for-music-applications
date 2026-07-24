"""
===========================================================
Hand Object

Stores all information about one detected hand.

Every frame, HandDetector returns one or more Hand objects.
GestureRecognizer works ONLY with this class.
===========================================================
"""

from dataclasses import dataclass, field
from typing import List, Tuple
import math


# ----------------------------------------------------------
# One landmark
# ----------------------------------------------------------

@dataclass
class Landmark:

    id: int

    x: int
    y: int

    nx: float
    ny: float
    nz: float


# ----------------------------------------------------------
# Hand
# ----------------------------------------------------------

@dataclass
class Hand:

    handedness: str

    landmarks: List[Landmark] = field(default_factory=list)

    bbox: Tuple[int, int, int, int] = (0, 0, 0, 0)

    center: Tuple[int, int] = (0, 0)

    confidence: float = 0.0

    fingers_up: List[bool] = field(default_factory=list)

    raw_landmarks: object = None

    ##########################################################
    # Return landmark
    ##########################################################

    def landmark(self, idx):

        return self.landmarks[idx]

    ##########################################################
    # Pixel Distance
    ##########################################################

    def distance(self, id1, id2):

        p1 = self.landmarks[id1]

        p2 = self.landmarks[id2]

        return math.hypot(
            p2.x - p1.x,
            p2.y - p1.y
        )

    ##########################################################
    # Midpoint
    ##########################################################

    def midpoint(self, id1, id2):

        p1 = self.landmarks[id1]

        p2 = self.landmarks[id2]

        return (
            (p1.x + p2.x) // 2,
            (p1.y + p2.y) // 2
        )

    ##########################################################
    # Vector
    ##########################################################

    def vector(self, id1, id2):

        p1 = self.landmarks[id1]

        p2 = self.landmarks[id2]

        return (

            p2.x - p1.x,

            p2.y - p1.y

        )

    ##########################################################
    # Angle
    ##########################################################

    def angle(self, a, b, c):

        """
        Returns angle ABC
        """

        pa = self.landmarks[a]

        pb = self.landmarks[b]

        pc = self.landmarks[c]

        ba = (

            pa.x - pb.x,

            pa.y - pb.y

        )

        bc = (

            pc.x - pb.x,

            pc.y - pb.y

        )

        dot = ba[0] * bc[0] + ba[1] * bc[1]

        mag1 = math.hypot(ba[0], ba[1])

        mag2 = math.hypot(bc[0], bc[1])

        if mag1 == 0 or mag2 == 0:
            return 0

        cosine = max(-1, min(1, dot / (mag1 * mag2)))

        return math.degrees(math.acos(cosine))

    ##########################################################
    # Bounding Box Area
    ##########################################################

    @property
    def area(self):

        _, _, w, h = self.bbox

        return w * h

    ##########################################################
    # Pinch Distance
    ##########################################################

    @property
    def pinch_distance(self):

        return self.distance(4, 8)

    ##########################################################
    # Palm Width
    ##########################################################

    @property
    def palm_width(self):

        return self.distance(5, 17)

    ##########################################################
    # Palm Height
    ##########################################################

    @property
    def palm_height(self):

        return self.distance(0, 9)

    ##########################################################
    # Pinch Ratio
    ##########################################################

    @property
    def pinch_ratio(self):

        width = self.palm_width

        if width == 0:
            return 0

        return self.pinch_distance / width

    ##########################################################
    # Open Percentage
    ##########################################################

    @property
    def openness(self):

        return sum(self.fingers_up) / 5.0
    
    

    ##########################################################
    # Dictionary
    ##########################################################

    def to_dict(self):

        return {

            "handedness": self.handedness,

            "bbox": self.bbox,

            "center": self.center,

            "confidence": self.confidence,

            "pinch_distance": self.pinch_distance,

            "pinch_ratio": self.pinch_ratio,

            "fingers": self.fingers_up

        }

    ##########################################################
    # String
    ##########################################################

    def __str__(self):

        return (

            f"Hand("
            f"{self.handedness}, "
            f"center={self.center}, "
            f"pinch={self.pinch_distance:.1f})"

        )