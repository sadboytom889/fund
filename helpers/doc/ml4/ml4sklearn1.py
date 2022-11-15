import numpy as np;
import pandas as pd;
from sklearn import tree;
from sklearn.datasets import load_iris;
from sklearn.metrics import accuracy_score;

from matplotlib import pyplot as plt;

from ml4_2 import createtree;

# 获取鸢尾花数据集 X, 与标记 y;
x, y = load_iris( return_X_y = True )
# x = [ [ 5.1 3.5 1.4 0.2 ]
#       [ 4.9 3.  1.4 0.2 ]
#       [ 4.7 3.2 1.3 0.2 ]
#       [ 4.6 3.1 1.5 0.2 ]
#       [ 5.  3.6 1.4 0.2 ]
#       ...
#       [ 6.7 3.  5.2 2.3 ]
#       [ 6.3 2.5 5.  1.9 ]
#       [ 6.5 3.  5.2 2.  ]
#       [ 6.2 3.4 5.4 2.3 ]
#       [ 5.9 3.  5.1 1.8 ] ]

# y = [0 0 0 0 0 ... 2 2 2 2 2]

############################## 手写 C4.5 模型算法 ##############################
createtree( np.hstack( [ x, y.reshape( -1, 1 ) ] ).tolist(),
	[ "Sepal length", "Sepal width", "Petal length", "Petal width" ] );
# {
# 	'Petal length':
# 	{
# 		'>1.9':
# 		{
# 			'Petal width':
# 			{
# 				'>1.7':
# 				{
# 					'Sepal length':
# 					{
# 						'>5.9': 2.0,
# 						'<=5.9':
# 						{
# 							'Sepal width':
# 							{
# 								'>3.1': 1.0,
# 								'<=3.1': 2.0
# 							}
# 						}
# 					}
# 				},
# 				'<=1.7':
# 				{
# 					'Sepal length':
# 					{
# 						'>7.1': 2.0,
# 						'<=7.1':
# 						{
# 							'Sepal width':
# 							{
# 								'>2.8': 1.0,
# 								'<=2.8': 1.0
# 							}
# 						}
# 					}
# 				}
# 			}
# 		},
# 		'<=1.9': 0.0
# 	}
# }

############################## sklearn C4.5 模型 ##############################

# 建立模型
# criterion: 分类方式
# min_samples_leaf: 限制叶子节点最少的样本数
c45tree = tree.DecisionTreeClassifier( criterion = "entropy", min_samples_leaf = 5 );

# 训练模型
c45tree.fit( x, y )

# 预测值
yhat = c45tree.predict( x );
# [0 0 0 0 0 ... 2 2 2 2 2]

# 准确率
accuracy = accuracy_score( y, yhat );
# 0.9733333333333334

