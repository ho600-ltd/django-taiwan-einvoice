營業人利用「Turnkey系統」開立 B2C 存證電子發票
===============================================================================

本文閱讀對象只針對「營業人」，其他的一般組織、團體、政府機關的角色並不適用。

線上申請 TURNKEY傳輸
    * 提供 2 個固定 IP ， 1 個供正式環境，另 1 個供測試環境
    * 通過後，即可到 https://wwwtest.einvoice.nat.gov.tw/ 使用工商憑證開通「營業人」用之 admin 帳號
    * 開放「營業人B2C發票作業/存證資料查詢-B2C及異常發票處理作業、電子發票專用字軌號碼取號/電子發票專用字軌號碼取號(營業人)、基本資料/發票號碼設定」權限給 developer
    * 以 admin 帳號登入 https://wwwtest.einvoice.nat.gov.tw/ ，上傳軟體憑證(.cer)，而軟體憑證私錀(.key)置入 Turnkey 系統。
      軟體憑證製作方式請參考「財政部電子發票整合服務平台的申請軟體憑證使用手冊」
    * 設定三種密碼種子: QRcode, turnkey, 下載清冊。先參照「加解密API使用說明書」來製作密碼種子 Hex (ex: 密碼種子是 24634102 ，則密碼種子 Hex 是 FE05F029154F6AA67A78B338ED2F6601 ):
        * 密碼種子 Hex 的製作:
            .. code-block:: sh

                $ ./genKey.sh  

                ===Enter [q] to exit program===
                Enter passphrase: 24634102
                [2021/08/26 16:33:26][INFO][][]  - begin gen key...
                [2021/08/26 16:33:26][INFO][][]  - end gen key...(OK)
                [2021/08/26 16:33:26][INFO][][]  - com.tradevan.geinv.kms.dist.DistKMSService begin init...
                [2021/08/26 16:33:26][INFO][][]  - com.tradevan.geinv.kms.dist.DistKMSService begin init...(OK)
                Result(Hex)==>FE05F029154F6AA67A78B338ED2F6601
        * 使用密碼種子 Hex 作 AES 加密:
            .. code-block:: sh

                $ python3 assets/qrcode_aes_encrypt.py FE05F029154F6AA67A78B338ED2F6601 XF000012349876
                CamotDNRUN8bVyY5S1BhFQ==

.. note::

    在使用 Turnkey 傳輸時，因為有綁定 IP ，原本有測試看能不能用 https, ssl proxy 方式來讓 Turnkey 裝在公司內部網路，\
    但使用 AWS 上的 https, ssl proxies 作轉換。其中測試 ssh 部份的參數如下:

        # ~/.ssh/config

        Host tsftp.einvoice.nat.gov.tw

        Ciphers 3des-cbc

        KexAlgorithms diffie-hellman-group1-sha1

        $ sftp -P 2222 -o "ProxyCommand /usr/bin/nc -X connect -x $ProxyHost:$ProxyPort %h %p" $account@tsftp.einvoice.nat.gov.tw

    但 Turnkey 的 Java 程式並未特別作使用 Proxy 設定，且有些動作可能不只使用了 tsftp.einvoice.nat.gov.tw, tgw.einvoice.nat.gov.tw 網址，\
    結果並不成功。

    最終方案是將 Turnkey 裝在 AWS 中，並為它套上 Web API ，這樣電商系統可利用 Web API 去通知 Turnkey 上傳/下載發票資訊，\
    無須與 Turnkey 系統安裝在同一台伺服器中。

