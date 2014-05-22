from scrapy.spider import Spider
from scrapy.selector import Selector
from scrapy import signals
from scrapy.xlib.pydispatch import dispatcher
from ..items import BuscadorItem
import json, csv
import urllib2
import os.path
import datetime

from scrapy.http.request import Request


class Troa(Spider):  
        name = "troa"
        allowed_domains = ["troa.es"]
        start_urls = []

        # def __init__(self, isbn='./'):
        #     self.isbn_txt=isbn+"isbn.txt"  
            
        #     reader = open(self.isbn_txt, 'r')
        #     if os.path.isfile('./temp.txt'):
        #         temp = open('./temp.txt', 'r')
        #         lista_temp = []
        #         for isbn in temp:
        #             lista_temp.append(isbn.strip())

        #         for isbn in reader:
        #             if isbn.strip() in lista_temp:
        #                 continue
        #             else:
        #                 self.start_urls.append("http://www.troa.es/busqueda/listaLibros.php?tipoBus=full&palabrasBusqueda="+isbn.strip())
        #     else:
        #         for isbn in reader:
        #             self.start_urls.append("http://www.troa.es/busqueda/listaLibros.php?tipoBus=full&palabrasBusqueda="+isbn.strip())              
            
        #     dispatcher.connect(self.elimina_temp, signals.spider_closed) 


        def __init__(self, isbn=''):
            
            self.start_urls.append("http://www.troa.es/busqueda/listaLibros.php?tipoBus=full&palabrasBusqueda="+isbn.strip())
            
            #dispatcher.connect(self.elimina_temp, signals.spider_closed) 


        def parse(self, response):
            try:
                sel = Selector(response)
                div = sel.css('div.product-info')
                url = div.xpath('.//a/@href')[0].extract()       
                yield Request('http://www.troa.es'+url, callback=self.leer)                                                           
            except:
                url = response.url.split("=")[2]
                self.escribe_temp(url)
                print "ISBN "+url+" procesado (No existe libro)"
        
        def leer(self, response):           
            sel = Selector(response)           
            con_titulo = sel.css('div.product-info')
            con_ficha = sel.css('ul#product-details')
            con_disp = sel.css('span#disponibilidad_entrega')
            con_precio = sel.css('div#product-buy-small')

            titulo = con_titulo.xpath('.//span/text()')[0].extract()
            autor = con_titulo.xpath('.//a/text()')[0].extract()
            editorial = con_ficha.xpath('.//li')[0].xpath('.//a/text()')[0].extract()
            isbn = con_ficha.xpath('.//li')[3].xpath('.//span/text()')[1].extract()
            paginas = con_ficha.xpath('.//li')[4].xpath('.//span/text()')[1].extract()
            disponibilidad = con_disp.xpath('.//span/text()')[1].extract()
            precio = con_precio.xpath('.//p/text()')[0].extract()

            item = BuscadorItem()
            item['ISBN'] = isbn
            item['titulo'] = titulo
            item['autor'] = autor
            item['num_pag'] = paginas
            item['editorial'] = editorial
            item['precio'] = precio
            item['disponibilidad'] = disponibilidad

            #self.escribe_temp(isbn)

            return item            
        
        def escribe_temp(self, isbn):
            temp = open('./temp.txt', 'ab')
            temp.write(isbn.strip()+"\n")
            temp.close()        

        def elimina_temp(self):
            os.remove('./temp.txt')