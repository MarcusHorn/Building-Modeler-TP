#Marcus Horn; marcush; Section H

import cv2
import numpy as np
import sys
import time
import stitch

#Stitch.py file used as external module for panorama stitching
#Retrieved from GitHub repository /marcpare/stitch
#Author: Marc Pare


class Video(object):
    def __init__(self, title = "Panorama Stitcher", camera = 0, 
            size = cv2.CV_WINDOW_AUTOSIZE):
        self.title = title
        self.camera = camera
        self.size = size
        self.cap = None

    def initializeWindow(self):
        cv2.namedWindow(self.title, self.size)

    def startVideo(self):
        self.cap = cv2.VideoCapture(self.camera)
        self.cap.open(self.camera)

    def updateCurrentFrame(self):
        return self.cap.read()

    def release(self):
        self.cap.release()

    def show(self, curImage):
        cv2.imshow(self.title, curImage.frame)

class Image(object):
    def __init__(self, ret, frame):
        self.ret = ret
        self.frame = frame

    def blur(self, k):
        self.frame = cv2.blur(self.frame, (k, k))

    def Canny(self, low, high):
        self.frame = cv2.Canny(self.frame, low, high)

class Panorama(Image):
    def __init__(self, images):
        self.images = images
        self.frame = None

    def makePanoramaWrapper(self):
        panWidth = 400 #Size for images to be set to
        finalImage = makePanorama(self.images)
        self.frame = finalImage

def makePanorama(images):
    if len(images) == 1:
        return images[0].frame
    elif len(images) == 2:
        image1 = images[0].frame
        image2 = images[1].frame
        return stitch.runStitch(image1, image2)
    else:
        mid = len(images) // 2
        half1 = makePanorama(images[:mid])
        half2 = makePanorama(images[mid:])
        return stitch.runStitch(half1, half2)

#Loop structure retrieved from OpenCV tutorial
#Authors: Vasu Agrawal and Kim Kleiven

def runCamera():
    savedImages = []
    curVideo = Video()
    curVideo.initializeWindow()
    curVideo.startVideo()
    edgeLoThresh = 80
    edgeHiThresh = 135
    madePanorama = False #Tracks whether a panorama of a room was made
    havePanorama = False #Tracks whether a panorama is being generated
    CanniedPanorama = False #Tracks whether the panorama was Cannied
    panoramaImages = []
    timerDelay = .2 #Timer delay in seconds
    blurK = 7 #Value to use in blurring command
    numberOfImagesLeft = 2
    while True:
        if madePanorama:
            if not CanniedPanorama:
                curPanorama.blur(blurK)
                curPanorama.Canny(edgeLoThresh, edgeHiThresh)
                CanniedPanorama = True
            curVideo.show(curPanorama) #Displays the created panorama

        elif havePanorama: #Creates the panorama
            curPanorama = Panorama(panoramaImages)
            curPanorama.makePanoramaWrapper()
            havePanorama = False
            madePanorama = True

        else: #Otherwise, continue taking pictures
            ret, frame = curVideo.updateCurrentFrame()
            curImage = Image(ret, frame)
            curVideo.show(curImage)

        k = cv2.waitKey(1) & 0xFF

        if k == 27: #Escape Key
            cv2.destroyAllWindows()
            curVideo.release()
            if madePanorama: #Returns a panorama to Tkinter if one was made
                return curPanorama.frame
            else:
                return None


        elif k == ord('d') and not madePanorama and numberOfImagesLeft > 0:
            if curImage.frame is not None and not havePanorama:
                #Adds the photo to the list of collected images
                panoramaImages.append(curImage) #Adds current frame to panorama
                time.sleep(timerDelay) #Waits before processing another image
                numberOfImagesLeft -= 1
            if numberOfImagesLeft == 0:
                havePanorama = True #Stops once images of 4 views are taken


