import time

class Logger :
	__fileName = ''

	def __init__(self, fileName) :
		self.__fileName = '../log/' + fileName

	def info(self, msg) :
		logMsg = time.strftime("[%Y-%m-%d %H:%M:%S]", time.localtime()) + ' ' + msg + '\n'
		with open(time.strftime(self.__fileName, time.localtime()), 'a', encoding='UTF-8') as f :
			f.write(logMsg)
		print(logMsg)
