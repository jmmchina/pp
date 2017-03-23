from urllib.request import urlopen
from bs4 import BeautifulSoup
import re
import pymysql

conn = pymysql.connect(host='.my3w.com', unix_socket='/tmp/mysql.sock',user='', passwd='', db='',charset='utf8')
cur = conn.cursor()

def store(title, content,title_url,content_url,count):
    cur.execute("INSERT INTO pages (title, content,title_url,content_url,count) VALUES (%s,%s,%s,%s,%s)",(title, content,title_url,content_url,count))
    cur.connection.commit()

def getTexts(collectPage):
    urls = []
    html = urlopen("https://www.zhihu.com/collection/38887091?page="+str(collectPage))
    bsObj = BeautifulSoup(html,"html.parser")
    titles = bsObj.findAll("a",href=re.compile("^(/question/)((?!answer).)*$"))
    for title in titles:
        url = title.attrs['href']
        if url is not None:
            if url not in urls:
                urls.append(url)
                url2 = 'https://www.zhihu.com'+url
                print(url2)
                text = title.get_text()
                
                answer = bsObj.find("div",{"data-entry-url":re.compile("^("+url+"/answer)")})
                answerUrl = 'https://www.zhihu.com'+answer.attrs['data-entry-url']
                print(answerUrl)
                print(text+"\n")
                print(answer.div.get_text(strip=True).replace("显示全部","\n"))
                content = answer.div.get_text(strip=True).replace("显示全部","")
                count = bsObj.find("div",{"data-atoken":answerUrl[47:]}).find("span",{"class","count"})
                count = count.get_text().replace('K','000')
                print("赞同数为："+count+"\n")
                
                #store(text,content,url,answerUrl,count)
                #cur.execute("INSERT INTO pages (title, content,title_url,content_url,count) VALUES (%s,%s,%s,%s,%d)",(text,content,url,answerUrl,count))
                cur.execute("INSERT INTO pages (title, content,title_url,content_url,count) VALUES (%s,%s,%s,%s,%s)",(text,content,url2,answerUrl,count))
                cur.connection.commit()
    print('页面'+str(collectPage)+'保存完毕\n*********************************\n')
    return urls

def showCounts(count):
    cur.execute("delete from pages where id not in (select id from (select id,max(`count`) FROM pages group by `title_url` ,`content_url`,`count` ) aa );")
    cur.execute("select * from pages order by count desc limit 0,%s",count)
    showDates = cur.fetchall()
    n = 1
    for showDate in showDates:
        print('No:'+str(n)+'；')
        n += 1
        print('id号：'+str(showDate[0]))
        print('标题是: \n'+showDate[1])
        print('回答简要： \n'+showDate[2])
        print('网址是：\n'+showDate[4]+'\n'+showDate[5])
        print('赞同数：'+str(showDate[6])+'\n ==============================')
          

i = 183
while i <340 :
    getTexts(i)
    i += 1

showCounts(10)
cur.close()
conn.close()
print("数据保存完毕")
'''
for url in urls:
    print(url)
***

'''
