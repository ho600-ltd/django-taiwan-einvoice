import pyotp, base64
from datetime import datetime
from math import floor



class CounterBasedOTPinRow(object):
    """ N_TIMES_IN_A_ROW means the otp sequence must match N times in a row.

        and it also means to allow the minute offset between generator and verifier.
    """
    N_TIMES_IN_A_ROW = 0
    SECRET = ''
    def __init__(self, SECRET=b'0' * 40, N_TIMES_IN_A_ROW=3):
        self.SECRET = SECRET
        if N_TIMES_IN_A_ROW <= 0:
            raise Exception("N_TIMES_IN_A_ROW must be bigger than 0")
        self.N_TIMES_IN_A_ROW = N_TIMES_IN_A_ROW
        self.hotp = pyotp.HOTP(base64.b32encode(self.SECRET))


    def generate_otps(self):
        iun = int(datetime.utcnow().strftime('%Y%m%d%H%M'))
        safe_period = self.N_TIMES_IN_A_ROW
        margin = floor(safe_period / 2)
        return [self.hotp.at(i) for i in range(iun - margin, iun + safe_period - margin)]
        

    def verify_otps(self, otps):
        iun = int(datetime.utcnow().strftime('%Y%m%d%H%M'))
        safe_period = self.N_TIMES_IN_A_ROW * 3
        margin = floor(safe_period / 2)
        _votps = [self.hotp.at(i) for i in range(iun - margin, iun + safe_period - margin)]

        if ','.join(otps) in ','.join(_votps):
            return _votps
        else:
            return None
        
