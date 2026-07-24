"""
=============================================================
hand_detector.py

Professional Hand Detector
Author : ChatGPT + Emmanuel Judson

Uses MediaPipe Hands to detect:

• Handedness
• 21 Landmarks
• Bounding Box
• Palm Center
• Finger States
• Pinch Distance

Returns Hand objects instead of raw landmark arrays.
=============================================================
"""

from __future__ import annotations

import cv2
import mediapipe as mp

from typing import List
from typing import Optional

import config

from vision.hand import Hand
from vision.hand import Landmark


class HandDetector:

    """
    Wrapper around MediaPipe Hands.

    Every frame:

        image
          ↓
      MediaPipe
          ↓
      Hand Objects
    """

    def __init__(

        self,

        static_mode=False,

        max_hands=config.MAX_NUM_HANDS,

        detection_confidence=config.DETECTION_CONFIDENCE,

        tracking_confidence=config.TRACKING_CONFIDENCE

    ):

        self.static_mode = static_mode

        self.max_hands = max_hands

        self.detection_confidence = detection_confidence

        self.tracking_confidence = tracking_confidence

        ####################################################
        # MediaPipe
        ####################################################

        self.mp_hands = mp.solutions.hands

        self.mp_draw = mp.solutions.drawing_utils

        self.mp_styles = mp.solutions.drawing_styles

        self.hands = self.mp_hands.Hands(

            static_image_mode=self.static_mode,

            max_num_hands=self.max_hands,

            min_detection_confidence=self.detection_confidence,

            min_tracking_confidence=self.tracking_confidence

        )

        ####################################################
        # Results
        ####################################################

        self.results = None

        self.image_width = 0

        self.image_height = 0

    #########################################################
    # Detect
    #########################################################

    def detect(self, frame):

        """
        Detect hands.

        Parameters
        ----------

        frame : BGR image

        Returns
        -------

        list[Hand]
        """

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        self.image_height, self.image_width = frame.shape[:2]

        self.results = self.hands.process(rgb)

        hands = []

        if self.results.multi_hand_landmarks is None:

            return hands

        handedness_list = self.results.multi_handedness

        landmark_list = self.results.multi_hand_landmarks

        ####################################################
        # Iterate over every detected hand
        ####################################################

        for hand_index in range(len(landmark_list)):

            hand_landmarks = landmark_list[hand_index]

            handedness = handedness_list[hand_index]

            hand = self._create_hand(

                hand_landmarks,

                handedness

            )

            hand.raw_landmarks = hand_landmarks
            hands.append(hand)

        return hands
        #########################################################
    # Create Hand Object
    #########################################################

    def _create_hand(

        self,

        hand_landmarks,

        handedness

    ) -> Hand:

        label = handedness.classification[0].label

        confidence = handedness.classification[0].score

        landmarks = []

        xs = []

        ys = []

        ####################################################
        # Convert MediaPipe landmarks
        ####################################################

        for idx, lm in enumerate(hand_landmarks.landmark):

            px = int(lm.x * self.image_width)

            py = int(lm.y * self.image_height)

            xs.append(px)

            ys.append(py)

            landmarks.append(

                Landmark(

                    id=idx,

                    x=px,

                    y=py,

                    nx=lm.x,

                    ny=lm.y,

                    nz=lm.z

                )

            )

        ####################################################
        # Bounding Box
        ####################################################

        xmin = min(xs)
        xmax = max(xs)

        ymin = min(ys)
        ymax = max(ys)

        width = xmax - xmin
        height = ymax - ymin

        bbox = (

            xmin,

            ymin,

            width,

            height

        )

        ####################################################
        # Center
        ####################################################

        center = (

            xmin + width // 2,

            ymin + height // 2

        )

        ####################################################
        # Build Hand Object
        ####################################################

        hand = Hand(

            handedness=label,

            landmarks=landmarks,

            bbox=bbox,

            center=center,

            confidence=confidence

        )

        ####################################################
        # Calculate fingers immediately
        ####################################################

        hand.fingers_up = self._calculate_fingers(hand)

        return hand
        #########################################################
    # Landmark Helper
    #########################################################

    def get_landmark(self, hand: Hand, index: int) -> Landmark:
        """
        Return a landmark by index.
        """
        return hand.landmarks[index]

    #########################################################
    # Finger State Detection
    #########################################################

    def _calculate_fingers(self, hand: Hand):
        """
        Returns:
            [thumb, index, middle, ring, pinky]
        """

        fingers = [False] * 5

        lm = hand.landmarks

        # -------------------------------
        # Thumb
        # -------------------------------
        #
        # Right hand:
        # Thumb tip should be to the RIGHT
        #
        # Left hand:
        # Thumb tip should be to the LEFT
        #

        if hand.handedness == "Right":
            fingers[0] = lm[4].x > lm[3].x
        else:
            fingers[0] = lm[4].x < lm[3].x

        # -------------------------------
        # Other four fingers
        # -------------------------------

        tip_ids = [8, 12, 16, 20]

        for i, tip in enumerate(tip_ids, start=1):

            tip_y = lm[tip].y
            pip_y = lm[tip - 2].y

            fingers[i] = tip_y < pip_y

        return fingers

    #########################################################
    # Is Finger Up?
    #########################################################

    def finger_up(self, hand: Hand, finger: int) -> bool:

        if finger < 0 or finger > 4:
            return False

        return hand.fingers_up[finger]

    #########################################################
    # Count Raised Fingers
    #########################################################

    def finger_count(self, hand: Hand):

        return sum(hand.fingers_up)

    #########################################################
    # Pinch Distance
    #########################################################

    def pinch_distance(self, hand: Hand):

        return hand.distance(4, 8)

    #########################################################
    # Palm Center
    #########################################################

    def palm_center(self, hand: Hand):

        return hand.center

    #########################################################
    # Bounding Box
    #########################################################

    def bounding_box(self, hand: Hand):

        return hand.bbox
        #########################################################
    # Draw MediaPipe Landmarks
    #########################################################

    def draw_landmarks(
        self,
        frame,
        hand_landmarks,
        draw_connections=True
    ):
        """
        Draw the 21 MediaPipe landmarks.
        """

        if draw_connections:

            self.mp_draw.draw_landmarks(

                frame,

                hand_landmarks,

                self.mp_hands.HAND_CONNECTIONS,

                self.mp_styles.get_default_hand_landmarks_style(),

                self.mp_styles.get_default_hand_connections_style()

            )

        else:

            for lm in hand_landmarks.landmark:

                x = int(lm.x * self.image_width)
                y = int(lm.y * self.image_height)

                cv2.circle(
                    frame,
                    (x, y),
                    4,
                    (0, 255, 0),
                    cv2.FILLED
                )

    #########################################################
    # Draw Bounding Box
    #########################################################

    def draw_bbox(
        self,
        frame,
        hand: Hand,
        color=(0,255,0),
        thickness=2
    ):

        x, y, w, h = hand.bbox

        padding = 15

        cv2.rectangle(

            frame,

            (x-padding, y-padding),

            (x+w+padding, y+h+padding),

            color,

            thickness

        )

    #########################################################
    # Draw Center Point
    #########################################################

    def draw_center(
        self,
        frame,
        hand: Hand
    ):

        cx, cy = hand.center

        cv2.circle(

            frame,

            (cx, cy),

            6,

            (255,0,255),

            cv2.FILLED

        )

    #########################################################
    # Draw Landmark Numbers
    #########################################################

    def draw_landmark_ids(
        self,
        frame,
        hand: Hand
    ):

        for landmark in hand.landmarks:

            cv2.putText(

                frame,

                str(landmark.id),

                (landmark.x+4, landmark.y-4),

                cv2.FONT_HERSHEY_PLAIN,

                0.8,

                (255,255,255),

                1

            )
        #########################################################
    # Draw Finger States
    #########################################################

    def draw_finger_states(
        self,
        frame,
        hand: Hand
    ):

        names = [

            "Thumb",

            "Index",

            "Middle",

            "Ring",

            "Pinky"

        ]

        x, y, _, _ = hand.bbox

        startY = y - 120

        for i in range(5):

            state = "UP" if hand.fingers_up[i] else "DOWN"

            color = (0,255,0) if hand.fingers_up[i] else (0,0,255)

            cv2.putText(

                frame,

                f"{names[i]} : {state}",

                (x, startY + i*20),

                cv2.FONT_HERSHEY_PLAIN,

                1,

                color,

                1

            )
        #########################################################
    # Draw Pinch Visualization
    #########################################################

    def draw_pinch(
        self,
        frame,
        hand: Hand
    ):

        thumb = hand.landmark(4)

        index = hand.landmark(8)

        cv2.circle(
            frame,
            (thumb.x, thumb.y),
            8,
            (0,255,255),
            cv2.FILLED
        )

        cv2.circle(
            frame,
            (index.x,index.y),
            8,
            (0,255,255),
            cv2.FILLED
        )

        cv2.line(

            frame,

            (thumb.x,thumb.y),

            (index.x,index.y),

            (255,0,255),

            3

        )

        midX = (thumb.x + index.x)//2
        midY = (thumb.y + index.y)//2

        cv2.circle(

            frame,

            (midX,midY),

            6,

            (255,255,0),

            cv2.FILLED

        )

        distance = hand.pinch_distance

        cv2.putText(

            frame,

            f"{distance:.0f}",

            (midX+15,midY),

            cv2.FONT_HERSHEY_PLAIN,

            1.2,

            (255,255,255),

            2

        )
        #########################################################
    # Draw Hand Information
    #########################################################

    def draw_hand_info(
        self,
        frame,
        hand: Hand
    ):

        x, y, _, _ = hand.bbox

        text = (

            f"{hand.handedness} "

            f"{hand.confidence:.2f}"

        )

        cv2.putText(

            frame,

            text,

            (x, y-25),

            cv2.FONT_HERSHEY_SIMPLEX,

            0.6,

            (0,255,0),

            2

        )

        cv2.putText(

            frame,

            f"Fingers : {self.finger_count(hand)}",

            (x, y-5),

            cv2.FONT_HERSHEY_SIMPLEX,

            0.55,

            (255,255,255),

            2

        )

    #########################################################
    # Draw Everything
    #########################################################

    def draw(
        self,
        frame,
        hand: Hand,
        show_ids=False
    ):

        self.draw_bbox(frame, hand)

        self.draw_center(frame, hand)

        self.draw_hand_info(frame, hand)

        self.draw_finger_states(frame, hand)

        self.draw_pinch(frame, hand)

        if show_ids:

            self.draw_landmark_ids(frame, hand)
    