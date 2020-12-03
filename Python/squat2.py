# Dit programma berkent de lichaamsposities van alle foto's in een map
# Wanneer de hoek van de knie het kleinst is zal het programma checken
# of je knie voor je voeten uitsteekt of niet en je een score geven

import sys
import cv2
import os
from sys import platform
import argparse
import time
import numpy as np
import ntpath
import json

def angle(a, b, c, d):
    A = np.sqrt((d[0] - c[0])**2 + (d[1] - c[1])**2)
    D = np.sqrt((b[0] - a[0])**2 + (b[1] - a[1])**2)
    B = np.sqrt((b[0] - a[0] + d[0] - c[0])**2 + (b[1] - a[1] + d[1] - c[1])**2)

    cos_theta = (A**2 + D**2 - B**2)/(2 * A * D)

    return np.arccos(cos_theta)

def check(poses, angles, min_index):
    min_keyp = poses[min_index]

    ye = [min_keyp[0][knie][0], min_keyp[0][teen][0]]
    yee = [min_keyp[0][knie][1], min_keyp[0][heup][1]]
    yeye = min(ye)/max(ye)
    yeyee = min(yee)/max(yee)
    knie_teen = min_keyp[0][knie][0] - min_keyp[0][teen][0]
    knie_heup = min_keyp[0][knie][1] - min_keyp[0][heup][1]
    """
    if yeye < 0.9:
        print("Slecht, je kan er niks van. Dit is je score:", yeye)
    elif yeye < 0.95:
        print("Hmm, niet slecht, maar dit kan beter. Dit is je score:", yeye)
    elif yeye < 0.99:
        print("Super! Je bent echt goed in squats. Dit is je score:", yeye)
    else:
        print("Jij bent de squatkoning/squatkoningin. Dit is je score:", yeye)
    """
    print("Staat de knie boven de voet? Score:", yeye)
    print("Is de heup op de hoogte van de knie? Score:", yeyee)
    print("Afstand tussen knie en teen (op x-as):", knie_teen)
    print("Afstand tussen knie en heup (op y-as):", knie_heup)

try:
    # Import Openpose (Windows/Ubuntu/OSX)
    dir_path = os.path.dirname(os.path.realpath(__file__))
    try:
        # Windows Import
        if platform == "win32":
            # Change these variables to point to the correct folder (Release/x64 etc.)
            sys.path.append(dir_path + '/../../python/openpose/Release');
            os.environ['PATH']  = os.environ['PATH'] + ';' + dir_path + '/../../x64/Release;' +  dir_path + '/../../bin;'
            import pyopenpose as op
        else:
            # Change these variables to point to the correct folder (Release/x64 etc.)
            sys.path.append('../../python');
            # If you run `make install` (default path is `/usr/local/python` for Ubuntu), you can also access the OpenPose/python module from there. This will install OpenPose and the python library at your desired installation path. Ensure that this is in your python path in order to use it.
            # sys.path.append('/usr/local/python')
            from openpose import pyopenpose as op
    except ImportError as e:
        print('Error: OpenPose library could not be found. Did you enable `BUILD_PYTHON` in CMake and have this Python script in the right folder?')
        raise e

    # Flags
    parser = argparse.ArgumentParser()
    parser.add_argument("--image_dir", default="../../../examples/media/", help="Process a directory of images. Read all standard formats (jpg, png, bmp, etc.).")
    parser.add_argument("--no_display", default=False, help="Enable to disable the visual display.")
    args = parser.parse_known_args()

    # Custom Params (refer to include/openpose/flags.hpp for more parameters)
    params = dict()
    params["model_folder"] = "../../../models/"

    # Add others in path?
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

    # Construct it from system arguments
    # op.init_argv(args[1])
    # oppython = op.OpenposePython()

    # Starting OpenPose
    opWrapper = op.WrapperPython()
    opWrapper.configure(params)
    opWrapper.start()

    # Read frames on directory
    imagePaths = op.get_images_on_directory(args[0].image_dir);
    start = time.time()

    poses = []
    angles = []
    # Process and display images

    # Geef de coordinaten van bepaalde lichaamsdelen naargelang de richting waarnaar de persoon kijkt

    index = 0
    for imagePath in imagePaths:
        imagename = ntpath.basename(imagePath)
        if os.path.isfile("keypoints_" + imagename + ".txt"):
            keypoints = np.loadtxt("keypoints_" + imagename + ".txt")
            keyp = [keypoints]
            poses.append(keyp)
            if keyp[0][1][0] > keyp[0][8][0]:
                heup, knie, enkel = 9, 10, 11
                schouder, pols = 2, 4
                teen = 23
            else:
                heup, knie, enkel = 12, 13, 14
                schouder, pols = 5, 7
                teen = 20
            theta = angle(keyp[0][heup], keyp[0][knie], keyp[0][knie], keyp[0][enkel])
            angles.append(theta)
            print("----------------------")
            print(index+1)
            check(poses, angles, index)
            """
            if index > 0:
                if angles[index] > angles[index - 1]:
                    break
                        """
            index += 1

        else:       
            datum = op.Datum()
            imageToProcess = cv2.imread(imagePath)
            datum.cvInputData = imageToProcess
            opWrapper.emplaceAndPop([datum])
            keyp = datum.poseKeypoints
            np.savetxt("keypoints_" + imagename + ".txt", keyp[0])
            poses.append(keyp)
            if keyp[0][1][0] > keyp[0][8][0]:
                heup, knie, enkel = 9, 10, 11
                schouder, pols = 2, 4
                teen = 23
            else:
                heup, knie, enkel = 12, 13, 14
                schouder, pols = 5, 7
                teen = 20
            theta = angle(keyp[0][heup], keyp[0][knie], keyp[0][knie], keyp[0][enkel])
            angles.append(theta)
            print("----------------------")
            print(index+1)
            check(poses, angles, index)
            """
            if index > 0:
                if angles[index] > angles[index - 1]:
                    break
                        """
            index += 1

    end = time.time()
    print("Total time: " + str(end - start) + " seconds")
except Exception as e:
    print(e)
    sys.exit(-1)
