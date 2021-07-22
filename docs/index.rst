導入財政部電子發票服務之文件集
===============================================================================

.. note::

    本文件集中所提及、引用、截取的文句、畫面多來自 \
    `https://www.einvoice.nat.gov.tw/ <https://www.einvoice.nat.gov.tw/>`_ 。\
    其著作權之合理使用，\
    請詳見該平台之「 `著作權保護政策 <https://www.einvoice.nat.gov.tw/index!showCopyRights>`_ 」一文。

.. note::

    本文件集乃基於忠實、客觀、利己且利他等原則寫作，\
    難免還是有錯字、過版、語意模糊、誤用等情事發生。\
    請利用人就自身風險擔負能力來利用本文件集，本文件集作者不擔保任何責任。

    若對本文件集有任何意見、建議或改正，\
    歡迎寄信到 `hoamon@ho600.com <hoamon@ho600.com>`_ 。

本文件集之著作權公開授權模式
-------------------------------------------------------------------------------

.. raw:: html

    <div class="widget" id="license">
        <div style="text-align: left;">
            <a href="http://creativecommons.org/licenses/by-sa/3.0/tw/" rel="license">
                <img alt="Creative Commons License" style="border-width:0"
                src="http://i.creativecommons.org/l/by-sa/3.0/tw/88x31.png">
            </a>
        </div>
        <span href="http://purl.org/dc/dcmitype/Text" rel="dct:type">
            <span href="http://purl.org/dc/dcmitype/Text"
                rel="dct:type">django-taiwan-einvoice.readthedocs.io</span>
                網站內容為 <a href="https://www.ho600.info/" rel="cc:attributionURL">ho600 Ltd.</a> 所創作，
                除非另有說明，否則皆採用
                <a href="http://creativecommons.org/licenses/by-sa/3.0/tw/"
                rel="license">創用 CC 姓名標示-相同方式分享 3.0 台灣 授權條款</a>授權。
        </span>
    </div>
    <br/>
    <br/>

本文件集之目標
-------------------------------------------------------------------------------

* 協助消費者設定發票載具 (完成)
* 協助營業人自行生成、上傳、作廢電子發票，包含 B2B, B2C 類型 (撰寫中)
* 協助營業人透過加值服務中心完成電子發票相關服務 (待續)
* 「查詢電子發票API」教學 (待續)

事前準備說明
-------------------------------------------------------------------------------

1. **測試用** 財政部電子發票整合服務平台: `營業人身份(https://wwwtest.einvoice.nat.gov.tw/index!changeFocusType?newFocus=F1348636625449) <https://wwwtest.einvoice.nat.gov.tw/index!changeFocusType?newFocus=F1348636625449>`_ 頁面
#. **正式用** 財政部電子發票整合服務平台: `營業人身份(https://www.einvoice.nat.gov.tw/index!changeFocusType?newFocus=F1348636625449) <https://www.einvoice.nat.gov.tw/index!changeFocusType?newFocus=F1348636625449>`_ 頁面
#. 效期內的「工商憑證」 - 一般營利事業單位用，申請網站請到 `MOEACA <https://moeaca.nat.gov.tw/>`_
#. 效期內的「XCA 憑證」 - 一般組織、團體單位用，申請網站請到 `XCA <https://xca.nat.gov.tw/>`_
#. 效期內的「GCA 憑證」 - 一般政府機關單位用，申請網站請到 `GCA <https://gca.nat.gov.tw/>`_
#. 效期內的「自然人憑證」 - 一般正常人用，請親自到 **任一** 戶政事務所辦理，說明在 `此 <https://moica.nat.gov.tw/rac.html>`_
#. 使用憑證前，可至 `經濟部工商憑證管理中心的瀏覽器檢測 <https://moeacaweb.nat.gov.tw/MoeaeeWeb/other/checker.aspx>`_ 頁面驗證相關元件
#. 電子發票字軌號碼申請書(含電子發票開立系統自行檢測表) - `下載連結 <https://www.etax.nat.gov.tw/etwmain/front/ETW118W/CON/441/6304811861295645753>`_
#. 使用電子發票承諾書 - 本文件與「電子發票字軌號碼申請書(含電子發票開立系統自行檢測表)」是放在同一個壓縮檔中

參考文件
-------------------------------------------------------------------------------

* `財政部電子發票整合服務平台 <https://www.einvoice.nat.gov.tw/>`_
    * 營業人
        * 財政部傳輸軟體(Turnkey)
            * 線上申請說明下載
            * 電子發票Turnkey上線前自行檢測作業
            * 各項手冊與相關文件:
                * Turnkey-使用手冊_v2.9
                * 電子發票 PostgreSQL資料庫安裝參考說明
            * Turnkey-2.0.2-linux
        * 文件下載
            * 營業人常用文件
                * 電子發票整合服務平台營業人導入與操作說明


.. toctree::
    :maxdepth: 4
    :caption: 目錄

    consumer_operations
    merchant_create_b2b_invoice
    install_turnkey_in_linux
    merchant_create_b2c_invoice
    merchant_operations
    agent
    inquire_api

.. toctree::
    :maxdepth: 1
    :caption: 版本修訂紀錄

    v0_changelog

文件撰寫中之待辦事項
-------------------------------------------------------------------------------

.. todolist::