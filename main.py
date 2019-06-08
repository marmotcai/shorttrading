#coding=utf-8

import stockinfo
import stock
import threading
import http.server as hs


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

    # stocks_code = ['601988', '601939', '601398', '300096']
    stocks_code = ['300096']
    stocks_obj = {}

    for num in range(0, stocks_code.__len__()):

        startinfo = stockinfo.startinfos()

        startinfo.set_stock_code(stocks_code[num]) # 股票代码
        startinfo.set_minimum_profit(100) # 单次交易最小盈利
        startinfo.set_minimum_volume(500) # 单次交易数量
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




