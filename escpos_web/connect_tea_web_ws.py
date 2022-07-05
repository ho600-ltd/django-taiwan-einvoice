#!/usr/bin/env python3

import json, os, django, sys, asyncio, websockets, logging
from time import sleep
from channels.db import database_sync_to_async
from libs import get_boot_seed

SSL = False
dir = os.path.abspath(__file__)
print(dir)
sys.path.append(dir)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "escpos_web.settings")
django.setup()
from escpos_printer.models import TEAWeb, Printer, Receipt, ReceiptLog

logging.basicConfig()
lg = logging.getLogger(__name__)
lg.setLevel('INFO')

async def connect_and_print_receipt(tea_web):
    token_auth = tea_web.generate_token_auth()
    url = "{}{}/".format(tea_web.url, token_auth)
    async with websockets.connect(url, ssl=SSL) as websocket:
        i = 0
        await database_sync_to_async(print_receipt)(tea_web.id, i, '', '')
        while True:
            boot_seed = get_boot_seed()
            data_json = await websocket.recv()
            data= json.loads(data_json)
            if '???' == boot_seed:
                invoice_data = json.loads(data['invoice_json'])
                result = {"meet_to_tw_einvoice_standard":
                            invoice_data['meet_to_tw_einvoice_standard'],
                          "track_no": invoice_data['track_no'],
                          "unixtimestamp": data['unixtimestamp'],
                          "status": False,
                          "status_message": "「發票機」開機時，未產生通行碼種子"}
            else:
                pass_key = data.get('pass_key', '')
                if boot_seed != pass_key:
                    invoice_data = json.loads(data['invoice_json'])
                    result = {"meet_to_tw_einvoice_standard":
                                invoice_data['meet_to_tw_einvoice_standard'],
                              "track_no": invoice_data['track_no'],
                              "unixtimestamp": data['unixtimestamp'],
                              "status": False,
                              "status_message": "通行碼(Pass Key {})錯誤".format(pass_key)}
                else:
                    result = await database_sync_to_async(print_receipt)(tea_web.id,
                                                                         data['serial_number'],
                                                                         data['unixtimestamp'],
                                                                         data['invoice_json'])
            token_auth = tea_web.generate_token_auth()
            url = "{}print_result/{}/".format(tea_web.url, token_auth)
            lg.info("url: {}".format(url))
            lg.info("ssl: {}".format(SSL))
            lg.info("result: {}".format(result))
            async with websockets.connect(url, ssl=SSL) as ws:
                await ws.send(json.dumps(result))
            i += 1
            lg.info("print order: {}".format(i))

        
def print_receipt(tea_web_id, serial_number, unixtimestamp, invoice_json):
    lg.info("tea_web_id: {}".format(tea_web_id))
    lg.info("serial_number: {}".format(serial_number))
    lg.info("unixtimestamp: {}".format(unixtimestamp))
    lg.info("type: {} => should be str".format(type(invoice_json)))
    lg.info("invoice_json: {}".format(invoice_json))
    try:
        invoice_data = json.loads(invoice_json)
    except:
        return 'Init'
    result = {"meet_to_tw_einvoice_standard": invoice_data['meet_to_tw_einvoice_standard'],
              "track_no": invoice_data['track_no'],
              "unixtimestamp": unixtimestamp,
             }
    re_print_original_copy = invoice_data.get('re_print_original_copy', False)
    print_mark = invoice_data.get('print_mark', False)
    if invoice_data.get('details_with_einvoice_in_the_same_paper', False):
        extra_content = json.loads(invoice_json).get('details_content', [])
    else:
        extra_content = []
    tea_web = TEAWeb.objects.get(id=tea_web_id)
    r = Receipt.create_receipt(tea_web, invoice_json, re_print_original_copy=re_print_original_copy)
    try:
        p1 = Printer.objects.get(serial_number=serial_number)
    except Printer.DoesNotExist:
        result['status'] = False
        result['status_message'] = "印表機 {} 不存在".format(serial_number)
    else:
        try:
            _result = r.print(p1,
                              print_mark=print_mark,
                              re_print_original_copy=re_print_original_copy,
                              extra_content=extra_content,
                             )
        except Exception as e:
            result['status'] = False
            result['status_message'] = "Exception: {}".format(e)
        else:
            if True != _result:
                result['status'] = False
                result['status_message'] = _result[1]
            else:
                result['status'] = True
    lg.info('status: {}'.format(result['status']))
    lg.info('status message: {}'.format(result.get('status_message', '__none__')))
    return result


async def connect_and_check_print_status(tea_web):
    interval_seconds = 1.7
    while_order = 0
    token_auth = tea_web.generate_token_auth()
    url = "{}status/{}/".format(tea_web.url, token_auth)
    async with websockets.connect(url, ssl=SSL) as websocket:
        while True:
            try:
                printers = await database_sync_to_async(check_printer_status)(while_order)
                printers['interval_seconds'] = {"value": interval_seconds}
                await websocket.send(json.dumps(printers))
            except websockets.ConnectionClosed:
                break
            else:
                lg.info(printers)
                sleep(interval_seconds)
                while_order += 1

        
def check_printer_status(while_order):
    lg.info("while_order: {}".format(while_order))
    result = Printer.load_printers(idVendor_idProduct_set=((0x04b8, 0x0202),
                                                           (0x0483, 0x5743),
                                  ), setup=False)
    return result


if '__main__' == __name__:
    method = sys.argv[1]
    args = sys.argv[2:]
    url = args[0]
    SSL = True if args[1] == 'ssl=true' else False

    if 'print_receipt' == method:
        tea_web = TEAWeb.objects.get(url=url)
        asyncio.get_event_loop().run_until_complete(connect_and_print_receipt(tea_web))
    elif 'check_printer_status' == method:
        tea_web = TEAWeb.objects.get(url=url)
        asyncio.get_event_loop().run_until_complete(connect_and_check_print_status(tea_web))

