import json, os, django, sys, asyncio, websockets
from channels.db import database_sync_to_async

dir = os.path.abspath(__file__)
print(dir)
sys.path.append(dir)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "escpos_web.settings")
django.setup()
from escpos_printer.models import TEWeb, Printer, Receipt, ReceiptLog

async def connect_te_web():
    uri = "ws://localhost:8000/ws/taiwan_einvoice/escpos_web/2/"
    async with websockets.connect(uri) as websocket:
        i = 0
        await database_sync_to_async(save_receipt)(i)
        while True:
            print(i)
            J = await websocket.recv()
            message = json.loads(J)['message']
            print(f"< {message}")
            count = await database_sync_to_async(save_receipt)(message)
            print("Printer count: {}".format(count))
            i += 1
        
def save_receipt(message):
    print("type: {}".format(type(message)))
    print("save_receipt: {}".format(message))
    try:
        j_message = json.loads(message)
    except:
        return "Init"
    for k, v in Printer.load_printers().items():
        print(k, v)
    te_web = TEWeb.objects.get(url='ws://localhost:8000/ws/taiwan_einvoice/escpos_web/2/')
    r = Receipt.create_receipt(te_web, message)
    p1 = Printer.objects.get(serial_number='4E3346460074210000')
    r.print(p1)
    return "Done"


if '__main__' == __name__:
    print(Printer.objects.count())
    asyncio.get_event_loop().run_until_complete(connect_te_web())