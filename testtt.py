from bs4 import BeautifulSoup
import requests
import csv
import xlsxwriter
from requests.exceptions import RequestException


def get_one_page(page):
    url = "https://sz.lianjia.com/"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36',
        'Host': 'sz.lianjia.com',
        'Referer': 'https://www.lianjia.com/',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.9'
    }
    newUrl = url + 'ershoufang/' + 'pg' + str(page)
    try:
        response = requests.get(newUrl, headers=headers)
    except RequestException as e:
        print("error: " + response.status_code)

    soup = BeautifulSoup(response.text, 'html.parser')
    print("newUrl: " + newUrl)
    print('--------')

    #  需要抓取： 小区名称， 面积大小， 均价， 以及详细信息的链接
    workbook = xlsxwriter.Workbook('d:/table.xlsx')
    worksheet = workbook.add_worksheet("sz_house")
    for index, item in enumerate(soup.select('li .clear')):
        # for index, item in soup.items:
        detailed_info = item.select('div .houseInfo')[0].text
        # community_name = detailed_info.split('|')[1].strip()
        community_name = item.select('div .positionInfo a')[0].text
        # index = 2
        area = detailed_info.split('|')[2].strip()
        average_price = item.select('div .unitPrice span')[0].text
        detailed_url = item.select('a')[0].get('href')
        print("%s\t%s\t%s\t%s"%(community_name, area, average_price, detailed_url))
        print(index)

        worksheet.write(index, 0, community_name)  # 第index 行0列
        worksheet.write(index, 1, area)
        worksheet.write(index, 2, average_price)
        worksheet.write(index, 3, detailed_url)

    workbook.close()


def main():
    get_one_page(2)

if __name__ == '__main__':
    main()