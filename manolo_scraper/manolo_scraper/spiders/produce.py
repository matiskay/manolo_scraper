# -*- coding: utf-8 -*-
import datetime
from datetime import timedelta

import scrapy

from spiders import ManoloBaseSpider
from ..item_loaders import ManoloItemLoader
from ..items import ManoloItem
from ..utils import make_hash


class ProduceSpider(ManoloBaseSpider):
    name = 'produce'
    allowed_domains = ['http://www2.produce.gob.pe']

    def start_requests(self):
        d1 = datetime.datetime.strptime(self.date_start, '%Y-%m-%d').date()
        d2 = datetime.datetime.strptime(self.date_end, '%Y-%m-%d').date()

        delta = d2 - d1

        for i in range(delta.days + 1):
            date = d1 + timedelta(days=i)
            date_str = date.strftime('%d/%m/%Y')

            print('SCRAPING: %s' % date_str)

            request = scrapy.FormRequest('http://www2.produce.gob.pe/produce/transparencia/visitas/',
                                         formdata={
                                             'desFecha': date_str,
                                             'desFechaF': date_str,
                                             'buscar': 'Consultar'
                                         },
                                         callback=self.parse)

            request.meta['date'] = date_str
            yield request

    def parse(self, response):
        date_obj = datetime.datetime.strptime(response.meta['date'], '%d/%m/%Y')
        date = datetime.datetime.strftime(date_obj, '%Y-%m-%d')

        rows = response.xpath('//table[@class="tabla-login" and @width="100%"]//tr')

        for row in rows:
            data = row.xpath('td[@valign="top"]')

            if len(data) > 9:

                l = ManoloItemLoader(item=ManoloItem(), selector=row)

                l.add_value('institution', 'produce')
                l.add_value('date', date)

                l.add_xpath('time_start', './td[3]/text()')
                l.add_xpath('full_name', './td[4]/text()')
                l.add_xpath('id_document', './td[5]/text()')
                l.add_xpath('id_number', './td[6]/text()')
                l.add_xpath('reason', './td[7]/text()')
                l.add_xpath('host_name', './td[8]/text()')
                l.add_xpath('office', './td[9]/text()')
                l.add_xpath('time_end', './td[10]/text()')

                item = l.load_item()

                item = make_hash(item)

                yield item
