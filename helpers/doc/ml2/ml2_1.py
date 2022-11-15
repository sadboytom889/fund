import numpy as np;
import pandas as pd;
from matplotlib import pyplot as plt;
from sklearn.datasets import make_classification;
from sklearn.metrics import accuracy_score;

# np.exp( n ):
# 返回 e 的 n 次方. 常数 e: 2.71828;

# np.expand_dims 扩展数组形状
# np.zeros( [ 2 ] );
# [ 0. 0. ]

# np.zeros( [ 2, 3 ] );
# [ [ 0. 0. 0. ]
#   [ 0. 0. 0. ] ]

# np.zeros( [ 2, 3, 4 ] );
# [ [ [ 0. 0. 0. 0. ]
#     [ 0. 0. 0. 0. ]
#     [ 0. 0. 0. 0. ] ]

#   [ [ 0. 0. 0. 0. ]
#     [ 0. 0. 0. 0. ]
#     [ 0. 0. 0. 0. ] ] ]

# x = np.arange( 1, 7 ).reshape( 2, 3 );
# [ [ 1, 2, 3 ]
#   [ 4, 5, 6 ] ]

# np.expand_dims( x, axis = 0 );
# [ [ [ 1, 2, 3 ]
#     [ 4, 5, 6 ] ] ]

# np.expand_dims( x, axis = 1 );
# [ [ [ 1, 2, 3 ] ]
#   [ [ 4, 5, 6 ] ] ]

# np.expand_dims( x, axis = 2 );
# [ [ [ 1 ]
#     [ 2 ]
#     [ 3 ] ]
#   [ [ 4 ]
#     [ 5 ]
#     [ 6 ] ] ]

# 生成分类模型随机数据
x, y = make_classification( random_state = 2 );

x = x.T[ :2, : ];
# [ [ -0.26623674, 0.09555698, ..., 0.19678527, 0.40029749 ]
#   [ 1.578341456, -1.2759612, ..., -1.4952491, 1.54721615 ] ]
# x.shape (2, 100), 代表: 特征值: 2, 样本数据: 100

y = np.expand_dims( y, axis = 0 );
# [ [ 1 0 1 0 ... 1 1 0 1 ] ]
# y.shape (1, 100) 代表: 真实结果: 1, 样本数据: 100

# 初始值
theta = np.zeros( [ 2, 1 ] );
# [ [ 0 ]
#   [ 0 ] ]
# theta.shape (2, 1)

bias = np.zeros( [ 1 ] );
# [ 0 ]
# bias.shape (1,)

# 长度
size = x.shape[ 1 ];

def sigmoid ( z ):
	# p( x ) = 1 ⁄ ( 1 + e⁻ᶿᵀˣ );
	return 1 / ( 1 + np.exp( -z ) );

def getyhat ( x, theta, bias ):
	# 其中 theta.T.shape = (1, 2)
	# 其中 x.shape = (2, 100)
	# g( θᵀx ) = θ₁ * X₁₁ + θ₂ * X₂₁ + θ₀,
	#			 θ₁ * X₁₂ + θ₂ * X₂₂ + θ₀,
	#			 ... ... ,
	#			 θ₁ * X₁ₙ + θ₂ * X₂ₙ + θ₀

	z = np.dot( theta.T, x ) + bias;
	yhat = sigmoid( z );
	return yhat;

def costfunction ( x, y, theta, bias ):
	# e` = ¹⁄ₙ * ∑ⁿᵢ₌₁( yⁱ` * log( p( xⁱ ) ) + ( 1 - yⁱ` ) * log( 1 - p( xⁱ ) ) );

	yhat = getyhat( x, theta, bias );

	return -np.sum( y * np.log( yhat ) - ( 1 - y ) * np.log( 1 - yhat ) ) / size;

def gradient ( x, y, theta, bias ):
	# ∂j(θ)⁄∂θ  = ¹⁄ₙ * ∑ⁿᵢ₌₁( x * ( p(x) - yⁱ ) );
	# 设 k = yhat - y;
	# 其中 x.shape = (2, 100);
	# 其中 k.shape = (100, 1);
	# np.dot( x, ( yhat - y ).T ) = [ [ x₁₁ * k₁ + x₁₂ * k₂ + ... + x₁₁₀₀ * k₁₀₀ ]
	#								  [ x₂₁ * k₁ + x₂₂ * k₂ + ... + x₂₁₀₀ * k₁₀₀ ] ]

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

		if abs( lastcost - currentcost ) < 1e-15:
			break;

	return theta, bias;

# theta, bias = run( theta, bias, x, y );

yhat = np.squeeze( getyhat( x, theta, bias ) );

for idx, i in enumerate( yhat ):
	yhat[ idx ] = 1 if yhat[ idx ] >= 0.5 else 0;

accuracy = accuracy_score( np.squeeze( y ), yhat );

print( "theta0", bias[ 0 ] );
print( "theta1", theta[ 0, 0 ] );
print( "theta2", theta[ 1, 0 ] );
print( "公式: {} + {} * x₁ + {} * x₂ = 0".format(
	bias[ 0 ], theta[ 0, 0 ], theta[ 1, 0 ] ) );

print( "accuracy", accuracy );

def fn ( x ):
	# θ₀ + θ₁ * x₁ + θ₂ * x₂ = 0;
	return ( 0 - bias - theta[ 0, 0 ] * x ) / theta[ 1, 0 ];

plt.plot( x[ 0 ], fn( x[ 0 ] ), color = "r", linewidth = 0.8 );

plt.scatter( x[ 0 ], x[ 1 ], c = y, s = 4 );
plt.xlabel( "x1" )
plt.xlabel( "x2" )
plt.show();

