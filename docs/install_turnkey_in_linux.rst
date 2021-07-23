在 Linux 安裝 Turnkey-2.0.2
===============================================================================

下載點: https://www.einvoice.nat.gov.tw/EINSM/ein_upload/html/ENV/1536133205094.html

最低需求: 

1. 僅支援 Ubuntu 10.4 以上，Redhat ES 5.4 以上，支援 32、64 位元版本
#. 需搭配 Xwindow 及中文字集包，以正常顯示中文
#. 請確認 OpenJDK 版本為 8

創建資料庫:

.. code-block:: sql 

    # create database dte Encoding='UTF8' LC_Collate='zh_TW.UTF-8' LC_Ctype='zh_TW.UTF-8' template=template1;
    # create  user dte with password 'dte';
    # alter database dte owner to dte;

.. code-block:: sh 

    $ psql -h 127.0.0.1 -U dte -W dte < EINVTurnkey2.0.2-linux/DBSchema/PostgreSQL/PostgreSQL.sql

設定 Turnkey 所需參數:

.. code-block:: sh

    $ cd ${SOME_WHERE}/EINVTurnkey2.0.2-linux/linux
    $ ./runFirst.sct

.. figure:: install_turnkey_in_linux/run_first.png

    設定資料庫、工作目錄

執行 Turnkey:

.. code-block:: sh

    $ ./einvTurnkey.sct

.. figure:: install_turnkey_in_linux/einv_turnkey.png

    更新中

成功執行後，可見:

.. figure:: install_turnkey_in_linux/turnkey_ui.png

    Turnkey UI


自動配發字軌、自動配號、手動取號

傳統發票:

* 手開二聯
* 手開三聯
* 收銀機二聯
* 收銀機三聯
* 電子計算機。在 2021 年 1 月 1 日正式停用

發票狀態:

* 開立
* 作廢
* 折讓
* 退回
* 註銷(僅供存證發票使用，且註銷後必然跟著開立)

何時作廢、何時折讓:當期發票用作廢，跨期用折讓

非加值型營業稅法: 農產品經銷、證券業