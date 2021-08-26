EPW / TKW / TE 架構
===============================================================================

TE 是一個 django-based 的 python app ，可直接以 Web Api 方式執行，或是導入至其他 django-based 的專案中。\
TE 支援 WebSocket 模式，當 EPW 系統開機後，會連線至 TE Web Api 或 CEC 中，由 TE 提供的 Web Api 。\
當 TE 有列印發票的指令，其包含的發票資料格式為 JSON ，會透過 WebSocket 傳至 EPW ， EPW 再將發票 JSON 轉譯為 esc 指令，\
再送至系統 OS 所控管的 thermal esc printer 。

當 TE 要上傳發票至 EI 大平台時，一樣先由 TKW 以 WebSocket 模式連線至 TE Web Api 或 CEC 中，由 TE 提供的 Web Api 。\
TE 以 WebSocket 模式傳送要上傳的發票 JSON 給 TKW ， TKW 會將發票 JSON 轉成 MIG 標準的 xml ，並存入 Turnkey 系統，\
由 Turnkey 系統負責與 EI 大平台的發票上傳作業。