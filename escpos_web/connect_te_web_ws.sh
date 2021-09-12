while [[ 1 ]]; do
	echo "sh"
	./connect_te_web_ws.py check_printer_status 'ws://localhost:8000/ws/taiwan_einvoice/escpos_web/2/'
	sleep 1.7
done
