#!/usr/bin/python
# Please makes sure you change the API Token

import sys  
from PyQt4.QtGui import *  
from PyQt4.QtCore import *  
from PyQt4.QtWebKit import *  
from lxml import html 
import requests
import csv

import requests
s = requests.Session()

api_token = "api-your-here"
conduit = "https://phabricator.wikimedia.org/api/maniphest.query" 

# since most of phab is rendered after page load, we need this cute thing
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
completeIds = []

# We need to remove that extra stuff from start of IDs 
for link in pbab_links_in_proj:
	completeIds.append(link[2:])
	

# We are doing a mass query to the phabricator API, making sure we do not ping again and again 
args = { 'ids[]': completeIds, "api.token": api_token }
req = requests.Request('POST', conduit, data=args)
prepped = s.prepare_request(req)
resp = s.send(prepped)
resp.raise_for_status()
completeResponse =  resp.json()['result'].values()

# We are writing things to the CSV file now 
with open('importedgci.csv', 'w') as csvfile:
	fieldnames = ['name', 'description', 'external_url' ]
	spamwriter = csv.DictWriter(csvfile, fieldnames=fieldnames)
	for task in completeResponse:
		row = {}
		row['name'] = task['title'].encode('ascii', 'ignore').decode('ascii')
		row['description'] = task['description'].encode('ascii', 'ignore').decode('ascii')
		row['external_url'] = task['uri'].encode('ascii', 'ignore').decode('ascii')
		spamwriter.writerow(row)