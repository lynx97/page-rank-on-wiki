import scrapy
from scrapy.crawler import CrawlerProcess
import numpy as np
from scipy.sparse import csc_matrix
import networkx as nx
from mechanize import Browser

# create list contain dicts {url_web_wiki: list_url}
pages = {}
node = 1
#create list contain title
page_title = {}
g_nodes = []
class TestSpider(scrapy.Spider):
    name = 'test'
    start_urls = [
        'https://en.wikipedia.org/wiki/Donald_Trump'
    ]
    def parse(self, response):
        global pages
        global node
        yield {
            'url': response.request.url,
            'title': response.xpath("//title/text()").extract_first()
        }

        list_page = response.xpath("//a[starts-with(@href,'/wiki') and not(contains(@href,':'))]/@href").extract()

        key = response.request.url.replace("https://en.wikipedia.org", "")
        pages[key] = list_page
        page_title[key] = response.xpath("//title/text()").extract_first()

        # for link in list_page:
        #     if (link.startswith('/wiki/')):
        #         print("https://en.wikipedia.org" + link)
        #         nodes = nodes + 1
        if (list_page is not None) and node < 2:
            node = node + len(list_page)
            for next_page in list_page:
                yield response.follow(next_page, callback=self.parse)

def PR(G, max_iter = 200, tol=.01):
    return nx.pagerank(G, alpha=0.9)

def build_matrix(wiki_pages):
    nodes = []

    for key in list(wiki_pages.keys()):
        if key not in nodes:
            nodes.append(key)
    print("done-key")
    for value in list(wiki_pages.values()):
        for v in value:
            if v not in nodes:
                nodes.append(v)

    print("done-value")
    nodes=nodes[:10000]
    size = len(nodes)
    print("********")
    print(size)

    matrix = np.zeros(shape=(size, size), dtype=np.int32)

    for i in range(size):
        cur_page = nodes[i]
        for j in range(size):

            if i == j:  # 2 trang web trùng tên, bỏ qua
                matrix[i][j] = 1

            try:
                list_urls = wiki_pages[cur_page]
                if nodes[j] in list_urls:
                    matrix[i][j] = 1
            except:
                continue
    
    tmp = nx.from_numpy_matrix(matrix)
    res = PR(tmp)
    writeFile(res, nodes)
    return res

def writeFile(res, nodes):
    file = open('20182_IT4868_Assignment01_Group1_ranking.txt', 'w')
    line_1 = 'https://en.wikipedia.org/wiki/Donald_Trump' + '\t' + str(len(res)) + '\n'
    file.write(line_1)
    line_2 = 'PageRank' + '\t' + 'Title' + '\n'
    file.write(line_2)

    sort_res = (sorted(res.items(), key = 
             lambda kv:(kv[1], kv[0]), reverse=True)) 
    for k,v in sort_res:
        tmp = nodes[k]
        # #lay ra tieu de
        # link = "https://vi.wikipedia.org" + tmp
        # br = Browser()
        # br.open(link)
        # title_i = br.title()
        v_i = round(v,4)
        line_i = tmp + '\t' + str(v_i) + '\n'
        file.write(line_i)
    file.close()


if __name__ == '__main__':
    # os.remove('result.json')
    process = CrawlerProcess({
        'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)',
    })

    process.crawl(TestSpider)
    process.start()
    build_matrix(pages)
