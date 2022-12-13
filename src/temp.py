import smtplib
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.header import Header
import time
import random
import requests
import jieba.posseg as psg
import wordcloud
from bs4 import BeautifulSoup
import bs4
import json

log = []
data = []
data_json = []
system_end_time = time.mktime(time.strptime("2022-12-30 13:00:00",'%Y-%m-%d %H:%M:%S'))
send_flag = False

def writeLog(msg) :
	global log
	log_msg = time.strftime("[%Y-%m-%d %H:%M:%S]", time.localtime()) + ' ' + msg + '\n'
	log.append(log_msg)
	print(log_msg)

def getHTMLFrom(url, cookie):
	try:
		kv = {
			"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.93 Safari/537.36 Edg/96.0.1054.53",
			"Cookie": cookie
		}
		r = requests.get(url, headers=kv, timeout=30)
		r.raise_for_status()
		r.encoding = r.apparent_encoding
		r.close()
		writeLog('successed to get HTML from ' + url)
		return r.text
	except:
		writeLog('failed to get HTML from ' + url)
		return "error"

def getPreprocessedData(html) :
	soup = BeautifulSoup(html, 'html.parser')
	pre_items = soup.find_all('tr')
	normal_items = []
	for e in pre_items :
		writeLog(' e in pre_items:' + str(e))
		try :
			if e.find('td', attrs={'class': 'td-01 ranktop'}).string.isdigit() :
				normal_items.append(e.find('td', attrs={'class': 'td-02'}).a.string)
		except :
			pass
	writeLog('length of normal_items: ' + str(len(normal_items)))
	writeLog('normal_items: ' + str(normal_items))
	return normal_items

def processData(data) :
	s = {}
	s['time'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
	s['source'] = 'weibo'
	s['items'] = data
	data_json.append(s)
	file_name = time.strftime("%Y_%m_%d.png", time.localtime())
	words = getWordsFrom(data)
	text = ' '.join(words)
	err = getWordcloudFrom(text, file_name)
	if err == 'error' :
		html = "<h3>Word cloud today:</h3><p>failed to generate the wordcloud</p>"
	else :
		html = "<h3>Word cloud today:</h3><p><img decoding='async' src='cid:image1' alt='result' width='1080' height='720'></p>"

	wordcount = {}
	for word in words :
		wordcount[word] = wordcount.get(word, 0) + 1
	wordcount = sorted(wordcount.items(), key=lambda x: x[1], reverse=True)[:20]
	html += '<ol><h3>Top words today:</h3>'
	for e in wordcount :
		html += "<li>" + str(e[0]) + ' score = ' + str(e[1]) + "</li>"
	html += '</ol>'

	sentcount = {}
	for sent in data :
		sentcount[sent] = sentcount.get(sent, 0) + 1
	sentcount = sorted(sentcount.items(), key=lambda x: x[1], reverse=True)[:20]
	html += '<ol></h3>Top topics today:</h3>'
	for e in sentcount:
		html += "<li>" + str(e[0]) + ' score = ' + str(e[1]) + "</li>"
	html += '</ol>'

	writeLog('html built successfully')
	return html

def getWordsFrom(items) :
	words = []
	for item in items :
		for e in psg.cut(item) :
			if e.flag in ['n', 'nr', 'ns'] and len(e.word) :
				words.append(e.word)
	return words

def getWordcloudFrom(text, file_name) :
	w = wordcloud.WordCloud(font_path='simhei.ttf', width=1080, height=720, background_color='white')
	writeLog('text[:300] in getWordcloudFrom():' + text[:300])
	try :
		w.generate(text)
	except :
		writeLog('failed to generate wordcloud')
		return 'error'
	w.to_file(file_name)
	writeLog('filename of wordcloud picture: ' + file_name)
	return 'ok'

def sendEmailTo(mail_msg, to_addrs) :
	from_addr='hairlessvillager@qq.com'
	qqCode='fhbczkwjlcazcfbb'
	smtp_server='smtp.qq.com'
	smtp_port = 465
	stmp = smtplib.SMTP_SSL(smtp_server,smtp_port)
	stmp.login(from_addr,qqCode)
	t = time.localtime()

	msgRoot = MIMEMultipart('related')
	msgRoot['From'] = Header("HairlessVillager Daily News System", 'utf-8')
	msgRoot['To'] =  Header("Registered user", 'utf-8')
	msgRoot['Subject'] = Header(time.strftime("Daily News %Y-%m-%d",t), 'utf-8')

	msgAlternative = MIMEMultipart('alternative')
	msgRoot.attach(msgAlternative)

	msgAlternative.attach(MIMEText(mail_msg, 'html', 'utf-8'))

	fp = open(time.strftime("%Y_%m_%d.png", time.localtime()), 'rb')
	msgImage = MIMEImage(fp.read())
	fp.close()

	msgImage.add_header('Content-ID', '<image1>')
	msgRoot.attach(msgImage)

	try:
		writeLog('try to send smail to ' + to_addrs + '...')
		stmp.sendmail(from_addr, to_addrs, msgRoot.as_string())
		writeLog('send successfully')
	except Exception as e:
		writeLog('failed to send email to ' + to_addrs + ' as ' + str(e))

def sendEmails(mail_msg) :
	with open('to_addrs.txt', 'r', encoding='UTF-8') as f :
		for to_addr in f.readlines() :
			sendEmailTo(mail_msg, to_addr.strip())

while time.mktime(time.localtime()) < system_end_time :
	morning_today = time.mktime(
		time.strptime(
			str(time.localtime().tm_year)
			+ ' ' + str(time.localtime().tm_mon)
			+ ' ' + str(time.localtime().tm_mday)
			+ ' ' + '7 00 00', '%Y %m %d %H %M %S'))
	noon_today = time.mktime(
		time.strptime(
			str(time.localtime().tm_year)
			+ ' ' + str(time.localtime().tm_mon)
			+ ' ' + str(time.localtime().tm_mday)
			+ ' ' + '12 00 00', '%Y %m %d %H %M %S'))
	afternoon_today = time.mktime(
		time.strptime(
			str(time.localtime().tm_year)
			+ ' ' + str(time.localtime().tm_mon)
			+ ' ' + str(time.localtime().tm_mday)
			+ ' ' + '14 00 00', '%Y %m %d %H %M %S'))
	night_today = time.mktime(
		time.strptime(
			str(time.localtime().tm_year)
			+ ' ' + str(time.localtime().tm_mon)
			+ ' ' + str(time.localtime().tm_mday)
			+ ' ' + '23 00 00', '%Y %m %d %H %M %S'))

	html = getHTMLFrom(
		url="https://s.weibo.com/top/summary?cate=realtimehot",
		cookie='UOR=,,login.sina.com.cn; ALF=1666445729; SCF=AscEHVE2sTV05zTwYj5M7tduM7Zz3ktqPi21c2dTBB0sGFGcFIldixokcQ1yN8xFwVW-ywKnUt3rugqpWgzVXsE.; SINAGLOBAL=7267933806159.166.1634959444829; SUB=_2AkMW3d0wf8NxqwJRmPERzW_nbIx0yQ7EieKggSzrJRMxHRl-yT9jqhdftRB6PV3z3z21fp5a3CkZMXy5gZcyj15_nia0; SUBP=0033WrSXqPxfM72-Ws9jqgMF55529P9D9W56DO1wnAXX89yZnIENST5-; _s_tentry=-; Apache=6131946571247.373.1639292770571; ULV=1639292770592:2:1:1:6131946571247.373.1639292770571:1634959444907')
	if html != 'error' :
		preprocessed_data = getPreprocessedData(html)
		data.extend(preprocessed_data)

	if time.mktime(time.localtime()) > noon_today and time.mktime(time.localtime()) < afternoon_today and send_flag == False :
		html = processData(data)
		sendEmails(html)
		# sendEmailTo(html, to_addrs='1278783738@qq.com')
		# sendEmailTo(html, to_addrs='hairlessvillager@qq.com')
		# sendEmailTo(html, to_addrs='world_hamster@qq.com')
		with open(time.strftime("log_%Y_%m_%d.txt", time.localtime()), 'a+', encoding='utf-8') as f :
			f.write('\n'.join(log))
		with open(time.strftime("data_%Y_%m_%d.json", time.localtime()), 'w', encoding='utf-8') as f :
			json.dump(data_json, f)
		log = []
		data = []
		send_flag = True
		writeLog('let send_flag = True')
	elif time.mktime(time.localtime()) > afternoon_today and send_flag == True :
		send_flag = False;
		writeLog('let send_flag = False')
		writeLog('no send email')
	else :
		writeLog('let send_flag = True')
		writeLog('no send email')

	if time.mktime(time.localtime()) > morning_today and time.mktime(time.localtime()) < night_today :
		t = random.uniform(5 * 60, 10 * 60)
		writeLog('sleep, time = ' + str(t))
		time.sleep(t)
	else :
		t = random.uniform(30 * 60, 60 * 60)
		writeLog('sleep, time = ' + str(t))
		time.sleep(t)
