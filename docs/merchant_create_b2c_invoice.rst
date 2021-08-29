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
        .. code-block:: sh

            $ ./genKey.sh  

            ===Enter [q] to exit program===
            Enter passphrase: 24634102
            [2021/08/26 16:33:26][INFO][][]  - begin gen key...
            [2021/08/26 16:33:26][INFO][][]  - end gen key...(OK)
            [2021/08/26 16:33:26][INFO][][]  - com.tradevan.geinv.kms.dist.DistKMSService begin init...
            [2021/08/26 16:33:26][INFO][][]  - com.tradevan.geinv.kms.dist.DistKMSService begin init...(OK)
            Result(Hex)==>FE05F029154F6AA67A78B338ED2F6601
        * 密碼種子 Hex 的驗證:
            .. code-block:: sh

            $ 
.. todo::

    把 https://gist.github.com/WJWang/1855ce92c2b1bac1313e1d1484297926 轉成 Python 版

.. code-block:: sh

    # ~/.ssh/config
    Host tsftp.einvoice.nat.gov.tw
        Ciphers 3des-cbc
        KexAlgorithms diffie-hellman-group1-sha1
    $ sftp -P 2222 -o "ProxyCommand /usr/bin/nc -X connect -x $ProxyHost:$ProxyPort %h %p" $account@tsftp.einvoice.nat.gov.tw
