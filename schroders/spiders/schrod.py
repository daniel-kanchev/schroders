import scrapy
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst
from datetime import datetime
from schroders.items import Article


class SchrodSpider(scrapy.Spider):
    name = 'schrod'
    start_urls = ['https://www.schroders.com/en/insights/']

    def parse(self, response):
        links = response.xpath('//div[@class="row insight-section "]//div[@class="col-xs-12"]/a/@href').getall()
        yield from response.follow_all(links, self.parse_article)

        next_page = response.xpath('//li[@class="next "]/a/@href').get()
        if next_page:
            yield response.follow(next_page, self.parse)

    def parse_article(self, response):
        item = ItemLoader(Article())
        item.default_output_processor = TakeFirst()

        title = response.xpath('//h1[@itemprop="headline"]/text()').get().strip()
        date = response.xpath('//p[@class="date hidden-xs hidden-sm show-print"]/text()').get().strip()
        date = datetime.strptime(date, '%d %B %Y')
        date = date.strftime('%Y/%m/%d')
        content = response.xpath('//div[@id="mainBody"]//text()').getall()
        content = [text for text in content if text.strip()]
        content = "\n".join(content).strip()
        category = response.xpath('//span[@class="no-print"]//span[@class="category"]/text()').get()
        if category:
            category = category.strip()
        author = response.xpath('//p[@class="name"]/text()').get()
        if author:
            author = author.strip()

        item.add_value('title', title)
        item.add_value('date', date)
        item.add_value('link', response.url)
        item.add_value('content', content)
        item.add_value('author', author)
        item.add_value('category', category)

        return item.load_item()
