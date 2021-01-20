import typing

import pygame
import random
import numpy
import dataclasses

colors = {
    "RED": (255, 0, 0),
    "GREEN": (0, 255, 0),
    "BLUE": (0, 0, 255),
    "YELLOW": (255, 255, 0),
    "MAGENTA": (255, 0, 255),
    "CYAN": (0, 255, 255),
    "BLACK": (0, 0, 0),
    "GRAY": (128, 128, 128),
    "WHITE": (255, 255, 255)
}


def index_to_color(color_index: int) -> typing.Tuple:
    try:
        return colors.get(list(colors)[int(color_index)])
    except:
        print(f'Failed at provided: {type(color_index)}, with value {color_index}')
