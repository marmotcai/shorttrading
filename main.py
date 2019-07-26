#coding=utf-8

import stockinfo
import stock
import threading
import http.server as hs

import pandas as pd
from matplotlib import pyplot as plt

#########################################################################################

datafile = "./data/stock.csv"

class Learning():

    def __init__(self, data_file):
        self.loaddata(data_file)

    def loaddata(self, data_file):
        # Import data
        self.data = pd.read_csv(data_file)

#########################################################################################

class ServerException(Exception):
    '''服务器内部错误'''
    pass

class RequestHandler(hs.BaseHTTPRequestHandler):

    def send_content(self, page, status=200):

        self.send_response(status)
        self.send_header("Content-type", "text/html")
        self.send_header("charset", "utf-8")
        # self.send_header("Content-Length", str(len(page)))
        self.end_headers()
        self.wfile.write(bytes(page, encoding='utf-8'))

    def do_GET(self):
        stockinfo_body = ""

        content = ""
        index_file.seek(0)
        text_lines = index_file.readlines()
        for line in text_lines:
            if ("msg" in line):
                for num in range(0, stocks_code.__len__()):
                    if ("msg" + str(num) in line):
                        stock_obj = stocks_obj[num]
                        content += line.replace("msg" + str(num), stock_obj.s.get_state_htmlitem())
            else:
                content += line


        self.send_content(content, 200)

    Error_Page = """ \
                    <html>
                    <body>
                    <h1>Error accessing {path}</h1>
                    <p>{msg}</p>
                    </body>
                    </html>
                    """

    def handle_error(self, msg):
        content = self.Error_Page.format(path=self.path, msg=msg)
        self.send_content(content, 404)

#########################################################################################

if __name__ == '__main__':

    learning = Learning(datafile)

    exit(0)

    # stocks_code = ['601988', '601939', '601398', '300096']
    stocks_code = ['300096']
    stocks_obj = {}

    input_values = [1, 2, 3, 4, 5]  # 指定输入参数
    squares = [1, 4, 9, 16, 25]  # 指定输出参数
    plt.plot(input_values, squares, linewidth=5)  # 调用绘制函数，传入输入参数和输出参数

    plt.title("Stock Quotes", fontsize=16)  # 指定标题，并设置标题字体大小
    plt.xlabel("time", fontsize=12)  # 指定X坐标轴的标签，并设置标签字体大小
    plt.ylabel("prices", fontsize=12)  # 指定Y坐标轴的标签，并设置标签字体大小
    plt.tick_params(axis='both', labelsize=12)  # 参数axis值为both，代表要设置横纵的刻度标记，标记大小为14
    plt.show()

    exit(0)


    for num in range(0, stocks_code.__len__()):

        startinfo = stockinfo.startinfos()

        startinfo.set_stock_code(stocks_code[num]) # 股票代码
        startinfo.set_minimum_profit(100) # 单次交易最小盈利
        startinfo.set_minimum_volume(1000) # 单次交易数量
        startinfo.set_maximum_capital(100000) # 资金总额
        startinfo.set_old_position(50000) # 存量老股，用于T+0

        stock_obj = stock.BaseStock(startinfo)

        stocks_obj[num] = stock_obj

        threading.Thread(target=stock_obj.run, name=str(stock_obj.s.startinfo.stock_code)).start()

    # server_obj = server.BaseServer(stock_obj)
    # server_obj.run()

    index_file = open("./html/index.html", "r")  # 以二进制读取文件内容
    httpAddress = ('', 5588)
    httpd = hs.HTTPServer(httpAddress, RequestHandler)
    httpd.serve_forever()
    index_file.close()




