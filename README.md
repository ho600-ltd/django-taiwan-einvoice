# django-taiwan-einvoice
[![Documentation Status](https://readthedocs.org/projects/django-taiwan-einvoice/badge/?version=latest)](https://django-taiwan-einvoice.readthedocs.io/zh_TW/latest/?badge=latest)

# 導入財政部電子發票服務之工具集暨文件集

本文件集中所提及、引用、截取的文句、畫面多來自 \
`財政部電子發票整合服務平台(https://www.einvoice.nat.gov.tw/) <https://www.einvoice.nat.gov.tw/>`_、\
`財政部北區國稅局(https://www.ntbna.gov.tw/) <https://www.ntbna.gov.tw/>`_。\
其著作權之合理使用，\
請詳見其平台之「`著作權保護政策 <https://www.einvoice.nat.gov.tw/index!showCopyRights>`_」\
及「`政府網站資料開放宣告 <https://www.ntbna.gov.tw/singlehtml/18025799a2014c6e8be6f305f2e474ca>`_」網頁。

本文件集乃基於忠實、客觀、利己且利他等原則寫作，
難免還是有錯字、過版、語意模糊、誤用等情事發生。
請利用人就自身風險擔負能力來利用本文件集，
**本文件集作者不擔保任何責任**。

若對本文件集有任何意見、建議或改正，
歡迎寄信到 <hoamon@ho600.com> 。

## 文件集之目標

* 協助消費者設定電子發票載具
* 協助營業人在大平台處理 B2B 電子發票相關作業(撰寫中)
* 協助營業人自建 Turnkey-3+ 來處理 B2C 電子發票相關作業(撰寫中)
* 協助營業人透過加值服務中心完成電子發票相關作業(待續)
* 「查詢電子發票API」教學(待續)

全文件集詳見 [https://django-taiwan-einvoice.readthedocs.io/](https://django-taiwan-einvoice.readthedocs.io/) 。

## 工具集之目標

* 基於 Turnkey-3+ 來建構 Web API 服務(所需資料庫僅支援 PostgreSQL/MySQL/MariaDB)
* 基於 MIG-3.2.1 來開立、作廢、註銷 B2C 電子發票
* 使用 Raspberry PI/Linux OS 透過感熱式印表機列印電子發票紙本證明聯

### 設定範例

...