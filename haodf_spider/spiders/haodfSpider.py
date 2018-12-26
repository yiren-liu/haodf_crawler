import scrapy
from haodf_spider.items import Review

headers = {}
URL = 'https://www.haodf.com'

class haodfSpider(scrapy.Spider):
	name = "haodfSpider"
	#allowed_domains = ['https://www.haodf.com']


	def start_requests(self):
		urls = [
			'https://www.haodf.com/sitemap-tp/p_1'
		]
		for url in urls:
			yield scrapy.Request(url=url, callback=self.parse_province)

	def parse_province(self, response):
		province_url = response.xpath('/html/body/div[2]/div[3]/div[2]/li/a/@href').extract()
		province_name = response.xpath('/html/body/div[2]/div[3]/div[2]/li/a/text()').extract()
		for idx, url in enumerate(province_url):
			for pageNum in range(1, 10):
				url = url.split('_')
				url[-1] = str(pageNum)
				url = "_".join(url)

				#self.log('parse_province called')
				yield scrapy.Request(url='https:'+url,
				                     callback=self.parse_hospital, meta={'province':province_name[idx]})

	def parse_hospital(self, response):
		#self.log('parse_hospital called')

		new_meta = response.meta

		hospital_url = response.xpath('/html/body/div[2]/div[3]/div[3]/li/a/@href').extract()
		hospital_name = response.xpath('/html/body/div[2]/div[3]/div[3]/li/a/text()').extract()

		for idx, url in enumerate(hospital_url):
			new_meta['hospital'] = hospital_name[idx]
			if not (url.startswith('http://') or url.startswith('https://')):
				url = URL + url

			yield scrapy.Request(url=url, callback=self.parse_dept, meta=new_meta)




	def parse_dept(self, response):

		new_meta = response.meta

		dept_url = response.xpath('/html/body/div[2]/div[3]/div[2]/li/a/@href').extract()
		dept_name = response.xpath('/html/body/div[2]/div[3]/div[2]/li/a/text()').extract()

		for idx, url in enumerate(dept_url):
			new_meta['department'] = dept_name[idx]
			if not (url.startswith('http://') or url.startswith('https://')):
				url = URL + url
				for pageNum in range(1, 5):
					url = url.split('_')
					url[-1] = str(pageNum)
					url = "_".join(url)

					yield scrapy.Request(url=url, callback=self.parse_review,meta=new_meta)

	def parse_review(self, response):

		patient_names = response.xpath(
			'/html/body/div[2]/div[3]/div/table/tr[2]/td[2]/table/tr[1]/td[1]/text()'
		).extract()

		disease_names = response.xpath(
			'/html/body/div[2]/div[3]/div/table/tr[2]/td[2]/table/tr[2]/td/a/text()'
		).extract()

		review_times = response.xpath(
			'/html/body/div[2]/div[3]/div/table/tr[2]/td[2]/table/tr[1]/td[2]/text() |'
			'/html/body/div[2]/div[3]/div/table/tr[2]/td[2]/table/tr[1]/td[2]/span/text()'
		).extract()

		# get doctor names
		doc_names = []
		for i in range(8):
			doc_name = response.xpath(
				'/html/body/div[2]/div[3]/div/table[' + str(i + 1) + ']/tr[2]/td[2]/table/tr[3]/td[1]/a/text()'
			).extract()
			if len(doc_name) == 0:
				doc_names.append('')
			else:
				doc_names.append(doc_name[0])

		doc_urls = response.xpath(
			'/html/body/div[2]/div[3]/div/table/tr[2]/td[2]/table/tr[3]/td[1]/a/@href'
		).extract()

		# payments
		payments = response.xpath(
			'/html/body/div[2]/div[3]/div/table/tr[2]/td[2]/table/tr[4]/td/span/text()'
		).extract()
		# for i, payment in enumerate(payments):
		# 	payments[i] = payment.split('：')[-1]
		for i in range(8):
			if i < len(payments):
				payments[i] = payments[i].split('：')[-1]
			else:
				payments.append('')


		# get attitude_ratings
		attitude_ratings = []
		for i in range(8):
			attitude_rating = response.xpath(
				'/html/body/div[2]/div[3]/div/table[' + str(i + 1) + ']/tr[2]/td[2]/table/tr[3]/td[2]/span/text()'
			).extract()
			if len(attitude_rating) == 0:
				attitude_ratings.append('')
			else:
				attitude_ratings.append(attitude_rating[0])
		# attitude_ratings = response.xpath(
		# 	'/html/body/div[2]/div[3]/div/table/tr[2]/td[2]/table/tr[3]/td[2]/span/text()'
		# ).extract()

		#*** GET SUBJECTIVE FEEDBACKS ***
		# subjective_feedbacks = []
		# temp_subjective_feedbacks= response.xpath(
		# 	'/html/body/div[2]/div[3]/div/table/tr[2]/td[2]/table/tr[2]/td[2]/span/text()'
		# ).extract()
		# for i in range(len(temp_subjective_feedbacks)):
		# 	feedback = (
		# 		response.xpath(
		# 		'/html/body/div[2]/div[3]/div/table['+str(i+1)+']/tr[2]/td[2]/table/tr[2]/td[2]/span/text()'
		# 	).extract()
		# 	)
		# 	if not len(feedback) == 0:
		# 		subjective_feedbacks.append(feedback[0])
		# 	else:
		# 		subjective_feedbacks.append('')

		# *** GET SUBJECTIVE FEEDBACKS ***
		subjective_feedbacks = []

		for i in range(8):
			feedback = (
				response.xpath(
					'/html/body/div[2]/div[3]/div/table[' +
					str(i + 1) + ']/tr[2]/td[2]/table/tr[2]/td[2]/span/text()'
				).extract()
			)
			if not len(feedback) == 0:
				subjective_feedbacks.append(feedback[0])
			else:
				subjective_feedbacks.append('')

		# *** GET REVIEW TEXTS ***
		temp_review_texts = response.xpath(
			'/html/body/div[2]/div[3]/div/table/tr[3]/td[2]/table/tr[2]/td/text()[1] | '
			'/html/body/div[2]/div[3]/div/table/tr[3]/td[2]/table/tr[2]/td/text()[3]'
		).extract()
		review_texts=[]
		for review in temp_review_texts:
			if review is not '\n':
				review = review.strip().replace('\r\n',' ')
				review_texts.append(review)

		# save items #
		for i in range(len(patient_names)):
			new_item = Review()
			new_item['province'] = response.meta['province']
			new_item['hospital'] = response.meta['hospital']
			new_item['department'] = response.meta['department']

			new_item['patient'] = patient_names[i]
			new_item['disease'] = disease_names[i]
			new_item['time'] = review_times[i]
			new_item['doctor'] = doc_names[i]
			new_item['payment'] = payments[i]
			new_item['effect_rating'] = subjective_feedbacks[i]
			new_item['attitude_rating'] = attitude_ratings[i]
			new_item['text'] = review_texts[i]

			yield new_item

	# filename = 'test.txt'
	# with open(filename, 'w') as f:
	#     f.write(str(department))
	# self.log('Saved file %s' % filename)

