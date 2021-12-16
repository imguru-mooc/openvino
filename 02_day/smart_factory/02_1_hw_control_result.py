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
            elif index == "2":
                ctrl.system_stop()
            elif index == "3":
                ctrl.red = ~~ctrl.red
            elif index == "4":
                ctrl.orange = ~~ctrl.orange
            elif index == "5":
                ctrl.green = ~~ctrl.green
            elif index == "6":
                ctrl.conveyor = ~~ctrl.conveyor
            elif index == "7":
                ctrl.push_actuator(1)
            elif index == "8":
                ctrl.push_actuator(2)
            elif index == "q":
                break
            else:
                print("Input the index number (to quit : q)")

    print("Quit the Program!")


if __name__ == '__main__':
    try:
        main()
    except Exception:
        os._exit()
