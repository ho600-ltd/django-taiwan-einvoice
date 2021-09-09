import json, os, django, sys, asyncio, websockets
from channels.db import database_sync_to_async

dir = os.path.abspath(__file__)
print(dir)
sys.path.append(dir)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "escpos_web.settings")
django.setup()
from escpos_printer.models import Printer, ReceiptLog

async def connect_te_web():
    uri = "ws://localhost:8000/ws/chat/lobby/"
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
    print("save_receipt: {}".format(message))
    for k, v in Printer.load_printers().items():
        print(k, v)
    return Printer.objects.count()


if '__main__' == __name__:
    print(Printer.objects.count())
    asyncio.get_event_loop().run_until_complete(connect_te_web())