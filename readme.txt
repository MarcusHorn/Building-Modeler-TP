

=== 3-D Building Modeler ===
Author: Marcus Horn
Python version: 2.7
Modules: operator, random, math, sys, time, numpy, cv2, string, Tkinter, PIL


=== Project Description ===

The 3-D Building Modeler included here is a set of python scripts that run
a simulation window that allows the user to generate, modify, and view a
three-dimensional model of a building floor plan. Rooms of the building are
represented by cubes that connect to each other via doorways. The program has
a fully functional random generation mode along with a work-in-progress camera
capture mode for analyzing physical rooms to create the model.


=== Using the Program ===

To use the program, run the Building Viewer Client file using Python ver. 2.7.
This requires the external files PanoramaStitching.py, stitch.py, and the Stitching directory to be included at the same level as this file.

To get started, click the ‘?’ icon at the top-right of the screen to see the concise list of relevant commands. Most notably, press N or click the large ‘+’ icon to create a new room. The first room will be automatically placed, while for subsequent rooms you must choose one of the nodes that will appear on the screen in order to attach the new room to the previous one. This allows you to decide which door the two rooms will share and in which direction you wish to expand the model.

Also, press “ESC” to exit camera capture mode.

=== Dependencies ===

The program requires the built-in modules operator, random, math, sys, time,
string, and Tkinter to run. It also requires the external libraries OpenCV,
PIL, and NumPy. Installing these packages is easiest by using Pip via terminal.

OpenCV: 'pip install cv2' in terminal or www.opencv.org
PIL: 'pip install Pillow' or https://python-pillow.org
NumPy: pip install numpy or www.numpy.org