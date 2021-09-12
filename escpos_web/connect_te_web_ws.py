#!/usr/bin/env python3

import json, os, django, sys, asyncio, websockets, logging
from time import sleep
from channels.db import database_sync_to_async

dir = os.path.abspath(__file__)
print(dir)
sys.path.append(dir)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "escpos_web.settings")
django.setup()
from escpos_printer.models import TEWeb, Printer, Receipt, ReceiptLog

logging.basicConfig()
lg = logging.getLogger(__name__)
lg.setLevel('INFO')

async def connect_and_print_receipt(te_web):
    async with websockets.connect(te_web.url) as websocket:
        i = 0
        await database_sync_to_async(print_receipt)(te_web.id, '', i)
        while True:
            data_json = await websocket.recv()
            data= json.loads(data_json)
            count = await database_sync_to_async(print_receipt)(te_web.id, data['serial_number'], data['invoice_json'])
            # if 'Print Fail' == count:
            #     await websocket.send(json.dumps({"serial_number": data['serial_number'], "invoice_json": "", "status": False}))
            # else:
            #     await websocket.send(json.dumps({"serial_number": data['serial_number'], "invoice_json": "", "status": True}))
            i += 1
            lg.info("print order: {}".format(i))

        
def print_receipt(te_web_id, serial_number, invoice_json):
    lg.info("te_web_id: {}".format(te_web_id))
    lg.info("serial_number: {}".format(serial_number))
    lg.info("type: {}".format(type(invoice_json)))
    lg.info("invoice_json: {}".format(invoice_json))
    try:
        invoice_data = json.loads(invoice_json)
    except:
        return "Init"
    for k, v in Printer.load_printers().items():
        lg.info("{}: {}".format(k, v))
    te_web = TEWeb.objects.get(id=te_web_id)
    r = Receipt.create_receipt(te_web, invoice_json)
    try:
        p1 = Printer.objects.get(serial_number=serial_number)
    except Printer.DoesNotExist:
        return "Print Fail"
    else:
        r.print(p1)
        return "Print Done: {}".format(invoice_data['track_no'])


async def connect_and_check_print_status(te_web, while_order=0):
    async with websockets.connect(te_web.url + 'status/') as websocket:
        while True:
            try:
                printers = await database_sync_to_async(check_print_status)(while_order)
                await websocket.send(json.dumps(printers))
            except websockets.ConnectionClosed:
                break
            else:
                sleep(1.7)
                while_order += 1

        
def check_print_status(while_order):
    lg.info("while_order: {}".format(while_order))
    result = Printer.load_printers(setup=False)
    return result


if '__main__' == __name__:
    method = sys.argv[1]
    args = sys.argv[2:]
    if 'print_receipt' == method:
        url = args[0]
        te_web = TEWeb.objects.get(url=url)
        asyncio.get_event_loop().run_until_complete(connect_and_print_receipt(te_web))
    elif 'check_printer_status' == method:
        url = args[0]
        te_web = TEWeb.objects.get(url=url)
        asyncio.get_event_loop().run_until_complete(connect_and_check_print_status(te_web))