# -*- coding: utf-8 -*-
import os
import sys
import json
import requests

from database import *

pcms_api_prefix = "http://pcms-b-alpha.itruemart.com/api/v4/"
#pcms_api_prefix = "http://localhost:8888/pcms/"
pcms_api_increase = pcms_api_prefix + "stock/increase"
pcms_api_decrease = pcms_api_prefix + "stock/decrease"
pcms_api_sku_create = pcms_api_prefix + "sku/create"
pcms_api_order_update_status = pcms_api_prefix + "orders/update-status"

class failure_messages_recovery:
    @classmethod
    def recover(cls):
        logfile = open('failure_messages_recovery.log', 'w')
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
                #print("inc")
                pcms_api = pcms_api_increase
            elif record[3] == "stock/decrease":
                #print("dec")
                pcms_api = pcms_api_decrease
            elif record[3] == "sku/create":
                #print("sku")
                pcms_api = pcms_api_sku_create
            elif record[3] == "orders/update-status":
                #print("update")
                pcms_api = pcms_api_order_update_status
            else:
                print("Unknown message type. Type = {}".format(record[3]))
                exit()

            headers = {'content-type': 'application/json'}
            try:
                response = requests.post(
                    pcms_api,
                    headers=headers,
                    data=json.dumps(payload)
                )

                if int(response.json()["code"]) == 200:
                    # mark this record to 'close'
                    database.mark_message_close(record[0])
                else:
                    failed = True
            except:
                failed = True

            if failed:
                print('Message id = {} failed with payload = {}'.format(record[0], payload))
                exit()


if __name__ == "__main__":
    database.create_connection(
        host='localhost',
        user='root',
        passwd='1q2w3e4r',
        db='ops_structure'
    )
    failure_messages_recovery.recover()
