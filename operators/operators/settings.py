# Scrapy settings for operators project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://docs.scrapy.org/en/latest/topics/settings.html
#     https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://docs.scrapy.org/en/latest/topics/spider-middleware.html

BOT_NAME = "operators"

SPIDER_MODULES = ["operators.spiders"]
NEWSPIDER_MODULE = "operators.spiders"


# Crawl responsibly by identifying yourself (and your website) on the user-agent
USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/114.0"

# Obey robots.txt rules
ROBOTSTXT_OBEY = True

# Set settings whose default value is deprecated to a future-proof value
REQUEST_FINGERPRINTER_IMPLEMENTATION = "2.7"
TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"
FEED_EXPORT_ENCODING = "utf-8"

# Pipeline for MongoDB Connection
ITEM_PIPELINES = {
  "operators.pipelines.MongoDBPipeline": 500
}

MONGODB_URI = "Your URI Connection String"
MONGODB_DATABASE = "Your Database Name"
MONGODB_COLLECTION = "Your Collection Name"