# pip install --upgrade scikit-learn
from sklearn.linear_model import LinearRegression;
from sklearn.metrics import mean_squared_error, r2_score;
import numpy as np;
import pandas as pd;

from matplotlib import pyplot as plt;

dataframe = pd.read_csv( "./data2.ml1.csv", header = 0 );
# x   y
# 0   1   7
# 1   2   9
# 2   3  11
# 3   4  13
# 4   5  15
# 5   6  17
# 6   7  19
# 7   8  21
# 8   9  23
# 9  10  25

x = np.array( dataframe.loc[ :, "x" ] ).reshape( -1, 1 );
# (10, 1)
y = np.array( dataframe.loc[ :, "y" ] ).reshape( -1, 1 );
# (10, 1)

plt.figure();

plt.scatter( x, y, s = 2 );

plt.show();

# 创建线性模型: 普通最小二乘线性回归
model = LinearRegression();

# 拟合线性模型
model.fit( x, y );

# 查看系数
a = model.coef_;
# [[2.]]

b = model.intercept_;
# [5.]

# 预测值
yhat = model.predict( x );

# 模型评估 MSE 均方误差
MSE = mean_squared_error( y, yhat );
# 3.1554436208840474e-31

# 模型评估 R2
R2 = r2_score( y, yhat );
# 1.0
