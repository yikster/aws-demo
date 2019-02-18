from selenium import webdriver
from html.parser import HTMLParser
import json
import time
import xlsxwriter
import copy
import random

JSON_URLS = "file:///test_requirements.json" ## { name: "aaa", url:"https://abc.com"}
DETAIL_URL_PATTERN = "https://www.example.com/path/%s/%s"

driver = webdriver.Chrome('/Applications/chromedriver')

driver.get(JSON_URLS)

time.sleep(15)
#driver.get()

## Parse JSON text
e = driver.find_elements_by_xpath("//pre")

obj = json.loads(e[0].text)

def get_detail(url):
  driver.get(url)
  r_list = []
  record = {}
  rows = driver.find_elements_by_xpath("//tr")
  for row in rows:
    tds = row.find_elements_by_xpath("td")
    if len(tds) == 2:
      record[tds[0].text] = tds[1].text
    else:
      record["Title"] = tds[0].text  
      for td in tds:
        res = td.find_elements_by_xpath("div[@class='topic-response collapse']")
        for i in res:
          new_record = copy.deepcopy(record)
          new_record["col8"] = i.get_attribute("innerHTML").replace("\n","").strip()
          r_list.append(new_record)

    
  return r_list

workbook = xlsxwriter.Workbook("results.xlsx")
worksheet = workbook.add_worksheet()

key_index = {}
row = 0
col_str = "col0 col1	col2	col3	col4	col5	col6	col7	col8"
columns = col_str.split("\t")
for col, key in enumerate(columns):
  worksheet.write(row, col, key)
  key_index[key] = col
row += 1

def add_records_on_sheet(worksheet, records):
  global row
  for line in records:
    for key in line.keys():
      worksheet.write(row, key_index[key], line[key]) 
    worksheet.write(row, 0, row) 
    row += 1
results = []

for e in obj["results"]:
  records = get_detail((DETAIL_URL_PATTERN % ( e["id1"], e["id2"])))
  add_records_on_sheet(worksheet, records)

  # random delay like human
  time.sleep(random.randint(1,3))
  #results.extend(records)

workbook.close()
#print(results)


