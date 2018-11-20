from crawler import *

url = 'http://bbs.tianya.cn/post-free-5946616-1.shtml'

soup, rsp = getSoup(url)

bbsGlobal = parseBBSGlobal(soup.findAll('script'))

reward, rrsp = fetchRewardInfo(bbsGlobal)
