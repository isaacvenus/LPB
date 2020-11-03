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

def angle(a, b, c, d):
    A = np.sqrt((d[0] - c[0])**2 + (d[1] - c[1])**2)
    D = np.sqrt((b[0] - a[0])**2 + (b[1] - a[1])**2)
    B = np.sqrt((b[0] - a[0] + d[0] - c[0])**2 + (b[1] - a[1] + d[1] - c[1])**2)

    cos_theta = (A**2 + D**2 - B**2)/(2 * A * D)

    return np.arccos(cos_theta)

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
    theta_1 = angle([keyp[0][1][0], keyp[0][8][1]], keyp[0][8], keyp[0][8], keyp[0][1])
    theta_2 = angle(keyp[0][8], keyp[0][1], keyp[0][2], keyp[0][3])
    print("-------------------------------")
    print("Hoek tussen rug en horizontale:")
    print(np.degrees(theta_1))
    print("-------------------------------")
    print("Hoek tussen rug en opperarmbeen:")
    print(np.degrees(theta_2))
    
    # berekenen van de correctie op het zadel om de hoek tussen de rug en de
    # horizontale 45° te maken
    lengte_rug = np.sqrt((keyp[0][1][0] - keyp[0][8][0])**2 + (keyp[0][1][1] - keyp[0][8][1])**2)
    hoogte_schouder = (keyp[0][8][1] - keyp[0][1][1])
    l = np.sqrt(0.5) * lengte_rug
    verhogen = hoogte_schouder - l
    print("-------------------------------")
    print("Mag ik voorstellen om het zadel te verhogen/verlagen met:")
    print(verhogen)
    

    # Display Image
    #print("Body keypoints: \n" + str(datum.poseKeypoints))
    cv2.imshow("OpenPose 1.6.0 - Tutorial Python API", datum.cvOutputData)
    cv2.waitKey(0)
except Exception as e:
    print(e)
    sys.exit(-1)
