BOT_NAME = 'ana'
SPIDER_MODULES = ['ana.spiders']
NEWSPIDER_MODULE = 'ana.spiders'
# Absolute path that will be used to save the datasets
ABSOLUTE_PATH = r'C:\Users\tceco\OneDrive\Documentos\THIAGO\CODIGO_FONTE\PROJETOS\ana_gov\ana\ana\datasets'
# Obey robots.txt rules
ROBOTSTXT_OBEY = False
# Configure item pipelines
# See https://docs.scrapy.org/en/latest/topics/item-pipeline.html
ITEM_PIPELINES = {
   'ana.pipelines.AnaPipeline': 300,
}
# Enable and configure the AutoThrottle extension (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/autothrottle.html
AUTOTHROTTLE_ENABLED = True
# The initial download delay
AUTOTHROTTLE_START_DELAY = 1
# The maximum download delay to be set in case of high latencies
AUTOTHROTTLE_MAX_DELAY = 3

