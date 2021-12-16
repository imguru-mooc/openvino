#!/usr/bin/env python3

import os
import threading
from argparse import ArgumentParser
from queue import Empty, Queue
from time import sleep

import cv2
from iotdemo import ColorDetector, FactoryController, MotionDetector

FORCE_STOP = False


def thread_cam1(q):
    # Motion Detect Init
    det = MotionDetector()
    det.load_preset("resources/factory/motion.cfg", "default")

    # Init Video/Camera
    cap = cv2.VideoCapture("resources/factory/conveyor.mp4")

    while not FORCE_STOP:
        sleep(0.03)

        # Read frame
        _, frame = cap.read()
        if frame is None:
            break

        # Enqueue
        q.put(('VIDEO:Cam1 live', frame))

        # Motion Detect
        detected = det.detect(frame)
        if detected is None:
            continue

        # Enqueue
        q.put(('VIDEO:Cam1 detected', detected))

    # Exit Video/Camera
    cap.release()

    # Enqueue DONE
    q.put(('DONE', None))

    exit()


def thread_cam2(q):
    # Motion Detect Init
    det = MotionDetector()
    det.load_preset("resources/factory/motion.cfg", "default")

    # Color Detect Init
    color = ColorDetector()
    color.load_preset("resources/factory/color.cfg", "default")

    # Init Video/Camera
    cap = cv2.VideoCapture("resources/factory/conveyor.mp4")

    while not FORCE_STOP:
        sleep(0.03)

        # Read frame
        _, frame = cap.read()
        if frame is None:
            break

        # Enqueue
        q.put(('VIDEO:Cam2 live', frame))

        # Motion Detect
        detected = det.detect(frame)
        if detected is None:
            continue

        # Enqueue
        q.put(('VIDEO:Cam2 detected', detected))

        # Color Detect

        # Get result & compute

        # Print Result

    # Exit Video/Camera
    cap.release()

    # Enqueue DONE
    q.put(('DONE', None))

    exit()


def imshow(title, frame, pos=None):
    cv2.namedWindow(title)
    if pos:
        cv2.moveWindow(title, pos[0], pos[1])
    cv2.imshow(title, frame)


def main():
    global FORCE_STOP

    parser = ArgumentParser(prog='python3 factory.py',
                            description="Factory tool")

    parser.add_argument("-d",
                        "--device",
                        default=None,
                        type=str,
                        help="Arduino port")
    args = parser.parse_args()

    # Factory Controll event queue
    q = Queue()

    # Camera processing threads
    t1 = threading.Thread(target=thread_cam1, args=(q, ), daemon=True)
    t2 = threading.Thread(target=thread_cam2, args=(q, ), daemon=True)

    t1.start()
    t2.start()

    with FactoryController(args.device) as ctrl:
        while not FORCE_STOP:
            if cv2.waitKey(10) & 0xff == ord('q'):
                break

            # Dequeue
            try:
                event = q.get_nowait()
            except Empty:
                continue

            # Event to name, data
            name, data = event

            # Show the data
            if name.startswith('VIDEO:'):
                imshow(name[6:], data)

            # Exit
            if name == 'DONE':
                FORCE_STOP = True

    cv2.destroyAllWindows()


if __name__ == '__main__':
    try:
        main()
    except Exception:
        os._exit()
