文章写在我的[csdn博客](https://blog.csdn.net/Fourierrr_/article/details/80053877)，感兴趣的给个赞啦~
 -----

#前言
一般来说，在学习某个新技术之前，都会写一个Hello World！的小程序，这个程序简单但是包含了一个程序所必须具备的一切。MapReduce程序也有自己的Hello World，那即是Word Count。

在学习用python编写word count的过程中，遇到了许多坑，网上许多教程都过时了或者版本不对，许多基于python的word count教程都是转载自或者翻译自这片文章http://www.michael-noll.com/tutorials/writing-an-hadoop-mapreduce-program-in-python/.

从截图来判断，文章是2007年写的，使用的可能是python2.x，Hadoop0.x版本。现在来看显然已经过时了。参考了那篇文章后，本文使用python3.6，Hadoop2.7.4在ubuntu16.04的环境下实现python编写的wordcount的MapReduce程序。
#正文
实现wordcount任务，我们分别编写mapper.py和reducer.py，其中mapper.py负责将文章切分为单个单词，以<单词，1>的元组形式输出，其中1代表数量，英文mapper只负责分割，所以每个单词数量都是1，注意会有重复的单词，比如you，那么会多次出现元组<you,1>。到了reducer时，再讲相同的单词合并，数量相加，成为一个元组。

##mapper.py
首先我们来编写mapper，逻辑不负责，代码如下：

```
#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @Date    : 2018-04-16 14:13:44

"""mapper.py"""
import sys
import re
# print("hello world")

for line in sys.stdin:
	line = line.strip()
	words = re.split('[,.?\s"]',line)
	for word in words:
		word = word.strip(',|.|?|\s')
		if word:
			
			print("{0}\t{1}".format(word,1))
```
从标准输入里边读取数据，然后直接使用split分词，然后打印。注意，这里用的re.split而不是str.split主要因为前者可以添加多个分词规则。
##reducer.py
这个逻辑相对复杂一点，循环比较当前单词与上个单词，相同就数量加一，不同说明当前单词统计结束，输出它，然后开始统计下一个单词的数量。

最开始我看这个逻辑有点懵，后来看了书才知道，Hadoop会自动在map后对输出结果进行排序，所以这个reducer.py是基于排序后的mapper的结果的。

代码如下：

```
#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @Date    : 2018-04-16 16:13:15

"""resucer.py"""
import sys

current_word = None
current_count = 0
word = None

for line in sys.stdin:
	word = line.split('\t',1)[0]
	count = line.split('\t',1)[1]
	count = int(count)
	if current_word == word:
		current_count+=count
	else:
		if current_word:
			print("{0}\t{1}".format(current_word,current_count))
		current_word = word
		current_count = count

if word:
	print("{0}\t{1}".format(current_word,current_count))

```
##测试
我们先用简单的shell测试一下我们写的代码逻辑对不对。

由于是直接运行的python文件所以要自己手动加上排序，不然reducer没法正常运行

```
$ echo "you? you, wow" | mapper.py | sort | reducer.py
```
echo 作为标准输入传给mapper，输出结果排序后又作为标准输入传给reducer。最后输出结果如下：

```
wow    1
you    2
```
与预期结果一样，说明是没问题的
##在Hadoop上运行
接下来把我们的代码放到Hadoop上运行，由于Hadoop是java编写的，运行时需要导入程序的jar包才行，正常情况下，可以用eclipse自带的打包工具打包写好的java代码。

然而，我们是用python编写的，怎么办呢？这个时候就需要用到Hadoop自带的工具streaming了，它可以自动帮我们将标准输入输出流串起来。且streaming.jar是Hadoop可运行的。

cd到Hadoop目录下，我们先启动hdfs，将本地文件put到dfs上用户的test文件夹下，这里我选择的是2014年卡梅伦挽留苏格兰脱英的演讲稿lets_stick_together

```
$ hdfs dfs -put /lets_stick_together ./test
```
然后运行一下shell，注意，下边代码中Hadoop-streaming工具的位置是Hadoop2.7.4中的。如果版本不同，可能位置也不同，按照开头那篇文章的示例代码是找不到streaming的。

```
bin/hadoop jar share/hadoop/tools/lib/hadoop-streaming-2.7.4.jar \
-file ~/SublimProjects/mapper.py -mapper ~/SublimProjects/word_count/mapper.py \
-file ~/SublimProjects/reducer.py -reducer ~/SublimProjects/word_count/reducer.py \
-input ./test/* -output ./test_out1
```
注意输出目录在运行前不能存在，test_out1会自动在MapReduce运行后创建。运行成功会有很多info，其中有map任务和reduce任务的进度等等，如下图：
![](https://img-blog.csdn.net/20180424143339427?watermark/2/text/aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L0ZvdXJpZXJycl8=/font/5a6L5L2T/fontsize/400/fill/I0JBQkFCMA==/dissolve/70)
当然内容不止这一点点，前后还有许多，图太长就不放全部了。

接下来我们可以在test_out1文件夹中找到输出的文件了，我们先-ls看下：
![这里写图片描述](https://img-blog.csdn.net/20180424143852504?watermark/2/text/aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L0ZvdXJpZXJycl8=/font/5a6L5L2T/fontsize/400/fill/I0JBQkFCMA==/dissolve/70)
其中，_SUCCESS代表MapReduce任务成功，真正的输出结果是分段保存在part-xxxxx文件中的，由于我们的程序很简单，所以就只有一段，我们用cat指令打开看看：

```
$ hdfs dfs -cat ./test_out1/part-00000
```
输出结果如下图所示，成功统计了不同词语的次数：
![](https://img-blog.csdn.net/20180424144332108?watermark/2/text/aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L0ZvdXJpZXJycl8=/font/5a6L5L2T/fontsize/400/fill/I0JBQkFCMA==/dissolve/70)
成功！
#结语
这只是一个最简单的MapReduce任务，但却包含了其所必须具备的一切。其实，这个程序我们还可以做一些优化，比如reducer.py我们可以用使用生成器节约内存等等。
