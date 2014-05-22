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


class Babel(Spider):  
        name = "babel"
        allowed_domains = ["http://www.babellibros.com/"]
        start_urls = []

        def __init__(self, isbn='./'):
            self.isbn_txt=isbn+"isbn.txt"  
            
            reader = open(self.isbn_txt, 'r')
            if os.path.isfile('./temp.txt'):
                temp = open('./temp.txt', 'r')
                lista_temp = []
                for isbn in temp:
                    lista_temp.append(isbn.strip())

                for isbn in reader:
                    if isbn.strip() in lista_temp:
                        continue
                    else:
                        self.start_urls.append("http://www.babellibros.com/busqueda/listaLibros.php?tipoBus=full&palabrasBusqueda="+isbn.strip()+"&boton=Buscar")
            else:
                for isbn in reader:
                    self.start_urls.append("http://www.babellibros.com/busqueda/listaLibros.php?tipoBus=full&palabrasBusqueda="+isbn.strip()+"&boton=Buscar")              
            
            dispatcher.connect(self.elimina_temp, signals.spider_closed) 

        def parse(self, response):
            try:
                sel = Selector(response)
                div = sel.css('div.blMinifichaTextG')
                url = div.xpath('.//a/@href')[0].extract()
                print 'http://www.babellibros.com'+url             
                yield Request('http://www.babellibros.com'+url, callback=self.leer)                                                           
            except:
                url = response.url.split("=")[2].split("&")[0]
                self.escribe_temp(url)
                print "ISBN "+url+" procesado (No existe libro)"
        
        def leer(self, response):           
            sel = Selector(response)           
            con_ficha = sel.css('div.blMinifichaTextG')
            print 'Titulo: ' +con_ficha.xpath('.//dd/text()')[0].extract()
            print 'Autor: ' + con_ficha.xpath('.//dd')[2].xpath('.//a/text()')[0].extract()
            print 'Editorial: ' + con_ficha.xpath('.//dd')[3].xpath('.//a/text()')[0].extract()
            print 'Isbn: ' + con_ficha.xpath('.//dd/text()')[4].extract()
            con_dispo = sel.css('div.blDisponibilidad')
            print 'Disponibilidad: ' + con_dispo.xpath('.//text()')[0].extract().split('\t')[11].split('d')[0]
            print 'Paginas: ' + con_ficha.xpath('.//dd/text()')[5].extract()   
            con_precio = sel.css('div.blTextPrice')
            print 'Precio: ' + con_precio.xpath('.//text()')[2].extract().split(' ')[0]
            print '----------------------\n'
            self.escribe_temp(con_ficha.xpath('.//dd/text()')[4].extract())
        
        def escribe_temp(self, isbn):
            temp = open('./temp.txt', 'ab')
            temp.write(isbn.strip()+"\n")
            temp.close()        

        def elimina_temp(self):
            os.remove('./temp.txt')