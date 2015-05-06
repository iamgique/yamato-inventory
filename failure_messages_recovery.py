# -*- coding: utf-8 -*-
# PCMS retry script version 1.2
import os
import sys
import json
import requests

from database import *

pcms_api_prefix = "http://pcms-b-alpha.itruemart.com/api/v4/"
pcms_api_increase = pcms_api_prefix + "stock/increase"
pcms_api_decrease = pcms_api_prefix + "stock/decrease"
pcms_api_sku_create = pcms_api_prefix + "sku/create"
pcms_api_sku_update = pcms_api_prefix + "sku/update"
pcms_api_order_update_status = pcms_api_prefix + "orders/update-status"

class failure_messages_recovery:
    @classmethod
    def process_update_stock(cls, payload):
        json_array = json.loads(payload)
        response_array = []
        for update_row in json_array:
            sku = update_row['sku']
            update_row['quantity'] = 0
            update_row['note'] = 'recovery stock synchronization'
            mat_count = mat_count = database.count_virtual_stock_by_sku(sku)[0]
            physical_count = database.count_items_by_sku(sku)[0]
            if mat_count is None:
                mat_count = '0'
            if physical_count is None:
                physical_count = '0'
            update_row['total'] = int(mat_count) + int(physical_count)
            response_array.append(update_row)
        return json.dumps(response_array)


    @classmethod
    def recover(cls):
        logfile = open('failure_messages_recovery.log', 'a')
        records = database.get_all_failure_messages()
        pcms_api = None
        failed = False

        # record index mapping
        # [0] => id
        # [1] => message_body
        # [2] => response
        # [3] => type
        # [4] => status
        for record in records:
            payload = record[1]
            # Check message type
            if record[3] == "stock/increase":
                try:
                    payload = failure_messages_recovery.process_update_stock(payload)
                except:
                    print("failed to update stock increase message {}").format(payload.encode('utf-8'))
                    database.mark_message_failed_after_retry(record[0])
                    exit()
                pcms_api = pcms_api_increase
            elif record[3] == "stock/decrease":
                try:
                    payload = failure_messages_recovery.process_update_stock(payload)
                except:
                    print("failed to update stock decrease message {}").format(payload.encode('utf-8'))
                    database.mark_message_failed_after_retry(record[0])
                pcms_api = pcms_api_decrease
            elif record[3] == "sku/create":
                pcms_api = pcms_api_sku_create
            elif record[3] == "sku/update":
                pcms_api = pcms_api_sku_update
            elif record[3] == "orders/update-status":
                pcms_api = pcms_api_order_update_status
            else:
                print("Unknown message type. Type = {}".format(record[3]))
                exit()

            headers = {'Content-Type': 'application/json'}
            try:
                # write to file before send
                logfile.write(payload.encode('utf-8'))
                response = requests.post(
                    pcms_api,
                    headers=headers,
                    data=payload.encode('utf-8')
                )

                if int(response.json()["code"]) == 200:
                    database.mark_message_close(record[0])
                else:
                    print response.json()
                    failed = True
            except:
                print "Unexpected error:", sys.exc_info()
                failed = True

            if failed:
                print('Message id = {} api = {} failed with payload = {}'.format(record[0], record[3], payload.encode('utf-8')))
                database.mark_message_failed_after_retry(record[0])
                exit()


if __name__ == "__main__":
    database.create_connection(
        host='localhost',
        user='root',
        passwd='',
        db='ops'
    )
    failure_messages_recovery.recover()
