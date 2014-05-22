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


class Picasso(Spider):  
        name = "picasso"
        allowed_domains = ["librerias-picasso.com"]
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
                        self.start_urls.append("http://www.librerias-picasso.com/busqueda/listaLibros.php?tipoBus=full&palabrasBusqueda="+isbn.strip()+"&botbusqueda=Buscar")
            else:
                for isbn in reader:
                    self.start_urls.append("http://www.librerias-picasso.com/busqueda/listaLibros.php?tipoBus=full&palabrasBusqueda="+isbn.strip()+"&botbusqueda=Buscar")              
            
            dispatcher.connect(self.elimina_temp, signals.spider_closed) 

        def parse(self, response):
            try:
                sel = Selector(response)
                div = sel.css('div#resultadosbusqueda')
                url = div.xpath('.//a/@href')[0].extract()            
                yield Request('http://www.librerias-picasso.com'+url, callback=self.leer)                                                            
            except:
                url = response.url.split("=")[2].split("&")[0]
                self.escribe_temp(url)
                print "ISBN "+url+" procesado (No existe libro)"
        
        def leer(self, response):            
            sel = Selector(response)
            con_titulo = sel.css('div#otrasopbusqueda')
            print 'Titulo: ' +con_titulo.xpath('.//h3/text()')[0].extract()
            con_ficha = sel.css('div.fichalibroCol')
            print 'Autor: ' + con_ficha.xpath('.//dd')[0].xpath('.//a/text()')[0].extract()
            print 'Editorial: ' + con_ficha.xpath('.//dd')[1].xpath('.//a/text()')[0].extract()
            print 'Isbn: ' + con_ficha.xpath('.//dd/text()')[4].extract()
            print 'Disponibilidad: ' + con_ficha.xpath('.//dd/text()')[5].extract()
            print 'Paginas: ' + con_ficha.xpath('.//dd/text()')[6].extract()   
            con_precio = sel.css('div.botonComprar')
            print 'Precio: ' + con_precio.xpath('.//div/text()')[0].extract().split('\t')[11].split(' ')[0]
            print '----------------------\n'
            self.escribe_temp(con_ficha.xpath('.//dd/text()')[4].extract())
        
        def escribe_temp(self, isbn):
            temp = open('./temp.txt', 'ab')
            temp.write(isbn.strip()+"\n")
            temp.close()        

        def elimina_temp(self):
            os.remove('./temp.txt')