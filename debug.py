from crawler import *

url = 'http://bbs.tianya.cn/post-funinfo-7681616-1.shtml'

soup, rsp = getSoup(url)

bbsGlobal = parseBBSGlobal(soup.findAll('script'))

reward, rrsp = fetchRewardInfo(bbsGlobal)
