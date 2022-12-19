# weibo-hot-search-spider
24小时爬取微博热搜榜，并将分析结果发送到邮箱 Climb the hot search list 24 hours a day and send the analysis results to the email

## 配置

1. 安装`jieba`库，命令行输入`pip install jieba`
1. 根据提示，替换掉`main.py`和`spider.py`中的中文非注释部分
1. 在`to_addrs.txt`中写入收信人的邮箱
1. 新建与`src`文件夹同级目录，命名为`log`
1. 如果不是 Linux 系统，那么将`main.py`第 150 行从`os.system('sudo python3 spider.py')`替换成`os.system('python3 spider.py')`
1. 在`src`目录下新建一个名为`crawledData.json`的文件，文件扩展名是`.json`

## 运行

在已经安装了 Python 环境的前提条件下，进入`src`目录，命令行输入`python main.py`即可运行。
