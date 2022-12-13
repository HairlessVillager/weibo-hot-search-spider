import json
import time
import requests
from bs4 import BeautifulSoup
import logger

log = logger.Logger('spider-%Y-%m-%d.log')

class Spider :

	def run(self) :
		data = []
		data.append(self.__getDataFromWeibo())
		self.__saveData(data)
		log.info('crawledData: %s' % (str(data)))

	def __getDataFromWeibo(self) :
		data = {}
		data['time'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
		data['source'] = 'weibo'
		data['items'] = []

		text = ''
		try:
			response = requests.get(
					url="https://s.weibo.com/top/summary?cate=realtimehot",
					headers={
				"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.93 Safari/537.36 Edg/96.0.1054.53",
				"Cookie": "UOR=,,login.sina.com.cn; ALF=1666445729; SCF=AscEHVE2sTV05zTwYj5M7tduM7Zz3ktqPi21c2dTBB0sGFGcFIldixokcQ1yN8xFwVW-ywKnUt3rugqpWgzVXsE.; SINAGLOBAL=7267933806159.166.1634959444829; SUB=_2AkMW3d0wf8NxqwJRmPERzW_nbIx0yQ7EieKggSzrJRMxHRl-yT9jqhdftRB6PV3z3z21fp5a3CkZMXy5gZcyj15_nia0; SUBP=0033WrSXqPxfM72-Ws9jqgMF55529P9D9W56DO1wnAXX89yZnIENST5-; _s_tentry=-; Apache=6131946571247.373.1639292770571; ULV=1639292770592:2:1:1:6131946571247.373.1639292770571:1634959444907"},
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
