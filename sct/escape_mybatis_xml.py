import os
from lxml import etree
import xml.etree.ElementTree as ET

#parser = etree.XMLParser(recover=True)
for root, dirs, files in os.walk('.'):
    for file in files:
        print (root)
        if file.endswith(".xml"):
            full_path = os.path.join(root, file)
            data = ""
            with open(full_path, 'r') as myfile:
                data=myfile.read()
            print (full_path)
            print (len(data))
            root = ET.fromstring(data)
            #root.findall(".")
            #root = tree.getroot()
            #print(root.iter("statement"))
