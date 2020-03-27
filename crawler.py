import requests
import logging
import asyncio
from bs4 import  BeautifulSoup
import  time
from threading import Thread

‘’‘
TODO:

’‘’


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
# create file handler which logs even debug messages
fh = logging.FileHandler('tianyan.log')
fh.setLevel(logging.DEBUG)
# create console handler with a higher log level
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
# create formatter and add it to the handlers
formatter = logging.Formatter('%(asctime)s  - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
ch.setFormatter(formatter)
# add the handlers to the logger
logger.addHandler(fh)
logger.addHandler(ch)

logger.info('You can find this written in myLogs.log')

def my_request(url, retry_time = 10):

    r = requests.get(url)


    if retry_time < 10:

        logger.info("Retry Requests " + str(10- retry_time))

    if retry_time < 0:

        logger.info("Download False,Stop retry")

        return 0

    retry_time = retry_time-1
    if r.status_code == 200:

        return r.text

    else:

        logger.info("Request Error, will retry later")

        time.sleep(10)

        return  my_request(url,retry_time-1)


def get_book(page_num):

    url_base = "https://novel.zhwenpg.com/"

    page_base = "https://novel.zhwenpg.com/?page="

    book_list = list()

    logger.info("正在获取第" + str(page_num) + "列书")

    url = page_base + str(page_num)

    data = my_request(url)

    soup = BeautifulSoup(data, 'lxml')

    for link in soup.select("table > tr > td > div > a"):

        url = url_base + link['href']

        book_list.append([link.div.text, url])      # 书名，url

    return book_list


already_have = ['一代大侠','九星毒奶','从火凤凰开始的特种兵','元尊','六朝燕歌行','剑来','剑耀九歌','北宋大丈夫','十景缎','反叛的大魔王','大国战隼','大数据修仙','大明天下','大明春色','天唐锦绣','姐夫的荣耀','学霸的黑科技系统','宿主','寒门状元','异能小神农','恐怖修仙世界','我师兄实在太稳健了','我有一座恐怖屋','我真没想重生啊','抢救大明朝','最强狂兵','民国谍影','江山云罗','特 拉福买家俱乐部','狂探','神话版三国','绝世战魂','舅妈的不伦亲情','芝加哥1990','萧齐艳史','诡秘之主','超神机械师','轮回乐 园','逍遥小散仙','锦绣江山传','鱼龙舞']

def get_content(book_info):     # [name,url]

    name = book_info[0]

    url = book_info[1]
    

    if name in already_have:

        return

    logger.info("Start Download Book" + name)

    data = my_request(url)

    soup = BeautifulSoup(data,'lxml')

    content = list()

    for link in soup.select("#dulist > li > a[href]"):

        tmp = [link.text,link['href']]

        content.append(tmp)



    content = [[x[0], 'https://novel.zhwenpg.com/' + x[1]] for x in content]


    for i in soup.select("#revbtn"):      # 反转目录

        if i.text == "正序":

            content.reverse()

    # logger.info(name + '的目录是')

    # logger.info(content)

    f = open('./txt/' + name + '.txt', 'a', encoding='utf-8')

    for page in content:

        logger.info("downloading :" + name +": " + page[0])

        biaoti = '[color=#FF0000][b]' + page[0] +'[/b][/color]\n'

        url = page[1]

        data = my_request(url)

        soup = BeautifulSoup(data,'lxml')

        text = soup.select('#tdcontent > span > p')

        story = list()

        story.append(biaoti)

        for i in text:

            story.append(i.text.replace(u'\u3000', u''))

        story = '\n'.join(story)

        story = story + '\n'

        f.write(story)

    f.close()
    logger.info("下载完成: " + name)



if __name__ == "__main__":

    max_page = 12

    threads = []

    for i in range(2,max_page+1):

        books = get_book(i)

        for book in books:

            try:
                if book[0] in already_have:
                    logger.info(book[0] + "已经下载过了,跳过此书")
                    continue

                logger.info("Add Book" + book[0])

                t = Thread(target=get_content, args=(book,))

                threads.append(t)

            except:

                logger.error("无法创建线程")


    n = 8

    threads = [threads[i:i + n] for i in range(0, len(threads), n)]  # 切片成n个一组

    for thread in threads:

        [t.start() for t in thread]

        [t.join()  for t in thread]





