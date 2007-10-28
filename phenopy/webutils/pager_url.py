import math


def pager_params(args, total_count=1, page_size=10):
    page = 1
    try:
        if 'page' in args and int(args['page']) > 0:
            page = args['page']
    except:
        pass
    
    offset = int(page_size * (int(page) - 1))
    pages_total = int(math.ceil(float(total_count) / page_size))
    return (pages_total, page, offset)

