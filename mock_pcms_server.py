import web

urls = (
    '/stock/increase', 'index',
    '/stock/decrease', 'index',
    '/sku/create', 'index',
    '/sku/update', 'index',
    '/orders/update-status', 'index'
)

class index:
    def POST(self):
        i = web.input()
        print "received: %s" % i
        return "{\"status\":\"error\",\"code\":401\"message\":\"Mock response\",\"data\":\"\"}"

if __name__ == "__main__":
    web.config.debug = True
    app = web.application(urls, globals())
    app.run()
