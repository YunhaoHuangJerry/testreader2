from utils_Yunhao import find_circle2, findDominantColors
import cv2
import numpy as np
import json
import os
from sklearn.svm import SVC
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

def auto_canny(image, sigma=0.33):
    v = np.median(image)
    lower = int(max(0, (1.0 - sigma) * v))
    upper = int(min(255, (1.0 + sigma) * v))
    edged = cv2.Canny(image, lower, upper)
    return edged

def find_contours(img):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    edges = auto_canny(blurred)
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    return contours

def get_mean_color(img, contour):
    mask = np.zeros_like(img)
    cv2.drawContours(mask, [contour], -1, (255, 255, 255), thickness=cv2.FILLED)
    mask_gray = cv2.cvtColor(mask, cv2.COLOR_BGR2GRAY)
    masked_img = cv2.bitwise_and(img, img, mask=mask_gray)
    pixels = masked_img.reshape(-1, 3)
    non_black_pixels_mask = np.all(pixels != [0, 0, 0], axis=1)
    non_black_pixels = pixels[non_black_pixels_mask]
    mean_color = np.mean(non_black_pixels, axis=0) if non_black_pixels.size else [0, 0, 0]
    return mean_color

def get_mean_colors_from_image(image_path):
    img = cv2.imread(image_path)
    contours = find_contours(img)

    # Find the two largest contours, assuming that these two contours are the area of interest
    contours = sorted(contours, key=cv2.contourArea, reverse=True)[:2]

    mean_colors = []
    for contour in contours:
        mean_color = get_mean_color(img, contour)
        mean_colors.append(mean_color.tolist())
    
    if len(mean_colors) == 2:
        mean_color = np.mean(mean_colors, axis=0).tolist()
    else:
        mean_color = [0, 0, 0]

    return mean_color

def get_mean_colors_from_directory(directory_path):
    mean_colors = []
    for filename in os.listdir(directory_path):
        if filename.endswith((".jpg", ".jpeg", ".png")):
            img_path = os.path.join(directory_path, filename)
            mean_color = get_mean_colors_from_image(img_path)
            mean_colors.append(mean_color)
    return mean_colors

def store_all_sample_colors(positive_dir, negative_dir):
    positive_colors = get_mean_colors_from_directory(positive_dir)
    negative_colors = get_mean_colors_from_directory(negative_dir)

    samples = {
        "positive": positive_colors,
        "negative": negative_colors
    }

    with open("sample_colors.json", "w") as f:
        json.dump(samples, f)

    # Output positive and negative RGB information
    print("Positive RGB values:")
    for color in samples['positive']:
        print(color)
    
    print("Negative RGB values:")
    for color in samples['negative']:
        print(color)

def train_svm_classifier(samples):
    positive_colors = np.array(samples['positive'])
    negative_colors = np.array(samples['negative'])

    X = np.concatenate((positive_colors, negative_colors), axis=0)
    y = np.array([1] * len(positive_colors) + [0] * len(negative_colors))

    svm_classifier = SVC(kernel='linear')
    svm_classifier.fit(X, y)

    return svm_classifier

def visualize_data(samples, classifier):
    positive_colors = np.array(samples['positive'])
    negative_colors = np.array(samples['negative'])

    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')

    ax.scatter(positive_colors[:, 0], positive_colors[:, 1], positive_colors[:, 2], c='r', label='Positive')
    ax.scatter(negative_colors[:, 0], negative_colors[:, 1], negative_colors[:, 2], c='b', label='Negative')

    # Draw the SVM splitting plane
    coef = classifier.coef_[0]
    intercept = classifier.intercept_

    xx, yy = np.meshgrid(range(256), range(256))
    zz = (-coef[0] * xx - coef[1] * yy - intercept) / coef[2]

    ax.plot_surface(xx, yy, zz, color='y', alpha=0.5)

    ax.set_xlabel('Red')
    ax.set_ylabel('Green')
    ax.set_zlabel('Blue')
    ax.legend()
    plt.show()

if __name__ == "__main__":
    positive_dir = "positive_samples"
    negative_dir = "negative_samples"
    store_all_sample_colors(positive_dir, negative_dir)
    print("Sample colors stored successfully.")

    samples = json.load(open("sample_colors.json"))
    svm_classifier = train_svm_classifier(samples)
    print("SVM classifier trained successfully.")

    visualize_data(samples, svm_classifier)

