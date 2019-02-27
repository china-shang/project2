# 基于Python3异步技术开发的垂直搜索引擎
爬取Github与码云上的代码库数据，使用ElasticSearch数据库建立倒排索引。

抓取过程运行截图:
![ScreenShot](Picture1.png)
部分数据截图：
![ScreenShot](Picture2.png)

运行一段时间后抓取码云代码库数据336 164条，Github数据2 640 436条。

之后使用ElasticSearch建立倒排索引，Jinja2编写界面。

界面截图：![ScreenShot](Picture3.png))
