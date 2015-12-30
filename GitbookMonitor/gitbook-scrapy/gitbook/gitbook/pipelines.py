# coding=utf-8
import smtplib
import MySQLdb
# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html


def send_mail(to, url):
    SERVER = "localhost"
    FROM = "mipe@mipe.com"
    SUBJECT = "gitbook更新提醒"
    TEXT = "您订阅的gitbook有内容更新，具体请查看以下链接\n{}".format(url)
    message = """\
    From: {}
    To: {}
    Subject: {}

    {}
    """.format(FROM, ', '.join(to), SUBJECT, TEXT)

    server = smtplib.SMTP(SERVER)
    server.sendmail(FROM, to, message)
    server.quit()


class GitbookPipeline(object):
    def __init__(self, host, user, passwd, db):
        self.host = host
        self.user = user
        self.passwd = passwd
        self.db = db

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            host=crawler.settings.get('HOST'),
            user=crawler.settings.get('USER'),
            passwd=crawler.settings.get('PASSWD'),
            db=crawler.settings.get('DB')
        )

    def open_spider(self, spider):
        self.conn = MySQLdb.connect(
            host=self.host,
            user=self.user,
            passwd=self.passwd,
            db=self.db,
            charset='utf8'
        )
        self.cur = self.conn.cursor()

    def close_spider(self, spider):
        self.cur.close()
        self.conn.close()

    def process_item(self, item, spider):
        book_updated = {}
        book_url = '/'.join(item['url'].split('/')[:5]) + '/'
        item['book_id'] = self.find_book_id(book_url)

        if self.cur.execute(
            '''SELECT content FROM Chapter WHERE title=%s''',
            (item['title'],)
        ):
            content = self.cur.fetchone()
            if content != item['content']:
                book_updated[item['book_id']] = True
                self.cur.execute(
                    '''UPDATE Chapter SET content=%s WHERE title=%s''',
                    (item['content'], item['title'])
                )
                self.conn.commit()

                # send mail
                self.cur.execute(
                    "SELECT User.email FROM User, Subscribe "
                    "WHERE User.id=Subscribe.user_id and Subscribe.book_id=%s",
                    (item['book_id'], )
                )
                to = [mail[0] for mail in self.cur]
                send_mail(to, item['url'])
            else:
                pass
        else:
            self.cur.execute(
                '''INSERT INTO Chapter (url, title, content, book_id)'''
                '''VALUES (%s, %s, %s, %s)''',
                (item['url'], item['title'], item['content'], item['book_id'])
            )
            self.conn.commit()
        print book_updated
        return item

    def find_book_id(self, url):
        self.cur.execute(
            '''SELECT id FROM Book WHERE url=%s''',
            (url,)
        )
        return self.cur.fetchone()[0]
