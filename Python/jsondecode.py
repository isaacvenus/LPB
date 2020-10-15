import json
import numpy as np

##
# XDDDDD
class decode:
    def __init__(self, json_file):
        self._file = json.load(open(json_file, 'r'))
    ##
    # Geeft de coordinaten van het lichaam
    def get_pose_keypoints(self):
        return self._file['people'][0]['pose_keypoints_2d']
    ##
    # Geeft de coordinaten van het gezicht
    def get_face_keypoints(self):
        return self._file['people'][0]['face_keypoints_2d']

    ##
    # Geeft de coordinaten van het linker hand
    def get_hand_left_keypoints(self):
        return self._file['people'][0]['hand_left_keypoints_2d']

    ##
    # Geeft de coordinaten van het rechter hand
    def get_hand_right_keypoints(self):
        return self._file['people'][0]['hand_right_keypoints_2d']

##
# Maak een dictionary van de gekregen lijst van als value [x, y, acc] en als key
# de code van die coordinaat
def add_coor(li):
    num = 0
    d = {}
    for i in range(0, len(li), 3):
        d[num] = li[i:i+3]
        num += 1
    return d

def angle(a, b, c, d):
    A = np.sqrt((d[0] - c[0])**2 + (d[1] - c[1])**2)
    D = np.sqrt((b[0] - a[0])**2 + (b[1] - a[1])**2)
    B = np.sqrt((b[0] - a[0] + d[0] - c[0])**2 + (b[1] - a[1] + d[1] - c[1])**2)

    cos_theta = (A**2 + D**2 - B**2)/(2 * A * D)

    return np.arccos(cos_theta)

def main():
    # Improrteer het json bestand
    Decode = decode('/Users/isaac/Desktop/man_keypoints.json')
    # Haal er de gewenste info uit en geef de coordinaten een naam
    coor = add_coor(Decode.get_pose_keypoints())
    # Bereken de hoek en print het
    print(np.degrees(angle(coor[0], coor[1], coor[1], coor[5])))


if __name__ == '__main__':
    main()
