#!/usr/bin/env python3

import os
import threading
from argparse import ArgumentParser
from queue import Empty, Queue
from time import sleep

import cv2
from iotdemo import FactoryController

FORCE_STOP = False


def thread_cam1(q):
    # Init Video/Camera

    while not FORCE_STOP:
        sleep(0.03)

        # Read frame

        # Enqueue

    # Exit Video/Camera

    # Enqueue DONE

    exit()


def thread_cam2(q):
    # Init Video/Camera

    while not FORCE_STOP:
        sleep(0.03)

        # Read frame

        # Enqueue

    # Exit Video/Camera

    # Enqueue DONE

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

            # Event to name, data

            # Show the data

            # Exit

    cv2.destroyAllWindows()


if __name__ == '__main__':
    try:
        main()
    except Exception:
        os._exit()
