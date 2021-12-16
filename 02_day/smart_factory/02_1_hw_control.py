#!/usr/bin/env python3

import os

from iotdemo import FactoryController

FORCE_STOP = False


def main():
    global FORCE_STOP

    with FactoryController('/dev/ttyS4') as ctrl:
        while not FORCE_STOP:
            print("Arduino Control Code")

            # Arduino Control Code
            index = input("Input the index: ")
            if index == "1":
                ctrl.system_start()
            elif index == "q":
                break
            else:
                print("Input the index number (to quit : q)")


if __name__ == '__main__':
    try:
        main()
    except Exception:
        os._exit()
