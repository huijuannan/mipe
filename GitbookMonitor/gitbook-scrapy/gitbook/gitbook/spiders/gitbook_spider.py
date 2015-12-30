# coding=utf-8
import scrapy
import MySQLdb
from gitbook.items import GitbookItem
from gitbook.settings import USER, PASSWD


def get_start_urls():
    conn = MySQLdb.connect(
        host='localhost',
        user=USER,
        passwd=PASSWD,
        db='mipe'
    )
    cur = conn.cursor()
    cur.execute('SELECT url FROM Book')
    links = [link[0] for link in cur]
    return links


class GitbookSpider(scrapy.Spider):
    name = "mipe"
    start_urls = get_start_urls()

    def parse(self, response):
        links = response.css('li.chapter').xpath('a/@href').extract()
        for link in links:
            url = response.urljoin(link)
            yield scrapy.Request(url, callback=self.parse_links)

    def parse_links(self, response):
        self.logger.info('A response from %s just arrived!', response.url)
        item = GitbookItem()

        item['url'] = response.url

        title = response.xpath('//title/text()').extract()[0]
        title = title.split('|')[0].strip()
        title = title.encode('utf-8')
        item['title'] = title

        content = response.xpath('//section[@class="normal"]').extract()
        content = content[0].encode('utf-8')
        item['content'] = content

        return item
