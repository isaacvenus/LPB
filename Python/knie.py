# Dit programma is een aangepaste versie van de voorbeeldprogramma's van openpose

# Hoe te gebruiken:
# python fiets.py path/to/image
# Werkt enkel in de map /openpose/build/examples/tutorial_api_python
# Anders moet je params["model_folder"] = "../../../models/" aanpassen

import sys
import cv2
import os
import numpy as np
import sympy as sp
from sys import platform
import ntpath
import json

def angle(a, b, c, d):
    A = np.sqrt((d[0] - c[0])**2 + (d[1] - c[1])**2)
    D = np.sqrt((b[0] - a[0])**2 + (b[1] - a[1])**2)
    B = np.sqrt((b[0] - a[0] + d[0] - c[0])**2 + (b[1] - a[1] + d[1] - c[1])**2)

    cos_theta = (A**2 + D**2 - B**2)/(2 * A * D)

    return np.arccos(cos_theta)
def centimeter(lengtedijbeen,a,b):
    AB = np.sqrt((b[0] - a[0])**2 + (b[1] - a[1])**2)
    return lengtedijbeen/AB

def voorstel(keyp):
    lengtedijbeen = int(input("Wat is de lengte van je dijbeen in centimeter? "))
    # check naar welke richting de fietser kijkt
    if keyp[0][1][0] > keyp[0][8][0]:
        heup, knie, enkel = 9, 10, 11
    else:
        heup, knie, enkel = 12, 13, 14
    theta_1 = angle([keyp[0][1][0], keyp[0][8][1]], keyp[0][8], keyp[0][8], keyp[0][1])
    theta_2 = angle(keyp[0][8], keyp[0][1], keyp[0][2], keyp[0][3])
    theta_3 = angle(keyp[0][heup], keyp[0][knie], keyp[0][knie], keyp[0][enkel])
    print("-------------------------------")
    print("Hoek tussen rug en horizontale:")
    print(np.degrees(theta_1))
    print("-------------------------------")
    print("Hoek tussen rug en opperarmbeen:")
    print(np.degrees(theta_2))
    print("-------------------------------")
    print("Hoek van de knie")
    print(np.degrees(theta_3))

    # Bepalen van de zadelhoogte om de optimale hoek van de knie te bekomen.

    lengte_dijbeen = np.sqrt((keyp[0][heup][0] - keyp[0][knie][0])**2 + (keyp[0][heup][1] - keyp[0][knie][1])**2)
    lengte_scheenbeen = np.sqrt((keyp[0][knie][0] - keyp[0][enkel][0])**2 + (keyp[0][knie][1] - keyp[0][enkel][1])**2)

    c = np.sqrt(lengte_scheenbeen**2 + lengte_dijbeen**2 - 2*lengte_dijbeen*lengte_scheenbeen*np.cos(np.radians(140)))
    A_y = keyp[0][enkel][1] - (np.sqrt(c**2-(keyp[0][enkel][0] - keyp[0][heup][0])**2)) 
    print("-------------------------------")
    print("Mag ik voorstellen om het zadel te verhogen/verlagen met:")
    print((keyp[0][8][1] - A_y)*centimeter(lengtedijbeen,keyp[0][heup],keyp[0][knie]), " centimeter")


try:
    dir_path = os.path.dirname(os.path.realpath(__file__))
    try:
        # Windows Import
        if platform == "win32":
            sys.path.append(dir_path + '/../../python/openpose/Release');
            os.environ['PATH']  = os.environ['PATH'] + ';' + dir_path + '/../../x64/Release;' +  dir_path + '/../../bin;'
            import pyopenpose as op
        else:
            #sys.path.append('../../python');
            sys.path.append('/usr/local/python')
            from openpose import pyopenpose as op
    except ImportError as e:
        print('Error: OpenPose library could not be found. Did you enable `BUILD_PYTHON` in CMake and have this Python script in the right folder?')
        raise e


    # Custom Params (refer to include/openpose/flags.hpp for more parameters)
    params = dict()
    params["model_folder"] = "../../../models/"
    
    imagename = ntpath.basename(sys.argv[1])
    imagename.replace(".png", "")
    imagename.replace(".jpg", "")
    imagename.replace(".jpeg", "")
    # check of je al de positie hebt berekend
    if os.path.isfile("keypoints_" + imagename + ".txt"):
        keypoints = np.loadtxt("keypoints_" + imagename + ".txt")
        keypoints = [keypoints]
        voorstel(keypoints)
    else:
        # Starting OpenPose
        opWrapper = op.WrapperPython()
        opWrapper.configure(params)
        opWrapper.start()
    
        # Process Image
        datum = op.Datum()
        imageToProcess = cv2.imread(sys.argv[1])
        datum.cvInputData = imageToProcess
        opWrapper.emplaceAndPop([datum])
        keyp = datum.poseKeypoints
        np.savetxt("keypoints_" + imagename + ".txt", keyp[0])
        voorstel(keyp)
        # Display Image
        #print("Body keypoints: \n" + str(datum.poseKeypoints))
        cv2.imshow("OpenPose 1.6.0 - Tutorial Python API", datum.cvOutputData)
        cv2.waitKey(0)
except Exception as e:
    print(e)
    sys.exit(-1)

## Algoritme voor wijzigen van de stemlengte mbv schouderhoek

def schouderhoek(H,S,Z):

    #H zijn coördinaten van hand op het stuur
    #S zijn coördinaten van de schouder
    #Z zijn coördinaten van het zadel (na eventueel aanpassen van hoogte)

    SZ = np.sqrt((S[0]-Z[0])**2 + (S[1]-Z[1])**2)
    HS = np.sqrt((S[0]-H[0])**2 + (S[1]-H[1])**2)
    HZ = np.sqrt((Z[0]-H[0])**2 + (Z[1]-H[1])**2)

    cos_alfa = (SZ**2 + HS**2 - HZ**2)/(2*SZ*HS)

    return np.arccos(cos_alfa)



def circle_intersection(circle1, circle2):
    '''
    @summary: calculates intersection points of two circles
    @param circle1: tuple(x,y,radius)
    @param circle2: tuple(x,y,radius)
    @result: tuple of intersection points (which are (x,y) tuple)
    '''
     # return self.circle_intersection_sympy(circle1,circle2)
    x1, y1, r1 = circle1
    x2, y2, r2 = circle2
    # http://stackoverflow.com/a/3349134/798588
    dx, dy = x2 - x1, y2 - y1
    d = np.sqrt(dx * dx + dy * dy)
    if d > r1 + r2:
        print("#1")
        return None  # no solutions, the circles are separate
    if d < abs(r1 - r2):
        print("#2")
        return None  # no solutions because one circle is contained within the other
    if d == 0 and r1 == r2:
        print("#3")
        return None  # circles are coincident and there are an infinite number of solutions

    a = (r1 * r1 - r2 * r2 + d * d) / (2 * d)
    h = np.sqrt(r1 * r1 - a * a)
    xm = x1 + a * dx / d
    ym = y1 + a * dy / d
    xs1 = xm + h * dy / d
    xs2 = xm - h * dy / d
    ys1 = ym - h * dx / d
    ys2 = ym + h * dx / d

    return (xs1, ys1), (xs2, ys2)


def wijzig_stemlengte(H,S,Z):
    # H zijn coördinaten van hand op het stuur
    # S zijn coördinaten van de schouder
    # Z zijn coördinaten van het zadel (na eventueel aanpassen van hoogte)

    SZ = np.sqrt((S[0]-Z[0])**2 + (S[1]-Z[1])**2)
    HS = np.sqrt((S[0]-H[0])**2 + (S[1]-H[1])**2)

    alfa = schouderhoek(H,S,Z)
    if (np.pi/2) < alfa < (np.pi/2 + 5/180 * np.pi):
        print("De lengte van de stuurpen is goed")
    elif alfa < np.pi/2:
        global a
        a = 1
        while alfa < np.pi/2:
            H[0] -= a
            snijpunten = circle_intersection((H[0],H[1],HS),(Z[0],Z[1],SZ))
            #S is nu het snijpunt met de kleinste y-waarde, dus het snijpunt dat het hoogst gelegen is op de foto
            hoogste_snijpunt = snijpunten[0]
            if snijpunten[1][1] > snijpunten[0][1]:
                hoogste_snijpunt = snijpunten[1]

            alfa = schouderhoek(H,hoogste_snijpunt,Z)
            a += 1

    print(a)

    return a
