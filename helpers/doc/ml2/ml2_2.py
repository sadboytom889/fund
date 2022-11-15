import numpy as np;
import pandas as pd;
from matplotlib import pyplot as plt;
from sklearn.datasets import make_classification;
from sklearn.metrics import accuracy_score;

print( "======================新生成数据完善决策边界======================" );

# 生成分类模型随机数据
x, y = make_classification( random_state = 2 );

x = x.T[ :2, : ];

x1min, x1max = x[ 0, : ].min(), x[ 0, : ].max();

x2min, x2max = x[ 1, : ].min(), x[ 1, : ].max();

x = np.vstack( [ x, np.square( x ), np.expand_dims(
	np.array( x[ 0, : ] * x[ 1, : ] ), axis = 0 ) ] );
# shape (5, 100)

y = np.expand_dims( y, axis = 0 );

# 初始值
theta = np.zeros( [ 5, 1 ] );
# theta.shape (5, 1)

bias = np.zeros( [ 1 ] );
# bias.shape (1,)

# 长度
size = x.shape[ 1 ];

def sigmoid ( z ):
	return 1 / ( 1 + np.exp( -z ) );

def getyhat ( x, theta, bias ):
	z = np.dot( theta.T, x ) + bias;
	yhat = sigmoid( z );
	return yhat;

def costfunction ( x, y, theta, bias ):
	yhat = getyhat( x, theta, bias );

	return -np.sum( y * np.log( yhat ) - ( 1 - y ) * np.log( 1 - yhat ) ) / size;

def gradient ( x, y, theta, bias ):
	yhat = getyhat( x, theta, bias );

	return np.dot( x, ( yhat - y ).T ) / size, np.mean( yhat - y );

# 主函数
def run ( theta, bias, x, y, step = 0.01 ):
	while True:
		lasttheta = theta;

		lastbias = bias;

		grad = gradient( x, y, theta, bias );

		theta = theta - step * grad[ 0 ];

		bias = bias - step * np.array( [ grad[ 1 ] ] );

		lastcost = costfunction( x, y, theta, bias );

		currentcost = costfunction( x, y, lasttheta, lastbias );

		print(abs( lastcost - currentcost ))

		if abs( lastcost - currentcost ) < 1e-15:
			break;

	return theta, bias;

theta, bias = run( theta, bias, x, y );

yhat = np.squeeze( getyhat( x, theta, bias ) );

for idx, i in enumerate( yhat ):
	yhat[ idx ] = 1 if yhat[ idx ] >= 0.5 else 0;

accuracy = accuracy_score( np.squeeze( y ), yhat );

theta0 = bias[ 0 ];
theta1, theta2, theta3, theta4, theta5 = theta[ 0, 0 ], theta[ 1, 0 ], theta[ 2, 0 ], theta[ 3, 0 ], theta[ 4, 0 ];

print( "theta0", theta0 );
print( "theta1", theta1 );
print( "theta2", theta2 );
print( "theta3", theta3 );
print( "theta4", theta4 );
print( "theta5", theta5 );
print( "公式: {} + {} * x₁ + {} * x₂ + {} * x₁² + {} * x₂² + {} * x₁ * x₂ = 0".format(
	theta0, theta1, theta2, theta3, theta4, theta5 ) );
print( "accuracy", accuracy );

def fn ( x ):
	# θ₀ + θ₁ * x₁ + θ₂ * x₂ + θ₃ * x₁² + θ₄ * x₂² + θ₅ * x₁ * x₂ = 0;
	# θ₄ * x₂² + ( θ₅ * x₁ + θ₂ ) * x₂ + ( θ₀ + θ₁ * x₁ + θ₃ * x₁² ) = 0;
	# 令 a = θ₄;
	# 令 b = θ₅ * x₁ + θ₂;
	# 令 c = θ₀ + θ₁ * x₁ + θ₃ * x₁²;
	# a * x₂² + b * x₂ + c = 0;
	# 解1: x₁ = ( -b + √( b² - 4 * a * c ) ) ⁄ 2 * a;
	# 解2: x₂ = ( -b - √( b² - 4 * a * c ) ) ⁄ 2 * a;
	# 根据条件应取 x₁

	a = theta4;
	b = theta5 * x + theta2;
	c = theta0 + theta1 * x + theta3 * x * x;

	return ( -b + np.sqrt( b * b - 4 * a * c ) ) / ( 2 * a );

plt.scatter( x[ 0 ], x[ 1 ], c = y, s = 4 );

x = np.linspace( x1min, x1max, 10000 );

plt.plot( x, fn( x ), color = "r", linewidth = 0.8 );

plt.xlabel( "x1" );

plt.xlabel( "x2" );

plt.show();

