#!/usr/bin/env python3

import os
import threading
from argparse import ArgumentParser
from queue import Empty, Queue
from time import sleep

import numpy as np

import cv2
from iotdemo import ColorDetector, FactoryController, MotionDetector
from openvino.inference_engine import IECore

FORCE_STOP = False


def thread_cam1(q):
    # Motion Detect Init
    det = MotionDetector()
    det.load_preset("resources/factory/motion.cfg", "default")

    # Load IR Files
    ie = IECore()
    net = ie.read_network(model='resources/factory/model.xml')
    exec_net = ie.load_network(network=net, device_name='CPU')

    input_name = next(iter(net.input_info))
    out_name = next(iter(net.outputs))

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

        # Abnormal Detect
        reshaped = detected[:, :, [2, 1, 0]]
        np_data = np.moveaxis(reshaped, -1, 0)
        preprocessed_numpy = [((np_data / 255.0) - 0.5) * 2]
        batch_tensor = np.stack(preprocessed_numpy, axis=0)

        # Inference the Detected Data
        res = exec_net.infer(inputs={input_name: batch_tensor})
        predict = res[out_name][0]

        # Print the Predict Ratio
        x_ratio = np.float32(predict[0]) * 100.
        circle_ratio = np.float32(predict[1]) * 100.
        print(f"X = {x_ratio:.2f}%, Circle = {circle_ratio:.2f}%")

        if circle_ratio < 70:
            q.put(('Push', 1))
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
        predict = color.detect(detected)
        if not predict:
            continue

        # Get result & compute
        name, ratio = predict[0]
        ratio *= 100.

        # Print Result
        print(f"{name}: {ratio:.2f}%")
        if name == 'blue' and ratio > .5:
            q.put(('Push', 2))

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

    # args.device
    # print(args.device)
    with FactoryController(args.device) as ctrl:
    # 프로그램 실행 시 python3 06_1_defect_detect_result_jason.py -d /dev/ttyS11
    # with FactoryController('/dev/ttyS5') as ctrl:
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

            if name == 'Push':
                print(f"{name}, {data}, {ctrl.red}, {ctrl.orange}")
                if data == 1:
                    ctrl.push_actuator(1)
                elif data == 2:
                    ctrl.push_actuator(2)

            # Exit
            if name == 'DONE':
                FORCE_STOP = True

    cv2.destroyAllWindows()


if __name__ == '__main__':
    try:
        main()
    except Exception:
        os._exit()
