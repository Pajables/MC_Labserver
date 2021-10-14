import numpy as np
import cv2 as cv

class AzoSynthesis:
    def __init__(self):
        pass

    def get_reaction_colour(self, img, roi):
        cropped_image = img[roi[1]:roi[1]+roi[3], roi[0]:roi[0]+roi[2]]
        mask = self.generate_mask(cropped_image)
        result = cv.bitwise_and(cropped_image, cropped_image, mask=mask)
        return self.get_colour(result)

    def get_colour(self, img):
        average_colour = img.mean(axis=0).mean(axis=0)
        for i, c in enumerate(average_colour):
            average_colour[i] = round(c)
        return average_colour

    def generate_mask(self, img):
        # extract centre of image where colour is dominant
        height = len(img)
        width = len(img[0])
        lower_height = int(height/3)
        upper_height = int(height/3) * 2
        lower_width = int(width/3)
        upper_width = int(width/3)*2
        hsv_img = cv.cvtColor(img, cv.COLOR_BGR2HSV_FULL)
        centre_of_img = img[lower_height:upper_height, lower_width:upper_width]
        avg_colour = self.get_colour(centre_of_img)
        avg_img = np.ones((200,200,3), np.uint8)
        avg_img[:,:] = avg_colour
        hsv_ave_img = cv.cvtColor(avg_img, cv.COLOR_BGR2HSV_FULL)
        hsv_ave = hsv_ave_img[0][0]
        lower_limit = np.array([hsv_ave[0]-15, int(hsv_ave[1]/2), int(hsv_ave[2]/2)])
        upper_limit = np.array([hsv_ave[0]+15, 255, 255])
        return cv.inRange(hsv_img, lower_limit, upper_limit)

    