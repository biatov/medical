import re

import scrapy
from ..items import MedicalItem


class Medical(scrapy.Spider):
    name = 'main'
    allowed_domains = ['medicalboard.gov.au']
    start_urls = ['http://www.medicalboard.gov.au/News/Past-Consultations.aspx']

    def parse(self, response):

        def default_item(xpath_value):
            try:
                return response.xpath(xpath_value).extract_first().strip()
            except AttributeError:
                return ''

        try:
            EVENTTARGET = default_item('//a[@class="consultationSummaryBtn"]/@href').split("'")[1]
        except (TypeError, IndexError):
            EVENTTARGET = ''

        VIEWSTATEFIELDCOUNT = default_item('//input[@id="__VIEWSTATEFIELDCOUNT"]/@value')
        VIEWSTATE = default_item('//input[@id="__VIEWSTATE"]/@value')
        VIEWSTATE1 = default_item('//input[@id="__VIEWSTATE1"]/@value')
        VIEWSTATEGENERATOR = default_item('//input[@id="__VIEWSTATEGENERATOR"]/@value')
        SCROLLPOSITIONX = '0'
        SCROLLPOSITIONY = '0'
        EVENTVALIDATION = default_item('//input[@id="__EVENTVALIDATION"]/@value')
        ctl22_ctl00_ddBoards = 'http://www.medicalboard.gov.au/'
        ctl22_ddBoards = ctl22_ctl00_ddBoards
        ItemId = default_item(
            '//input[@name="content_0$contentcolumnmain_0$rptPastConsultations$ctl00$hdnConsultationItemId"]/@value'
        )
        DetailedContent = default_item(
            '//input[@name="content_0$contentcolumnmain_0$rptPastConsultations$ctl00$hdnDetailedContent"]/@value'
        )
        Submissions = default_item(
            '//input[@name="content_0$contentcolumnmain_0$rptPastConsultations$ctl00$hdnSubmissions"]/@value'
        )

        yield scrapy.FormRequest(
            url=self.start_urls[0],
            formdata={
                '__EVENTTARGET': EVENTTARGET,
                '__VIEWSTATEFIELDCOUNT': VIEWSTATEFIELDCOUNT,
                '__VIEWSTATE': VIEWSTATE,
                '__VIEWSTATE1': VIEWSTATE1,
                '__VIEWSTATEGENERATOR': VIEWSTATEGENERATOR,
                '__SCROLLPOSITIONX': SCROLLPOSITIONX,
                '__SCROLLPOSITIONY': SCROLLPOSITIONY,
                '__EVENTVALIDATION': EVENTVALIDATION,
                'ctl22$ctl00$ddBoards': ctl22_ctl00_ddBoards,
                'ctl22$ddBoards': ctl22_ddBoards,
                'content_0$contentcolumnmain_0$rptPastConsultations$ctl00$hdnConsultationItemId': ItemId,
                'content_0$contentcolumnmain_0$rptPastConsultations$ctl00$hdnDetailedContent': DetailedContent,
                'content_0$contentcolumnmain_0$rptPastConsultations$ctl00$hdnSubmissions': Submissions,
                '__EVENTARGUMENT': '',
                '__LASTFOCUS': '',
                '__VIEWSTATEENCRYPTED': '',
                'ctl22$ctl00$ucSearch$txtSearch': '',
                'ctl22$ucSearch$txtSearch': '',

            },
            headers={
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
                'Accept-Encoding': 'gzip, deflate',
                'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.6,en;q=0.4',
                'Cache-Control': 'max-age=0',
                'Connection': 'keep-alive',
                'Content-Type': 'application/x-www-form-urlencoded',
                'Host': 'www.medicalboard.gov.au',
                'Origin': 'http://www.medicalboard.gov.au',
                'Referer': 'http://www.medicalboard.gov.au/News/Past-Consultations.aspx',
                'Upgrade-Insecure-Requests': '1',
                'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.91 Safari/537.36',
            },
            callback=self.parse_comments
        )

    def parse_comments(self, response):
        item = MedicalItem()
        no_data = ''
        data = response.xpath('//div[@id="content_0_contentcolumnmain_0_pnlViewComments"]').xpath('div[contains(@class, "indent")]')
        for count, each in enumerate(data):
            try:
                user = list(
                    filter(
                        None,
                        map(
                            lambda i: i.strip(),
                            re.split(
                                '[).+(]',
                                each.xpath('li/p[@class="postUser"]/text()').extract_first()[::-1],
                                maxsplit=2
                            )
                        )
                    )
                )
            except (AttributeError, TypeError):
                user = list()
            try:
                item['name'] = user[-1][::-1] if user else no_data
            except IndexError:
                item['name'] = no_data
            try:
                item['profession'] = user[0][::-1] if user else no_data
            except IndexError:
                item['profession'] = no_data

            try:
                datetime = each.xpath('li/p[@class="postDate"]/text()').extract_first().strip().split(': ')[1].split()
            except (AttributeError, TypeError, IndexError):
                datetime = list()
            item['date'] = ' '.join(datetime[:3]) if datetime else no_data
            item['time'] = ' '.join(datetime[3:]) if datetime else no_data

            try:
                item['text'] = each.xpath('li/p[@class="postComment"]/text()').extract_first().strip()
            except AttributeError:
                item['text'] = no_data

            try:
                current_indent = int(each.xpath('@class').extract_first().strip().replace('indent', ''))
            except (AttributeError, TypeError):
                current_indent = 0

            if current_indent:

                prev_count = 0

                while current_indent - int(
                        data[count-prev_count].xpath('@class').extract_first().replace('indent', '')
                ) <= 0:
                    prev_count += 1

                try:
                    item['response'] = data[count-prev_count].xpath(
                        'li/p[@class="postDate"]/text()'
                    ).extract_first().strip().split(': ')[1]
                except (AttributeError, TypeError, IndexError):
                    item['response'] = no_data
            else:
                item['response'] = no_data
            yield item
