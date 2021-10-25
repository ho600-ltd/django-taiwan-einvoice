#!/usr/bin/env python3

import json, os, django, sys, asyncio, websockets, logging
from time import sleep
from channels.db import database_sync_to_async

SSL = False
dir = os.path.abspath(__file__)
print(dir)
sys.path.append(dir)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "escpos_web.settings")
django.setup()
from django.utils.translation import ugettext_lazy as _
from escpos_printer.models import TEWeb, Printer, Receipt, ReceiptLog

logging.basicConfig()
lg = logging.getLogger(__name__)
lg.setLevel('INFO')

async def connect_and_print_receipt(te_web):
    token_auth = te_web.generate_token_auth()
    url = "{}{}/".format(te_web.url, token_auth)
    async with websockets.connect(url, ssl=SSL) as websocket:
        i = 0
        await database_sync_to_async(print_receipt)(te_web.id, i, '', '')
        while True:
            data_json = await websocket.recv()
            data= json.loads(data_json)
            result = await database_sync_to_async(print_receipt)(te_web.id,
                                                                data['serial_number'],
                                                                data['batch_no'],
                                                                data['invoice_json'])
            token_auth = te_web.generate_token_auth()
            url = "{}print_result/{}/".format(te_web.url, token_auth)
            async with websockets.connect(url, ssl=SSL) as ws:
                await ws.send(json.dumps(result))
            i += 1
            lg.info("print order: {}".format(i))

        
def print_receipt(te_web_id, serial_number, batch_no, invoice_json):
    lg.info("te_web_id: {}".format(te_web_id))
    lg.info("serial_number: {}".format(serial_number))
    lg.info("batch_no: {}".format(batch_no))
    lg.info("type: {} => should be str".format(type(invoice_json)))
    lg.info("invoice_json: {}".format(invoice_json))
    try:
        invoice_data = json.loads(invoice_json)
    except:
        return 'Init'
    result = {"meet_to_tw_einvoice_standard": invoice_data['meet_to_tw_einvoice_standard'],
              "track_no": invoice_data['track_no'],
              "batch_no": batch_no,
             }
    te_web = TEWeb.objects.get(id=te_web_id)
    r = Receipt.create_receipt(te_web, invoice_json)
    try:
        p1 = Printer.objects.get(serial_number=serial_number)
    except Printer.DoesNotExist:
        result['status'] = False
        result['status_message'] = _("{} is not exist").format(serial_number)
    else:
        try:
            _result = r.print(p1)
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


async def connect_and_check_print_status(te_web):
    interval_seconds = 1.7
    while_order = 0
    token_auth = te_web.generate_token_auth()
    url = "{}status/{}/".format(te_web.url, token_auth)
    async with websockets.connect(url, ssl=SSL) as websocket:
        while True:
            try:
                printers = await database_sync_to_async(check_print_status)(while_order)
                printers['interval_seconds'] = {"value": interval_seconds}
                await websocket.send(json.dumps(printers))
            except websockets.ConnectionClosed:
                break
            else:
                lg.info(printers)
                sleep(interval_seconds)
                while_order += 1

        
def check_print_status(while_order):
    lg.info("while_order: {}".format(while_order))
    result = Printer.load_printers(setup=False)
    return result


if '__main__' == __name__:
    method = sys.argv[1]
    args = sys.argv[2:]
    url = args[0]
    SSL = True if args[1] == 'ssl=true' else False

    if 'print_receipt' == method:
        te_web = TEWeb.objects.get(url=url)
        asyncio.get_event_loop().run_until_complete(connect_and_print_receipt(te_web))
    elif 'check_printer_status' == method:
        te_web = TEWeb.objects.get(url=url)
        asyncio.get_event_loop().run_until_complete(connect_and_check_print_status(te_web))

