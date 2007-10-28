

class Pager(object):

    def __init__(self, page_num, page_size, page_total, page_url):
        self.page_num = page_num
        self.page_size = page_size
        self.page_total = page_total
        self.page_url = page_url


class Filter(object):
    def __init__(self, list):
        self.tags = list
        if len(list):
            self.url = "+".join(list)
        
            
