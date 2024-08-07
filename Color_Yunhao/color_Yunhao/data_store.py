import cv2
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC
from sklearn.metrics import classification_report, confusion_matrix
from utils_Yunhao import findDominantColors, plotColors

def extract_color_data(imgpath, number_of_colors):
    img = cv2.imread(imgpath)
    if img is None:
        raise ValueError(f"Image not found or cannot be opened: {imgpath}")
    
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    dominant, palette, counts = findDominantColors(img, number_of_colors)
    purple_like_colors = palette[1:]  # 忽略第一主导颜色
    color_data = pd.DataFrame(purple_like_colors, columns=['R', 'G', 'B'])
    return color_data

def process_images(image_paths, number_of_colors):
    all_color_data = pd.DataFrame()
    
    for path in image_paths:
        color_data = extract_color_data(path, number_of_colors)
        all_color_data = pd.concat([all_color_data, color_data], ignore_index=True)
    
    return all_color_data

if __name__ == '__main__':
    image_paths = [
        'positive_color_strips.bmp',
        'sample_image_2.bmp',
        'sample_image_3.bmp',
    ]
    number_of_colors = 5

    try:
        all_color_data = process_images(image_paths, number_of_colors)
        all_color_data.to_csv('combined_color_data.csv', index=False)
        print("Combined color data saved to 'combined_color_data.csv'")

        # 加载数据
        data = pd.read_csv('combined_color_data.csv')
        features = data[['R', 'G', 'B']]
        labels = data['Label']  # 假设你的CSV已经有标签

        # 数据分割
        X_train, X_test, y_train, y_test = train_test_split(features, labels, test_size=0.20, random_state=42)

        # 特征缩放
        scaler = StandardScaler()
        X_train = scaler.fit_transform(X_train)
        X_test = scaler.transform(X_test)

        # 创建SVM分类器
        svm_classifier = SVC(kernel='rbf', random_state=42)
        svm_classifier.fit(X_train, y_train)

        # 预测测试集结果
        y_pred = svm_classifier.predict(X_test)

        # 打印结果
        print(confusion_matrix(y_test, y_pred))
        print(classification_report(y_test, y_pred))
    
    except ValueError as e:
        print(e)
