導入財政部電子發票服務之文件集
===============================================================================

.. note::

    本文件集中所提及、引用、截取的文句、畫面多來自 \
    `財政部電子發票整合服務平台(https://www.einvoice.nat.gov.tw/) <https://www.einvoice.nat.gov.tw/>`_、\
    `財政部北區國稅局(https://www.ntbna.gov.tw/) <https://www.ntbna.gov.tw/>`_。\
    其著作權之合理使用，\
    請詳見其平台之「`著作權保護政策 <https://www.einvoice.nat.gov.tw/index!showCopyRights>`_」\
    及「`政府網站資料開放宣告 <https://www.ntbna.gov.tw/singlehtml/18025799a2014c6e8be6f305f2e474ca>`_」網頁。

.. warning::

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
                rel="dct:type">Django-taiwan-einvoice.readthedocs.io</span>
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

* (完成)協助消費者在整合平台設定發票載具
* (撰寫中)協助營業人在整合服務平台上，開立、作廢、開立折讓、作廢折讓、退回 B2B 電子發票
* (撰寫中)協助營業人透過 **Linux** 版的 Turnkey-3+ 系統存證開立、作廢、註銷、開立折讓、作廢折讓 B2C 電子發票。所使用版本:
    * Turnkey 軟體版本: **3.0.2**
    * 電子發票資料交換標準訊息建置指引(Message Implementation Guideline)版本: **3.2.1**
* (撰寫中)協助營業人利用 Django-taiwan-einvoice app 為 Turnkey 系統提供 Web API 服務
* (待續)協助營業人透過加值服務中心完成電子發票相關服務
* (待續)「查詢電子發票API」教學

.. note:: 名詞釋疑

    所謂 B2B 、 B2C ，並不完全套用以字面上的 Business 及 Customer 。\
    因為 B2B 發票可以開給機關、組織，而 B2C 發票也可以開給一般營利公司。

    我這邊提供比較適當的解釋， B 是法人、準法人(商業行號)， C 則是除自然人外，也包含法人、準法人。\
    所以 B2B 一定是買賣雙方都有統編方可使用的服務，而 B2C 則是買方可以是自然人(無統編)也可以是法人、準法人。

名詞定義
-------------------------------------------------------------------------------

* EI: 財政部電子發票整合服務平台，也稱「大平台」
* EPW: 使用 Django-based escpos_web App 建構的發票列印管理系統。 EPW 系統加上感熱式印表機可簡稱「發票機」
* TKW: 使用 Django-based turnkey_web 程式來擴充 Turnkey 系統，使其提供 Web Api 功能的電子發票管理系統
* CEC: 叫用 EPW 及 TKW 系統的自架電子商務銷售系統(Customize E-Commercial system)，也可稱「小平台」
* TEA: 提供 CEC 系統叫用的 Django-based taiwan_einvoice App 。
  如果說 CEC 是 CPython 撰寫的，那 CEC 就直接利用 TEA 函式庫去跟 EPW/TKW 互動，若 CEC 是 PHP/.Net/Java/... 撰寫的，
  那就先叫用導入(import) TEA 的 Web Api Service (TEAWEB 或 taiwan_einvoice_web)，間接與 EPW/TKW 互動

使用 EI 大平台開立 B2B 電子發票的事前準備說明
-------------------------------------------------------------------------------

1. **測試用** 財政部電子發票整合服務平台:
   `營業人身份(https://wwwtest.einvoice.nat.gov.tw/index!changeFocusType?newFocus=F1348636625449)
   <https://wwwtest.einvoice.nat.gov.tw/index!changeFocusType?newFocus=F1348636625449>`_ 頁面
#. **正式用** 財政部電子發票整合服務平台:
   `營業人身份(https://www.einvoice.nat.gov.tw/index!changeFocusType?newFocus=F1348636625449)
   <https://www.einvoice.nat.gov.tw/index!changeFocusType?newFocus=F1348636625449>`_ 頁面
#. 效期內的實體憑證，依身份別來申辦:
    #. 「工商憑證」 - 一般營利事業單位用，申請網站請到 `MOEACA <https://moeaca.nat.gov.tw/>`_
    #. 「XCA 憑證」 - 一般組織、團體單位用，申請網站請到 `XCA <https://xca.nat.gov.tw/>`_
    #. 「GCA 憑證」 - 一般政府機關單位用，申請網站請到 `GCA <https://gca.nat.gov.tw/>`_
    #. 「自然人憑證」 - 一般正常人用，請親自到 **任一** 戶政事務所辦理，說明在
       `此 <https://moica.nat.gov.tw/rac.html>`_
#. 使用實體憑證前，可至 `經濟部工商憑證管理中心的瀏覽器檢測
   <https://moeacaweb.nat.gov.tw/MoeaeeWeb/other/checker.aspx>`_ 頁面驗證相關元件
#. 電子發票字軌號碼申請書(含電子發票開立系統自行檢測表) - 位於 EI 大平台/營業人文件下載頁面
#. 使用電子發票承諾書 - 此文件與「電子發票字軌號碼申請書(含電子發票開立系統自行檢測表)」是放在同一個壓縮檔中

自建 Turnkey-3+ 來開立 B2C 電子發票的事前準備說明
-------------------------------------------------------------------------------

1. 實體憑證註冊 EI 大平台帳號
#. 線上申請 Turnkey 正式區及驗證區: 申請網頁在 EI 大平台/Turnkey傳輸作業/Turnkey傳輸申請
#. 申辦軟體憑證。雖然 Turnkey 也接受以實體憑證來傳輸發票檔，但實體憑證插讀卡機在上容易衍生資安疑慮
#. 營業人應用 API 申請(捐贈碼、手機條 碼檢核及信用卡載具 等 API)
#. 電子發票Turnkey上線前自行檢測作業 - 須於測試環境完成Turnkey上線前自行檢測作業，確保發票傳輸的正確性

參考資料
-------------------------------------------------------------------------------

* `財政部電子發票整合服務平台 <https://www.einvoice.nat.gov.tw/>`_
    * 營業人
        * 財政部傳輸軟體(Turnkey)
            * 線上申請說明下載
            * 各項手冊與相關文件:
                * Turnkey-使用手冊_v3.2
            * Turnkey-3.0.2-linux
        * 文件下載
            * 營業人常用文件
                * 電子發票整合服務平台營業人導入與操作說明
                * 電子發票整合服務平台服務申請表
                * 電子發票營業人應用API(V1.7)
                * 軟體憑證製作手冊
                * 電子發票資料交換標準文件與範例(V3.2.1)
                * 電子發票Turnkey上線前自行檢測作業(V4.6)
                * 營業人比對上傳發票結果流程說明
                * 電子發票證明聯一維及二維條碼規格說明(V1.8)
                * 加解密API使用說明書(V1.12)
                * 電子發票QRCode加解密工具/營業人啟用第2層資訊防偽機制流程說明文件v20160817
                * 電子發票字軌號碼申請書(含電子發票開立系統自行檢測表)
* `財政部北區國稅局>主題專區>稅務專區>營業稅>電子發票專區 <https://www.ntbna.gov.tw/multiplehtml/724e140e325f497d82ba12d7509ec6ec>`_
    * 財政部財政資訊中心電子發票服務躍升計畫教育訓練-初級: `初級簡報 <https://www.ntbna.gov.tw/download/16a9f7f7937000009138a0f265d996cb>`_、`初級影片 <https://youtu.be/XuMKrTba-KI>`_
    * 財政部財政資訊中心電子發票服務躍升計畫教育訓練-中級: `中級簡報 <https://www.ntbna.gov.tw/download/16a9f7fca430000051f5a5d72c858058>`_、`中級影片 <https://youtu.be/SGrMUKy_LeM>`_
    * 財政部財政資訊中心電子發票服務躍升計畫教育訓練-高級: `高級簡報 <https://www.ntbca.gov.tw/registration/detail/e86d4d7cd08644c7a9733caefa1b4d59/bea437d010f6429abbb953dc2b59ab42>`_、`高級影片 <https://youtu.be/gs76_POvXGk>`_

.. toctree::
    :maxdepth: 4
    :caption: 目錄

    consumer_operations
    merchant_create_b2b_invoice
    merchant_operations
    b2c_invoice_brief
    create_software_certification
    EPW_TKW_TEA_brief
    install_epw_in_pi
    epw_user_manual
    install_tkw_in_linux
    merchant_create_b2c_invoice
    turnkey_download_E0501
    turnkey_download_E0504
    self_checklist_before_turnkey_online
    self_checklist_before_applying_track_no
    import_django_taiwan_einvoice
    check_point_and_sop
    agent
    inquire_api

.. toctree::
    :maxdepth: 1
    :caption: 版本修訂紀錄

    v0_changelog

文件撰寫中之待辦事項
-------------------------------------------------------------------------------

.. todolist::
