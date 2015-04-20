# -*- coding: utf-8 -*-
import os
import sys
import json
import requests

from database import *

pcms_api = "http://pcms-b-alpha.itruemart.com/api/v4/stock/increase"

class pcms_stock:
    @classmethod
    def sync_total(cls):
        records = database.get_all_skus()

        stocks = []
        for record in records[:102]:
            total = 0
            sku = record[0]

            physical = database.count_items_by_sku(sku)
            virtual = database.count_virtual_stock_by_sku(sku)

            total += int(physical[0])
            total += int(virtual[0]) if virtual else 0

            stock = cls.build_sku_stock_update(sku, total)
            stocks.append(stock)

        # while stocks != []:
        #     skus = stocks[:10]
        #     print "round: %s" % skus
        #     del stocks[:10]

        headers = {'content-type': 'application/json'}
        response = requests.post(
            pcms_api,
            headers=headers,
            data=json.dumps(stocks)
        )

        if response.json()['status'] == "error":
            print "{}: {}".format(response.json()['message'], response.json()['data'])
        else:
            print "Sync stock completed."

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
        host='localhost',
        user='root',
        passwd='1q2w3e4r',
        db='ops'
    )
    pcms_stock.sync_total()
