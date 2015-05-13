# -*- coding: utf-8 -*-
# PCMS retry script version 1.5
import os
import sys
import json
import requests
import yaml
import logging.config
import logging
import re
import sys, traceback

from database import *
from tendo import singleton

pcms_api_prefix = "http://pcms.itruemart.com/api/v4/sku/create"

def setup_logging(default_path='logging.yaml'):
    #Loading logging config
    with open(default_path, 'rt') as f:
        config = yaml.load(f.read())
    logging.config.dictConfig(config)


class null_inventory_skus_recovery:
    @classmethod
    def recover(cls):
        records = database.get_null_inventory_skus()

        # record index mapping
        # [0] => sku_id
        # [1] => product_name
        # [2] => color
        # [3] => size
        # [4] => brand_id
        # [5,6] => selling price / special price
        # [7] primary cat id
        for record in records:
            sku_obj = {}
            sku_obj['sku_id'] = record[0]
            sku_obj['name'] = record[1]
            sku_obj['color'] = record[2]
            sku_obj['size'] = record[3]
            sku_obj['brand'] = record[4]
            sku_obj['unit_type'] = "piece"
            sku_obj['selling_price'] = str(record[5])
            sku_obj['special_price'] = str(record[6])
            sku_obj['material_code'] = ""
            sku_obj['category_id'] = record[7]


            payload = '[' + json.dumps(sku_obj) + ']'
            headers = {'Content-Type': 'application/json'}
            try:
                # write to file before send
                main_logger.info(payload)
                response = requests.post(
                    pcms_api_prefix,
                    headers=headers,
                    data=payload.encode('utf-8')
                )
                if response.status_code == 200:
                    if int(response.json()["code"]) == 200:
                        main_logger.info("successfully sent sku")
                    else:
                        main_logger.error(response.json())
                else:
                    main_logger.error('failed to sent null inventory sku. status_code:' + str(response.status_code))
            except:
                exc_type, exc_value, exc_traceback = sys.exc_info()
                err_line = traceback.format_exception(exc_type, exc_value, exc_traceback)
                main_logger.error(err_line)

if __name__ == "__main__":
    logging_config =  os.path.dirname(os.path.realpath(__file__)) + "/logging.yaml"
    me = singleton.SingleInstance()
    database.create_connection(
        host='localhost',
        user='root',
        passwd='',
        db='ops'
    )

    setup_logging(logging_config)
    main_logger = logging.getLogger('main_module')
    null_inventory_skus_recovery.recover()
