import numpy as np
import cv2
import matplotlib.pyplot as plt
import argparse
import glob

def auto_canny(image, sigma=0.20):
    # Compute the median of the single channel pixel intensities
    v = np.median(image)
    # Apply automatic Canny edge detection using the computed median
    lower = int(max(0, (1.0 - sigma) * v))
    upper = int(min(255, (1.0 + sigma) * v))
    edged = cv2.Canny(image, lower, upper)
    return edged 

def findAverageColor(img):
    # Ignore the alpha channel if it exists
    img = img[:, :, :-1]
    # Compute the average color
    average = img.mean(axis=0).mean(axis=0)
    return average

def findDominantColors(img, number_of_colors=2):
    # Convert image pixels to floating point and reshape into 1D array
    pixels = np.float32(img.reshape(-1, 3))

    # Ignore black pixels
    mask = np.all(pixels > [10, 10, 10], axis=1)  # Filter out pixels close to black
    pixels = pixels[mask]

    if pixels.size == 0:
        return None, None, None  # If there are no pixels after filtering, return None
    
    # Define the stopping condition for K-means clustering
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 200, 0.1)
    flags = cv2.KMEANS_RANDOM_CENTERS
    
    # Clustering pixel colors using the K-means algorithm
    _, labels, palette = cv2.kmeans(pixels, number_of_colors, None, criteria, 10, flags)
    _, counts = np.unique(labels, return_counts=True)
    
    # Find the color that appears most times as the dominant color
    dominant = palette[np.argmax(counts)]
    
    # Returns the dominant color, palette, and color count
    return dominant, palette, counts

def plotColors(img, palette, counts):
    # Sort the palette by color count
    indices = np.argsort(counts)[::-1]
    freqs = np.cumsum(np.hstack([[0], counts[indices] / counts.sum()]))
    rows = np.int_(img.shape[0] * freqs)
    dom_patch = np.zeros(shape=img.shape, dtype=np.uint8)
    
    # Fill color blocks according to the palette
    for i in range(len(rows) - 1):
        dom_patch[rows[i]:rows[i + 1], :, :] += np.uint8(palette[indices[i]])
    
    # Create a side-by-side display of an image and color blocks
    fig, (ax0, ax1) = plt.subplots(1, 2, figsize=(12, 6))
    ax0.imshow(img)
    ax0.set_title('original')
    ax0.axis('off')
    ax1.imshow(dom_patch)
    ax1.set_title('Dominant colors')
    ax1.axis('off')
    plt.show()

def find_circle(img):
    # Apply median filtering to smooth the image
    gimg = cv2.medianBlur(img, 5)
    
    # Detecting circles using Hough circle transform
    circles = cv2.HoughCircles(gimg, cv2.HOUGH_GRADIENT, 4, 2, param1=50, param2=20, minRadius=0, maxRadius=0)
    circles = np.uint16(np.around(circles))
    
    # Draw the detected circle on the image
    for i in circles[0, :]:
        cv2.circle(img, (i[0], i[1]), i[2], (0, 255, 0), 2)
        cv2.circle(img, (i[0], i[1]), 2, (0, 0, 255), 3)
    
    # Display the result image and wait for the user to press a key
    cv2.imshow('detected circles', img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    
    # Returns the detected circle
    return circles

def find_circle2(img):
    # Convert the image to grayscale
    gimg = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # Apply median filtering to smooth the image
    gimg = cv2.medianBlur(gimg, 5)
    
    # Use automatic Canny edge detection
    edges = auto_canny(img)
    
    # Return edge image
    return edges

def distance(color1, color2):
    """
    Calculate the distance between two colors
    """
    d = np.sqrt(np.square((color1[0] - color2[0])) + np.square((color1[1] - color2[1])) + np.square((color1[2] - color2[2])))
    
    # Returns the color distance
    return d