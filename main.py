
import time
import cv2

import config

from vision.hand_detector import HandDetector
from vision.gesture_recognition import GestureRecognizer
from vision.gesture import GestureType
from vision.gesture import gesture_description

from controllers.spotify_controller import SpotifyController
from controllers.volume_controller import VolumeController


def main():

    ##########################################################
    # Camera
    ##########################################################

    cap = cv2.VideoCapture(config.CAMERA_INDEX)

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, config.FRAME_WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, config.FRAME_HEIGHT)

    if not cap.isOpened():
        print("Unable to open webcam.")
        return

    ##########################################################
    # Components
    ##########################################################

    detector = HandDetector()

    recognizer = GestureRecognizer()

    spotify = SpotifyController()

    volume = VolumeController()

    ##########################################################
    # Runtime State
    ##########################################################

    last_executed = GestureType.NONE

    missing_frames = 0

    previous_time = time.time()
    while True:
        success, frame = cap.read()
        if not success:
            break
        if config.FLIP_CAMERA:
            frame = cv2.flip(frame, 1)
        hands = detector.detect(frame)
        if len(hands) == 0:
            missing_frames += 1
        else:
            missing_frames = 0
        if missing_frames >= 10:
            last_executed = GestureType.NONE
        for hand in hands:

            if hand.raw_landmarks is not None:

                detector.draw_landmarks(
                    frame,
                    hand.raw_landmarks
                )

            detector.draw(
                frame,
                hand,
                show_ids=True
            )

            ##################################################
            # Gesture Recognition
            ##################################################

            result = recognizer.detect(hand)

            if not result.is_valid():
                continue

            ##################################################
            # Debug
            ##################################################

            print(gesture_description(result))

            ##################################################
            # Continuous Gesture
            ##################################################

            if result.gesture == GestureType.PINCH:

                volume.execute(

                    result.gesture,

                    result.pinch_ratio

                )

            ##################################################
            # One-shot Gestures
            ##################################################

            elif result.gesture != last_executed:

                spotify.execute(

                    result.gesture

                )

                volume.execute(

                    result.gesture,

                    result.pinch_ratio

                )

                last_executed = result.gesture

            ##################################################
            # Display Gesture
            ##################################################

            cv2.putText(

                frame,

                result.gesture.name,

                (20, 40),

                cv2.FONT_HERSHEY_SIMPLEX,

                1,

                (0, 255, 0),

                2

            )

            cv2.putText(

                frame,

                f"Confidence : {result.confidence:.2f}",

                (20, 75),

                cv2.FONT_HERSHEY_SIMPLEX,

                0.6,

                (255, 255, 255),

                2

            )

        ######################################################
        # FPS
        ######################################################

        current_time = time.time()

        fps = 1 / (current_time - previous_time)

        previous_time = current_time

        cv2.putText(

            frame,

            f"FPS : {int(fps)}",

            (20, config.FRAME_HEIGHT - 20),

            cv2.FONT_HERSHEY_SIMPLEX,

            0.7,

            (255, 255, 0),

            2

        )

        ######################################################
        # Display
        ######################################################

        cv2.imshow(

            config.WINDOW_NAME,

            frame

        )

        ######################################################
        # Exit
        ######################################################

        key = cv2.waitKey(1) & 0xFF

        if key == 27 or key == ord("q"):
            break

    ##########################################################
    # Cleanup
    ##########################################################

    cap.release()

    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()