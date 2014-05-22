# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

from scrapy.item import Item, Field

class BuscadorItem(Item):
	ISBN = Field()
	titulo = Field()
	autor = Field()
	num_pag = Field()
	editorial = Field()
	precio = Field()
	disponibilidad = Field()