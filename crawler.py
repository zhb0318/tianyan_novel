import json

from bs4 import BeautifulSoup

import time

import git

from threading import Thread

from config import sync_interval

from util import logger, my_request



url_base = "https://novel.zhwenpg.com/"





class Book:

    # book_info example:{"name":"逍遥小散仙","author":"迷男","cover":"image/cover/kun6m7.jpg","book_url":"b.php?id=kun6m7","TOC":[["楔子","r.php?id=35482"]]]}

    def __init__(self, book_info):

        self.book_info = book_info

        self.name = book_info["name"]

        self.author = book_info["author"]

        self.boo_url = url_base + book_info["book_url"]

        self.local_toc = self.get_local_toc()



    # 获取本地已经下载文件的最新一个章节，每个章节命令是[章节名，url]防止同名章节出现

    # 用json保存下载完成的bookinfo

    def get_local_toc(self):

        logger.info("Loading Local TOC of Book" + self.name + self.author)

        try:

            with open('./novel/' + self.name + '+' + self.author + '.json', 'r', encoding='utf-8') as f_toc:

            	data = json.load(f_toc)

        except Exception:

            data = None

        if data:

            return data

        else:

            data = self.book_info

            data["TOC"] = []

            return data



    def save_local_toc(self, ):

        f_toc = open('./novel/' + self.name + '+' + self.author + '.json', 'w', encoding='utf-8')

        json.dump(self.local_toc, f_toc, ensure_ascii=False)

        f_toc.close()



    # 修改文件名字为name+author

    def change_name(self):

        pass



    # 和云端目录进行比较，返回需要继续下载的目录，目前只从最后一节开始，不比较遗漏部分

    def compare_with_remote(self):

        logger.info("Gen Diff TOC of Book:" + self.name + self.author)

        index = 0

        if self.local_toc["TOC"]:

            latest_chapter = self.local_toc["TOC"][-1]

            if self.local_toc["TOC"][-1] in self.book_info["TOC"]:

                index = self.book_info["TOC"].index(latest_chapter)

        result = self.book_info["TOC"][index + 1:]

        if not result:

            logger.info("No Update in Book:" + self.name + self.author)

        return result  # 返回目录列表



    def download(self):

        f_book = open('./novel/' + self.name + '+' + self.author + '.txt', 'a', encoding='utf-8')

        diff_toc = self.compare_with_remote()

        for chapter in diff_toc:

            logger.info("Downloading :" + self.name + ":" + chapter[0])

            biaoti = '[color=#FF0000][b]' + chapter[0] + '[/b][/color]\n'

            url = 'https://novel.zhwenpg.com/' + chapter[1]

            data = my_request(url)

            soup = BeautifulSoup(data, 'lxml')

            text = soup.select('#tdcontent > span > p')

            story = list()

            story.append(biaoti)

            for i in text:

                story.append(i.text.replace(u'\u3000', u''))

            story = '\n'.join(story)

            story = story + '\n'

            f_book.write(story)

            self.local_toc["TOC"].append(chapter)

            self.save_local_toc()

        f_book.close()

        logger.info("下载完成: " + self.name + '+' + self.author)





# 书单生成器 每次返回一列书：[[书名，url后缀],]

def booklists():

    url_base = "https://novel.zhwenpg.com/"

    data = my_request(url_base)

    soup = BeautifulSoup(data, 'lxml')

    max_page = int(soup.select(".pageidx > a ")[-1]["href"].split('=')[-1])

    page_base = "https://novel.zhwenpg.com/?page="

    for page_num in range(1, max_page + 1):

        logger.info("正在获取第" + str(page_num) + "列书")

        url = page_base + str(page_num)

        data = my_request(url)

        soup = BeautifulSoup(data, 'lxml')

        book_list = list()

        for link in soup.select("table > tr > td > div > a"):

            book_list.append([link.div.text, link['href']])  # 书名，url

        yield book_list





# 获取书籍信息,返回book_info

def get_bookinfo(book):  # [name,url]

    book_info = dict()

    name = book[0]

    url = book[1]

    author = "无名氏"

    cover = ""

    logger.info("Start Download Book:" + name)

    data = my_request(url_base + url)

    soup = BeautifulSoup(data, 'lxml')

    if soup.select(".fontwt"):

        author = soup.select(".fontwt")[0].text

    if soup.select(".ccover3"):

        cover = soup.select(".ccover3")[0]["data-src"]

    content = list()

    for link in soup.select("#dulist > li > a[href]"):

        tmp = [link.text, link['href']]

        content.append(tmp)

    for i in soup.select("#revbtn"):  # 反转目录

        if i.text == "正序":

            content.reverse()

    # book_info example:{"name":"逍遥小散仙","author":"迷男","cover":"image/cover/kun6m7.jpg","book_url":"b.php?id=kun6m7","TOC":[["楔子","r.php?id=35482"]]]}

    book_info["name"] = name

    book_info["author"] = author

    book_info["cover"] = cover

    book_info["book_url"] = url

    book_info["TOC"] = content

    return book_info





def download_book(book_info):

    book = Book(book_info)

    book.download()





def push_remote():

    try:

        from git import Repo

        import os

        path = os.getcwd()

        repo = Repo(path)

        remote = repo.remote()

        repo.git.add(all=True)

        repo.index.commit("Update Latest Novel")

        remote.push()

        logger.info("Push New Novel to Github Success")

    except Exception:

        logger.error("Error:Fail to Push to Github.")





if __name__ == "__main__":

    while True:

        for booklist in booklists():

            for book in booklist:

                book_info = get_bookinfo(book)

                download_book(book_info)

            push_remote()

        time.sleep(sync_interval)




