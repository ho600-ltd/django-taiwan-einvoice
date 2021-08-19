在 Linux 安裝 Turnkey 及 DTE 伺服器
===============================================================================

下載點: https://www.einvoice.nat.gov.tw/EINSM/ein_upload/html/ENV/1536133205094.html

最低需求: 

1. 僅支援 Ubuntu 10.4 以上，Redhat ES 5.4 以上，支援 32、64 位元版本
#. 需搭配 Xwindow 及中文字集包，以正常顯示中文
#. 請確認 OpenJDK 版本為 8

安裝建議:

1. EI 平台有限制 Turnkey 系統的來源 IP ，所以建議到雲端平台去建立 DTE 伺服器，本文中範例是運作在 AWS
#. Turnkey 須搭配 Xwindow ，所以建議使用「Amazon Linux 2 with .Net Core, PowerShell, Mono, and MATE Desktop Environment」AMI，有 LTS 支援
#. 若需創建多台 Turnkey 系統(如: 不同分店各自擁有 Turnkey 系統)，建議安裝 OpenVPN 伺服器，並設定 NAT 模式

創建 PostgreSQL 資料庫:

.. code-block:: sql 

    # create database dte Encoding='UTF8' LC_Collate='zh_TW.UTF-8' LC_Ctype='zh_TW.UTF-8' template=template1;
    # create  user dte with password 'dte';
    # alter database dte owner to dte;

.. code-block:: sh 

    $ psql -h 127.0.0.1 -U dte -W dte < EINVTurnkey2.0.2-linux/DBSchema/PostgreSQL/PostgreSQL.sql

設定 Turnkey 所需基本參數:

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
