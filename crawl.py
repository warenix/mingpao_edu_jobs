import datetime
import urllib2
from HTMLParser import HTMLParser
import re

__author__ = 'warenix'


keyword_list = [

        u'\u5e38\u984d'.encode('utf-8', 'ignore'), # regular
        #u'\u4e2d'.encode('utf-8', 'ignore'), # chinese
        u'\u5c0f\u5b78'.encode('utf-8', 'ignore'), # primary school
        u'\u4e2d\u6587'.encode('utf-8', 'ignore'), # chinese subject
        'chinese'.encode('utf-8', 'ignore'),
        u'\u5404\u79d1'.encode('utf-8', 'ignore'), # every subject
        u'\u6587\u6191'.encode('utf-8', 'ignore'), # certified teacher
        'primary'.encode('utf-8', 'ignore'),
    ]

company_keyword_list = [
        u'\u5c0f\u5b78'.encode('utf-8', 'ignore'), # primary school
        'primary'.encode('utf-8', 'ignore'),
    ]


class Link(object):
    #base_url = 'http://jump.mingpao.com/cfm/'
    base_url = 'https://jump.mingpao.com/job/detail/Jobs/2/'
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
    date = None
    jobid = None
    content = None

    def __init__(self, jobid, position, company, date):
        self.jobid = jobid
        self.position = position
        self.company = company
        self.date = date

    def get_position(self):
        return self.position

    def get_company(self):
        return self.company

    def get_date(self):
        return self.date

    def get_url(self):
        return 'https://jump.mingpao.com/job/detail/Jobs/2/' + self.jobid

    def get_content(self):
        return self.content

def getKey(me, other):
    # compare company
    me_company = me.get_company()
    other_company= other.get_company()
    result_company = compare_by_keyword(company_keyword_list, me_company, other_company)
    if result_company != 0:
        return result_company

    # compare position
    me_position = me.get_position()
    other_position = other.get_position()

    result_position = compare_by_keyword(keyword_list, me_position, other_position)
    if result_position != 0:
        return result_position

    # compare content
    me_content = me.get_content()
    other_content = other.get_content()
    result_content = compare_by_keyword(keyword_list, me_content, other_content)
    if result_content != 0:
        return result_content

    return me_content < other_content



def compare_by_keyword(keyword_list, me, other):
    me_label = me.lower()
    other_label = other.lower()

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

class BaseHTMLParser(HTMLParser):

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

class MyHTMLParser(BaseHTMLParser):
    STATE_START = 0
    STATE_FIND_POSITION = 1
    STATE_ROW_FOUND = 2
    STATE_TABLE_EXIT = 3
    STATE_FIND_COMPANY = 4
    STATE_FIND_NEXT_JOB = 5
    STATE_FIND_NEXT_JOB_ENTERED = 6
    STATE_FOUND_POSITION = 7
    STATE_FIND_COMPANY = 8
    STATE_FOUND_COMPANY = 9
    STATE_FIND_DATE = 10
    STATE_FOUND_DATE = 11
    STATE_END = -1

    state = STATE_START

    job_ad_list = None
    position = None
    company = None
    date = None

    same_date = None

    def handle_starttag(self, tag, attrs):
        # print "Encountered a start tag:", tag
        if self.STATE_START == self.state:
            if self.checkInTag('ul', 'id', 'jobListing', tag, attrs):
                self.state = self.STATE_FIND_NEXT_JOB

        elif self.STATE_FIND_NEXT_JOB == self.state:
            # if self.checkInTag('a', 'target', '_top', tag, attrs):
            if tag == 'li' and self.hasAttr('adid', attrs):
                jobid = self.getFromAttrs('adid', attrs)
                # print jobid
                self.jobid = jobid
                self.state = self.STATE_FIND_NEXT_JOB_ENTERED

        elif self.STATE_FIND_NEXT_JOB_ENTERED == self.state:
            if self.checkInTag('div', 'class', 'thum50percent color_position', tag, attrs):
                self.state = self.STATE_FOUND_POSITION
                print 'found position'

        elif self.STATE_FIND_COMPANY == self.state:
            # if tag == 'div' and self.hasAttr('class', attrs):
            if self.checkInTag('div', 'class', 'thum37percent', tag, attrs):
                self.state = self.STATE_FOUND_COMPANY

        elif self.STATE_FIND_DATE == self.state:
            # if tag == 'div' and self.hasAttr('class', attrs):
            if self.checkInTag('div', 'class', 'thum13percent', tag, attrs):
                self.state = self.STATE_FOUND_DATE


    def handle_endtag(self, tag):
        if self.state == self.STATE_FIND_NEXT_JOB_ENTERED:
            if 'li' == tag:
                self.state = self.STATE_FIND_NEXT_JOB

            if 'ul' == tag:
                self.state = self.STATE_START
        pass

    def handle_data(self, data):
        # print "Encountered some data  :", data
        if self.STATE_FOUND_POSITION == self.state:
            data = data.strip()
            if not data == '':
                #print data
                self.position = data
                self.state = self.STATE_FIND_COMPANY
                pass

        elif self.STATE_FOUND_COMPANY == self.state:
            data = data.strip()
            if not data == '':
                #print data
                self.company = data
                self.state = self.STATE_FIND_DATE
                pass

        elif self.STATE_FOUND_DATE == self.state:
            data = data.strip()
            if not data == '':
                #print data
                self.date = data

                if self.same_date is not None and self.same_date != self.date:
                    self.state = self.STATE_END
                    print 'end same date at ' + data + self.jobid
                    raise EOFError()
                else:
                    if self.same_date is None:
                        self.same_date = self.date
                        print 'set same date ' + self.same_date

                    # add a job of the same date
                    # print 'add a job ' + self.position
                    self.job_ad_list.append(JobAd(
                        self.jobid,
                        self.position,
                        self.company,
                        self.date
                        ))
                    self.state = self.STATE_FIND_NEXT_JOB_ENTERED
                    pass

        pass

    def get_job_ad_list(self):
        return self.job_ad_list


def fetch_mingpao(page_no):
    #url = 'http://jump.mingpao.com/cfm/JobSearch2.cfm?JobAreaID=10&DaysBefore=1&Sort=1D&PageID=%d' % page_no
    #url = 'https://jump.mingpao.com/job/search/Jobs?Keyword=%s&IndustryID=10&Page=%d' % (u'\u4e2d'.encode('utf-8', 'ignore'), page_no)
    # keyword: chinese
    # url = 'https://jump.mingpao.com/job/search/Jobs?Keyword=%E4%B8%AD%E6%96%87&IndustryID=10&Page=' + str(page_no)
    # url = 'https://jump.mingpao.com/job/search/Jobs?Keyword=&IndustryID=10&Page=' + str(page_no)
    url = 'https://jump.mingpao.com/job/search/Jobs/2?Keyword=&JobAreaID%5B%5D=10-2&IndustryID=10&SortBy=&Page=' + str(page_no)

    response = urllib2.urlopen(url)
    html = response.read()
    #html.decode("UTF-8", 'ignore')

    parser = MyHTMLParser()
    parser.job_ad_list = []
    parser.feed(html
                #.decode("big5", 'ignore')
                #.encode('utf-8', 'ignore')
                )

    # print html.decode("big5", 'ignore').encode('utf-8', 'ignore')

    return parser.get_job_ad_list()

class JobDetailParser(BaseHTMLParser):
    ignore_line_list = [
        '',
        'More jobs from this Company',
        'print',
        'save',
        'share',
        'Apply Now',
    ]

    STATE_FIND_JOB_DETAIL = 0
    STATE_FOUND_JOB_DETAIL = 1

    state = STATE_FIND_JOB_DETAIL

    content_line_list = []

    def handle_starttag(self, tag, attrs):
        if self.state == self.STATE_FIND_JOB_DETAIL:
            if tag == 'div' and self.checkInTag('div', 'id', 'job_detail', tag, attrs):
                self.state = self.STATE_FOUND_JOB_DETAIL
                # print '------------------'

        elif self.state == self.STATE_FOUND_JOB_DETAIL:
            if tag == 'script':
                self.state = self.STATE_FIND_JOB_DETAIL
        pass

    def handle_endtag(self, tag):
        pass

    def handle_data(self, data):
        if self.state == self.STATE_FOUND_JOB_DETAIL:
            data = data.strip()
            if data not in self.ignore_line_list:
                # print data
                self.content_line_list.append(data)
        pass

    def get_content(self):
        return "<br/>".join(self.content_line_list)


def fetch_job_detail(url):
    response = urllib2.urlopen(url)
    html = response.read()
    # print html

    parser = JobDetailParser()
    parser.content_line_list= []
    parser.feed(html)
    return parser.get_content()

def highlight(label, keyword_list):
    for keyword in keyword_list:
        pattern = re.compile(re.escape(keyword), re.IGNORECASE)
        label = pattern.sub('<span class="highlight">%s</span>' % keyword, label)
        if keyword in label:
            label = label.replace(keyword, '<span class="highlight">%s</span>' % keyword)
    return label

if __name__ == '__main__':
    job_ad_list = []

    page_no = 1
    while True:
        #print 'fetching page_no ', page_no

        try:
            result = fetch_mingpao(page_no)
            # print len(result)
            if len(result) == 0:
                break
            job_ad_list.extend(result)
            page_no += 1
        except EOFError:
            break

    # fetch job details
    for job_ad in job_ad_list:
        content = fetch_job_detail(job_ad.get_url())
        job_ad.content = content
        pass
    # exit()

    job_ad_list.sort(cmp=getKey, reverse=True)

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
    <h1>{count}/{total} {company}</p>
    <h2><a href=\"{position_url}\">{position_label}</a></h2>
    <div>{content}</div>
    </section>
    '''
    # print gen dat
    now = datetime.datetime.now()
    print format.format(company=u'\u6700\u5f8c\u66f4\u65b0'.encode('utf-8', 'ignore'),
                            position_url='',
                            position_label=now.strftime("%Y-%m-%d %H:%M").encode('utf-8', 'ignore'),
                            content='',
                            count='',
                            total='')

    # print keyword card
    print format.format(company=u'\u95dc\u9375\u5b57\u6b21\u5e8f'.encode('utf-8', 'ignore'),
                            position_url='',
                            position_label=' > '.join(keyword_list),
                            content='',
                            count='',
                            total=''
                            )

    total = len(job_ad_list)
    count = 0
    for job_ad in job_ad_list:
        count += 1
        print format.format(company=highlight(job_ad.get_company(), company_keyword_list),
                            position_url=job_ad.get_url(),
                            position_label=highlight(job_ad.get_position(), keyword_list),
                            content=highlight(job_ad.get_content(), keyword_list),
                            count=count,
                            total=total)

    print '''
    </body>
    </html>
        '''
