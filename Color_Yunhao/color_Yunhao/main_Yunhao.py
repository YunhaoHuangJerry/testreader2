# import cv2
# import numpy as np
# from utils_Yunhao import findDominantColors, plotColors, auto_canny
# import os

# print("Current Working Directory:", os.getcwd())
# os.chdir('/Users/huangyunhao/Desktop/testreader/Color_Yunhao')


# def quantify_colors(imgpath, number_of_colors):
#     img = cv2.imread(imgpath)
#     if img is None:
#         raise ValueError("Image not found or cannot be opened. Please check the file path.")
#     img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
#     #img = adjust_brightness_contrast(img)

#     # Apply auto_canny edge detection to enhance edge features
#     edges = auto_canny(cv2.cvtColor(img, cv2.COLOR_RGB2GRAY))
#     img_edges = cv2.bitwise_and(img, img, mask=edges)

#     # Set a threshold to ignore the black background
#     mask = img > [10, 10, 10]  # Threshold can be adjusted
#     masked_img = img[np.all(mask, axis=2)]

#     # Use k-means clustering to find the main colors
#     if masked_img.size == 0:
#         raise ValueError("No valid color regions found. Try adjusting the threshold.")
#     dominant, palette, counts = findDominantColors(masked_img, number_of_colors)

#     # Visualize the color distribution
#     plotColors(img, palette, counts)

#     return dominant, palette, counts, img

# if __name__ == '__main__':
#     imgpath = '1_10_dilution_positive.bmp'  # Ensure this path is correct
#     number_of_colors = 5

#     try:
#         dominant, palette, counts, img = quantify_colors(imgpath, number_of_colors)
#         print("Dominant Color (RGB):", dominant)
#         print("Palette of Colors (RGB):", palette)
#         print("Counts of each color:", counts)
#     except ValueError as e:
#         print(e)



# import cv2
# import numpy as np
# import matplotlib.pyplot as plt
# from utils_Yunhao import findAverageColor, findDominantColors, plotColors, find_circle2, distance

# def main(image_path):
#     # 加载图像
#     img = cv2.imread(image_path)
#     if img is None:
#         print("Error: Image not found.")
#         return
    
#     # 转换为RGB颜色空间
#     img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

#     # 创建一个掩码，排除黑色背景
#     mask = np.all(img_rgb > [10, 10, 10], axis=-1)  # 阈值可以调整

#     # 应用掩码
#     img_masked = img_rgb[mask]

#     # 如果需要将掩码区域重构回原始尺寸的图像（用于显示或其他目的）
#     reconstructed_image = np.zeros_like(img_rgb)
#     reconstructed_image[mask] = img_masked

#     # 分析有色区域的颜色
#     dominant_color, palette, counts = findDominantColors(img_masked.reshape(-1, 3), number_of_colors=3)
    
#     # 可视化结果
#     plotColors(reconstructed_image, palette, counts)

#     print("Dominant Color: ", dominant_color)

# if __name__ == '__main__':
#     image_path = '/Users/huangyunhao/Desktop/testreader/Color_Yunhao/1_5_dilution_positive.bmp'
#     main(image_path)


import cv2
import numpy as np
import matplotlib.pyplot as plt
from utils_Yunhao import findAverageColor, findDominantColors, plotColors, find_circle2

def quantify_colors(imgpath, number_of_colors):
    # 读取图像并转换颜色空间到RGB
    img = cv2.imread(imgpath)
    if img is None:
        raise ValueError("Image could not be read or path is incorrect.")
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    # 提取图像中的主要颜色
    dominant, palette, counts = findDominantColors(img_rgb, number_of_colors)
    plotColors(img_rgb, palette, counts)

    return dominant, palette, counts, img_rgb

def find_and_analyze_colors(image_path, number_of_circles, pixel_per_area):
    img = cv2.imread(image_path)
    if img is None:
        print("Error: Image not found.")
        return
    
     #确保图像是灰度图
    if len(img.shape) == 3:
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    else:
        gray = img  # 如果已经是灰度图，直接使用

    # # 转换为灰度图并检测边缘
    # gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    edges = find_circle2(gray)

    # 寻找轮廓
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        print("No contours found.")
        return

    # 寻找最大轮廓
    largest_contour = max(contours, key=cv2.contourArea)
    (x_center, y_center), radius = cv2.minEnclosingCircle(largest_contour)

    # 对每个圈内的颜色进行分析
    result_image = np.zeros_like(img)
    previous_radius = 0
    for i in range(number_of_circles):
        current_radius = int(radius + pixel_per_area * (i + 1))
        mask = np.zeros_like(gray)
        cv2.circle(mask, (int(x_center), int(y_center)), current_radius, 255, thickness=-1)
        mask_inside = np.zeros_like(gray)
        cv2.circle(mask_inside, (int(x_center), int(y_center)), previous_radius, 255, thickness=-1)
        actual_mask = cv2.bitwise_xor(mask, mask_inside)

        # 使用掩码提取颜色并计算平均颜色
        masked_img = cv2.bitwise_and(img, img, mask=actual_mask)
        mean_color = findAverageColor(masked_img)
        print(f"Average color for circle {i}: {mean_color}")
        previous_radius = current_radius

    # 显示处理后的图像
    cv2.imshow('Processed Image', result_image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

if __name__ == '__main__':
    img_path = '/Users/huangyunhao/Desktop/testreader/Color_Yunhao/1_5_dilution_positive.bmp'
    number_of_circles = 20
    pixel_per_area = 25
    find_and_analyze_colors(img_path, number_of_circles, pixel_per_area)


