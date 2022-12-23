import json
import time
import requests
from bs4 import BeautifulSoup
import logger

log = logger.Logger('spider-%Y-%m-%d.log')
settings = {}

class Spider :

	def __init__(self) :
		global settings
		with open('settings.json', 'r', encoding='UTF-8') as f :
			settings = json.load(f)

	def run(self) :
		data = []
		data.append(self.__getDataFromWeibo())
		self.__saveData(data)
		log.info('crawledData: %s' % (str(data)))

	def __getDataFromWeibo(self) :
		global settings
		data = {}
		data['time'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
		data['source'] = 'weibo'
		data['items'] = []

		text = ''
		try:
			response = requests.get(
					url=settings["url"],
					headers={
				"User-Agent": settings["user-agent"],
				"Cookie": settings["cookie"]},
				timeout=30)
			response.raise_for_status()
			response.encoding = response.apparent_encoding
			response.close()
			text = response.text
			log.info('get html text from weibo successfully')
		except:
			log.info('failed to get html from weibo')
			return data

		soup = BeautifulSoup(text, 'html.parser')
		pre_items = soup.find_all('tr')
		for e in pre_items :
			try :
				if e.find('td', attrs={'class': 'td-01 ranktop'}).string.isdigit() :
					data['items'].append(e.find('td', attrs={'class': 'td-02'}).a.string)
			except :
				pass
		return data

	def __saveData(self, data) :
		log.info('write crawledData.json...')
		with open('crawledData.json', 'w', encoding='UTF-8') as f :
			json.dump(data, f)

spider = Spider()
spider.run()
