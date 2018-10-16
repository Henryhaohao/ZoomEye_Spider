# !/user/bin/env python
# -*- coding:utf-8 -*-
# time: 2018/10/7--17:42
__author__ = 'Henry'

'''
项目:ZoomEye钟旭之眼的登录+爬取
注意:一页20条,最多显示100页,即2000条数据(对外开放的开发者版本，只能获取总结果的 30%，同时涵盖 10,000 结果条数上限。)
'''

import requests, execjs, re
import matplotlib.image as mpimg
import matplotlib.pyplot as plt
from Spiders.lianzhong_captcha import main


def Zoomeye():
    req = requests.Session()
    # 1.获取cookie,token
    url = 'https://sso.telnet404.com/cas/login/'
    headers = {
        'Origin': 'https://sso.telnet404.com',
        'Host': 'sso.telnet404.com',
        'Upgrade-Insecure-Requests': '1',
        'Referer': 'https://sso.telnet404.com/cas/login/',  # 不加referer:403错误(HTTPS防第三方劫持)
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36'
    }
    html = req.get(url, headers=headers)
    token = re.search(r"token' value='(.*?)'", html.text).group(1)
    print(token)
    # 2.获取验证码
    url = 'https://sso.telnet404.com/captcha/'
    html = req.get(url, headers=headers)
    with open('captcha.jpg', 'wb') as f:
        f.write(html.content)
    img = mpimg.imread('captcha.jpg')
    plt.imshow(img)
    plt.axis('off')
    plt.show()
    captcha = input('请输入验证码:')
    # 3.post提交账号密码,打码登录
    url = 'https://sso.telnet404.com/cas/login/'
    data = {
        'csrfmiddlewaretoken': token,
        'email': username,
        'password': password,
        'captcha': captcha
    }
    html = req.post(url, data=data, headers=headers)
    if 'login' in html.url:
        print('登录失败!请填写正确的账号密码验证码!')
    else:
        print('登录成功!')
    # 第一次重定向
    url = 'https://www.zoomeye.org/searchResult?q=666'
    headers = {
        'Host': 'www.zoomeye.org',
        'Upgrade-Insecure-Requests': '1',
        # 'Referer': 'https://www.zoomeye.org/login',
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36'
    }
    html = req.get(url, headers=headers)
    code = html.text.replace('\x00', '').replace('<script>', '').replace('</script>', '').replace('try{eval','try{return')
    func = execjs.compile(code).call('f')
    reg = re.search(r"document.cookie='(.*?)\+';Expires", func)
    reg_1 = re.search(r',\(function\(\){var (.*?)=document', func)
    if reg:
        if reg_1:
            code_2 = re.search(r"'__jsl_clearance=(.*?)\+';Expires", func).group(1)
            code_2 = ('\'' + code_2).replace('window', '{}')
            arg = re.search(r',\(function\(\){var (.*?)=document', code_2).group(1)
            code_2 = re.sub(r',\(function\(\){.*?return function', ',(function(){return function', code_2)
            reg = arg + '\.charAt'
            code_2 = re.sub(reg, '"www.zoomeye.org/".charAt', code_2)
        else:
            code_2 = re.search(r"'__jsl_clearance=(.*?)\+';Expires", func).group(1)
            code_2 = ('\'' + code_2).replace('window', '{}')
        jsl_clearance = execjs.eval(code_2)
        headers = {
            'Host': 'www.zoomeye.org',
            'Upgrade-Insecure-Requests': '1',
            'Referer': url,
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36'
        }
        html = req.get(url, headers=headers, allow_redirects=False)
        req.cookies['__jsl_clearance'] = jsl_clearance
        # 第二次重定向
        url = 'https://sso.telnet404.com/cas/login?service=https%3A%2F%2Fwww.zoomeye.org%2Flogin'
        headers = {
            'Host': 'sso.telnet404.com',
            'Upgrade-Insecure-Requests': '1',
            'Referer': 'https://www.zoomeye.org/login',
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36'
        }
        html = req.get(url, headers=headers)
        # 第三次重定向(获取返回的token,即Cube-Authorization)
        url = 'https://www.zoomeye.org/user/login?' + html.url.split('?')[1]
        headers = {
            'Host': 'www.zoomeye.org',
            'Upgrade-Insecure-Requests': '1',
            'Referer': html.url,
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36'
        }
        html = req.get(url, headers=headers)
        cube_auth = html.json()['token']
        print(req.cookies)
        print(cube_auth)
        # 最终访问接口,运行爬虫
        for page in range(1, 6):
            url = 'https://www.zoomeye.org/api/search?q=666&p={}'.format(str(page))  # q:搜索内容;P:页数
            headers = {
                'Host': 'www.zoomeye.org',
                'Upgrade-Insecure-Requests': '1',
                'Referer': 'https://www.zoomeye.org/searchResult?q=666',  # 根据搜索内容修改
                'Cube-Authorization': cube_auth,  # 加入用户验证
                'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36'
            }
            html = req.get(url, headers=headers)
            for i in html.json().get('matches'):
                data = {
                    'title':i.get('title'),
                    'site':i.get('site'),
                    'ip':i.get('ip')[0],
                    'type':i.get('type'),
                    'timestamp':i.get('timestamp'),
                    'country':i.get('geoinfo').get('country').get('names').get('zh-CN'),
                }
                print(data)
    else:
        print('Method 2-动态混淆,暂未解密...sorry~~')  # 请求快了,就会激发动态混淆,只需一个小时重新请求一次就好了
        exit()


if __name__ == '__main__':
    username = input('请输入您的ZoomEye用户名(邮箱):')
    password = input('请输入您的ZoomEye密码:')
    Zoomeye()
