import math;

# dict.setdefault( key, default = None ): 若键不存在于字典中则添加键并将值设为默认值

# list.extend( seq ): 在列表末尾一次性追加列表

# set: python 常用数据结构之一, 表示无序不重复元素的序列

####################################### ID3 #######################################

# 获取信息熵
def getshannonentropy ( data ):
	# 信息墒
	shannonentropy = 0.0;

	# 统计每个结果在样本中出现的次数
	labelcount = {};

	for item in data:
		if item[ -1 ] not in labelcount.keys():

			# setdefault(): 若键不存在于字典中则将添加键并将值设为默认值
			labelcount.setdefault( item[ -1 ], 0 );

		labelcount[ item[ -1 ] ] += 1;

	# 根据公式计算信息熵
	for key in labelcount:
		# 每个结果出现的概率
		prob = labelcount[ key ] / len( data );

		# 信息熵公式: ∑ⁿᵢ₌₁( pᵢ * log₂( 1 ⁄ pᵢ ) );
		shannonentropy += prob * math.log2( 1 / prob );

	return shannonentropy;

def splitata ( data, featureindex, featurevalue ):
	# 新数据列表
	newdata = [];

	# 拼装新数据列表
	for item in data:
		if item[ featureindex ] == featurevalue:
			temp = item[ :featureindex ];
			temp.extend( item[ featureindex + 1: ] );
			newdata.append( temp );

	return newdata;

#  获取最大信息增益对应的特征索引
def getmaxgainfeatureindex ( data ):
	# 特征数量
	featuresize = len( data[ 0 ] ) - 1;

	# 结果的信息熵
	shannonentropy = getshannonentropy( data );

	# 各特征中最大的信息增益
	maxgain = 0;

	# 最大的信息增益的特征索引
	maxgainfeatureindex = -1;

	for featureindex in range( featuresize ):

		# 条件熵
		conditionalentropy = 0;

		# 某特征值列表
		featureList = [ item[ featureindex ] for item in data ];

		# 无重复的某特征值集合
		uniqualfeatureset = set( featureList );

		# 计算条件熵
		for featurevalue in uniqualfeatureset:

			# 用于计算条件熵的新数据
			newdata = splitata( data, featureindex, featurevalue );

			# 当前特征出现的频率
			prob = len( newdata ) / len( data );

			# 条件熵: h( y | x ) = ∑ⁿᵢ₌₁( p( x = xᵢ ) * h( x = xᵢ ) );
			conditionalentropy += prob * getshannonentropy( newdata );

		# 信息增益 = 结果的信息熵 - 各条件熵
		gain = shannonentropy - conditionalentropy;

		# 筛选最大信息增益
		if gain > maxgain:

			# 统计最大信息增益
			maxgain = gain;

			# 统计最大信息增益对应的特征索引
			maxgainfeatureindex = featureindex;

	return maxgainfeatureindex;

# 获取结果中个数最多的结果
def getmaxcountclass ( classList ):
	classcount = {};

	for res in classList:

		if res not in classcount.keys():

			classcount.setdefault( res, 0 );

		classcount[ res ] += 1;

	sortedclasscount = sorted(
		classcount.items(), key = lambda i: i[ 1 ], reverse = True );

	return sortedclasscount[ 0 ][ 0 ];

# 创建数结构
def createtree ( data, labels ):

	# 类别列表
	classList = [ item[ -1 ] for item in data ];

	# 若剩余样本类别相同, 停止划分并返回剩余类别
	if classList.count( classList[ 0 ] ) == len( classList ):
		return classList[ 0 ];

	# 若层级达到要求则可进入投票不再产生新的节点
	if len( data[ 0 ] ) == 1:
		return getmaxcountclass( classList );

	# 最大的信息增益的特征索引
	maxgainfeatureindex = getmaxgainfeatureindex( data );

	# 最大的信息增益的特征标签
	maxgainfeaturelabel = labels[ maxgainfeatureindex ];

	# 构建数结构
	tree = { maxgainfeaturelabel: {} };

	# 将已排序的 label 从 labels 中删除
	del ( labels[ maxgainfeatureindex ] );

	featureList = [ item[ maxgainfeatureindex ] for item in data ];

	uniqualfeatureset = set( featureList );

	# 对原数据基于信息增益最大的特征进行拆分
	for featurevalue in uniqualfeatureset:

		# 构成剩余数据样本
		newdata = splitata( data, maxgainfeatureindex, featurevalue );

		# 获取树结构
		subtree = createtree( newdata, labels );

		# 递归拼装树结构
		tree[ maxgainfeaturelabel ][ featurevalue ] = subtree;

	return tree;

labels = [ "发冷", "喉咙痛", "咳嗽", "头痛", "鼻塞", "疲劳", "发烧" ];

data1 = [ [ 1, 1, 2, 0, 1, 1, 0, "感冒" ],
		  [ 2, 0, 3, 2, 0, 2, 2, "流感" ],
		  [ 3, 0, 0, 1, 1, 1, 1, "流感" ],
		  [ 0, 0, 1, 1, 1, 0, 1, "感冒" ],
		  [ 3, 1, 2, 2, 0, 2, 2, "流感" ],
		  [ 0, 1, 2, 0, 1, 0, 0, "感冒" ],
		  [ 2, 0, 2, 2, 0, 2, 2, "流感" ],
		  [ 3, 1, 3, 0, 0, 1, 1, "感冒" ] ];

print( createtree( data1, labels ) );
# {
# 	'头痛': {
# 		0: '感冒',
# 		1: {
# 			'发冷': {
# 				0: '感冒',
# 				3: '流感'
# 			}
# 		},
# 		2: '流感'
# 	}
# }

