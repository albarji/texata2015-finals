# -*- coding: utf-8 -*-
"""
Module for loading data into memory

@author: Álvaro Barbero JIménez
"""

import xml.etree.ElementTree
import glob
import re
from datetime import datetime
import locale
from elasticsearch import Elasticsearch
from bs4 import BeautifulSoup

from text import Text

# Connect to ElasticSearch
es = Elasticsearch([{'host': 'localhost', 'port': 9200}])

# DEPRECATED
#class CDETSCorpus():
#    """Class representing a corpus of text data from CDETS"""
#    
#    def __init__(self, defects):
#        # Map of defects and correponding text files
#        self._defects = defects
#        
#    def alltexts(self):
#        """Generator of all texts in the corpus"""
#        for key in self._defects:
#            defect = self._defects[key]
#            yield defect["description"]
#            for note in defect["notes"]:
#                yield note
#                
#    def textsbygroups(self):
#        """Generator of texts groups by defects"""
#        for key in self._defects:
#            defect = self._defects[key]
#            texts = [defect["description"]]
#            for note in defect["notes"]:
#                texts.append(note)
#            yield texts
#        
#    def __str__(self):
#        return str(self._defects)

# DEPRECATED
#def CDETSload(folder):
#    """Loads all CDETS bug data files located in a folder
#    
#    Inputs:
#        folder: directory where the data is located
#        
#    Outpus:
#        CDETSCorpus with all the read data
#    """     
#    
#    defects = {}    
#    
#    # Iterate over XML files in the folder
#    for f in glob.glob(folder + "/*.xml"):
#        root = xml.etree.ElementTree.parse(f).getroot()
#        # Iterate over Defects declared in the file
#        for defect in root.iter('{cdetsng}Defect'):
#            # Note defect id
#            id = defect.attrib['id']
#            defectdata = {}
#            defectdata['notes'] = []
#            # Iterate over fields in the defect report
#            for field in defect.iter('{cdetsng}Field'):
#                # Take in only the useful fields
#                if field.attrib['name'] == "Description":
#                    defectdata["description"] = field.text
#                if field.attrib['name'] == "Note":
#                    defectdata['notes'].append(field.text) 
#            # Pack fields
#            defects[id] = defectdata
#                
#    # Return dictionary of read data
#    return CDETSCorpus(defects)
    
def CDETSloadES(folder):
    """Loads all CDETS bug data files located in a folder into ElasticSearch
    
    Inputs:
        folder: directory where the data is located
    """     
    
    defects = {}    
    
    # Iterate over XML files in the folder
    for f in glob.glob(folder + "/*.xml"):
        try:
            root = xml.etree.ElementTree.parse(f).getroot()
            # Iterate over Defects declared in the file
            for defect in root.iter('{cdetsng}Defect'):
                # Note defect id
                id = defect.attrib['id']
                defectdata = {}
                defectdata['comments'] = []
                # Iterate over fields in the defect report
                for field in defect.iter('{cdetsng}Field'):
                    # Take in only the useful fields
                    if field.attrib['name'] == "Description":
                        defectdata["text"] = field.text
                    if field.attrib['name'] == "Note":
                        defectdata['comments'].append({"text" : field.text}) 
                # Pack fields
                defects[id] = defectdata
                # Save in Elasticsearch
                es.index(index='cdets', doc_type='post', id=id, body=defectdata)
        except:
            pass
    
# DEPRECATED
#class ForumCorpus():
#    """Class representing a corpus of text data from CISCO support forum"""
#    
#    def __init__(self, posts):
#        # Map of posts and correponding info
#        self._posts = posts
#        
#    def alltexts(self):
#        """Generator of all texts in the corpus"""
#        for post in self._posts:
#            yield post['text']
#            for reply in post['replies']:
#                yield reply['text']
#                
#    def textsbygroups(self):
#        """Generator of texts groups by posts"""
#        for post in self._posts:
#            texts = [post['text']]
#            for reply in post['replies']:
#                texts.append(reply['text'])
#            yield texts
#        
#    def __str__(self):
#        return str(self._posts)
        
# DEPRECATED
#def forumsload(folder):
#    """Loads all forum data files located ina  folder
#    
#    Inputs:
#        folder: directory where the data is located
#        
#    Outpus:
#        CDETSCorpus with all the read data
#    """
#    
#    locale.setlocale(locale.LC_ALL, "en_US.utf8")
#    
#    posts = {}
#    
#    # Prepare section markers detectors
#    titledetector = re.compile("^Title:")
#    urldetector = re.compile("^URL:")
#    statsdetector = re.compile("^Statistics:")
#    descdetector = re.compile("^Description:")
#    replydetector = re.compile("^Reply:")
#    
#    # Prepare fields detectors
#    repliesdetector = re.compile("Replies: ([0-9]+)")
#    ratingdetector = re.compile("Avg. Rating: ([0-9\.]+)")
#    viewsdetector = re.compile("Views: ([0-9]+)")
#    votesdetector = re.compile("Votes: ([0-9]+)")
#    inlinevotesdetector = re.compile(" ([0-9]+) votes$")
#    sharesdetector = re.compile("Shares: ([0-9]+)")
#    userdetector = re.compile("(?:Description|Reply): ([^/]+)")
#    datedetector = re.compile("(?:Description|Reply): (?:[^/]+)/ (.*)")
#    daysuffixdetector = re.compile("(st|nd|rd|th)")
#    
#    # Prepare dates formatter
#    dateformat = "%b %d, %Y"
#    datetimeformat = "%a, %m/%d/%Y - %H:%M"
#    
#    # Iterate over text files in the folder
#    posts = []
#    for fname in glob.glob(folder + "/*.txt"):
#        post = {}
#        with open(fname, "r") as f:
#            # Initialize values
#            post['title'] = None
#            post['url'] = None
#            post['nreplies'] = None
#            post['rating'] = None
#            post['views'] = None
#            post['votes'] = None
#            post['shares'] = None
#            post['replies'] = []
#            post['author'] = None
#            post['date'] = None
#            post['text'] = None
#            line = f.readline()
#            while line:
#                # Detect and read different kinds of data blocks
#                if titledetector.match(line):
#                    # Title name in the next line
#                    post['title'] = f.readline().rstrip()
#                elif urldetector.match(line):
#                    # URL in the next line
#                    post['url'] = f.readline().rstrip()
#                elif statsdetector.match(line):
#                    # Several fields in the same line
#                    post['nreplies'] = repliesdetector.search(line).groups()[0]
#                    try:
#                        post['rating'] = ratingdetector.search(line).groups()[0]
#                    except:
#                        post['rating'] = None
#                    post['views'] = viewsdetector.search(line).groups()[0]
#                    post['votes'] = votesdetector.search(line).groups()[0]
#                    post['shares'] = sharesdetector.search(line).groups()[0]
#                elif descdetector.match(line):
#                    # Author and date in the same line
#                    post['author'] = userdetector.search(line).groups()[0].rstrip()
#                    datetxt = datedetector.search(line).groups()[0]
#                    # Remove st, th, nd, ... day suffixes
#                    datetxt = daysuffixdetector.sub("", datetxt)
#                    post['date'] = datetime.strptime(datetxt, dateformat)
#                    # Text in the next line
#                    text = f.readline()
#                    # Remove vote count at end
#                    # TODO: remove also the trailing "I have this problem too." text
#                    text = inlinevotesdetector.sub("", text).rstrip()
#                    post['text'] = Text(text)
#                elif replydetector.match(line):
#                    reply = {}
#                    # Author and date/time in the same line
#                    reply['author'] = userdetector.search(line).groups()[0].rstrip()
#                    datetxt = datedetector.search(line).groups()[0]
#                    reply['date'] = datetime.strptime(datetxt, datetimeformat)
#                    # Text of the reply in the following line
#                    text = f.readline().rstrip()
#                    reply['text'] = Text(text)
#                    post['replies'].append(reply)
#                # Ignore other lines
#                else:
#                    pass
#                # Read next line
#                line = f.readline()
#        # Store only posts with info on them
#        if post['text']:
#            posts.append(post)
#                    
#    return ForumCorpus(posts)
    
def forumsloadES(folder):
    """Loads into ES all forum data files located in a folder
    
    Inputs:
        folder: directory where the data is located
    """
    
    locale.setlocale(locale.LC_ALL, "en_US.utf8")
    
    # Prepare section markers detectors
    titledetector = re.compile("^Title:")
    urldetector = re.compile("^URL:")
    statsdetector = re.compile("^Statistics:")
    descdetector = re.compile("^Description:")
    replydetector = re.compile("^Reply:")
    
    # Prepare fields detectors
    repliesdetector = re.compile("Replies: ([0-9]+)")
    ratingdetector = re.compile("Avg. Rating: ([0-9\.]+)")
    viewsdetector = re.compile("Views: ([0-9]+)")
    votesdetector = re.compile("Votes: ([0-9]+)")
    inlinevotesdetector = re.compile(" ([0-9]+) votes$")
    sharesdetector = re.compile("Shares: ([0-9]+)")
    userdetector = re.compile("(?:Description|Reply): ([^/]+)")
    datedetector = re.compile("(?:Description|Reply): (?:[^/]+)/ (.*)")
    daysuffixdetector = re.compile("(st|nd|rd|th)")
    
    # Prepare dates formatter
    dateformat = "%b %d, %Y"
    datetimeformat = "%a, %m/%d/%Y - %H:%M"
    
    # Iterate over text files in the folder
    for fname in glob.glob(folder + "/*.txt"):
        post = {}
        with open(fname, "r") as f:
            # Initialize values
            post['comments'] = []
            line = f.readline()
            while line:
                # Detect and read different kinds of data blocks
                if titledetector.match(line):
                    # Title name in the next line
                    post['title'] = f.readline().rstrip()
                elif urldetector.match(line):
                    # URL in the next line
                    post['url'] = f.readline().rstrip()
                elif statsdetector.match(line):
                    # Several fields in the same line
                    post['nreplies'] = repliesdetector.search(line).groups()[0]
                    try:
                        post['rating'] = ratingdetector.search(line).groups()[0]
                    except:
                        pass
                    post['views'] = viewsdetector.search(line).groups()[0]
                    post['votes'] = votesdetector.search(line).groups()[0]
                    post['shares'] = sharesdetector.search(line).groups()[0]
                elif descdetector.match(line):
                    # Author and date in the same line
                    post['author'] = userdetector.search(line).groups()[0].rstrip()
                    datetxt = datedetector.search(line).groups()[0]
                    # Remove st, th, nd, ... day suffixes
                    datetxt = daysuffixdetector.sub("", datetxt)
                    post['date'] = datetime.strptime(datetxt, dateformat)
                    # Text in the next line
                    text = f.readline()
                    # Remove vote count at end
                    # TODO: remove also the trailing "I have this problem too." text
                    text = inlinevotesdetector.sub("", text).rstrip()
                    post['text'] = text
                elif replydetector.match(line):
                    reply = {}
                    # Author and date/time in the same line
                    reply['author'] = userdetector.search(line).groups()[0].rstrip()
                    datetxt = datedetector.search(line).groups()[0]
                    reply['date'] = datetime.strptime(datetxt, datetimeformat)
                    # Text of the reply in the following line
                    text = f.readline().rstrip()
                    reply['text'] = text
                    post['comments'].append(reply)
                # Ignore other lines
                else:
                    pass
                # Read next line
                line = f.readline()
        # Store only posts with info on them
        if 'text' in post:
            es.index(index="support-forums", doc_type="post", id=fname, body=post)
    
def techzoneESloader(folder):
    """Loads all techzone data files located in a folder
    
    The files read here are not the original files, but those already
    proprocessed where each XML tree has been split into a separate file.    
    
    Inputs:
        folder: directory where the data is located
    """     
    
    # Iterate over XML files in the folder
    for f in glob.glob(folder + "/*.xml.*"):
        root = xml.etree.ElementTree.parse(f).getroot()
        # Get techZoneContent fields
        for tzcontent in root.iter('{cdetsng}techZoneContent'):
            # Get id for tzcontent
            id = tzcontent.attrib["id"]
            # Get actual text for the content
            for content in tzcontent.iter('{cdetsng}content'):
                text = content.text
                # Add document to database
                es.index(index="techzone", doc_type="post", id=id, body={"text":text})
                
def stackoverflowESLoader(folder):
    """Loads into ES all Stackoverflow data files located in a folder and subfolders
    
    Inputs:
        folder: directory where the data is located. Must contain a subfolder
            for each stackexchange community, with a Posts.xml file with
            the community posts
    """
    
    tagdetector = re.compile("<[^>]+>")
    
    # Iterate over each subolder (community)
    for communityfolder in glob.glob(folder + '/*.com'):
        # Get community name
        communityname = communityfolder.split('/')[-1]
        # Process the post file for such community
        root = xml.etree.ElementTree.parse(communityfolder + "/Posts.xml").getroot()
        # Get all posts
        for row in root.iter('row'):
            id = row.attrib["Id"]
            body = {}
            # Get text withouth the HTML tags
            html = row.attrib["Body"]
            soup = BeautifulSoup(html, "lxml")
            body["text"] = soup.getText()
            # Get post tags
            if "Tags" in row.attrib:
                tagsraw = row.attrib["Tags"]
                body["tags"] = tagdetector.findall(tagsraw)
            # Add to Elasticsearch
            es.index(index=communityname, doc_type="post", id=id, body=body,
                     request_timeout=30)
