import cv2
import numpy as np
import matplotlib.pyplot as plt
from utils_Yunhao import findAverageColor, findDominantColors, plotColors, find_circle2, distance


def filter_purple_areas(img):
    hsv_img = cv2.cvtColor(img, cv2.COLOR_RGB2HSV)
    # Updated HSV color range to match purple more accurately
    lower_purple = np.array([130, 40, 40]) 
    upper_purple = np.array([160, 255, 255])
    purple_mask = cv2.inRange(hsv_img, lower_purple, upper_purple)
    
    # Apply morphological operations to purify the mask
    kernel = np.ones((5,5), np.uint8)
    purple_mask = cv2.morphologyEx(purple_mask, cv2.MORPH_CLOSE, kernel)
    purple_mask = cv2.morphologyEx(purple_mask, cv2.MORPH_OPEN, kernel)
    
    return purple_mask

# def filter_white_areas(img):
#     hsv_img = cv2.cvtColor(img, cv2.COLOR_RGB2HSV)
#     lower_white = np.array([0, 0, 200])  
#     upper_white = np.array([180, 25, 255])
#     white_mask = cv2.inRange(hsv_img, lower_white, upper_white)

#    
#     kernel = np.ones((5, 5), np.uint8)
#     white_mask = cv2.morphologyEx(white_mask, cv2.MORPH_CLOSE, kernel)
#     white_mask = cv2.morphologyEx(white_mask, cv2.MORPH_OPEN, kernel)
    
#     return white_mask


def quantify_colors(imgpath, numberofcolors):
    img = cv2.imread(imgpath)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    purple_mask = filter_purple_areas(img)
    # white_mask = filter_white_areas(img)
    # combined_mask = cv2.bitwise_or(purple_mask, white_mask) #？？？
    img_masked = cv2.bitwise_and(img, img, mask=purple_mask)
    dominant, palette, counts = findDominantColors(img_masked, numberofcolors)
    plotColors(img, palette, counts)
    return dominant, palette, counts, img

if __name__ == '__main__':
    imgpath = '/Users/huangyunhao/Desktop/testreader/Color_Yunhao/1_1_positive_white_background.bmp'  # Change to your new image path
    numberofcolors = 5
    dominant, palette, counts, img = quantify_colors(imgpath, numberofcolors)
    print("Dominant Color (RGB):", dominant)
    # Showing an image with a purple filter mask
    mask = filter_purple_areas(img)
    plt.figure()
    plt.imshow(mask, cmap='gray')
    plt.title('Purple Mask')
    plt.show()

    edges = find_circle2(img)
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if contours:
        big_contour = max(contours, key=cv2.contourArea)
        (x_center, y_center), radius = cv2.minEnclosingCircle(big_contour)
        center = (int(x_center), int(y_center))
        print(f"Center of the detected area: {center}, Radius: {radius}")

        # Draw the detected circle and center on the image
        cv2.circle(img, center, int(radius), (0, 255, 0), 2)
        cv2.circle(img, center, 5, (255, 0, 0), -1)

        numberofcircles = 20
        pixel_per_area = 25
        result_image = np.zeros_like(img)
        previous_radius = 0

        for each in range(numberofcircles):
            current_radius = int(radius + pixel_per_area * (each + 1))
            mask = np.zeros_like(img)
            cv2.circle(mask, center, current_radius, (255, 255, 255), thickness=-1)
            mask_gray = cv2.cvtColor(mask, cv2.COLOR_BGR2GRAY)
            masked_img = cv2.bitwise_and(img, img, mask=mask_gray)
            pixels = masked_img.reshape(-1, 3)
            non_black_pixels_mask = np.all(pixels != [0, 0, 0], axis=1)
            non_black_pixels = pixels[non_black_pixels_mask]
            mean_color = np.mean(non_black_pixels, axis=0) if non_black_pixels.size else [0, 0, 0]
            result_image[mask_gray == 255] = mean_color
            previous_radius = current_radius
        
        # Display final result
        cv2.imshow('Detected Areas with Average Colors', result_image)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    # Showing an image with purple and white filter masks
    # purple_mask = filter_purple_areas(img)
    # white_mask = filter_white_areas(img)
    # plt.figure()
    # plt.subplot(1, 2, 1)
    # plt.imshow(purple_mask, cmap='gray')
    # plt.title('Purple Mask')
    # plt.subplot(1, 2, 2)
    # plt.imshow(white_mask, cmap='gray')
    # plt.title('White Mask')
    # plt.show()
