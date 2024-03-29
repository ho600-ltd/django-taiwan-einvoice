申請及製作軟體憑證供 Turnkey 正式區、測試區使用
===============================================================================

電子發票使用 Turnkey 上傳時，需使用憑證加簽，若 Turnkey 系統是安裝在個人電腦上，\
則發票在上傳 EI (大平台)前，可透過讀卡機插入「各式實體憑證: 工商憑證、自然人憑證、…」來加簽電子發票 XML 檔。

若不希望長時間將實體憑證插在讀卡機上，又或是 Turnkey 系統是安裝在遠端伺服器上，\
那就建議使用軟體憑證來完成發票加簽作業。

申請「有效」的軟體憑證，請到「非IC申請網址: https://moeacaweb.nat.gov.tw/MoeaeeWeb/apply/apply_3.aspx 」，\
每張有效軟體憑證的效期為 5 年。此有效軟體憑證可同時用在大平台的正式區及測試區。

首先確認已有使用 Turnkey 系統生成 XXX.csr 請求檔(可參考「軟體憑證製作手冊」來製作 XXX.csr)，以及手邊有工商憑證正卡或附卡。

.. figure:: create_software_certification/01.png

    點擊「線上填寫申請資料」

.. figure:: create_software_certification/02.png

    點擊「我同意條款內容」
    
.. figure:: create_software_certification/03.png

    選擇「非IC卡申請」，類別則依實際情況來選擇。點擊「下一頁」後會讀取所插入工商憑證中的統一編號資訊

.. figure:: create_software_certification/04.png

    確認統一編號

.. figure:: create_software_certification/05.png

    確認公司相關資訊

.. figure:: create_software_certification/06.png

    填寫聯絡人各項資料

.. figure:: create_software_certification/07.png

    自定用戶代碼，並選擇 XXX.csr 檔

.. figure:: create_software_certification/08.png

    備份「用戶代碼」

.. figure:: create_software_certification/09.png

    確認資料後，前往付費系統

.. figure:: create_software_certification/10.png

    輸入「用戶代碼」

.. figure:: create_software_certification/11.png

    選擇付費方式

.. figure:: create_software_certification/12.png

    填寫此筆繳費發票的買受人資訊

.. figure:: create_software_certification/13.png

    再次確認付費方式

.. figure:: create_software_certification/14.png

    此為信用卡繳費的頁面

.. figure:: create_software_certification/15.png

    信用卡繳費成功

.. figure:: create_software_certification/16.png

    點擊「列印申請書及郵寄信封地址條」連結

.. figure:: create_software_certification/17.png

    再次輸入「用戶代碼」

.. figure:: create_software_certification/18.png

    直接列印或先下載 PDF 再列印

最後，將此紙本申請書蓋上公司大、小章後，即可掛號郵寄到經濟部中部辦公室。

大約 1 星期後，程序無誤即會發出軟體憑證(yyy.cer)，再自行到 `經濟部工商憑證管理中心/下載專區(https://moeaca.nat.gov.tw/download/download_4.html) <https://moeaca.nat.gov.tw/download/download_4.html>`_ 的「憑證查詢及下載」頁面下載軟體憑證。再將此軟體憑證上傳至大平台。

.. figure:: create_software_certification/cer-01.png

    先到「營業人功能選單」/「基本資料」/「軟體憑證資料登錄作業」頁面，選擇剛剛下載的軟體憑證(yyy.cer)，按下「登錄軟體憑證」

.. figure:: create_software_certification/cer-02.png

    確認「憑證內容」無誤後，按下「確認登錄」

登錄成功後， Turnkey 方能上傳發票 MIG XML，若是未完成這個「軟體憑證登錄作業」，則上傳發票 MIG XML 後，會拿到 E0310(66803) 錯誤。