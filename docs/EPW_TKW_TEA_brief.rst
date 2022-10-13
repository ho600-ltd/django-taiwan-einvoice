EPW / TKW / TEA 架構
===============================================================================

本專案 Django-Taiwan-EInvoice (DTEI) 是由 3 部份: EPW / TKW / TEA 所組成。

TEA 是一個 Django-based 的 Python app ，可直接以 Web Api Service 方式執行，\
或是導入至其他 Django-based 的專案中。 TEA 支援 WebSocket 協定，\
當 EPW 系統開機後， EPW 會連線至 TEA WebSocket Api 或 CEC WebSocket Api(以導入 TEA)。

當 TEA 有列印電子發票證明聯的需求，可送出其發票資料(JSON)，\
發票 JSON 透過 WebSocket Channel 傳至 EPW ， EPW 再將發票 JSON 轉譯為 ESC/POS 指令，\
再送至系統 OS 所控管的 Thermal ESC/POS Printer ，由 Printer 印出發票證明聯。

當 TEA 要上傳發票至 EI 大平台時，會使用 HTTP POST 傳送批次編號資料至 TKW 的 Api Endpoint ，\
成功後，再以 HTTP POST 傳送批次編號相關所有發票的 JSON ，\
該批次編號發票傳送完畢後， TKW 會將發票 JSON 轉成 MIG 標準的 xml ，\
存入本地端的 Turnkey 系統，再由 Turnkey 系統處理與 EI 大平台的發票上傳作業。

TEA 資料設定
-------------------------------------------------------------------------------

1. 創建「統編(legalentity)」紀錄
#. 創建「賣家(seller)」紀錄
#. 創建「Turnkey 服務(turnkeyservice)」紀錄:
    * name
    * note
    * seller
    * transport_id: EI 提供
    * party_id: EI 提供
    * routing_id: EI 提供
    * hash_key: 可自動隨機產生
    * qrcode_seed: 須透過 turnkey 程式>工具>守門員>QRCode驗證 來產生
    * turnkey_seed: 須透過 turnkey 程式>工具>守門員>QRCode驗證 來產生
    * download_seed: 須透過 turnkey 程式>工具>守門員>QRCode驗證 來產生
    * epl_base_set: 預設值是 GHIJKLMNOPQRSTUVWXYZ ，用來驗證「電子發票證明聯列印序號」用的字元集合，建議使用「大寫英文、符號」並打亂順序
    * auto_upload_c0401_einvoice: True/False ; if True, then it upload B2C certificate invoices at upload_cronjob_format time 
    * upload_cronjob_format: 5, 10, 15, 20, 30, 60; 5 => "\*/5 \* \* \* \*"(cron format)
#. 創建「發票機(escposweb)」紀錄:
    * name: 建議包含發票機外形、地點、特徵
    * slug: 可自動隨機產生
    * hash_key: 可自動隨機產生

EPW 資料設定
-------------------------------------------------------------------------------

.. note::

    EPW 安裝部份，請見: :doc:`./install_epw_in_pi` 。

1. 套用 TEA 的 escposweb 紀錄來新增 EPW 中的 TEAWeb 紀錄，需要資料有:
    * escpos_web uri ，如: wss://<CEC or TEA url>/ws/taiwan_einvoice/escpos_web/<turnkeyservice id>/
    * slug ，如: BB737
    * hash_key ，如: 5817f0172c9482605d16386a263a7296de8b22f8
#. 更新 EPW 中的 Printer 紀錄，當 USB printer 開機並連線到 EPW 後，系統就會自動抓取 serial_number, type, vendor_number, product_name, profile ，後 3 者是在 python-escpos 函式庫有支援下，才能正確讀取。需要手動更新的，只有 3 個欄位:
    * nickname: 建議在列表機外殼，標記代號，並將此代號紀錄至本欄位
    * receipt_type: 選項有 0, 5, 6, 8 。意義分別是 0 表不能使用、 5 表 58mm 收據、 6 表 58mm 電子發票、 8 表 80mm 收據
    * default_encoding: 選項有 B, G 。為印表機內置的編碼表設定，其中 B 表 CP950 、 G 表 GB18030 編碼表
#. 若 TEAWeb 紀錄設定超過 1 個，那建議額外設定 EPW Portal

TKW 資料設定
-------------------------------------------------------------------------------

.. note::

    TKW 安裝部份，請見: :doc:`./install_tkw_in_linux` 。

1. 將 TKW 中的 EITurnkey Api Endpoint 登記到 CEC 中，類似 SNS subscribe 模式，先瀏覽 https://<tkw url>/turnkey_wrapper/api/v1/eiturnkey/ ，再使用 HTTP POST 新增 EITurnkey 紀錄，輸入欄位有:
    * execute_abspath: 以 / 開頭的本地端路徑來指出 EINVTurnkey 程式的 einvTurnkey.sct 的資料夾所在
    * data_abspath: 放置 Data 的資料夾所在
    * transport_id: 對應 turnkeyservice 紀錄
    * party_id: 對應 turnkeyservice 紀錄
    * routing_id: 對應 turnkeyservice 紀錄
    * hash_key: 對應 turnkeyservice 紀錄
    * tea_turnkey_service_endpoint ，如: https://<CEC or TEA url>/taiwan_einvoice/api/v1/turnkeyservice/<turnkeyservice id>/
    * endpoint: 無需填寫， POST 後由 TKW 自動計算
    * allow_ips: 若要使用 TKW Portal 功能，才需填寫

TEA supports ASGI with daphne, supervisor and nginx
-------------------------------------------------------------------------------

.. code-block:: sh

    $ sudo apt install nginx supervisor
    $ sudo mkdir /run/daphne/
    $ sudo chown jenkins:jenkins /run/daphne/ # I use jenkins user to execute app
    $ cat << 'EOF' > /usr/lib/tmpfiles.d/daphne.conf
    d /run/daphne 0755 jenkins jenkins
    EOF

.. code-block:: text

    #/etc/supervisor/conf.d/my-site.com.conf
    [fcgi-program:my_site]
    # TCP socket used by Nginx backend upstream
    socket=tcp://localhost:8001

    # Directory where your site's project files are located
    directory=/var/www/my-site.com

    # Each process needs to have a separate socket file, so we use process_num
    # Make sure to update "mysite.asgi" to match your project name
    command=/var/www/my-site.com-py3-env/bin/daphne -u /run/daphne/daphne%(process_num)d.sock --fd 0 --access-log - --proxy-headers my_site.asgi:application

    # Number of processes to startup, roughly the number of CPUs you have
    numprocs=4

    # Give each process a unique name so they can be told apart
    process_name=asgi%(process_num)d

    # Automatically start and recover processes
    autostart=true
    autorestart=true

    # Choose where you want your log to go
    stdout_logfile=/var/www/my-site.com.asgi.log
    redirect_stderr=true

.. code-block:: sh

    $ sudo supervisorctl reread
    $ sudo supervisorctl update

.. code-block:: text

    #/etc/nginx/site-enabled/my-site.conf
    server {
        server_name     www.my-site.com;
        access_log      /var/log/nginx/my-site.log;
        error_log       /var/log/nginx/my-site_error.log;

        listen          443 ssl;       # Listen on port 80 for IPv4 requests

        include         /native-nginx/conf.d/ssl.conf;
        ssl_certificate /native-nginx/certs/my-site.com/fullchain.pem; # managed by Certbot
        ssl_certificate_key /native-nginx/certs/my-site.com/privkey.pem; # managed by Certbot

        add_header      Content-Security-Policy "frame-ancestors 'self' hwww.my-site.com hwww.bio-pipe.com";

        location / {
            proxy_pass http://127.0.0.1:8001;
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection "upgrade";
            proxy_read_timeout 631;
            proxy_send_timeout 631;
            proxy_set_header    Host $host;
            proxy_set_header    X-Real-IP $remote_addr;
            proxy_set_header    X-Forwarded-For $remote_addr;
            proxy_set_header    REMOTE_ADDR $remote_addr;
            proxy_set_header    HTTP_HOST $host;
        }
    }

.. code-block:: sh

    $ sudo nginx -t
    $ sudo systemctl restart nginx

