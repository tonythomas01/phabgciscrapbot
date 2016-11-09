import sys  
from PyQt4.QtGui import *  
from PyQt4.QtCore import *  
from PyQt4.QtWebKit import *  
from lxml import html 
import requests

class Render(QWebPage):  
  def __init__(self, url):  
    self.app = QApplication(sys.argv)  
    QWebPage.__init__(self)  
    self.loadFinished.connect(self._loadFinished)  
    self.mainFrame().load(QUrl(url))  
    self.app.exec_()  
  
  def _loadFinished(self, result):  
    self.frame = self.mainFrame()  
    self.app.quit() 

url = 'https://phabricator.wikimedia.org/project/view/2304/'  
r = Render(url)  
result = r.frame.toHtml()
tree = html.fromstring(str(result.toAscii()))
pbab_links_in_proj = tree.xpath('//ul[@data-meta="0_103"]/li//div[@class="phui-object-item-name"]/span/a/@href')
for link in pbab_links_in_proj:
	phab_link = "http://phabricator.wikimedia.org" + link
	#now we have the link, we need to open this thing up and get the description and details, and post to the GCI website

  