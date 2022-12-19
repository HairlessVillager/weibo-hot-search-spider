import os
import smtplib
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.header import Header
import time
import random
import jieba.posseg as psg
import json
import logger

log = logger.Logger('main-%Y-%m-%d.log')

class EmailSender :

	def sendEmails(self, content) :
		with open('to_addrs.txt', 'r', encoding='UTF-8') as f :
			for addr in f.readlines() :
				self.__sendEmail(addr, content)

	def __sendEmail(self, msgTo, content) :
		'''
		这里利用了 QQ 邮箱的 SMTP 服务，具体原理请百度：python QQ邮箱
		'''
		msgFrom = '这里写寄信人的邮箱'
		passwd = '这里写SMTP服务授权码'

		msg = MIMEMultipart()
		subject = Header(time.strftime("Daily News %Y-%m-%d", time.localtime()), 'utf-8')
		text = MIMEText(content, 'html', 'utf-8')
		msg.attach(text)

		msg['Subject'] = subject
		msg['From'] = msgFrom
		msg['To'] = msgTo
		log.info('try to send email to %s...' % (msgTo.rstrip()))
		try:
			s = smtplib.SMTP_SSL("smtp.qq.com", 465)
			s.login(msgFrom, passwd)
			s.sendmail(msgFrom, msgTo, msg.as_string())
			log.info('sent email to %s successfully' % (msgTo.rstrip()))
		except smtplib.SMTPException as e:
			log.info('failed to semd email to %s' % (msgTo.rstrip()))
		finally:
			s.quit()

class DataAnalyzer :
	__reportForm = ''

	def __init__(self, data) :
		self.__analyze(data)

	def __analyze(self, data) :
		log.info('analyzing...')
		self.__analyzeWord(data)
		self.__analyzeTopic(data)

	def __analyzeWord(self, data) :
		log.info('analyzing word...')
		words = []
		wordCount = {}
		for subData in data :
			for topic in subData['items'] :
				for e in psg.cut(topic) :
					if e.flag in ['n', 'nr', 'ns'] and len(e.word) >= 2 :
						words.append(e.word)
		for word in words :
			wordCount[word] = wordCount.get(word, 0) + 1
		wordCount = sorted(wordCount.items(), key=lambda x: x[1], reverse=True)[:20]
		log.info('%d words in total' % (len(words)))

		self.__reportForm += '<ol><h3>Top words today:</h3>'
		for e in wordCount:
			self.__reportForm += "<li>" + str(e[0]) + ' score = ' + str(e[1]) + "</li>"
		self.__reportForm += '</ol>'

	def __analyzeTopic(self, data) :
		log.info('analyzing topic...')
		topics = []
		topicCount = {}
		for subData in data :
			for topic in subData['items'] :
				topics.append(topic)
		for topic in topics :
			topicCount[topic] = topicCount.get(topic, 0) + 1
		topicCount = sorted(topicCount.items(), key=lambda x: x[1], reverse=True)[:20]
		log.info('%d topics in total' % (len(topics)))

		self.__reportForm += '<ol><h3>Top topics today:</h3>'
		for e in topicCount :
			self.__reportForm += "<li>" + str(e[0]) + ' score = ' + str(e[1]) + "</li>"
		self.__reportForm += '</ol>'

	def getReportForm(self) :
		return self.__reportForm

class HotSearchSpider :
	__emailSender = EmailSender()
	__updateFlag = True
	__noonToday = time.mktime(
		time.strptime(
			str(time.localtime().tm_year)
			+ ' ' + str(time.localtime().tm_mon)
			+ ' ' + str(time.localtime().tm_mday)
			+ ' ' + '12 00 00', '%Y %m %d %H %M %S'))
	__afternoonToday = time.mktime(
		time.strptime(
			str(time.localtime().tm_year)
			+ ' ' + str(time.localtime().tm_mon)
			+ ' ' + str(time.localtime().tm_mday)
			+ ' ' + '13 00 00', '%Y %m %d %H %M %S'))
	__crawledData = []

	def run(self) :
		self.__runMainLoop()

	def __runMainLoop(self) :
		while True :
			self.__crawledData.extend(self.__crawlAll())
			self.__tryUpdate()
			self.__wait()

	def __tryUpdate(self) :
		isAfterNoon = time.mktime(time.localtime()) > self.__noonToday
		isBeforeAfternoon = time.mktime(time.localtime()) < self.__afternoonToday
		log.info('__updateFlag : ' + str(self.__updateFlag))
		log.info('isAfterNoon : ' + str(isAfterNoon))
		log.info('isBeforeAfternoon : ' + str(isBeforeAfternoon))
		if isAfterNoon and isBeforeAfternoon and self.__updateFlag == False :
			log.info('updating...')
			self.__update()
			self.__updateFlag = True
		elif not isBeforeAfternoon and self.__updateFlag == True :
			self.__updateFlag = False
		else :
			pass

	def __update(self) :
		reportForm = self.__analyzeData(self.__crawledData)
		self.__emailSender.sendEmails(reportForm)
		self.__saveData(self.__crawledData)
		log.info('clear crawledData')
		self.__crawledData = []

	def __crawlAll(self) :
		''' spiderWaitTime is 5s '''
		spiderWaitTime = 5
		log.info('call spider.py...')
		os.system('sudo python3 spider.py')
		time.sleep(spiderWaitTime)
		log.info('read crawledData.json...')
		with open('crawledData.json', 'r', encoding='UTF-8') as f :
			return json.load(f)

	def __saveData(self, data) :
		log.info('write data...')
		with open(time.strftime("%Y-%m-%d.json", time.localtime()), 'w', encoding='UTF-8') as f :
			json.dump(data, f)

	def __analyzeData(self, data) :
		dataAnalyzer = DataAnalyzer(data)
		return dataAnalyzer.getReportForm()

	def __wait(self) :
		''' waitTime is 5~10 min '''
		waitTime = random.uniform(5 * 60, 10 * 60)
		log.info('sleep %f' % (waitTime))
		time.sleep(waitTime)

hotSearchSpider = HotSearchSpider()
hotSearchSpider.run()
