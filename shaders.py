from random import randint as rnd

border = 200


def red():
    r = rnd(border, 255)
    g = 0
    b = 0
    return r, g, b


def green():
    r = 0
    g = rnd(border, 255)
    b = 0
    return r, g, b


def blue():
    r = 0
    g = 0
    b = rnd(border, 255)
    return r, g, b


def yellow():
    r = rnd(border, 255)
    g = rnd(border, 255)
    b = 0
    return r, g, b


def grey():
    r = g = b = rnd(90, 120)
    return r, g, b


def dark_green():
    r = 0
    g = rnd(100, 150)
    b = 0
    return r, g, b


def orange():
    r = 255
    g = rnd(100, 150)
    b = 0
    return r, g, b


def black():
    r = g = b = rnd(0, 10)
    return r, g, b

