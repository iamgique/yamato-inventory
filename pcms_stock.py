# -*- coding: utf-8 -*-
import os
import sys
import json
import requests

from database import *

#pcms_api = "http://pcms.itruemart.com/api/v4/stock/increase"
pcms_api = "http://pcms.itruemart-dev.com/api/v4/stock/increase"

class pcms_stock:
    @classmethod
    def sync_total(cls):
        logfile = open('update_stock.txt', 'w')
        records = database.get_all_skus()

        for record in records:
            total = 0
            sku = record[0]

            print "sending sku: " + sku

            physical = database.count_items_by_sku(sku)
            virtual = database.count_virtual_stock_by_sku(sku)

            total += int(physical[0])

            if virtual[0] is not None:
                total += int(virtual[0])

            stock = cls.build_sku_stock_update(sku, total)
            payload = [stock]

            headers = {'content-type': 'application/json'}
            response = requests.post(
                pcms_api,
                headers=headers,
                data=json.dumps(payload)
            )

            log = "{}: {}".format(response.json()['message'], response.json()['data'])
            print log
            logfile.write("{}\n".format(log))

        logfile.close()


    @classmethod
    def build_sku_stock_update(cls, sku, total):
        payload = {
            "sku": sku,
            "quantity": "0",
            "note": "adjust yamato stock",
            "total": str(total)
        }
        return payload


if __name__ == "__main__":
    database.create_connection(
        #host='myl.iems.com',
        host='myl.iems-dev.com',
        user='ems_rw',
        passwd='1q2w3e4r',
        db='ems_db'
    )
    pcms_stock.sync_total()
