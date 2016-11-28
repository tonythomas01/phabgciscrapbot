'''
Licensed to the Apache Software Foundation (ASF) under one
or more contributor license agreements.  See the NOTICE file
distributed with this work for additional information
regarding copyright ownership.  The ASF licenses this file
to you under the Apache License, Version 2.0 (the
"License"); you may not use this file except in compliance
with the License.  You may obtain a copy of the License at

  http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing,
software distributed under the License is distributed on an
"AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
KIND, either express or implied.  See the License for the
specific language governing permissions and limitations
under the License.
'''

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

# You will have to paste in your conduit API key here
api_token = "api-your_api_key_here"
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

# This is kinda bad way to scrap, but we got no otherway! 
# Inspect the project column you need, and update the following regex accordingly

pbab_links_in_proj = tree.xpath('//ul[@data-meta="0_114"]/li//div[@class="phui-object-item-name"]/span/a/@href')
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
