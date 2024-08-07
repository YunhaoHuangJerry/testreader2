import sklearn
import matplotlib

print("sklearn version:", sklearn.__version__)
print("matplotlib version:", matplotlib.__version__)

# 验证3D绘图功能是否正常
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np

fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')

# 生成示例数据
x = np.linspace(-5, 5, 100)
y = np.linspace(-5, 5, 100)
z = x ** 2 + y ** 2

ax.plot(x, y, z, label='parabola')
ax.set_xlabel('X Label')
ax.set_ylabel('Y Label')
ax.set_zlabel('Z Label')
ax.legend()

plt.show()

