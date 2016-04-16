#!/usr/bin/python
import os
import urllib2
import xml.etree.ElementTree as ET
#
from CampusNetDrop import *
dirname, filename = os.path.split(os.path.abspath(__file__))

### Login
if not os.path.isfile(dirname+"/lmtdAccss.txt"):
  login()
else:
  print "Configure login? (y/N)"
  configure = raw_input()
  if configure=="yes" or configure=="y":
    login()

### Config
print "Configure courses? (Y/n)"
configure = raw_input()
if configure!="no" and configure!="n":
  # Create request and load XML into 'root'
  url = 'https://www.campusnet.dtu.dk/data/CurrentUser/Elements'
  req = createRequest(url)
  response = urllib2.urlopen(req)
  root = ET.fromstring(response.read())

  # Build list of groups and note subgroups for further processing
  groups = []
  process_subgroups = []
  for node in root:
    for child in node:
      group = {'id':child.get('Id'),'name':child.get('Name'),'type_name':node.get('Name')}
      groups.append(group)
      if int(child.get('SubgroupCount')) > 0:
        process_subgroups.append(group)

  # Fetch names for subgroups
  while process_subgroups != []:
    # Get elements for first item in list
    current = process_subgroups.pop()
    req = createRequest(url+'/'+current['id']+'/Elements')
    response = urllib2.urlopen(req)
    elements = ET.fromstring(response.read())
    # Add all elements to the group list, and queue any subgroups for processing
    for child in elements:
      group = {'id':child.get('Id'),'name':current['name']+' - '+child.get('Name'),'type_name':current['type_name']}
      groups.append(group)
      if int(child.get('SubgroupCount')) > 0:
        process_subgroups.append(group)

  # Open file to store configuration
  f = open(dirname+'/config.txt','w')

  ### Does the user want all courses, or just a few?
  print "Configure all? (Y/n)"
  configureAll = raw_input()
  if configureAll=="no" or configureAll=="n":
    # Run through 'root' node and save elementID, download path and versioning in config
    for group in groups:
      print "Add \"%s --- %s\" to Downloads? (y/N)" % (group['type_name'],group['name'])
      answer = raw_input()

      if answer=="yes" or answer=="y":
        print "Where to download the \"%s\" files? (Path)" % (group['name'])
        directory = raw_input()
        directory = directory.replace("\\","/")
        print cleanName("Saving \"%s\" files to \"%s\"" % (group['name'],directory))
        f.write(cleanName(group['name']+";"+group['id']+";"+directory+"\n"))
  else:
    # Fetch _all_ courses to default directory
    print "Where to download the files? (Path with trailing slash)"
    directory = raw_input()
    directory = directory.replace("\\","/")
    for group in groups:
      print cleanName("Saving \"%s\" files to \"%s\"" % (group['name'],directory+group['name']))
      f.write(cleanName(group['name']+";"+group['id']+";"+directory+group['name']+"\n"))
  f.close()
