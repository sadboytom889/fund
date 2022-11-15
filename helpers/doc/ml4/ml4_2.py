from math import log;

####################################### C4.5 #######################################

def createdataset():
	"""构建数据集
	"""
	return ( [ [ "是", "单身", 125, "否" ],
			   [ "否", "已婚", 100, "否" ],
			   [ "否", "单身",  70, "否" ],
			   [ "是", "已婚", 120, "否" ],
			   [ "否", "离异",  95, "是" ],
			   [ "否", "已婚",  60, "否" ],
			   [ "是", "离异", 220, "否" ],
			   [ "否", "单身",  85, "是" ],
			   [ "否", "已婚",  75, "否" ],
			   [ "否", "单身",  90, "是" ] ],
			[ "是否有房", "婚姻状况", "年收入(k)" ] );

def getshannonentropy( dataset ):
	"""计算信息熵
	"""
	shannonEnt = 0.0

	labelcounts = {};
	for i in dataset:
		currentlabel = i[ -1 ];

		if currentlabel not in labelcounts.keys():
			labelcounts[ currentlabel ] = 0;

		labelcounts[ currentlabel ] += 1;


	for label in labelcounts.keys():
		prob = float( labelcounts[ label ] ) / len( dataset );
		shannonEnt -= prob * log( prob, 2 );

	return shannonEnt;

def majoritycount ( classlist ):
	''' 获取结果中个数最多的结果
	'''
	classcount = {};

	for i in classlist:

		if i not in classcount.keys():

			classcount.setdefault( i, 0 );

		classcount[ i ] += 1;

	sortedclasscount = sorted(
		classcount.items(), key = lambda i: i[ 1 ], reverse = True );

	return sortedclasscount[ 0 ][ 0 ];

def splitdataset( dataset, axis, value ):
	""" 对离散型特征划分数据集
		dataset: 数据集
		axis: 数据集中离散特征值列索引;
		value: 数据集离散特征值对比参照值;
	"""
	retdataset = [];
	for i in dataset:
		if i[ axis ] == value:
			reducedfeatvec = i[ : axis ];
			reducedfeatvec.extend( i[ axis + 1 : ] );
			retdataset.append( reducedfeatvec );
	return retdataset;

def splitcontinuousdataset( dataset, axis, value, direction ):
	""" 对连续型特征划分数据集
		dataset: 数据集
		axis: 数据集中连续特征值列索引;
		value: 数据集连续特征值对比参照值;
		direction: 按照大于或小于划分点对数据集进行划分, 0: 大于, 1: 小于;
	"""
	subdataset = [];

	for i in dataset:
		if direction == 0:
			if i[ axis ] > value:
				reducedata = i[ : axis ];
				reducedata.extend( i [ axis + 1 : ] );
				subdataset.append( reducedata );

		if direction == 1:
			if i[ axis ] <= value:
				reducedata = i[ : axis ];
				reducedata.extend( i[ axis + 1: ] );
				subdataset.append( reducedata );

	return subdataset;

def choosebestfeatureToSplit( dataset, labels ):
	"""选择最好的数据集划分方式
	"""
	baseentropy = getshannonentropy( dataset );

	basegainratio = 0.0;

	bestfeature = -1;

	size = len( dataset[ 0 ] ) - 1;

	# 建立一个字典, 用来存储每一个连续型特征所对应最佳切分点的具体值
	bestsplitdic = {}

	for i in range( size ):
		# 当前特征列
		featvals = [ example[ i ] for example in dataset ];

		# 若该特征列为连续型数据
		if type( featvals[ 0 ] ).__name__ == "float" or type(
			featvals[ 0 ] ).__name__ == "int":

			# 特征列值排序
			sortedfeatvals = sorted( featvals );

			# 取相邻两样本值平均数做划分点, 数量: len( featvals ) - 1
			splitfeatlist = [];
			for j in range( len( featvals ) - 1 ):
				splitfeatlist.append(
					( sortedfeatvals[ j ] + sortedfeatvals[ j + 1 ] ) / 2.0 );

			# 遍历各切分点
			for j in range( len( splitfeatlist ) ):
				# 计算该划分方式得到数据集的条件熵 conditionalentropy
				conditionalentropy = 0.0;

				# 将数据集划分为大于切分点的子集
				greatersubdataset = splitcontinuousdataset(
					dataset, i, splitfeatlist[ j ], 0 );

				# 若大于切分点子集为空则必然存在熵
				if len( greatersubdataset ) == 0.0:
					continue;

				# 将数据集划分为小于切分点的子集
				smallsubdataset = splitcontinuousdataset(
					dataset, i, splitfeatlist[ j ], 1 );

				# 若小于切分点子集为空则必然存在熵
				if len( smallsubdataset ) == 0.0:
					continue;

				# 大于切分点的数据集对总数据集的占比
				prob0 = len( greatersubdataset ) / float( len( dataset ) );
				# 计算大于切分点的数据集条件熵: h( y | x ) = ∑ⁿᵢ₌₁( p( x = xᵢ ) * h( x = xᵢ ) );
				conditionalentropy += prob0 * getshannonentropy( greatersubdataset );

				# 小于切分点的数据集对总数据集的占比
				prob1 = len( smallsubdataset ) / float( len( dataset ) );
				# 计算小于切分点的数据集信息熵: h( y | x ) = ∑ⁿᵢ₌₁( p( x = xᵢ ) * h( x = xᵢ ) );
				conditionalentropy += prob1 * getshannonentropy( smallsubdataset );

				# 计算该划分方式对比总数据的信息熵: H( xᵢ ) = -( pᵢ * log₂( pᵢ ) )
				splitinfo = 0.0;
				splitinfo += -( prob0 * log( prob0, 2 ) );
				splitinfo += -( prob1 * log( prob1, 2 ) );

				# 计算信息增益率 = 信息增益 / 计算该划分方式对比总数据的信息熵
				# 信息增益: 信息增益 = 信息熵 - 条件熵;
				# 信息增益率: 信息增益率 = 信息增益 / 划分方式对总数据的信息熵;
				gainratio = float( baseentropy - conditionalentropy ) / splitinfo;
				if gainratio > basegainratio:
					# 记录当前最佳信息增益率;
					basegainratio = gainratio;

					# 记录当前最佳信息增益率对应的划分位置;
					bestsplit = j;

					# 记录当前最佳信息增益率对应的特征列索引;
					bestfeature = i;
			# 最佳切分点
			bestsplitdic[ labels[ i ] ] = splitfeatlist[ bestsplit ];

		# 若该特征列为离散型数据
		else:
			# 无重复的当前特征列
			uniqueVals = set( featvals );

			splitinfo = 0.0;

			# 计算条件熵 conditionalentropy
			conditionalentropy = 0.0;

			for j in uniqueVals:
				# 使用当前特征划分用于计算条件熵的新数据
				subdataset = splitdataset( dataset, i, j );

				# 当前特征出现的频率
				prob = len( subdataset ) / float( len( dataset ) );

				# 计算总数据的信息熵
				splitinfo -= prob * log( prob, 2 );

				# 条件熵: h( y | x ) = ∑ⁿᵢ₌₁( p( x = xᵢ ) * h( x = xᵢ ) );
				conditionalentropy += prob * getshannonentropy( subdataset );

			# 信息增益和对比总数据的信息熵都为 0, 则跳过该特征, 说明目前该特征对区分不作贡献;
			if splitinfo == 0.0:
				continue;

			# 计算信息增益率 = 信息增益 / 对比总数据的信息熵
			gainratio = float( baseentropy - conditionalentropy ) / splitinfo;

			if gainratio > basegainratio:
				# 记录当前最佳信息增益率;
				basegainratio = gainratio;

				# 记录当前最佳信息增益率对应的特征列索引;
				bestfeature = i;

	# 若最佳切分特征是连续型, 则最佳切分点为具体的切分值
	if type( dataset[ 0 ][ bestfeature ] ).__name__ == "float" or type(
			dataset[ 0 ][ bestfeature ] ).__name__ == "int":
		bestfeatvalue = bestsplitdic[ labels[ bestfeature ] ];

	# 若最佳切分特征时离散型, 则最佳切分点为特征名称
	if type( dataset[ 0 ][ bestfeature ] ).__name__ == "str":
		bestfeatvalue = labels[ bestfeature ];

	return bestfeature, bestfeatvalue

def createtree( dataset, labels ):
	""" 创建 C4.5 树
	"""

	classlist = [ i[ -1 ] for i in dataset ];

	# 若数据中类别完全相同则停止继续划分
	if classlist.count( classlist[ 0 ] ) == len( classlist ):
		return classlist[ 0 ];

	# 遍历完所有特征时返回出现次数最多的类别
	if len( dataset[ 0 ] ) == 1:
		return majoritycount( classlist );

	# 最佳区分特征列索引和区分值( 区分值对离散性数据无用 )
	bestfeature, bestfeatvalue = choosebestfeatureToSplit( dataset, labels );

	# 若无法选出最优分类特征, 返回出现次数最多的类别
	if bestfeature == -1:
		return majoritycount( classlist );

	# 最佳区分特征列名称
	bestfeatlabel = labels[ bestfeature ];

	# 构建树
	tree = { bestfeatlabel: {} };

	# 从 labels 中删除已确定的 labels;
	sublabels = labels[ :bestfeature ];
	sublabels.extend( labels[ bestfeature + 1 : ] );

	# 针对最佳切分特征是离散型
	if type( dataset[ 0 ][ bestfeature ] ).__name__ == "str":
		# 最佳特征列
		featvals = [ i[ bestfeature ] for i in dataset ];

		# 无重复最佳特征列
		uniqueVals = set( featvals );

		for i in uniqueVals:
			# 划分新数据
			reducedataset = splitdataset( dataset, bestfeature, i );

			# 递归构建树
			tree[ bestfeatlabel ][ i ] = createtree(
				reducedataset, sublabels );

	# 针对最佳切分特征为连续型特征
	if type( dataset[ 0 ][ bestfeature ] ).__name__ == "int" or type(
			dataset[ 0 ][ bestfeature ] ).__name__ == "float":

		# 将数据集划分为两个子集作为新数据, 针对每个子集分别建树
		greatersubdataset = splitcontinuousdataset(
			dataset, bestfeature, bestfeatvalue, 0 );
		smallsubdataset = splitcontinuousdataset(
			dataset, bestfeature, bestfeatvalue, 1 );

		# 针对连续型特征, 修改划分点的标签, 如 "> x.xxx", "<= x.xxx", 递归构建树
		tree[ bestfeatlabel ][ ">" + str( bestfeatvalue ) ] = createtree(
			greatersubdataset, sublabels );

		tree[ bestfeatlabel ][ "<=" + str( bestfeatvalue ) ] = createtree(
			smallsubdataset, sublabels );

	return tree;

def delcol( dataset, axis ):
	''' 删除列
	'''
	retdataset = [];
	for i in dataset:
		reducedfeatvec = i[ : axis ];
		reducedfeatvec.extend( i[ axis + 1 : ] );
		retdataset.append( reducedfeatvec );
	return retdataset;

def predictexample( tree, example ):
	for i in range( len( labels ) ):
		print( "i", i );
		print( "example 前", example );
		print( "得到: ", tree.get( labels[ i ], -1 ) );

		subtree = tree.get( labels[ i ], -1 );

		if subtree != -1:
			for j in subtree.keys():
				print( "--->", j[ 0 ], j[ 1: ] )

			print( "example[ i ]", example[ i ] )
			del example[ i ]

		print( "example 后", example );

# 预测值
def predictdataset( tree, labels, dataset ):

	x = delcol( dataset, len( dataset[ 0 ] ) - 1 );

	print( "tree", tree, labels );
	for example in x:
		predictexample( tree, example );
		print( "example", example );
		


if __name__ == "__main__":
	dataset, labels = createdataset();

	tree = createtree( dataset, labels );

	print( "C4.5 分类树: \n", tree );

	predictdataset( tree, labels, dataset );
