import time
import math
from collections import deque, defaultdict

import matplotlib.animation as animation
from matplotlib import pyplot as plt

import threading

from random import randint

import statistics


class DataPlot:
    def __init__(self, max_entries=20):
        self.axis_x = deque(maxlen=max_entries)
        self.axis_y = deque(maxlen=max_entries)
        self.axis_y2 = deque(maxlen=max_entries)
        self.axis_y3 = deque(maxlen=max_entries)

        self.max_entries = max_entries

        self.buf1 = deque(maxlen=5)
        self.buf2 = deque(maxlen=5)

    def add(self, x, y, y2,y3):
        self.axis_x.append(x)
        self.axis_y.append(y)
        self.axis_y2.append(y2)
        self.axis_y3.append(y3)


class RealtimePlot:
    def __init__(self, axes):
        self.axes = axes

        self.lineplot, = axes.plot([], [], "ro-")
        self.lineplot2, = axes.plot([], [], "go-")
        self.lineplot3, = axes.plot([], [], "bo-")

    def plot(self, dataPlot):
        self.lineplot.set_data(dataPlot.axis_x, dataPlot.axis_y)
        self.lineplot2.set_data(dataPlot.axis_x, dataPlot.axis_y2)
        self.lineplot3.set_data(dataPlot.axis_x, dataPlot.axis_y3)

        self.axes.set_xlim(min(dataPlot.axis_x), max(dataPlot.axis_x))
        ymin = min([min(dataPlot.axis_y), min(dataPlot.axis_y2)]) - 10
        ymax = max([max(dataPlot.axis_y), max(dataPlot.axis_y2)]) + 10
        self.axes.set_ylim(ymin, ymax)
        self.axes.relim();


def main():
    fig, axes = plt.subplots()
    plt.title('Plotting Data')

    data = DataPlot();
    dataPlotting = RealtimePlot(axes)

    try:
        count = 0
        while True:
            count += 1
            data.add(count, 30 + 1 / randint(1, 5), 35 + randint(1, 5))
            dataPlotting.plot(data)

            plt.pause(0.001)
    except KeyboardInterrupt:
        print('nnKeyboard exception received. Exiting.')
        plt.close()
        # ser.close()
        exit()


if __name__ == "__main__": main()
