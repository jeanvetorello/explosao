from cv2 import cv2
from pyclick import HumanClicker
from os import listdir
from random import randint

import time
import pyautogui
import numpy as np
import mss
import threading

# from skimage.metrics import structural_similarity

hc = HumanClicker()

def remove_suffix(input_string, suffix):
    if suffix and input_string.endswith(suffix):
        return input_string[:-len(suffix)]
    return input_string

#TODO tirar duplicata
def load_images(dir_name):
    file_names = listdir(dir_name)
    targets = {}
    for file in file_names:
        path = dir_name + file
        targets[remove_suffix(file, '.png')] = cv2.imread(path)

    return targets

if __name__ == '__main__':
    d = load_images( './images/')
    s = load_images( './small-digits/')
else:
    d = load_images( './captcha/images/')
    s = load_images( './captcha/small-digits/')

#TODO tirar duplicata
def positions(target, threshold=0.80,img = None):
    if img is None:
        img = printSreen()
    result = cv2.matchTemplate(img,target,cv2.TM_CCOEFF_NORMED)
    w = target.shape[1]
    h = target.shape[0]

    yloc, xloc = np.where(result >= threshold)

    rectangles = []
    for (x, y) in zip(xloc, yloc):
        rectangles.append([int(x), int(y), int(w), int(h)])
        rectangles.append([int(x), int(y), int(w), int(h)])

    rectangles, weights = cv2.groupRectangles(rectangles, 1, 0.2)
    return rectangles

def getDigits(d, img, gray=True, threshold=0.88):
    digits = []
    for i in range(10):
        if gray:
            template = cv2.cvtColor(d[str(i)], cv2.COLOR_BGR2GRAY)
        else:
            template = d[str(i)]

        p = positions(template,img=img,threshold=threshold)
        if len (p) > 0:
            digits.append({'digit':str(i),'x':p[0][0]})

    def getX(e):
        return e['x']

    digits.sort(key=getX)
    r = list(map(lambda x : x['digit'],digits))
    return(''.join(r))
    # getFirstDigits(first)

def printSreen():
    with mss.mss() as sct:
        monitor = sct.monitors[0]
        sct_img = np.array(sct.grab(monitor))
        # The screen part to capture
        # monitor = {"top": 160, "left": 160, "width": 1000, "height": 135}

        # Grab the data
        return sct_img[:,:,:3]

def captchaImg(img, pos,w = 520, h = 180):
    # path = "./captchas-saved/{}.png".format(str(time.time()))
    rx, ry, _, _ = pos

    x_offset = -10
    y_offset = 140

    y = ry + y_offset
    x = rx + x_offset
    cropped = img[ y : y + h , x: x + w]
    return cropped

def smallDigitsImg(img, pos, w = 200, h = 70):
    # path = "./captchas-saved/{}.png".format(str(time.time()))
    rx, ry, _, _ = pos

    x_offset = 150
    y_offset = 80

    y = ry + y_offset
    x = rx + x_offset
    cropped = img[ y : y + h , x: x + w]
    return cropped

def position(target, threshold=0.85,img = None):
    if img is None:
        img = printSreen()
    result = cv2.matchTemplate(img,target,cv2.TM_CCOEFF_NORMED)
    w = target.shape[1]
    h = target.shape[0]

    yloc, xloc = np.where(result >= threshold)


    rectangles = []
    for (x, y) in zip(xloc, yloc):
        rectangles.append([int(x), int(y), int(w), int(h)])
        rectangles.append([int(x), int(y), int(w), int(h)])

    rectangles, weights = cv2.groupRectangles(rectangles, 1, 0.2)
    if len(rectangles) > 0:
        x,y, w,h = rectangles[0]
        return (x+(w/2),y+h/2)

def getSliderPositions(screenshot, popup_pos):
    slider = position(d['slider'], img=screenshot)

    if slider is None:
        print('No slider')
        return None
    (start_x, start_y) = slider

    # pyautogui.moveTo(start_x,start_y+randint(0,10),1)
    hc.move((int(start_x), int(start_y)), 1)
    pyautogui.mouseDown()
    # pyautogui.moveTo(start_x+400,start_y+randint(0,10),1)
    hc.move((int(start_x+400), int(start_y)), 1)

    screenshot = printSreen()

    end = position(d['slider'], img=screenshot, threshold = 0.8)
    (end_x, end_y) = end
    size = end_x-start_x
    increment = size/6

    positions = []
    for i in range(7):
        # pyautogui.moveTo(start_x+increment*pos ,start_y+randint(0,10),1)
        positions.append((start_x+increment*i ,start_y+randint(0,10)))
        # screenshot = printSreen()
        # time.sleep(2)
        # pyautogui.mouseUp()
    return positions

def r():
    return randint(0,5)

def moveToReveal(popup_pos):
    # time.sleep(10)
    # return
    x,y,_,_ = popup_pos
    t = 2.5
    offset_x = 20
    offset_y = 140
    w = 453
    h = 160
    passes = 26
    increment_x = w/passes
    increment_y = h/passes
    start_x = x + offset_x
    start_y = y + offset_y
    # pyautogui.moveTo(start_x, start_y, t)
    # pyautogui.moveTo(start_x, start_y+h, t)
    # pyautogui.moveTo(start_x + w, start_y + h, t)
    # pyautogui.moveTo(start_x + w, start_y, t)
    hc.move((int(start_x), int(start_y)), t)
    hc.move((int(start_x), int(start_y + h)), t)
    hc.move((int(start_x + (w / 2)), int(start_y + h)), t)
    hc.move((int(start_x + w), int(start_y + h)), t)
    hc.move((int(start_x + w), int(start_y)), t)
    hc.move((int(start_x + (w / 2)), int(start_y)), t)
    hc.move((int(start_x), int(start_y)), t)

    for i in range(passes):
        x = start_x + i * increment_x
        y = start_y + h * (i % 2)
        # pyautogui.moveTo(x,y,1)
        hc.move((int(x), int(y)), t)
    # pyautogui.moveTo(start_x+ w + r(),start_y + h + r(),t)
    hc.move((int(start_x + w), int(start_y + h)), t)
    hc.move((int(start_x + w), int(start_y)), t)

    time.sleep(1)

def lookAtCaptcha():
    screenshot = printSreen()
    popup_pos = positions(d['robot'],img=screenshot)
    img = captchaImg(screenshot, popup_pos[0])
    return img

# def generateDiff(first,position):
    # gray_first = cv2.cvtColor(first, cv2.COLOR_BGR2GRAY)
    # screenshot = printSreen()
    # img = screenshot.copy()
    # second = captchaImg(img,position)
    # gray_second = cv2.cvtColor(second, cv2.COLOR_BGR2GRAY)


    # (_, diff) = structural_similarity(gray_first,gray_second, full=True)
    # diff = (diff * 255).astype("uint8")
    # cv2.imshow('img',diff)
    # cv2.waitKey(5000)

    # cv2.imshow('img',cp)
    # return diff

def preProcess(img):
    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    t,img = cv2.threshold(img,170,240,cv2.THRESH_BINARY_INV)
    return img

def add(img0, img1):
    return cv2.bitwise_and(img0, img1, mask = None)

def getDiff(data):
    if data[0] is None:
        img0 = preProcess(lookAtCaptcha())
        img1 = preProcess(lookAtCaptcha())
        data[0] = add(img0,img1)
    while data[1]:
        now = preProcess(lookAtCaptcha())
        data[0] = add(data[0],now)
    return
        # time.sleep()

def watchDiffs(data):
    thread = threading.Thread(target=getDiff, args =(data,))
    thread.start()
    return thread
    # thread.join()

def show(rectangles = None, img = None):

    if img is None:
        with mss.mss() as sct:
            img = np.array(sct.grab(sct.monitors[1]))

    if rectangles is not None:
        for (x, y, w, h) in rectangles:
            cv2.rectangle(img, (x, y), (x + w, y + h), (255,255,255,255), 2)

    # cv2.rectangle(img, (result[0], result[1]), (result[0] + result[2], result[1] + result[3]), (255,50,255), 2)
    cv2.imshow('img',img)
    cv2.waitKey(0)


def getBackgroundText():
    screenshot = printSreen()
    popup_pos = positions(d['robot'],img=screenshot)
    data = [None,True]
    thread = watchDiffs(data)
    moveToReveal(popup_pos[0])
    data[1]=False
    thread.join()
    # if __name__ == '__main__':
    #     path = "./tmp/{}.png".format(str(time.time()))
    #     cv2.imwrite(path,data[0])
    digits = getDigits(d, data[0])
    # cv2.imshow('test',data[0])
    # cv2.waitKey(0)
    # img = captchaImg(screenshot, popup_pos[0])
    # cv2.imshow('img',img)
    # cv2.waitKey(0)
    return digits

def getSmallDigits(img):
    # if __name__ == '__main__':
    #     path = "./tmp/small{}.png".format(str(time.time()))
    #     # cv2.imwrite(path,img)
    digits = getDigits(s, img, gray=False, threshold=0.92)
    # print('fg = {}'.format(digits))

    return digits

def solveCaptcha():
    screenshot = printSreen()
    img = screenshot.copy()
    popup_pos = positions(d['robot'],img=img)
    if len(popup_pos) == 0:
        print('No captcha popup found!')
        return
    img = captchaImg(img, popup_pos[0])
    background_digits = getBackgroundText()
    # print('background = {}'.format(background_digits))
    slider_positions = getSliderPositions(screenshot, popup_pos)

    if slider_positions is None:
        return

    for position in slider_positions:
        x, y = position
        # pyautogui.moveTo(x,y,1)
        hc.move((int(x), int(y)), 1)
        time.sleep(2)
        screenshot = printSreen()
        popup_pos = positions(d['robot'], img=screenshot)
        captcha_img = smallDigitsImg(screenshot, popup_pos[0])
        small_digits = getSmallDigits(captcha_img)
        # print( 'dig: {}, background_digits: {}'.format(small_digits, background_digits))
        if small_digits == background_digits:
            print('FOUND!')
            pyautogui.mouseUp()
            return
    print('Not found... trying again!')
    pyautogui.mouseUp()
    time.sleep(4)
    solveCaptcha()
    return

if __name__ == '__main__':
    solveCaptcha()
#TODO colocar positions em um arquivo separado e importar nos outros.
# tirar o load digits daqui e passar como argumento na funçao

        # (_, new_diff) = structural_similarity(img0,img1, full=True)
        # diff[0] = (new_diff * 255).astype("uint8")
# arrumar o mexer das posiçoes pra ele vazer mais movimentos verticais
# calcular n de sliders ou fazer recursivamente.
# fazer os and so no final
