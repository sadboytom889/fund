import numpy as np;

import pandas as pd;

from matplotlib import pyplot as plt;

from sklearn.linear_model import LinearRegression;

from sklearn.metrics import mean_squared_error, r2_score;

dataframe = pd.read_csv( "./data3.ml1.csv", header = 0 );

plt.figure();

fig1 = plt.subplot( 231 );
plt.scatter( dataframe.loc[ :, "Avg. Area Income" ],
			 dataframe.loc[ :, "Price" ],
			 s = 0.5 );
plt.title( "Price -- Income" );

fig2 = plt.subplot( 232 );
plt.scatter( dataframe.loc[ :, "Avg. Area House Age" ],
			 dataframe.loc[ :, "Price" ],
			 s = 0.5 );
plt.title( "Price -- Age" );

fig3 = plt.subplot( 233 );
plt.scatter( dataframe.loc[ :, "Avg. Area Number of Rooms" ],
			 dataframe.loc[ :, "Price" ],
			 s = 0.5 );
plt.title( "Price -- Number of Rooms" );

fig4 = plt.subplot( 234 );
plt.scatter( dataframe.loc[ :, "Area Population" ],
			 dataframe.loc[ :, "Price" ],
			 s = 0.5 );
plt.title( "Price -- Population" );

fig5 = plt.subplot( 235 );
plt.scatter( dataframe.loc[ :, "Size" ],
			 dataframe.loc[ :, "Price" ],
			 s = 0.5 );
plt.title( "Price -- Size" );

print();
print( "======================单因子模型======================" );
print();

# 输入数据
x = np.array( dataframe.loc[ :, "Size" ] ).reshape( -1, 1 );
y = np.array( dataframe.loc[ :, "Price" ] ).reshape( -1, 1 );

print( "输入数据: x" );
print( x );

print( "输入数据: y" );
print( y );

# 创建模型
model1 = LinearRegression();

# 训练模型
model1.fit( x, y );

# 预测值
yhat = model1.predict( x );

# 模型评估
MSE = mean_squared_error( y, yhat );
R2 = r2_score( y, yhat );

print( "预测数据:" );
print( yhat );

print( "模型评估: MSE: {}; R2: {}".format( MSE, R2 ) );

# 绘制
plt.figure();
plt.scatter( x, y, s = 0.5 );
plt.plot( x, yhat, "r" );

print();
print( "======================多因子模型======================" );
print();

# 输入数据
x = np.array( dataframe.drop( [ "Price" ], axis = 1 ) );
y = np.array( dataframe.loc[ :, "Price" ] ).reshape( -1, 1 );

print( "输入数据: x" );
print( x );

print( "输入数据: y" );
print( y );

# 创建模型
model2 = LinearRegression();

# 训练模型
model2.fit( x, y );

# 预测值
yhat = model2.predict( x );

# 模型评估
MSE = mean_squared_error( y, yhat );
R2 = r2_score( y, yhat );

print( "预测数据:" );
print( yhat );

print( "模型评估: MSE: {}; R2: {}".format( MSE, R2 ) );

# 查看系数
a = model2.coef_;
b = model2.intercept_;

print( "查看系数: a: {}, b: {}".format( a, b ) );

# 绘制
plt.figure();
plt.scatter( y, yhat, s = 0.5 );

# 已知条件:
# Avg. Area Income = 6500
# Avg. Area House Age = 5
# Avg. Area Number of Rooms = 5
# Area Population = 30000
# Size = 200
# 求解:
# Price

yhat = model2.predict(
	np.array( [ [ 65000, 5, 5, 30000, 200 ] ] ).reshape( 1, -1 ) );

print( '''
# 已知条件:
# Avg. Area Income = 6500
# Avg. Area House Age = 5
# Avg. Area Number of Rooms = 5
# Area Population = 30000
# Size = 200

# 求解:
# Price
''', yhat );

plt.show();
