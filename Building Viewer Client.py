
import operator
import math
import random
from Tkinter import *
from PIL import Image, ImageTk
import cv2
import numpy as np
import PanoramaStitching #Imports OpenCV code from the second file
import string

class Door():
    def __init__(self, x, y, z, w, h, d):
        self.x = x #Coordinates with respect to room
        self.y = y
        self.z = z
        self.depth = d
        self.width = w
        self.height = h

#Room class and its methods threeDIfy and drawRect are heavy modifications 
#of code for rectangle class from 3D in Tkinter Code Artifacts
#Author(s): 15-112 CA's

#way this works: I rotate firstly by using the z and x axis, then
#do the same thing again with the y and z axis
def threeDIfy(points, cx, cy, cz, rotX, rotY):
    #how much rotation there is for the ship's points
    angleX=-(math.pi/2)*(rotX)/90
    angleY=-(math.pi/2)*(rotY)/90
    for point in points:
        (x1,y1,z1)=point
        x = x1 - cx
        y = y1 - cy
        z = z1 - cz
        if z!=0:
            pointAngY=math.atan(abs(y/z))
        else: 
            #to avoid crashing
            if y>0: pointAngY=math.pi/2
            else: pointAngY=-math.pi/2
        #atan(-/-)!=atan(+/+), but treated the same by the division
        #so must handle individually
        if y>0 and z<0:
            pointAngY=math.pi-pointAngY
        elif y<=0 and z<0:
            pointAngY=math.pi+pointAngY
        elif y<0 and z>0:
            pointAngY=2*math.pi-pointAngY
        #change the angle
        finAng=pointAngY+angleY
        #figure out the magnitude of (y^2+z^2)^0.5
        pointMag=(y**2+z**2)**0.5
        point[1]=pointMag*math.sin(finAng) + cy
        point[2]=pointMag*math.cos(finAng) + cz
    #handle for x
    for point in points:
        (x1,y1,z1)=point
        x = x1 - cx
        y = y1 - cy
        z = z1 - cz
        if z!=0:
            pointAngX=math.atan(abs(x/z))
        else: 
            if x>0: pointAngX=math.pi/2
            else: pointAngX=-math.pi/2
        if x>0 and z<0:
            pointAngX=math.pi-pointAngX
        elif x<=0 and z<0:
            pointAngX=math.pi+pointAngX
        elif x<0 and z>0:
            pointAngX=2*math.pi-pointAngX
        finAng=pointAngX+angleX
        pointMag=(x**2+z**2)**0.5
        point[0]=pointMag*math.sin(finAng) + cx
        point[2]=pointMag*math.cos(finAng) + cz
    return points

class room():

    def __init__(self, x, y, width, height,depth = 0,z = 0,rotX = 90,
        rotY = 90):
        #3D parameters made optional
        self.x=x
        self.y=y
        self.z=z
        self.depth=depth
        self.width=width
        self.rotX=rotX
        self.rotY=rotY
        self.height=height
        self.color="beige"
        self.outline="blue"
        self.doors = []

    def addDoorWay(self, dx, dy, dz, dWidth, dHeight, dDepth):
        door = Door(dx, dy, dz, dWidth, dHeight, dDepth)
        self.doors.append(door)

    def recalcDoors(self, oldW, oldH, oldD):
        w, h, d = self.width, self.height, self.depth
        if w != oldW:
            ratio = float(w) / float(oldW)
            for door in self.doors:
                door.width *= ratio
                door.x *= ratio
                door.x = int(door.x)
        elif h != oldH:
            ratio = float(h) / float(oldH)
            for door in self.doors:
                door.height *= ratio
                door.y *= ratio
                door.y = int(door.y)
        elif d != oldD:
            ratio = float(d) / float(oldD)
            for door in self.doors:
                door.depth *= ratio
                door.z *= ratio
                door.z = int(door.z)

    def addDoorPoints(self, zoom):
        botY = self.height * zoom #Used to place bottom of doorway
        points = []
        for door in self.doors:
            dx = door.x * zoom
            dz = door.z * zoom
            w = door.width * zoom
            h = door.height * zoom
            d = door.depth * zoom #Dimensions of door
        #Either the width or depth will be zero due to constraints
            points += ([dx + w,h,dz + d],[dx - w,h,dz - d],
                [dx + w,-botY,dz + d],[dx-w,-botY,dz - d])
        return points

    def insideRoom(self, data, x, y):
        cx, cy, cz = data.modelCenter
        zoom = data.zoomLevel
        # rx = (self.x - cx)*zoom + cx #Applies zoom-based shift of objects
        # ry = (self.y - cy)*zoom + cy
        points = [[self.x, self.y, self.z], [self.x, self.y, self.z]]
        points = threeDIfy(points, cx, cy, cz, self.rotX, self.rotY)
        rx, ry, rz = points[0]
        radius = max(self.width, self.height, self.depth)
        return ((x - rx)**2 + (y-ry)**2)**.5 <= radius

    def drawRect(self, canvas, data):
        cx, cy, cz = data.modelCenter
        zoom = data.zoomLevel
        w = self.width*zoom
        h = self.height*zoom
        d = self.depth*zoom #Widens the dimensions based on zoom level
        points=[[w,h,d],[w,h,-d],[-w,h,-d],[-w,h,d],[w,-h,d],[w,-h,-d],
        [-w,-h,-d],[-w,-h,d]]
        doorPoints = self.addDoorPoints(zoom)
        poly1=(0,1,5,4)
        poly2=(1,2,6,5)
        poly3=(2,3,7,6)
        poly4=(4,5,6,7)
        poly5=(0,1,2,3)
        poly6=(7,4,0,3)
        polyList=[poly1,poly2,poly3,poly4,poly5,poly6]
        polyList=self.byDimension(polyList,points)
        x = (self.x - cx)*zoom + cx #Applies zoom-based shift of objects
        y = (self.y - cy)*zoom + cy
        z = (self.z - cz)*zoom + cz
        for point in points: #Points that make up the room itself       
            point[0] += x
            point[1] += y
            point[2] += z
        for point in doorPoints:
            point[0] += x
            point[1] += y
            point[2] += z
        doorPoints = threeDIfy(doorPoints, cx, cy, cz, self.rotX, self.rotY)
        points = threeDIfy(points, cx, cy, cz, self.rotX, self.rotY)

        #Creates the door of the room
        for poly in polyList:
            if data.wireFrameMode:
                canvas.create_polygon(points[poly[0]][0:2],points[poly[1]][0:2], 
                points[poly[2]][0:2], points[poly[3]][0:2], fill = "",
                outline=self.outline, width=data.lineWidth, 
                activeoutline = data.actColor)
                #Does not provide a fill if the program is set to wireframe
            else: 
                canvas.create_polygon(points[poly[0]][0:2], 
                points[poly[1]][0:2], points[poly[2]][0:2], 
                points[poly[3]][0:2], fill=self.color, outline=self.outline, 
                width=data.lineWidth, activeoutline = data.actColor)
        doorIndex = 0 #Tracks the number of the door currently being generated
        doorPoly=(0,1,3,2) #Doorway polygon, used for reference
        for door in self.doors:
            #Shifts indexes provided in doorPoly by 4 each time for each door
            poly1 = 4 * doorIndex
            poly2 = 4 * doorIndex + 1
            poly3 = 4 * doorIndex + 3
            poly4 = 4 * doorIndex + 2
            canvas.create_polygon(doorPoints[poly1][0:2],
                doorPoints[poly2][0:2], doorPoints[poly3][0:2], 
                doorPoints[poly4][0:2], fill = "white",
                outline=self.outline, width=data.lineWidth, 
                activeoutline = data.actColor)
            doorIndex += 1

    @staticmethod
    def byDimension(polyList, points):
        myList=[]
        for myPoints in polyList:
            myList.append((myPoints,room.smallestInPoly(myPoints, points)))
        myList=sorted(myList, key=operator.itemgetter(1))
        final=[]

        for bigTuple in myList:
            final.append(bigTuple[0])
        return final


    @staticmethod
    def smallestInPoly(aList, points):
        smallest=0
        total=0
        for val in aList:
            smallest+=points[val][2]
            total+=1
        return smallest/total

class Compass():
    def __init__(self, origin, length, rotX, rotY):
        self.x, self.y, self.z = origin
        self.length = length
        self.rotX = rotX
        self.rotY = rotY

    def drawCompass(self, canvas, data):
        cx, cy, cz = data.compassOrigin
        l = self.length #Width, height, and depth are all equal
        points = [[0,0,0], [0, l, 0], [l, 0, 0], [0, 0, l]]
        for point in points:
            point[0] += cx
            point[1] += cy
            point[2] += cz
        points = threeDIfy(points, cx, cy, cz, self.rotX, self.rotY)
        x0, y0, z0 = points[0]
        pointIndex = 0
        for label in ["y", "x", "z"]:
            pointIndex += 1
            x1, y1, z1 = points[pointIndex]
            canvas.create_line(x0, y0, x1, y1, fill = data.compassColor)
            canvas.create_text(x1, y1, anchor = S, text = label)

class Dot():
    def __init__(self, origin, radius, rotX, rotY):
        self.x, self.y, self.z = origin
        self.r = radius
        self.rotX = rotX
        self.rotY = rotY

    def getDotCenter(self, data):
        zoom = data.zoomLevel
        cx, cy, cz = data.modelCenter
        x, y, z = self.x, self.y, self.z
        x = (self.x - cx)*zoom + cx #Applies zoom-based shift of objects
        y = (self.y - cy)*zoom + cy
        z = (self.z - cz)*zoom + cz
        points = [[x,y,z], [0,0,0]]
        points = threeDIfy(points, cx, cy, cz, self.rotX, self.rotY)
        return points[0]

    def drawDot(self, canvas, data):
        point = self.getDotCenter(data)
        x = point[0]
        y = point[1]
        r = self.r
        canvas.create_oval(x-r,y-r,x+r,y+r, fill = data.windowColor,
            activefill = data.actColor)

class smallButton():
    def __init__(self, function, size, cx, cy):
        self.function = function
        self.size = size
        self.cx = cx
        self.cy = cy
        self.x0 = self.cx - self.size // 2
        self.y0 = self.cy - self.size // 2
        self.x1 = self.x0 + self.size
        self.y1 = self.y0 + self.size

    def insideButton(self, x, y):
        x0, x1 = self.x0, self.x1
        y0, y1 = self.y0, self.y1
        return x >= x0 and x <= x1 and y <= y1 and y >= y0

    def drawButton(self, canvas, data):
        x0, x1 = self.x0, self.x1
        y0, y1 = self.y0, self.y1
        canvas.create_rectangle(x0, y0, x1, y1, fill = data.windowColor,
            activeoutline = data.actColor)
        cx, cy = self.cx, self.cy
        if self.function == "zoom in":
            canvas.create_text(cx, cy, text = "+", font = "Helvetica 20 bold")
        elif self.function == "zoom out":
            canvas.create_text(cx, cy, text = "-", font = "Helvetica 20 bold")
        elif self.function == "up":
            canvas.create_line(cx, y1, cx, y0, arrow = "last")
        elif self.function == "down":
            canvas.create_line(cx, y0, cx, y1, arrow = "last")
        elif self.function == "left":
            canvas.create_line(x1, cy, x0, cy, arrow = "last")
        elif self.function == "right":
            canvas.create_line(x0, cy, x1, cy, arrow = "last")
        elif self.function == "rotate up":
            canvas.create_line(cx, y1, x0 - 5, cy, cx + 5, y0, smooth = True,
                splinesteps = 12, arrow = "last")
        elif self.function == "rotate down":
            canvas.create_line(cx, y0, x1 + 5, cy, cx - 5, y1, smooth = True,
                splinesteps = 12, arrow = "last")
        elif self.function == "rotate right":
            canvas.create_line(x0, cy, cx, y0 - 5, x1, cy + 5, smooth = True,
                splinesteps = 12, arrow = "last")
        elif self.function == "rotate left":
            canvas.create_line(x1, cy, cx, y0 - 5, x0, cy + 5, smooth = True,
                splinesteps = 12, arrow = "last")

    def performFunction(self, data):
        func = self.function
        if func == "zoom in":
            data.zoomLevel *= data.zoomInRatio
        elif func == "zoom out":
            data.zoomLevel *= data.zoomOutRatio
        elif func == "up":
            panRooms(data, 0, data.panAmount)
        elif func == "down":
            panRooms(data, 0, -data.panAmount)
        elif func == "left":
            panRooms(data, data.panAmount, 0)
        elif func == "right":
            panRooms(data, -data.panAmount, 0)
        elif func == "rotate up":
            rotateView(data, 0, 3*data.rotateAmount)
        elif func == "rotate down":
            rotateView(data, 0, -3*data.rotateAmount)
        elif func == "rotate left":
            rotateView(data, 3*data.rotateAmount, 0)
        elif func == "rotate right":
            rotateView(data, -3*data.rotateAmount, 0)

def init(data):
    data.border = 40
    data.lineWidth = 3 #Universal line thickness style
    initializeButtons(data)
    data.rooms = []
    data.wireFrameMode = True #Determines whether objects have fill
    data.bgColor = "light blue"
    data.windowColor = "gray"
    data.windowTitle = "3-D Building Modeler v1.08"
    data.compassColor = "red" #Color of the compass
    data.compassOrigin = (100,100, 0) #placement of the compass center
    data.compassLength = 40 #Length of each compass arrow
    data.modelCenter = (0,0,0)
    #True center of the model
    data.zoomLevel = 1.00 #Default value, applies a scalar to size of objects
    data.zoomInRatio = 1.25
    data.zoomOutRatio = .8 #Float values to multiple zoom level by
    data.actColor = "green" #Color to highlight element currently hovered over
    data.panAmount = 10 #Number of pixels to pan with each WASD stroke
    data.rotateAmount = 10 #Degrees to rotate by
    data.curRotX = 90 #Sets the current rotation angles for all rooms
    data.curRotY = 180 #Starts upright
    data.curPanorama = None #Holds image of the current panorama
    data.onHelpScreen = False
    data.possibleLocations = [] #Stores adjacent room placements as dots
    data.choosingNextLocation = False 
    #Stores whether user is selecting a spot for a new room currently
    data.chosenLocation = None
    data.locationRadius = 10 #XY radius for detecting location selection
    data.nextRoom = None #Temporarily stores a to-be-placed room
    data.compass = Compass(data.compassOrigin, data.compassLength, data.curRotX,
        data.curRotY)
    data.randomGenMode = True 
    #If user wishes, allows them to arbitrarily generate a map instead of 
    #scanning one.
    initializeCameraData(data)
    #Contains variables to store information about a room from the camera
    data.currentScale = 10 #Default box length equaling a meter
    data.scaleLocation = (2*data.border, data.height - 2*data.border)
    data.scaleLength = 100 #Visual length of the scale
    data.scaleMarkHeight = data.scaleLength // 10 #Height of scale markings
    data.metricUnits = ["m", "dm", "cm", "mm", "um"] 
    #Meters, decimeters, etc.
    data.selectedRoom = None
    data.textBoxLocation = (data.width // 2, data.height - data.border // 2)
    #Location of text entry box
    data.textBoxDims = (data.width // 12, data.border // 4) 
    #Length, height from center
    data.params = ["Width: ", "Height: ", "Depth: "]
    #Room parameters to alter
    data.enteredParam = False
    data.initializingParam = False
    data.currentParam = ""
    data.paramIndex = 0 #Current parameter to modify

def initializeButtons(data):
    data.buttonSize = 60 #Width/height of each button
    #Buttons are placed adjacent to each other starting from top-left corner
    data.helpButtonTopLeft = (data.width - data.buttonSize - 
        data.border, data.border) 
    data.helpButtonBotRight = (data.width - data.border, 
        data.border+data.buttonSize)
    data.viewButtonTopLeft = (data.width - 2*data.buttonSize - data.border, 
        data.border)
    data.viewButtonBotRight = (data.width - data.border - data.buttonSize, 
        data.border + data.buttonSize)
    data.newRoomButtonTopLeft = (data.width - 3*data.buttonSize - data.border,
        data.border)
    data.newRoomButtonBotRight = (data.width - 2*data.buttonSize - data.border,
        data.border + data.buttonSize)
    data.smallButtonSize = data.buttonSize // 3
    #Used for zoom, rotate, and pan buttons
    initializeSmallButtons(data)

def initializeSmallButtons(data):
    #Creates the zoom, pan, and rotate buttons
    x0, y0 = (data.width - 2*data.border, data.border + 2*data.buttonSize)
    size = data.smallButtonSize
    #Starting point of small buttons
    data.smallButtons = []
    zoomIn = smallButton("zoom in", size, x0, y0)
    zoomOut = smallButton("zoom out", size, x0, y0 + size)
    data.smallButtons.append(zoomIn)
    data.smallButtons.append(zoomOut)
    y0 += 3*size
    #Transitions to the panning D-pad
    up = smallButton("up", size, x0, y0)
    down = smallButton("down", size, x0, y0 + size)
    left = smallButton("left", size, x0 - size, y0 + size//2)
    right = smallButton("right", size, x0 + size, y0 + size//2)
    data.smallButtons.append(up)
    data.smallButtons.append(down)
    data.smallButtons.append(left)
    data.smallButtons.append(right)
    y0 += 3*size
    #Transitions to the rotating D-pad
    rup = smallButton("rotate up", size, x0, y0)
    rdown = smallButton("rotate down", size, x0, y0 + size)
    rleft = smallButton("rotate left", size, x0 - size, y0 + size//2)
    rright = smallButton("rotate right", size, x0 + size, y0 + size//2)
    data.smallButtons.append(rup)
    data.smallButtons.append(rdown)
    data.smallButtons.append(rleft)
    data.smallButtons.append(rright)

def initializeCameraData(data):
    data.roomWidth = None
    data.roomHeight = None
    data.roomDepth = None
    data.roomDoors = None

def analyzePanorama(data):
    #Gets the dimensions of the room and its doors
    return

def findDoors(data):
    return

def createNewRoom(data):
    #Generates rooms of random dimensions at the middle of the model
    if data.randomGenMode and not data.choosingNextLocation:
        width = random.randint(25, 50)
        height = random.randint(25, 50)
        depth = random.randint(25, 50)
        x = data.width // 2
        y = data.height // 2
        z = 0
        newRoom = room(x, y, width, height, depth, z, data.curRotX, 
            data.curRotY)
    elif not data.randomGenMode and data.curPanorama != None:
        analyzePanorama(data)
        width, height, depth = data.roomWidth, data.roomHeight, data.roomDepth
    if len(data.rooms) == 0:
        if not data.randomGenMode: 
        #Sets an arbitrary starting point for first captured room
            x = data.width // 2
            y = data.height // 2
            z = 0
        data.modelCenter = (x, y, z) #Sets first room as center of model
    else:
        if not data.choosingNextLocation:
            possibleLocations = getAdjacentRooms(data, width, 
                height, depth)
            for location in possibleLocations:
                dot = Dot(location, data.locationRadius, data.curRotX, 
                    data.curRotY)
                data.possibleLocations.append(dot)
            data.nextRoom = newRoom
            data.choosingNextLocation = True
            return
        else:
            newRoom = data.nextRoom
            curDot = data.chosenLocation
            x = curDot.x
            y = curDot.y
            z = curDot.z
            newRoom.x = x
            newRoom.y = y
            newRoom.z = z
            width = newRoom.width
            height = newRoom.height
            depth = newRoom.depth
            data.choosingNextLocation = False
            data.possibleLocations = []
            data.newRoom = None
    if data.randomGenMode:
        while len(newRoom.doors) < 3:
            dx, dy, dz, dWidth, dHeight, dDepth = createRandomDoorway(x, y, z,
                width, height, depth)
                    #Door dimensions
            newRoom.addDoorWay(dx, dy, dz, dWidth, dHeight, dDepth)
    else:
        findDoors(data)        
    data.rooms.append(newRoom)
    updateCenter(data)

def getAdjacentRooms(data, w, h, d):
    prevRoom = data.rooms[-1]
    prevX, prevY, prevZ = prevRoom.x, prevRoom.y, prevRoom.z
    prevW, prevH, prevD = prevRoom.width, prevRoom.height, prevRoom.depth
    possibleLocations = []
    for door in prevRoom.doors:
        doorX, doorY, doorZ = door.x, door.y, door.z
        doorW, doorH, doorD = door.width, door.height, door.depth
        y = prevY - prevH + h
        if doorW == 0:
            x = prevX + doorX
            if doorX < 0: x -= w
            else: x += w
            z = prevZ + doorZ
            if doorZ < 0: z -= d
            else: z += d
        elif doorD == 0:
            x = prevX + doorX
            if doorX < 0: x -= w
            else: x += w
            z = prevZ + doorZ
            if doorZ < 0: z -= d
            else: z += d
        possibleLocations.append((x, y, z))
        #Saves the xyz coord along with the shared door
    return possibleLocations

def createRandomDoorway(x, y, z, width, height, depth):
    dimensions = (x, z)
    constrainedDimension = random.choice(dimensions)
    #Constrains the doorway to a wall
    if constrainedDimension == x: 
        walls = (-width, width)
        dx, dWidth = random.choice(walls), 0
    else: 
        dWidth = random.randint(5, width/2 - 5)
        dx = random.randint(-width + dWidth, width - dWidth)
    if constrainedDimension == z: 
        walls = (-depth, depth)
        dz, dDepth = random.choice(walls), 0
    else: 
        dDepth = random.randint(5, depth/2 - 5)
        dz = random.randint(-depth + dDepth, depth - dDepth)
    dy, dHeight = 0, random.randint(5, height/2 - 5)
    return (dx, dy, dz, dWidth, dHeight, dDepth)

def updateCenter(data):
    #Runs algorithm to update the center of the model when +/- a room
    totalX = 0
    totalY = 0
    totalZ = 0
    if len(data.rooms) == 0: 
    #Prevents bad calculations if all rooms were deleted
        return
    else:
        for room in data.rooms:
            totalX += room.x
            totalY += room.y
            totalZ += room.z
        numRooms = len(data.rooms)
        finalX = totalX // numRooms
        finalY = totalY // numRooms
        finalZ = totalZ // numRooms #Calculates "center of mass" by averaging
        data.modelCenter = (finalX, finalY, finalZ)

def rotateView(data, rotX, rotY):
    #Rotates the model and updates existing rooms to this angle of rotation
    data.curRotX += rotX
    data.curRotY += rotY
    for room in data.rooms:
        room.rotX = data.curRotX
        room.rotY = data.curRotY
    data.compass.rotX = data.curRotX #Also updates the compass
    data.compass.rotY = data.curRotY

def panRooms(data, dx, dy):
    #Shifts current position of both the model center and each room
    for room in data.rooms:
        room.x += dx
        room.y += dy
        for door in room.doors:
            room.x += dx
            room.y += dy
    updateCenter(data)

def mousePressed(event, data):
    if withinHelpButton(data, event.x, event.y):
        data.onHelpScreen = not data.onHelpScreen #Toggles help screen
    elif data.onHelpScreen:
        return 
    #Prevents clicking buttons other than the help button if on the menu
    elif withinViewButton(data, event.x, event.y):
        data.wireFrameMode = not data.wireFrameMode #Toggles wireframe
    elif withinNewRoomButton(data, event.x, event.y):
        createNewRoom(data)
    elif data.choosingNextLocation:
        data.chosenLocation = selectedLocation(data, event.x, event.y)
        if data.chosenLocation != None:
            createNewRoom(data)
    elif clickedSmallButtons(data, event.x, event.y):
        return
    elif clickedRoom(data, event.x, event.y):
        return

def clickedSmallButtons(data, x, y):
    for button in data.smallButtons:
        if button.insideButton(x, y):
            button.performFunction(data)
            return True
    return False

def clickedRoom(data, x, y):
    for room in data.rooms:
        if room.insideRoom(data, x, y):
            data.selectedRoom = room
            data.initializingParam = True
            return True
    return False

def withinViewButton(data, x, y):
    if data.onHelpScreen: #Prevents changing viewmode while in help
        return False
    x1, y1 = data.viewButtonTopLeft
    x2, y2 = data.viewButtonBotRight
    return x >= x1 and y <= y2 and x <= x2 and y >= y1
    #Returns whether the coordinates are within the button's boundaries

def withinHelpButton(data, x, y):
    x1, y1 = data.helpButtonTopLeft
    x2, y2 = data.helpButtonBotRight
    return x >= x1 and y <= y2 and x <= x2 and y >= y1
    #Returns whether the coordinates are within the button's boundaries

def withinNewRoomButton(data, x, y):
    x1, y1 = data.newRoomButtonTopLeft
    x2, y2 = data.newRoomButtonBotRight
    return x >= x1 and y <= y2 and x <= x2 and y >= y1
    #Returns whether the coordinates are within the button's boundaries

def selectedLocation(data, x, y):
    r = data.locationRadius
    for dot in data.possibleLocations:
        coordinates = dot.getDotCenter(data) #Z isn't used in this
        x1 = coordinates[0]
        y1 = coordinates[1]
        if ((x - x1)**2 + (y - y1)**2)**.5 <= r:
            return dot
    return None

def keyPressed(event, data):
    #Prevents key commands on help menu
    if data.onHelpScreen:
        return
    elif data.selectedRoom != None:
        if event.keysym == "Return":
            data.enteredParam = True
        elif event.keysym == "BackSpace":
            data.currentParam = data.currentParam[:-1]
        elif event.keysym in string.digits:
            data.currentParam += event.keysym
    #Undo button
    elif event.keysym == "u":
        if not data.choosingNextLocation:
            data.rooms.pop()
            updateCenter(data)
        else: #Aborts generating a new room
            data.choosingNextLocation = False
            data.possibleLocations = []
            data.newRoom = None
    elif data.choosingNextLocation:
        return #Prevents any commands other than undo if choosing a room spot
    #Generates new room
    elif event.keysym == "n":
        createNewRoom(data)
    #Toggles random generation mode on/off
    elif event.keysym == "r":
        data.randomGenMode = not data.randomGenMode
    #Runs the camera
    elif event.keysym == "f":
        camCapture(data)
    #WASD keys pan the camera by a set amount by moving the rooms
    elif event.keysym == "w":
        panRooms(data, 0, data.panAmount)
    elif event.keysym == "s":
        panRooms(data, 0, -data.panAmount)
    elif event.keysym == "a":
        panRooms(data, data.panAmount, 0)
    elif event.keysym == "d":
        panRooms(data, -data.panAmount, 0)
    #UDLR keys rotate the camera
    elif event.keysym=="Up":
        rotateView(data, 0, data.rotateAmount)
    elif event.keysym=="Down":
        rotateView(data, 0, -data.rotateAmount)
    elif event.keysym=="Left":
        rotateView(data, data.rotateAmount, 0)
    elif event.keysym=="Right":
        rotateView(data, -data.rotateAmount, 0)
    elif event.keysym == "equal":
        data.zoomLevel *= data.zoomInRatio #Zooms in 25% if you hit +/=
    elif event.keysym == "minus":
        data.zoomLevel *= data.zoomOutRatio #Zooms out 20% if you hit -

def camCapture(data):
    #Retrieves a panorama from secondary file and stores it in data
    img = PanoramaStitching.runCamera()
    data.curPanorama = img

def timerFired(data):
    if data.selectedRoom != None:
        modifyRoomParams(data)

def modifyRoomParams(data):
    curParam = data.params[data.paramIndex]
    room = data.selectedRoom
    if data.enteredParam:
        entry = data.currentParam
        oldW, oldH, oldD = room.width, room.height, room.depth
        #Old dimensions of the room
        if curParam == "Width: ":
            if entry != None and entry != "" and entry != "0": 
                room.width = int(entry)
            #Prevents crashing
            data.paramIndex += 1
            data.currentParam = ""
            data.initializingParam = True
        elif curParam == "Height: ":
            if entry != None and entry != "" and entry != "0": 
                room.height = int(entry)
            data.paramIndex += 1
            data.currentParam = ""
            data.initializingParam = True
        else:
            if entry != None and entry != "" and entry != "0": 
                room.depth = int(entry)
            data.selectedRoom = None
            data.paramIndex = 0
            data.currentParam = ""
        data.enteredParam = False
        room.recalcDoors(oldW, oldH, oldD) #Refits the doors to the room
    elif data.initializingParam:
        if curParam == "Width: ":
            data.currentParam = str(room.width)
        elif curParam == "Height: ":
            data.currentParam = str(room.height)
        elif curParam == "Depth: ":
            data.currentParam = str(room.depth)
        data.initializingParam = False

def redrawAll(canvas, data):
    if data.onHelpScreen: 
        drawHelpScreen(canvas, data)
    else:
        drawRooms(canvas, data)
        drawSmallButtons(canvas, data)
        drawViewButton(canvas, data)
        drawNewRoomButton(canvas, data)
        drawCompass(canvas, data)
        drawVideo(canvas, data)
        drawScale(canvas, data)
        if data.choosingNextLocation:
            drawPossibleLocations(canvas, data)
    drawWindow(canvas, data)
    drawHelpButton(canvas, data)
    if data.selectedRoom != None:
        drawTextBox(canvas, data)

def drawTextBox(canvas, data):
    x, y = data.textBoxLocation
    w, h = data.textBoxDims
    canvas.create_rectangle(x - w, y - h, x + w, y + h, fill = "white")
    curParam = data.params[data.paramIndex]
    canvas.create_text(x - w, y, anchor = E, text = curParam, font = 
        "Helvetica 20 bold") #Creates label for current dimension
    entry = data.currentParam
    canvas.create_text(x + w, y, anchor = E, text = entry, font = 
        "Helvetica 20 bold")

def drawSmallButtons(canvas, data):
    for button in data.smallButtons:
        button.drawButton(canvas, data)

def drawWindow(canvas, data):
    #Top border
    canvas.create_rectangle(5, 5, data.width, data.border, 
        fill = data.windowColor, width = data.lineWidth)
    #Bottom border
    canvas.create_rectangle(5, data.height - data.border, 
        data.width, data.height,fill = data.windowColor,width = data.lineWidth)
    #Left border
    canvas.create_rectangle(5, 5, data.border, data.height, 
        fill = data.windowColor, width = data.lineWidth)
    #Right border
    canvas.create_rectangle(data.width - data.border, 5, data.width, 
        data.height, fill = data.windowColor, width = data.lineWidth)
    #Adding title of program
    canvas.create_text(data.width // 2, data.border // 2, 
        text = data.windowTitle, font = "Helvetica 20 bold")
    if data.randomGenMode:
        mode = "Random Generation"
        modeColor = "red"
    else:
        mode = "Camera Capture"
        modeColor = "blue"
    #Displays the current generation mode
    canvas.create_text(data.border + 5, data.border // 2, anchor = W,
        text = mode, fill = modeColor, font = "Helvetica 20 bold")

def drawViewButton(canvas, data):
    canvas.create_rectangle(data.viewButtonTopLeft, data.viewButtonBotRight,
        activeoutline = data.actColor, fill = data.windowColor, 
        width = data.lineWidth)
    innerX1, innerY1 = data.viewButtonTopLeft
    innerX2, innerY2 = data.viewButtonBotRight
    innerX1 += 10
    innerY1 += 10
    innerX2 -= 10
    innerY2 -= 10
    #Displays an icon based on which viewing mode is currently active
    if data.wireFrameMode:
        canvas.create_rectangle(innerX1, innerY1, innerX2, innerY2,
            fill = "beige", outline = "blue", width = 3)
    else:
        canvas.create_rectangle(innerX1, innerY1, innerX2, innerY2,
            outline = "blue", width = 3)

def drawHelpButton(canvas, data):
    x1, y1 = data.helpButtonTopLeft
    x2, y2 = data.helpButtonBotRight
    canvas.create_rectangle(x1, y1, x2, y2, activeoutline = data.actColor, 
        fill = data.windowColor, width = data.lineWidth)
    cx = (x1 + x2) // 2
    cy = (y1 + y2) // 2
    if data.onHelpScreen: #Sets to red if on the help screen, blue if not
        color = "red"
    else:
        color = "blue"
    canvas.create_text(cx, cy, text = "?", fill = color, 
        font = "Helvetica 40 bold")

def drawNewRoomButton(canvas, data):
    x1, y1 = data.newRoomButtonTopLeft
    x2, y2 = data.newRoomButtonBotRight
    canvas.create_rectangle(x1, y1, x2, y2, activeoutline = data.actColor, 
        fill = data.windowColor, width = data.lineWidth)
    cx = (x1 + x2) // 2
    cy = (y1 + y2) // 2
    canvas.create_text(cx, cy, text = "+", fill = "blue", 
        font = "Helvetica 40 bold")

def drawRooms(canvas, data):
    for room in data.rooms:
        room.drawRect(canvas, data)

def drawVideo(canvas, data):
    #Shows a panorama, mostly for testing purposes
    if data.curPanorama == None:
        pass
    else:
        image = Image.fromarray(data.curPanorama)
        photo = ImageTk.PhotoImage(image)
        label = Label(image = photo)
        label.image = photo
        label.pack(200, 200)

def drawCompass(canvas, data):
    data.compass.drawCompass(canvas, data)

def drawPossibleLocations(canvas, data):
    for dot in data.possibleLocations:
        dot.drawDot(canvas, data)

def drawHelpScreen(canvas, data):
    anchor = (data.border//2, data.border//2) #Top left corner of help screen
    helpText = """
    WASD - pan the camera
    Arrow Keys - rotate the model
    + and - zoom model in and out

    N - create first room and attach additional rooms
    U - undo previous room/exit room placement

    R - Toggles between random generation mode 
        and default camera capture
    F - Initiates camera mode (WARNING: BUGGY 
        AND UNFINISHED)
    """
    canvas.create_text(anchor, anchor = NW, text = helpText, fill = "blue",
        font = "Helvetica 30 bold")

def drawScale(canvas, data):
    x0, y0 = data.scaleLocation
    y1 = y0 - data.scaleMarkHeight
    x1 = x0 + data.scaleLength
    displayedLength = (data.scaleLength/(data.currentScale * data.zoomLevel))
        #Determines the current measurement based on settings and zoom
    unit, displayedLength = getUnit(data, displayedLength) 
    #Determines which metric unit to use and modifies displayedLength if it is 
    #smaller than a meter
    width = data.lineWidth
    canvas.create_line(x0, y0, x0, y1, width = width) #First marking
    canvas.create_line(x0, y0, x1, y0, width = width) #Scale
    canvas.create_line(x1, y0, x1, y1, width = width) #Second marking
    canvas.create_text((x1 + x0) // 2, (y1 + y0) // 2, anchor = S, 
        text = '%.2f' % displayedLength + unit, font = "Helvetica 20 bold")

def getUnit(data, distance, curIndex = 0):
    if curIndex == len(data.metricUnits): #Error handling
        return (data.metricUnits[-1], distance/10)
    elif distance > 1: #Base case
        return (data.metricUnits[curIndex], distance)
    else: #Recursive case
        return getUnit(data, distance*10, curIndex + 1)

def run(width=300, height=300):
    def redrawAllWrapper(canvas, data):
        canvas.delete(ALL)
        redrawAll(canvas, data)
        canvas.update()

    def mousePressedWrapper(event, canvas, data):
        mousePressed(event, data)
        redrawAllWrapper(canvas, data)

    def keyPressedWrapper(event, canvas, data):
        keyPressed(event, data)
        redrawAllWrapper(canvas, data)

    def timerFiredWrapper(canvas, data):
        timerFired(data)
        redrawAllWrapper(canvas, data)
        # pause, then call timerFired again
        canvas.after(data.timerDelay, timerFiredWrapper, canvas, data)
    # Set up data and call init
    class Struct(object): pass
    data = Struct()
    data.width = width
    data.height = height
    data.timerDelay = 100 # milliseconds
    init(data)
    # create the root and the canvas
    root = Tk()
    canvas = Canvas(root, width=data.width, height=data.height)
    canvas.pack()
    # set up events
    root.bind("<Button-1>", lambda event:
                            mousePressedWrapper(event, canvas, data))
    root.bind("<Key>", lambda event:
                            keyPressedWrapper(event, canvas, data))
    timerFiredWrapper(canvas, data)
    # and launch the app
    root.mainloop()  # blocks until window is closed

run(800, 600)