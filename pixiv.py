import requests, os, re
#import pixiv_crawler as pc
from lxml import html
from lxml import etree
import simplejson as json
from math import ceil
name="your_account"
passwd="passwd"
fileroot="/home/root"
login_url='https://accounts.pixiv.net/login'
pixiv_root="https://www.pixiv.net/"
url_artist_template=pixiv_root+"member_illust.php?id=%s&type=all&p=%d"
url_homepage=pixiv_root+"member.php?id=%d"
url_follower_template="https://www.pixiv.net/ajax/user/%d/following?offset=%d&limit=100&rest=show"
s=requests.session()
medium_page_temp="https://www.pixiv.net/member_illust.php?mode=medium&illust_id="
header={"authority": "www.pixiv.net",
"method": "GET",
"path": "/ajax/user/6662895/profile/all",
"scheme": "https",
"accept": "application/json",
"accept-encoding": "gzip, deflate, br",
"accept-language": "en-US,en;q=0.9,zh-CN;q=0.8,zh;q=0.7,zh-TW;q=0.6,ja;q=0.5",
"dnt": "1",
"referer": "https://www.pixiv.net/member_illust.php?id=6662895&type=all&p=1",
"user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36"}
header_image={"DNT": "1",
"Referer": "https://www.pixiv.net/member_illust.php?mode=medium&illust_id=57251557",
"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36"}

def login(name,passwd):
    r=s.get(login_url)
    tree=html.fromstring(r.text)
    authenticity_token=list(set(tree.xpath("//input[@name='post_key']/@value")))[0]
    payload={
		'pixiv_id':name,
		'password':passwd,
		'post_key':authenticity_token
	}
    r=s.post(login_url,
		data=payload,
		headers=dict(referer=login_url))
    r=s.get(pixiv_root)
    if re.search('not-logged-in',r.text)!=None:
        raise IOError('login failed')
    #else:
        #print("log in")

def get_address(artist_id,ifreturn):
    following_list=[]
    artist_following_num_url=url_homepage % artist_id
    fl_number=following_number(artist_following_num_url)
    artist_url="https://www.pixiv.net/ajax/user/%d/profile/all" % int(artist_id)
    r=s.get(artist_url,headers=header)
    r.raise_for_status()
    dict=json.loads(r.text)
    pixel_id=list(dict['body']['illusts'].keys())
    pixel_address_medium=[medium_page_temp+i for i in pixel_id]
    total_num=len(pixel_address_medium)
    print("the number of %d's pictures is %d in total" %(artist_id,total_num))
    print("Downloading =====================>")
    for i in range(total_num):
        url=pixel_address_medium[i]
        id=pixel_id[i]
        r=s.get(url)
        r.raise_for_status()
        r.encoding=r.apparent_encoding
        image_address=re.findall(r'regular+.{1,}p0_master1200.jpg',r.text)[0][10:].replace("\\","")
        save(image_address,artist_id,id)
        if ((i+1)%50==0):
            print("Processed %d of %d" %(i+1,total_num))
    for j in range(ceil(fl_number/100)):
        offset=100*j
        following_list+=get_following_list(artist_id,offset)
    following_list=[int(i[10:-1]) for i in following_list]
    if ifreturn:
        return following_list


def following_number(artist_following_num_url):
    r=s.get(artist_following_num_url)
    try:
        r.raise_for_status()
        following_number=int(re.findall(r'"following":\d{1,}',r.text)[0][12:])
        return following_number
    except:
        pass

def save(image_address,artist_id,id):
    id=int(id)
    r=s.get(image_address,headers=header_image)
    r.raise_for_status()
    with open (fileroot+"/%d_%d.jpg" %(artist_id,id), 'wb') as f:
        f.write(r.content)

def get_following_list(artist_id,offset):
    url_follower_url=url_follower_template %(artist_id,offset)
    r=s.get(url_follower_url)
    try:
        r.raise_for_status()
        follower_id=list(set(re.findall(r'"userId":"\d{1,10}"',r.text)))
        return follower_id
    except:
        pass

def main():
    login(name,passwd)
    following_list=get_address(6662895,True)
    for i in following_list:
        get_address(i,False)
