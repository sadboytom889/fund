import numpy as np;
from matplotlib import pyplot as plt;

#           -- --
# 向量:	v = | 4 |;
#           | 4 |
#           -- --
v1 = np.array( [ 4, 4 ] );

# 缩放比例
scale = 2;

# 旋转弧度: 360° = 2π
theta = 1 / 6 * np.pi;

#               --                           --
# 旋转矩阵 A1:	| cos( π / 6 ), -sin( π / 6 ) |, 将向量逆时针旋转 theta 弧度
#               | sin( π / 6 ),  cos( π / 6 ) |
#               --                           --
A1 = np.array( [ [ np.cos( theta ), -np.sin( theta ) ],
				 [ np.sin( theta ), np.cos( theta ) ] ] )

#               --                --
# 缩放矩阵 A2:	| x_scale,       0 |, 将向量在 x 轴方向缩放 x_scale 倍, 在 y 轴方向缩放 y_scale 倍
#               |       0, y_scale |
#               --                --
A2 = np.array( [ [ scale,      0 ],
				 [     0,  scale ] ] );

# 矩阵作用在向量上生成新向量
# --                           --   -- --   --                                            --
# | cos( π / 6 ), -sin( π / 6 ) | * | 4 | = | ( cos( π / 6 ) * 4 ) + ( -sin( π / 6 ) * 4 ) |;
# | sin( π / 6 ),  cos( π / 6 ) |   | 4 |   | ( sin( π / 6 ) * 4 ) + (  cos( π / 6 ) * 4 ) |
# --                           --   -- --   --                                            --
#                                           --         --
#                                         = | 2√(3) - 2 |
#                                           | 2 + 2√(3) |
#                                           --         --
#                                           --          --
#                                         = | 1.46410162 |
#                                           | 5.46410162 |
#                                           --          --
v2 = np.dot( A1, v1.T )
# [1.46410162 5.46410162]

# --   --   --  --  --                     --   -- --
# | 2 0 | * | 4 | = | ( 2 * 4 ) + ( 0 * 4 ) | = | 8 |;
# | 0 2 |   | 4 |   | ( 0 * 4 ) + ( 2 * 4 ) |   | 8 |
# --   --   -- --   --                     --   -- --
v3 = np.dot( A2, v1.T )
# [8 8]

v4 = np.dot( np.dot( A2, A1 ), v1.T )
# [ 2.92820323 10.92820323]

print( "对 v1 进行旋转: {} -> {}".format( v1, v2 ) )
print( "对 v1 进行缩放: {} -> {}".format( v1, v3 ) )
print( "对 v1 进行旋转后再缩放: {} -> {}".format( v1, v4 ) )

# 开始绘制
plt.figure( facecolor = "w" );

# 原点
origin = ( 0, 0 );

# 设置 x 轴的范围
plt.xlim( -12, 12 );

# 设置 y 轴的范围
plt.ylim( -12, 12 );

# 设置 x 坐标轴刻度线
plt.xticks( np.linspace( -12, 12, 12 * 2 + 1 ) );

# 设置 y 坐标轴刻度线
plt.yticks( np.linspace( -12, 12, 12 * 2 + 1 ) );

# 设置刻度字体大小
plt.tick_params( labelsize = 4 );

# 绘制向量 v3
plt.arrow( *origin, *v3, length_includes_head = True,
						 head_width = 0.2, color = "y" );

# 绘制向量 v4
plt.arrow( *origin, *v4, length_includes_head = True,
						 head_width = 0.2, color = "y" );

# 绘制向量 v1
plt.arrow( *origin, *v1, length_includes_head = True,
						 head_width = 0.2, color = "b" );

# 绘制向量 v2
plt.arrow( *origin, *v2, length_includes_head = True,
						 head_width = 0.2, color = "r" );

ax = plt.gca();

# 隐藏右边框
ax.spines[ "right" ].set_color( "none" );

# 隐藏上边框
ax.spines[ "top" ].set_color( "none" );

# 设置 x 刻度位置
ax.xaxis.set_ticks_position( "bottom" );

# 设置 y 刻度位置
ax.yaxis.set_ticks_position( "left" );

# 移动 x 轴
ax.spines[ "bottom" ].set_position( ( "data", 0 ) );

# 移动 y 轴
ax.spines[ "left" ].set_position( ( "data", 0 ) );

# 设置网格
plt.grid( True );

# 展示
plt.show();

############################## 计算在其他基构成坐标轴上的向量坐标值 ##############################

v = np.array( [ 2, 3 ] );
i = np.array( [ -1, 1 ] );
j = np.array( [ -1, -1 ] );

print( "向量 v {} 在基向量 i {} 和 j {} 为坐标轴的坐标为 [{}, {}]: ".format( v, i, j,
	np.dot( v, i / np.linalg.norm( i ) ),
	np.dot( v, j / np.linalg.norm( j ) ) ) );

