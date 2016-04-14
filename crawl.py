import datetime
import urllib2
from HTMLParser import HTMLParser
import re

__author__ = 'warenix'


keyword_list = [
        u'\u4e2d'.encode('utf-8', 'ignore'), # chinese
        'chinese'.encode('utf-8', 'ignore'),
        u'\u5404\u79d1'.encode('utf-8', 'ignore'), # every subject
        u'\u6587\u6191'.encode('utf-8', 'ignore'), # certified teacher
        u'\u5e38\u984d'.encode('utf-8', 'ignore'), # regular
        'primary'.encode('utf-8', 'ignore'),
    ]

class Link(object):
    base_url = 'http://jump.mingpao.com/cfm/'
    label = None
    url = None

    def __init__(self, label, url):
        if label is not None:
            for keyword in keyword_list:
                pattern = re.compile(re.escape(keyword), re.IGNORECASE)
                label = pattern.sub('<span class="highlight">%s</span>' % keyword, label)
                if keyword in label:
                    label = label.replace(keyword, '<span class="highlight">%s</span>' % keyword)
        else:
            label = 'N/A'
        self.label = label
        self.url = url

    def get_label(self):
        return self.label

    def get_url(self):
        return self.base_url + self.url

class JobAd(object):
    position = None
    company = None

    def __init__(self, position, company):
        self.position = position
        self.company = company

    def get_position(self):
        return self.position

    def get_company(self):
        return self.company

def getKey(me, other):

    # compare position
    me_position = me.get_position()
    other_position = other.get_position()

    result_position = compare_by_keyword(keyword_list, me_position, other_position)
    if result_position != 0:
        return result_position
    return me_position < other_position


def compare_by_keyword(keyword_list, me, other):
    me_label = me.get_label().lower()
    other_label = other.get_label().lower()

    for keyword in keyword_list:
        result = check_contain_keyword(keyword, me_label, other_label)
        if result != 0:
            return result

    return 0

def check_contain_keyword(keyword, me_label, other_label):
    if keyword in me_label and keyword in other_label:
        return 0
    elif keyword in me_label:
        return 1
    elif keyword in other_label:
        return -1
    return 0

class MyHTMLParser(HTMLParser):
    STATE_START = 0
    STATE_FIND_POSITION = 1
    STATE_ROW_FOUND = 2
    STATE_TABLE_EXIT = 3
    STATE_FIND_COMPANY = 4

    state = STATE_START

    job_ad_list = None
    position = None
    company = None

    def handle_starttag(self, tag, attrs):
        # print "Encountered a start tag:", tag
        if self.STATE_START == self.state:
            if self.checkInTag('tr', 'class', 'odd', tag, attrs) or self.checkInTag('tr', 'class', 'even', tag, attrs):
                self.state = self.STATE_FIND_POSITION

        elif self.STATE_FIND_POSITION == self.state:
            # if self.checkInTag('a', 'target', '_top', tag, attrs):
            if tag == 'a' and self.hasAttr('target', attrs):
                label = self.getFromAttrs('title', attrs)
                url = self.getFromAttrs('href', attrs)
                self.position = Link(label, url)

                self.state = self.STATE_FIND_COMPANY
                #
                # link = Link(label, url)
                # print link.get_label_url()

        elif self.STATE_FIND_COMPANY == self.state:
            if self.checkInTag('a', 'target', '_top', tag, attrs):
                label = self.getFromAttrs('title', attrs)
                url = self.getFromAttrs('href', attrs)
                self.company = Link(label, url)

                self.job_ad_list.append(JobAd(self.position, self.company))
                self.state = self.STATE_FIND_POSITION

    def handle_endtag(self, tag):
        if self.state == self.STATE_FIND_POSITION:
            if 'div' == tag:
                self.state = self.STATE_START
        pass

    def handle_data(self, data):
        # print "Encountered some data  :", data
        if self.STATE_ROW_FOUND == self.state:
            data = data.strip()
            if not data == '':
                # print data
                pass
            self.state = self.STATE_FIND_POSITION
        pass

    def checkInTag(self, target_tag, target_attr_name, target_attr_value, tag, attrs):
        if target_tag == tag:
            for attr in attrs:
                if target_attr_name == attr[0] and target_attr_value == attr[1]:
                    return True
        return False

    def hasAttr(self, target_attr_name, attrs):
        for attr in attrs:
            if target_attr_name == attr[0]:
                return True
        return False

    def getFromAttrs(self, target_attr_name, attrs):
        for attr in attrs:
            if target_attr_name == attr[0]:
                return attr[1]
        return None

    def get_job_ad_list(self):
        return self.job_ad_list


def fetch_mingpao(page_no):
    url = 'http://jump.mingpao.com/cfm/JobSearch2.cfm?JobAreaID=10&DaysBefore=1&Sort=1D&PageID=%d' % page_no

    response = urllib2.urlopen(url)
    html = response.read()
    #html.decode("UTF-8", 'ignore')

    parser = MyHTMLParser()
    parser.job_ad_list = []
    parser.feed(html
                .decode("big5", 'ignore')
                .encode('utf-8', 'ignore'))

    # print html.decode("big5", 'ignore').encode('utf-8', 'ignore')

    return parser.get_job_ad_list()


if __name__ == '__main__':
    job_ad_list = []

    page_no = 1
    while True:
        #print 'fetching page_no ', page_no

        result = fetch_mingpao(page_no)
        #print len(result)
        if len(result) == 0:
            break
        job_ad_list.extend(result)
        page_no += 1

    job_ad_list.sort(cmp=getKey, reverse=True)
    # exit()

    print '''
    <html>
    <head>
    <meta charset="UTF-8" />
    <link rel="stylesheet" href="a.css" type="text/css">
    </head>
    <body>
    '''

    format = '''
    <section class="card">
    <h1>{company}</p>
    <h2><a href=\"{position_url}\">{position_label}</a></h2>
    </section>
    '''
    # print gen dat
    now = datetime.datetime.now()
    print format.format(company=u'\u6700\u5f8c\u66f4\u65b0'.encode('utf-8', 'ignore'),
                            position_url='',
                            position_label=now.strftime("%Y-%m-%d %H:%M").encode('utf-8', 'ignore'))

    # print keyword card
    print format.format(company=u'\u95dc\u9375\u5b57\u6b21\u5e8f'.encode('utf-8', 'ignore'),
                            position_url='',
                            position_label=' > '.join(keyword_list))

    for job_ad in job_ad_list:
        print format.format(company=job_ad.get_company().get_label(),
                            position_url=job_ad.get_position().get_url(),
                            position_label=job_ad.get_position().get_label())

    print '''
    </body>
    </html>
        '''