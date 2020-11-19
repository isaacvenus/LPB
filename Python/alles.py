# Dit programma is een aangepaste versie van de voorbeeldprogramma's van openpose

# Hoe te gebruiken:
# python fiets.py path/to/image
# Werkt enkel in de map /openpose/build/examples/tutorial_api_python
# Anders moet je params["model_folder"] = "../../../models/" aanpassen

import sys
import cv2
import os
import numpy as np
from sys import platform
import ntpath
import json
import argparse

def angle(a, b, c, d):
    A = np.sqrt((d[0] - c[0])**2 + (d[1] - c[1])**2)
    D = np.sqrt((b[0] - a[0])**2 + (b[1] - a[1])**2)
    B = np.sqrt((b[0] - a[0] + d[0] - c[0])**2 + (b[1] - a[1] + d[1] - c[1])**2)

    cos_theta = (A**2 + D**2 - B**2)/(2 * A * D)

    return np.arccos(cos_theta)

def centimeter(lengtedijbeen,a,b):
    AB = np.sqrt((b[0] - a[0])**2 + (b[1] - a[1])**2)
    return lengtedijbeen/AB

def lengte(a, b):
    return np.sqrt((a[0] - b[0])**2 + (a[1] - b[1])**2)

def cos_regel(a, b, theta):
    return a**2 + b**2 - 2*a*b*np.cos(np.radians(theta))

def voorstel(keyp):
    lengtedijbeen = int(input("Wat is de lengte van je dijbeen in centimeter? "))
    # check naar welke richting de fietser kijkt
    if keyp[0][1][0] > keyp[0][8][0]:
        heup, knie, enkel = 9, 10, 11
        schouder, pols = 2, 4
    else:
        heup, knie, enkel = 12, 13, 14
        schouder, pols = 5, 7
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

    lengte_dijbeen = lengte(keyp[0][heup], keyp[0][knie])
    lengte_scheenbeen = lengte(keyp[0][knie], keyp[0][enkel])
    c = cos_regel(lengte_scheenbeen, lengte_dijbeen, 140)
    A_y = keyp[0][enkel][1] - (np.sqrt(c-(keyp[0][enkel][0] - keyp[0][heup][0])**2)) 
    A = [keyp[0][8][0], A_y]
    print("-------------------------------")
    print("Mag ik voorstellen om het zadel te verhogen/verlagen met:")
    print((keyp[0][8][1] - A_y)*centimeter(lengtedijbeen,keyp[0][heup],keyp[0][knie]), " centimeter")

    lengte_rug = lengte(keyp[0][8], keyp[0][1])
    lengte_arm = lengte(keyp[0][schouder], keyp[0][pols])
    c2 = cos_regel(lengte_rug, lengte_arm, 90)
    if keyp[0][1][0] > keyp[0][8][0]:
        pols_x = np.sqrt(c2 - (keyp[0][pols][1] - A[1])**2) + A[0]
    else:
        pols_x = -np.sqrt(c2 - (keyp[0][pols][1] - A[1])**2) + A[0]
    print("-------------------------------")
    print("Mag ik voorstellen om het stuur te verkorten/verlengen met:")
    print((pols_x - keyp[0][pols][0])*centimeter(lengtedijbeen,keyp[0][heup],keyp[0][knie]), " centimeter")



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
    
    
    parser = argparse.ArgumentParser()
    parser.add_argument("--image_path", default="../../../examples/media/COCO_val201    4_000000000192.jpg", help="Process an image. Read all standard formats (jpg, png, bm    p, etc.).")
    args = parser.parse_known_args()
    
    # Custom Params (refer to include/openpose/flags.hpp for more parameters)
    params = dict()
    params["model_folder"] = "../../../models/"
    for i in range(0, len(args[1])):
        curr_item = args[1][i]
        if i != len(args[1])-1: next_item = args[1][i+1]
        else: next_item = "1"
        if "--" in curr_item and "--" in next_item:
            key = curr_item.replace('-','')
            if key not in params:  params[key] = "1"
        elif "--" in curr_item and "--" not in next_item:
            key = curr_item.replace('-','')
            if key not in params: params[key] = next_item
    
    imagename = ntpath.basename(args[0].image_path)
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
        imageToProcess = cv2.imread(args[0].image_path)
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

