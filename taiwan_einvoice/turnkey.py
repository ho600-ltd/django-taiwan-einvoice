class TurnkeyReturnCode(object):
    _ERRORS = {
        "00000": ["", ""],
        "00000": ["訊息存證成功", "訊息存證成功"],
        "E0001": ["系統錯誤", "中心端系統發生錯誤,請與客服人員聯絡"],
        "E0002": ["資料庫存取失敗(系統)", "中心端存取資料庫時發生錯誤,請與客服人員聯絡"],
        "E0003": ["交易 LOG Table 失敗", "中心端進行記錄動作時發生錯誤,請與客服人員聯絡"],
        "E0004": ["驗章失敗(系統)", "中心端進行驗章時發生錯誤,請與客服人員聯絡"],
        "E0005": ["MQ 存取失敗", "中心端存取 MQ 時發生錯誤,請與客服人員聯絡"],
        "E0007": ["DES 加密資料失敗", "中心端進行加簽時發生錯誤,請與客服人員聯絡"],

        "E0201": ["No. $筆數 Inovice Validate Fail. 訊息重複", "該筆訊息已被處理過,請確認發票內容是否正確"],
        "E1003": ["B2C 發票重覆開立", "B2C 發票重覆開立,請確認發票內容是否正確"],
    }


    def __init__(self, return_code):
        self.return_code = return_code
        self.message, self.solution = self._ERRORS.get(return_code, ["未紀錄", "未載明"])


class TurnkeyWebReturnCode(object):
    _ERRORS = {
        "0": ["成功"],
        "001": ["儲存 EITurnkeyBatch 失敗"],
        "002": ["解析 gz_bodys 失敗"],
        "003": ["解析 batch_einvoice_begin_time 或 batch_einvoice_begin_time 失敗"],
        "004": ["儲存 EITurnkeyBatchEInvoice 失敗"],
        "005": ["EITurnkeyBatchEInvoice 已有開立紀錄"],
        "999": ["未知失敗"],
    }
    


    def __init__(self, return_code):
        self.return_code = return_code
        self.message = self._ERRORS.get(return_code, self._ERRORS["999"])[0]