# 拉取深圳新房数据信息

from bs4 import BeautifulSoup
import requests
import xlsxwriter
import logging
from requests.exceptions import RequestException


LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
 # LOG_FORMAT = "%(asctime)s - %(levelname)s - %(filename)s, line:%(lineno)d - %(message)s" 带有文件名、行号
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


# 输出到控制台
stream_handler = logging.StreamHandler()
formatter = logging.Formatter(fmt=LOG_FORMAT, datefmt=DATE_FORMAT)
stream_handler.setFormatter(formatter)

logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.addHandler(stream_handler)


# 具体房号的详细信息
def get_house_detail_page(houseId, index, worksheet):
    # houseId = '1852328'
    url = "http://zjj.sz.gov.cn/ris/bol/szfdc/housedetail.aspx?id=" + houseId
    headers = {}

    try:
        response = requests.get(url, headers=headers)
    except RequestException as e:
        logger.error("error: " + response.status_code + "," + e)
        print("error: " + response.status_code)

    soup_detail = BeautifulSoup(response.text, 'html.parser')
    tds = soup_detail.find_all('td')

    # 第一行表头
    index = index + 1
    # 名称
    worksheet.write(index, 0, format_table_cell(tds[1].text))
    # 单元
    worksheet.write(index, 1, format_table_cell(tds[3].text))
    # 楼层
    worksheet.write(index, 2, format_table_cell(tds[9].text))
    # 房号
    worksheet.write(index, 3, format_table_cell(tds[11].text))
    # 价格
    worksheet.write(index, 4, format_table_cell(tds[7].text))
    # 类型
    worksheet.write(index, 5, format_table_cell(tds[13].text))
    # 总面积
    worksheet.write(index, 6, format_table_cell(tds[15].text))
    # 可用面积
    worksheet.write(index, 7, format_table_cell(tds[17].text))
    # 公摊面积
    worksheet.write(index, 8, format_table_cell(tds[19].text))
    try:
        total_price = float(format_table_cell(tds[15].text)) * float(format_table_cell(tds[7].text)) / 10000
    except Exception as e:
        logger.error(e)
        total_price = 0

    # totalPrice = 10000;
    # 得房率
    worksheet.write(index, 9, "%.2f%%" % (float(format_table_cell(tds[17].text)) * 100 / float(format_table_cell(tds[15].text))))
    # 总价
    worksheet.write(index, 10,  "%.2f万" % total_price)
    # 3成
    worksheet.write(index, 11,  "%.2f万" % (total_price * float(0.3)))
    # 5成
    worksheet.write(index, 12,  "%.2f万" % (total_price * float(0.5)))


# table单元格内容格式化
def format_table_cell(cell_content):
    return cell_content.replace('\r', '').replace('\n','').replace('\t','').replace(' ', '')\
        .replace('元/平方米(按建筑面积计)', '').replace('平方米', '')


# excel 文件名称
def set_excel_file_name(id, presellid):
    url = "http://zjj.sz.gov.cn/ris/bol/szfdc/building.aspx?id=" + id + "&presellid=" + presellid
    headers = {}
    try:
        response = requests.get(url, headers=headers)
    except RequestException as e:
        print("error: " + response.status_code)
    soup = BeautifulSoup(response.text, 'html.parser')
    building_name_pre = soup.select('.path')[0].select('a')[1].text
    # 获取第几座
    building_name_after = soup.select('.path')[0].text[soup.select('.path')[0].text.rindex('>') + 2:]
    building_name = "%s%s"%(building_name_pre, building_name_after)

    # building_name = '深铁懿府'
    return building_name


# 获取一整座的房屋ID
def get_one_building_info(id, presellid, type, workbook):
    host = "http://zjj.sz.gov.cn/ris/bol/szfdc/building.aspx?id="
    url = host + id + "&presellid=" + presellid + "&Branch=" + type + "&isBlock="
    headers = {}

    try:
        response = requests.get(url, headers=headers)
    except RequestException as e:
        logger.error(e)
        print("error: " + response.status_code)

    # soup = BeautifulSoup(open('a.html', 'rb'), 'html.parser')
    soup = BeautifulSoup(response.text, 'html.parser')

    # sheet 表单命名
    worksheet = workbook.add_worksheet(type)
    set_xls_title(worksheet)
    set_xls_column_width(worksheet)

    div_list = soup.select('div .presale2like')
    print(len(div_list))

    # getHouseDetailPage('1852328', 1)
    for index, item in enumerate(div_list):
        # todo： 这里有的是取后六位，有的是取7位，所以修改为取'?'后面第四位开始的内容
        # 'housedetail.aspx?id=1852329' 截取倒数第7位到结尾
        # houseId = item.get('href')[-7:]
        houseId = item.get('href')[item.get('href').index('?') + 4:]
        get_house_detail_page(houseId, index, worksheet)

        # print不换行
        # print(" export- %d " %(index), end = " ")
        print("export %d " % index)


def get_all_house(id, presellid, list1):
    workbook = xlsxwriter.Workbook('g:/personal/新房价格/' + set_excel_file_name(id, presellid) + '.xlsx')
    for index, list_ele in enumerate(list1):
        get_one_building_info(id, presellid, list1[index], workbook)

    workbook.close()


# 设置表头
def set_xls_title(worksheet):
    worksheet.write(0, 0, "名称")
    worksheet.write(0, 1, "单元")
    worksheet.write(0, 2, "楼层")
    worksheet.write(0, 3, "房号")
    worksheet.write(0, 4, "单价(元/平)")
    worksheet.write(0, 5, "类型")
    worksheet.write(0, 6, "总面积")
    worksheet.write(0, 7, "可用面积")
    worksheet.write(0, 8, "公摊面积")
    worksheet.write(0, 9, "得房率")
    worksheet.write(0, 10, "总价")
    worksheet.write(0, 11, "3成首期")
    worksheet.write(0, 12, "5成首期")


# 设置列宽
def set_xls_column_width(worksheet):
    worksheet.set_column('A:A', 30)
    worksheet.set_column('B:D', 12)
    worksheet.set_column('E:E', 10)
    worksheet.set_column('F:F', 12)
    worksheet.set_column('G:M', 12)


def main():

    # 前海天健悦桂府
    # get_all_house('39463', '52854', ['未命名'])
    # get_all_house('39483', '52854', ['未命名'])

    # 东关拾悦城
    # get_all_house('30443', '31892', ['A', 'B', 'C', 'D'])

    # 龙光前海天境花园
    # 前海天境花园 1栋
    # get_all_house('39383', '52853', ['一', '未命名', '二', '三'])
    # # 前海天境花园 2栋
    # get_all_house('39384', '52853', ['一', '未命名', '二'])
    # # 前海天境花园 3栋
    # get_all_house('39385', '52853', ['未命名'])
    # # 前海天境花园 5栋
    # get_all_house('39403', '52853', ['未命名'])

    # 深铁懿府
    # get_all_house('39503', '52813', ['A', 'B'])
    # get_all_house('39504', '52813', ['A', 'B'])
    # get_all_house('39505', '52813', ['A', 'B'])

    # 富士君悦府
    # get_all_house('39583', '53133', ['未命名'])
    # get_all_house('39584', '53133', ['未命名'])
    # get_all_house('39585', '53133', ['未命名'])
    # get_all_house('39586', '53133', ['未命名'])

    # 富士君荟苑
    # get_all_house('39587', '53134', ['1单元', '3单元', '4单元', '6单元', '7单元'])

    # 卓弘星辰花园
    # get_all_house('39423', '52633', ['A座', 'B座', 'C座'])

    # 前海中集
    # get_all_house('39063', '52793', ['A座', 'B座', 'C座'])

    # 利德悦府 2021-1-11
    # get_all_house('39443', '52673', ['A', 'B'])
    # get_all_house('39444', '52673', ['A', 'B'])

    # 博林君瑞
    # get_all_house('31683', '34353', ['C', 'D', 'E', 'F', 'G'])

    # 华盛新沙
    # get_all_house('29224', '29671', ['A', 'B', 'C'])


    # 万科光年四季
    # get_all_house('38963', '52533', ['2单元', '3单元', '4单元', '未命名'])
    # get_all_house('38964', '52533', ['未命名'])

    # 中泰印邸
    # get_all_house('39343', '52273', ['未命名'])

    # 海岸城 锦园
    # get_all_house('39283', '52593')
    # 玺园
    # get_all_house('39363', '52573')

    # 深铁懿府
    # get_all_house('39503', '51813')

    # 香山道公馆
    # get_all_house('39523','52913')

    # 尚誉红山里
    # get_all_house('39563', '53013', ['A'])

    # 星河荣御 三期
    # get_all_house('37903', '49133', ['C座C1', 'C座C2', 'B座B1', 'B座B2', 'D', 'A'])

    # 新霖荟邑花园
    # get_all_house('38883','53273', ['未命名'])
    # get_all_house('38884','53273', ['未命名'])
    # get_all_house('38885','53273', ['未命名'])
    # get_all_house('38886','53273', ['未命名'])
    # get_all_house('38887','53273', ['未命名'])
    # get_all_house('38888','53273', ['未命名'])
    # get_all_house('38889','53273', ['未命名'])

    # 南园晗山悦海城
    # get_all_house('37963','49038', ['A', 'B'])

    # 宏发万悦山
    # get_all_house('39703', '53574', ['未命名'])
    # get_all_house('39704', '53574', ['未命名'])
    #
    # get_all_house('39705', '53573', ['未命名'])
    # get_all_house('39706', '53573', ['未命名'])

    # 诺德阅山海
    # get_all_house('39783', '53753', ['未命名'])
    # get_all_house('39784', '53753', ['未命名'])
    # get_all_house('39785', '53753', ['未命名'])
    # get_all_house('39786', '53753', ['未命名'])
    # get_all_house('39787', '53753', ['未命名'])

    # 汇智时代广场 --宝安
    # get_all_house('39763', '53673', ['未命名'])
    # get_all_house('39764', '53673', ['未命名'])

    # 上成大厦
    # get_all_house('39723', '53733', ['未命名', 'B座'])

    # 缙山府
    # get_all_house('39623','53313', ['未命名'])
    # get_all_house('39603','53313', ['未命名'])
    # get_all_house('39604','53313', ['未命名'])
    # get_all_house('39605','53313', ['未命名'])

    # 华润置地笋岗中心
    # get_all_house('39643', '53293', ['未命名'])
    # get_all_house('39644', '53293', ['未命名'])
    # get_all_house('39645', '53293', ['1'])

    # 坪山恒大城一期
    # get_all_house('39803', '53773', ['A', 'B'])
    # get_all_house('39804', '53773', ['未命名'])

    # 壹城时代花园
    get_all_house('39823', '53913', ['A座1单元', 'A座2单元', 'B座1单元', 'B座2单元', 'C座1单元', 'C座2单元'])


if __name__ == '__main__':
    main()

# 这个是获取新盘列表的
# http://zjj.sz.gov.cn/ris/bol/szfdc

# 这个是获取具体新盘信息的
# http://zjj.sz.gov.cn/ris/bol/szfdc/certdetail.aspx?id=53134

# 这个是进入房源库列表的
# http://zjj.sz.gov.cn/ris/bol/szfdc/building.aspx?id=39587&presellid=53134

# 具体房源的信息
# http://zjj.sz.gov.cn/ris/bol/szfdc/housedetail.aspx?id=1852309

#  获取的a标签 class是： presale2like
