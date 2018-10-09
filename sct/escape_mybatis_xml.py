import os
from lxml import etree
import xml.etree.ElementTree as ET

#parser = etree.XMLParser(recover=True)
for root, dirs, files in os.walk('.'):
    for file in files:
        print (root)
        if file.endswith(".xml"):
            full_path = os.path.join(root, file)
            print (full_path)
            root = ET.parse(full_path)
            #root.findall(".")
            #root = tree.getroot()
            #print(root.iter("statement"))
