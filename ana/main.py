from twisted.internet import reactor, defer
from scrapy.crawler import CrawlerRunner
from scrapy.utils.project import get_project_settings
from ana.spiders.new_files import NewFilesSpider
from ana.spiders.update_records import UpdadeRecordsSpider

'''
    This script was created to run the project's spiders sequencing.
    The crawl() method is responsible for starting the scraping process.
    You can pass a list of reservoirs you want to scrape or not pass anything.
    If you don't pass any list the spider new_files will scrape all reservoirs
    
'''


@defer.inlineCallbacks
def crawl(list_reservoirs=None):
    settings = get_project_settings()
    runner = CrawlerRunner(settings)
    yield runner.crawl(NewFilesSpider, list_names_reservoirs=list_reservoirs)
    yield runner.crawl(UpdadeRecordsSpider)
    reactor.stop()


def main():
    #list_names_reservoirs = ['Furnas', 'Sobradinho', 'Três Marias', 'Emborcação', 'Serra da Mesa', 'Tucurui']
    list_names_reservoirs = ['Furnas']
    crawl(None)
    reactor.run()  # the script will block here until the last crawl call is finished


if __name__ == '__main__':
    main()
