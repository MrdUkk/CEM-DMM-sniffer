# AI-assisted handmade conversion with corrections from 'Meterbox IMM' DT99Sprotocal.java to Python
# mising obtaining Ref value in dbM dbV mode AC-measurement (displayed on screen but not seen in packets)
# (c) its original authors for a DT99Sprotocal.java
# (c) dUkk 2026 https://blog.softdev.online for a dt99s_proto.py


import struct
from datetime import datetime, timedelta

class DT99Sprotocol:
    # Constants
    MEASURE_CURRENT = 1
    MEASURE_MAXMIN = 2
    MEASURE_REL = 3
    MEASURE_PEAK = 4
    MEASURE_DCAC = 5
    MEASURE_ACDB = 6
    MEASURE_HZ = 7
    MEASURE_OSC = 8
    MEASURE_LOGMSG = 9
    MEASURE_LOGDATA = 10

    # Static fields
    logstarttime = ""
    measuretype = 0

    arrayfun = [
        "Temperature", "VAC", "VDC", "mVDC", "RES", "CAP", "Temperature",
        "ADC", "mADC", "uADC", "4-20mA", "mVAC", "AAC", "mAAC", "uAAC",
        "Diode", "HZ", "VAC", "", "", "", "DC+AC(V)", "DC+AC(mV)",
        "DC+AC(A)", "DC+AC(mA)", "DC+AC(uA)"
    ]

    arrayunit = [
        "°F", "VAC", "VDC", "mVDC", "RES", "CAP", "°C",
        "ADC", "mADC", "uADC", "", "mVAC", "AAC", "mAAC", "uAAC",
        "V", "HZ", "VAC", "", "", "", "V", "mV", "A", "mA", "uA"
    ]

    logdatalist = []
    logtimelist = []
    Time = ""
    OscilloscopeStatus = ""
    page = 0
    Vp_p = ""
    Vpp = ""
    Frequency = ""
    SamplingRate = ""
    TriggerIco = 0
    SpeedSign = ""
    maindata = [0.0] * 300
    FFTdata = [0.0] * 120
    Fret = [""] * 120

    DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

    def __init__(self, databuf, measuretype):
        self.databuf = list(databuf)
        self.measuretype = measuretype

        # Instance fields
        self.averagesign = ""
        self.flag_bai = False
        self.flag_cf = False
        self.flag_diodesign = False
        self.flag_line = False
        self.flag_lo = False
        self.flag_part = False
        self.logdatanum = 0
        self.logpacketnum = 0
        self.logrectime = 0
        self.logsamprate = 0
        self.m_acdcvalue = 0.0
        self.m_acvalue = 0.0
        self.m_avgvalue = 0.0
        self.m_coef = 0.0
        self.m_coefavg = 0.0
        self.m_coefmax = 0.0
        self.m_coefmin = 0.0
        self.m_dbvalue = 0.0
        self.m_dcvalue = 0.0
        self.m_hzvalue = 0.0
        self.m_mainvalue = 0.0
        self.m_maxvalue = 0.0
        self.m_minvalue = 0.0
        self.m_range = 0.0
        self.m_refvalue = 0.0
        self.m_relvalue = 0.0
        self.maximumsign = ""
        self.minimumsign = ""
        self.point = 0
        self.pointavg = 0
        self.pointmax = 0
        self.pointmin = 0
        self.startrectime = ""
        self.stracdcsign = ""
        self.stracunit = ""
        self.stracvalue = ""
        self.strautosign = ""
        self.stravgtime = ""
        self.stravgunit = ""
        self.stravgvalue = ""
        self.strdatavalue = ""
        self.strdbunit = ""
        self.strdbvalue = ""
        self.strfun = ""
        self.strholdsign = ""
        self.strhzunit = ""
        self.strhzvalue = ""
        self.strmaxminsign = ""
        self.strmaxtime = ""
        self.strmaxunit = ""
        self.strmaxvalue = ""
        self.strmintime = ""
        self.strminunit = ""
        self.strminvalue = ""
        self.strpeaksign = ""
        self.strrefsign = ""
        self.strrefvalue = ""
        self.strrelsign = ""
        self.strrelunit = ""
        self.strrelvalue = ""
        self.strunit = ""

    def ProcessPacket(self):
        match self.measuretype:
            case DT99Sprotocol.MEASURE_CURRENT:
                self.AnalyzeCurrentData()
            case DT99Sprotocol.MEASURE_MAXMIN:
                self.AnalyzeMaxminData()
            case DT99Sprotocol.MEASURE_REL:
                self.AnalyzeRelData()
            case DT99Sprotocol.MEASURE_PEAK:
                self.AnalyzePeakData()
            case DT99Sprotocol.MEASURE_DCAC:
                self.AnalyzeDCACData()
            case DT99Sprotocol.MEASURE_ACDB:
                self.AnalyzeACDBData()
            case DT99Sprotocol.MEASURE_HZ:
                self.AnalyzeHZData()
            case DT99Sprotocol.MEASURE_OSC:
                self.AnalyzeOscData()
            case DT99Sprotocol.MEASURE_LOGMSG:
                self.AnalyzeLogMsg()
            case DT99Sprotocol.MEASURE_LOGDATA:
                self.AnalyzeLogData()

    def AnalyzeCurrentData(self):
        self.strfun = self.arrayfun[self.databuf[2]]

        if (self.databuf[3] & 1) != 0:
            self.strholdsign = "Hold"
        else:
            self.strholdsign = ""

        if (self.databuf[3] & 2) != 0:
            self.strautosign = "Manual Range"
        else:
            self.strautosign = "Auto Range"

        if (self.databuf[3] & 8) != 0:
            self.flag_lo = True
        else:
            self.flag_lo = False

        tempvalue = [0.0] * 2

        if self.strfun is not None and self.strfun == "4-20mA":
            values = [self.databuf[7], self.databuf[6], self.databuf[5], self.databuf[4]]
            values2 = [self.databuf[11], self.databuf[10], self.databuf[9], self.databuf[8]]
            value = self._int2byte(values)
            range_bytes = self._int2byte(values2)
            self._ByteToString(value)
            self._ByteToString(range_bytes)
            tempvalue[0] = self._ByteToFloat(value)
            tempvalue[1] = self._ByteToFloat(range_bytes)
        else:
            for i in range(2):
                b = bytes([
                    self.databuf[(i * 4) + 7] & 0xFF,
                    self.databuf[(i * 4) + 6] & 0xFF,
                    self.databuf[(i * 4) + 5] & 0xFF,
                    self.databuf[(i * 4) + 4] & 0xFF,
                ])
                tempvalue[i] = self._ByteToFloat(b)

        self.m_mainvalue = tempvalue[0]
        self.m_range = tempvalue[1]

        bytes2 = bytes([
            self.databuf[12] & 0xFF, self.databuf[13] & 0xFF,
            self.databuf[14] & 0xFF, self.databuf[15] & 0xFF,
        ])
        self.strunit = self._ByteToString(bytes2)
        self.strunit = self.strunit.strip()
        self.point = 5 - self.databuf[16]
        self.m_coef = 1.0
        self.CorrectUnitShow()
        self.m_mainvalue /= self.m_coef
        self.m_range /= self.m_coef

        if abs(self.m_mainvalue) > abs(self.m_range):
            self.strdatavalue = "OL"
        else:
            self.strdatavalue = self._FloatToString(self.m_mainvalue, self.point)

    def AnalyzeMaxminData(self):
        self.strmaxminsign = "Min Max"
        self.maximumsign = "Maximun"
        self.minimumsign = "Minimum"
        self.averagesign = "Average"
        self.strfun = self.arrayfun[self.databuf[2]]

        if (self.databuf[3] & 1) != 0:
            self.strholdsign = "Hold"
        else:
            self.strholdsign = ""

        if (self.databuf[3] & 4) != 0:
            self.flag_lo = True
        else:
            self.flag_lo = False

        tempvalue = [0.0] * 5
        for i in range(5):
            b = bytes([
                self.databuf[(i * 4) + 7] & 0xFF,
                self.databuf[(i * 4) + 6] & 0xFF,
                self.databuf[(i * 4) + 5] & 0xFF,
                self.databuf[(i * 4) + 4] & 0xFF,
            ])
            tempvalue[i] = self._ByteToFloat(b)

        self.m_mainvalue = tempvalue[0]
        self.m_maxvalue = tempvalue[1]
        self.m_minvalue = tempvalue[2]
        self.m_avgvalue = tempvalue[3]
        self.m_range = tempvalue[4]

        self.point = 5 - (self.databuf[24] & 3)
        self.pointmax = 5 - ((self.databuf[24] >> 2) & 3)
        self.pointmin = 5 - ((self.databuf[24] >> 4) & 3)
        self.pointavg = 5 - ((self.databuf[24] >> 6) & 3)

        self.m_coef = 1.0
        self.m_coefmax = 1.0
        self.m_coefmin = 1.0
        self.m_coefavg = 1.0

        tempstr = [""] * 4
        for i2 in range(4):
            b2 = bytes([
                self.databuf[(i2 * 4) + 25] & 0xFF,
                self.databuf[(i2 * 4) + 26] & 0xFF,
                self.databuf[(i2 * 4) + 27] & 0xFF,
                self.databuf[(i2 * 4) + 28] & 0xFF,
            ])
            tempstr[i2] = self._ByteToString(b2)
            tempstr[i2] = tempstr[i2].strip()

        self.strunit = tempstr[0]
        self.strmaxunit = tempstr[1]
        self.strminunit = tempstr[2]
        self.stravgunit = tempstr[3]

        self.CorrectUnitShow()
        self.m_mainvalue /= self.m_coef
        self.m_maxvalue /= self.m_coefmax
        self.m_minvalue /= self.m_coefmin
        self.m_avgvalue /= self.m_coefavg

        self.strmaxtime = "%02d:%02d:%02d" % (
            (self.databuf[41] // 16) * 10 + (self.databuf[41] % 16),
            (self.databuf[42] // 16) * 10 + (self.databuf[42] % 16),
            (self.databuf[43] // 16) * 10 + (self.databuf[43] % 16),
        )
        self.strmintime = "%02d:%02d:%02d" % (
            (self.databuf[44] // 16) * 10 + (self.databuf[44] % 16),
            (self.databuf[45] // 16) * 10 + (self.databuf[45] % 16),
            (self.databuf[46] // 16) * 10 + (self.databuf[46] % 16),
        )
        self.stravgtime = "%02d:%02d:%02d" % (
            (self.databuf[47] // 16) * 10 + (self.databuf[47] % 16),
            (self.databuf[48] // 16) * 10 + (self.databuf[48] % 16),
            (self.databuf[49] // 16) * 10 + (self.databuf[49] % 16),
        )
        self.startrectime = "%02d/%02d/%02d  %02d:%02d:%02d" % (
            (self.databuf[51] // 16) * 10 + (self.databuf[51] % 16),
            (self.databuf[52] // 16) * 10 + (self.databuf[52] % 16),
            (self.databuf[50] // 16) * 10 + (self.databuf[50] % 16),
            (self.databuf[53] // 16) * 10 + (self.databuf[53] % 16),
            (self.databuf[54] // 16) * 10 + (self.databuf[54] % 16),
            (self.databuf[55] // 16) * 10 + (self.databuf[55] % 16),
        )

        if abs(self.m_mainvalue) > abs(self.m_range):
            self.strdatavalue = "OL"
        else:
            self.strdatavalue = self._FloatToString(self.m_mainvalue, self.point)

        if abs(self.m_maxvalue) > abs(self.m_range):
            self.strmaxvalue = "OL"
        else:
            self.strmaxvalue = self._FloatToString(self.m_maxvalue, self.pointmax)

        if abs(self.m_minvalue) > abs(self.m_range):
            self.strminvalue = "OL"
        else:
            self.strminvalue = self._FloatToString(self.m_minvalue, self.pointmin)

        if abs(self.m_avgvalue) > abs(self.m_range):
            self.stravgvalue = "OL"
        else:
            self.stravgvalue = self._FloatToString(self.m_avgvalue, self.pointavg)

    def AnalyzeRelData(self):
        self.strfun = self.arrayfun[self.databuf[2]]

        if (self.databuf[3] & 1) != 0:
            self.strholdsign = "Hold"
        else:
            self.strholdsign = ""

        self.strautosign = "Manual Range"

        if (self.databuf[3] & 4) != 0:
            self.flag_bai = True
        else:
            self.flag_bai = False

        if (self.databuf[3] & 8) != 0:
            self.flag_lo = True
        else:
            self.flag_lo = False

        tempvalue = [0.0] * 4
        for i in range(4):
            b = bytes([
                self.databuf[(i * 4) + 7] & 0xFF,
                self.databuf[(i * 4) + 6] & 0xFF,
                self.databuf[(i * 4) + 5] & 0xFF,
                self.databuf[(i * 4) + 4] & 0xFF,
            ])
            tempvalue[i] = self._ByteToFloat(b)

        self.m_relvalue = tempvalue[0]
        self.m_refvalue = tempvalue[1]
        self.m_mainvalue = tempvalue[2]
        self.m_range = tempvalue[3]

        self.point = 5 - (self.databuf[24] & 3)

        bytes2 = bytes([
            self.databuf[20] & 0xFF, self.databuf[21] & 0xFF,
            self.databuf[22] & 0xFF, self.databuf[23] & 0xFF,
        ])
        self.strunit = self._ByteToString(bytes2)
        self.strunit = self.strunit.strip()

        self.m_coef = 1.0
        self.CorrectUnitShow()
        self.strrelunit = self.strunit
        self.strrefsign = "Reference"
        self.strrelsign = "REL"

        self.m_mainvalue /= self.m_coef
        self.m_refvalue /= self.m_coef
        self.m_relvalue /= self.m_coef
        self.m_range /= self.m_coef

        if abs(self.m_mainvalue) > abs(self.m_range):
            self.strdatavalue = "OL"
        else:
            self.strdatavalue = self._FloatToString(self.m_mainvalue, self.point)

        if abs(self.m_refvalue) > abs(self.m_range):
            self.strrefvalue = "OL"
        else:
            self.strrefvalue = self._FloatToString(self.m_refvalue, self.point)

        if abs(self.m_relvalue) > abs(self.m_range):
            self.strrelvalue = "OL"
        else:
            self.strrelvalue = self._FloatToString(self.m_relvalue, self.point)

        if self.flag_bai:
            self.strunit = "%"
            if -1.0e-9 <= self.m_refvalue <= 1.0e-9:
                self.m_mainvalue = 0.0
            else:
                self.m_mainvalue = (self.m_mainvalue / abs(self.m_refvalue)) * 100.0
            self.strdatavalue = self._FloatToString(self.m_mainvalue, 1)

    def AnalyzePeakData(self):
        self.strmaxminsign = "PEAK"
        self.maximumsign = "PeakMax"
        self.minimumsign = "PeakMin"
        self.averagesign = "Average"
        self.strfun = self.arrayfun[self.databuf[2]]

        if (self.databuf[3] & 1) != 0:
            self.strholdsign = "Hold"
        else:
            self.strholdsign = ""

        if (self.databuf[3] & 2) != 0:
            self.strautosign = "Manual Range"
        else:
            self.strautosign = "Auto Range"

        if (self.databuf[3] & 4) != 0:
            self.flag_cf = True
        else:
            self.flag_cf = False

        tempvalue = [0.0] * 5
        for i in range(5):
            b = bytes([
                self.databuf[(i * 4) + 7] & 0xFF,
                self.databuf[(i * 4) + 6] & 0xFF,
                self.databuf[(i * 4) + 5] & 0xFF,
                self.databuf[(i * 4) + 4] & 0xFF,
            ])
            tempvalue[i] = self._ByteToFloat(b)

        self.m_mainvalue = tempvalue[0]
        self.m_maxvalue = tempvalue[1]
        self.m_minvalue = tempvalue[2]
        self.m_avgvalue = tempvalue[3]
        self.m_range = tempvalue[4]

        self.point = 5 - (self.databuf[28] & 3)
        self.m_coef = 1.0

        bytes2 = bytes([
            self.databuf[24] & 0xFF, self.databuf[25] & 0xFF,
            self.databuf[26] & 0xFF, self.databuf[27] & 0xFF,
        ])
        self.strunit = self._ByteToString(bytes2)
        self.strunit = self.strunit.strip()
        self.strmaxunit = self.strunit
        self.strminunit = self.strunit
        self.stravgunit = self.strunit

        self.m_mainvalue /= self.m_coef
        self.m_maxvalue /= self.m_coef
        self.m_minvalue /= self.m_coef
        self.m_avgvalue /= self.m_coef

        self.strmaxtime = "%02d:%02d:%02d" % (
            (self.databuf[29] // 16) * 10 + (self.databuf[29] % 16),
            (self.databuf[30] // 16) * 10 + (self.databuf[30] % 16),
            (self.databuf[31] // 16) * 10 + (self.databuf[31] % 16),
        )
        self.strmintime = "%02d:%02d:%02d" % (
            (self.databuf[32] // 16) * 10 + (self.databuf[32] % 16),
            (self.databuf[33] // 16) * 10 + (self.databuf[33] % 16),
            (self.databuf[34] // 16) * 10 + (self.databuf[34] % 16),
        )
        self.stravgtime = "%02d:%02d:%02d" % (
            (self.databuf[35] // 16) * 10 + (self.databuf[35] % 16),
            (self.databuf[36] // 16) * 10 + (self.databuf[36] % 16),
            (self.databuf[37] // 16) * 10 + (self.databuf[37] % 16),
        )
        self.startrectime = "%02d/%02d/%02d  %02d:%02d:%02d" % (
            (self.databuf[39] // 16) * 10 + (self.databuf[39] % 16),
            (self.databuf[40] // 16) * 10 + (self.databuf[40] % 16),
            (self.databuf[38] // 16) * 10 + (self.databuf[38] % 16),
            (self.databuf[41] // 16) * 10 + (self.databuf[41] % 16),
            (self.databuf[42] // 16) * 10 + (self.databuf[42] % 16),
            (self.databuf[43] // 16) * 10 + (self.databuf[43] % 16),
        )

        if abs(self.m_mainvalue) > abs(self.m_range):
            self.strdatavalue = "OL"
        else:
            self.strdatavalue = self._FloatToString(self.m_mainvalue, self.point)

        if abs(self.m_maxvalue) > abs(self.m_range):
            self.strmaxvalue = "OL"
        else:
            self.strmaxvalue = self._FloatToString(self.m_maxvalue, self.point)

        if abs(self.m_minvalue) > abs(self.m_range):
            self.strminvalue = "OL"
        else:
            self.strminvalue = self._FloatToString(self.m_minvalue, self.point)

        if abs(self.m_avgvalue) > abs(self.m_range):
            self.stravgvalue = "OL"
        else:
            self.stravgvalue = self._FloatToString(self.m_avgvalue, self.point)

    def AnalyzeDCACData(self):
        self.strfun = self.arrayfun[self.databuf[2]]

        if (self.databuf[3] & 1) != 0:
            self.strholdsign = "Hold"
        else:
            self.strholdsign = ""

        if (self.databuf[3] & 2) != 0:
            self.strautosign = "Manual Range"
        else:
            self.strautosign = "Auto Range"

        tempvalue = [0.0] * 3
        for i in range(3):
            b = bytes([
                self.databuf[(i * 4) + 7] & 0xFF,
                self.databuf[(i * 4) + 6] & 0xFF,
                self.databuf[(i * 4) + 5] & 0xFF,
                self.databuf[(i * 4) + 4] & 0xFF,
            ])
            tempvalue[i] = self._ByteToFloat(b)

        self.m_dcvalue = tempvalue[0]
        self.m_acvalue = tempvalue[1]
        self.m_acdcvalue = tempvalue[2]

        bytes1 = bytes([
            self.databuf[23] & 0xFF, self.databuf[22] & 0xFF,
            self.databuf[21] & 0xFF, self.databuf[20] & 0xFF,
        ])
        self.m_range = self._ByteToFloat(bytes1)

        bytes2 = bytes([
            self.databuf[16] & 0xFF, self.databuf[17] & 0xFF,
            self.databuf[18] & 0xFF, self.databuf[19] & 0xFF,
        ])
        self.strunit = self._ByteToString(bytes2)
        self.strunit = self.strunit.strip()

        self.point = 5 - self.databuf[24]
        self.m_coef = 1.0

        if self.databuf[25] == 3:
            self.flag_part = True
        else:
            self.flag_part = False

        self.m_dcvalue /= self.m_coef
        self.m_acvalue /= self.m_coef
        self.m_acdcvalue /= self.m_coef
        self.m_range /= self.m_coef

        if self.flag_part:
            self.m_mainvalue = self.m_dcvalue
            if abs(self.m_acvalue) > abs(self.m_range):
                self.stracvalue = "OL"
            else:
                self.stracvalue = self._FloatToString(self.m_acvalue, self.point)
            tempunit = self.strunit
            self.strunit = tempunit + "DC"
            self.stracunit = tempunit + "AC"
        else:
            self.m_mainvalue = self.m_acdcvalue
            self.stracvalue = ""
            self.stracunit = ""
            if len(self.strunit) < 2:
                self.strunit = "     " + self.strunit
            else:
                self.strunit = " " + self.strunit
            self.stracdcsign = "AC+DC"

        if abs(self.m_mainvalue) > abs(self.m_range):
            self.strdatavalue = "OL"
        else:
            self.strdatavalue = self._FloatToString(self.m_mainvalue, self.point)

    def AnalyzeACDBData(self):
        self.strfun = "VAC+DB"

        if (self.databuf[2] & 1) != 0:
            self.strholdsign = "Hold"
        else:
            self.strholdsign = ""

        if (self.databuf[2] & 2) != 0:
            self.strautosign = "Manual Range"
        else:
            self.strautosign = "Auto Range"

        b = bytes([
            self.databuf[6] & 0xFF, self.databuf[5] & 0xFF,
            self.databuf[4] & 0xFF, self.databuf[3] & 0xFF,
        ])
        self.m_mainvalue = self._ByteToFloat(b)

        bytes1 = bytes([
            self.databuf[7] & 0xFF, self.databuf[8] & 0xFF,
            self.databuf[9] & 0xFF, self.databuf[10] & 0xFF,
        ])
        self.strunit = self._ByteToString(bytes1)
        self.strunit = self.strunit.strip()

        self.m_coef = 1.0
        self.point = 5 - self.databuf[11]

        bytes2 = bytes([
            self.databuf[15] & 0xFF, self.databuf[14] & 0xFF,
            self.databuf[13] & 0xFF, self.databuf[12] & 0xFF,
        ])
        self.m_range = self._ByteToFloat(bytes2)

        bytes3 = bytes([
            self.databuf[19] & 0xFF, self.databuf[18] & 0xFF,
            self.databuf[17] & 0xFF, self.databuf[16] & 0xFF,
        ])
        self.m_dbvalue = self._ByteToFloat(bytes3)

        bytes4 = bytes([
            self.databuf[20] & 0xFF, self.databuf[21] & 0xFF,
            self.databuf[22] & 0xFF, self.databuf[23] & 0xFF,
        ])
        self.strdbunit = self._ByteToString(bytes4)
        self.strdbunit = self.strdbunit.strip()
 
        if abs(self.m_mainvalue) > abs(self.m_range):
            self.strdatavalue = "OL"
        else:
            self.strdatavalue = self._FloatToString(self.m_mainvalue, self.point)

        if -1.0e-9 <= self.m_mainvalue <= 1.0e-9:
            self.strdbvalue = "OL"
        else:
            self.strdbvalue = self._FloatToString(self.m_dbvalue, 2)

    def AnalyzeHZData(self):
        self.strfun = "HZ"

        if (self.databuf[2] & 1) != 0:
            self.strholdsign = "Hold"
        else:
            self.strholdsign = ""

        if (self.databuf[2] & 2) != 0:
            self.strautosign = "Manual Range"
        else:
            self.strautosign = "Auto Range"

        if (self.databuf[2] & 4) != 0:
            self.strhzunit = "ms"
        else:
            self.strhzunit = "%"

        tempvalue = [0.0] * 2
        for i in range(2):
            b = bytes([
                self.databuf[(i * 4) + 6] & 0xFF,
                self.databuf[(i * 4) + 5] & 0xFF,
                self.databuf[(i * 4) + 4] & 0xFF,
                self.databuf[(i * 4) + 3] & 0xFF,
            ])
            tempvalue[i] = self._ByteToFloat(b)

        self.m_mainvalue = tempvalue[0]
        self.m_hzvalue = tempvalue[1]

        self.strunit = "HZ"
        if self.m_mainvalue > 500000.0:
            self.m_mainvalue /= 1000000.0
            self.strunit = "MHZ"
        elif self.m_mainvalue > 500.0:
            self.m_mainvalue /= 1000.0
            self.strunit = "KHZ"

        self.m_hzvalue *= 100.0

        if self.m_mainvalue > 100.0:
            self.point = 2
        elif self.m_mainvalue > 10.0:
            self.point = 3
        else:
            self.point = 4

        self.strdatavalue = self._FloatToString(self.m_mainvalue, self.point)
        self.strhzvalue = self._FloatToString(self.m_hzvalue, 2)

    def AnalyzeOscData(self):
        byteleng = len(self.databuf)
        if (self.databuf[0] == 224 and self.databuf[1] == 224
                and self.databuf[byteleng - 2] == 225
                and self.databuf[byteleng - 1] == 225):

            sm = [
                "", "500Sps", "1KSa/s", "2KSa/s", "5KSa/s", "10KSa/s",
                "20KSa/s", "50KSa/s", "100KSa/s", "200KSa/s", "500KSa/s",
                "1MSa/s", "2MSa/s", "5MSa/s", "10MSa/s", "20MSa/s",
                "50MSa/s", "100MSa/s"
            ]
            vppdata = [
                "", "100 V/div", "50.00 V/div", "20.00 V/div", "10.00 V/div",
                "5.00 V/div", "2.00 V/div", "1.00 V/div", "0.50 V/div",
                "200.0 mV/div", "100.0 mV/div", "50.00 mV/div"
            ]
            DEL_B = ["", "HOLD", "REC", "FFT"]
            vooParameter = [0, 40, 20, 8, 4, 20, 8, 4, 2, 8, 8, 8]
            smbyet = [
                0, 50000, 12500, 250000, 500000, 125000, 2500000, 50000,
                12500, 250000, 500000, 1250000, 2500000, 500000, 1250000,
                250000, 50000, 100000
            ]
            frepdata = [0, 2, 5, 10, 20, 50, 100, 200, 5, 10, 20, 50, 100, 20, 50, 100, 200, 200]
            maindatavpp = [0.0, 100.0, 50.0, 20.0, 10.0, 5.0, 2.0, 1.0, 0.5, 200.0, 100.0, 50.0]

            self.Time = "%04d-%02d-%02d %02d:%02d:%02d" % (
                (self.databuf[43] // 16) * 10 + (self.databuf[43] % 16) + 2000,
                (self.databuf[44] // 16) * 10 + (self.databuf[44] % 16),
                (self.databuf[45] // 16) * 10 + (self.databuf[45] % 16),
                (self.databuf[46] // 16) * 10 + (self.databuf[46] % 16),
                (self.databuf[47] // 16) * 10 + (self.databuf[47] % 16),
                (self.databuf[48] // 16) * 10 + (self.databuf[48] % 16),
            )

            self.OscilloscopeStatus = DEL_B[self.databuf[2]]

            if self.databuf[2] == 2:
                self.page = self.databuf[21]

            if self.OscilloscopeStatus == "FFT":
                voodata = (self.databuf[14] << 8) | self.databuf[15]
            else:
                voodata = ((self.databuf[9] - self.databuf[10]) * vooParameter[self.databuf[4]]) / 2

            if self.databuf[4] <= 4:
                self.Vp_p = str(int(10.0 * (voodata / 10.0)) / 10.0) + "V"
            elif self.databuf[4] <= 8:
                self.Vp_p = str(int(100.0 * (voodata / 100.0)) / 100.0) + "V"
            elif self.databuf[4] <= 11:
                self.Vp_p = str(int(voodata)) + "mV"

            self.Vpp = vppdata[self.databuf[4]]
            if self.databuf[11] == 0:
                self.Vpp = "AC " + self.Vpp
            else:
                self.Vpp = "DC " + self.Vpp

            if self.OscilloscopeStatus == "FFT":
                smdata = (self.databuf[16] << 8) | self.databuf[17]
            else:
                divisor = ((self.databuf[34] << 8) | self.databuf[35]) - ((self.databuf[32] << 8) | self.databuf[33])
                if divisor != 0:
                    smdata = smbyet[self.databuf[3]] / divisor
                else:
                    smdata = 0

            if self.databuf[3] <= 6:
                if smdata < 1000.0:
                    smdata5 = smdata / 10.0
                else:
                    smdata5 = smdata / 100.0
                self.Frequency = str(int(100.0 * smdata5) / 100.0) + "Hz"
            elif self.databuf[3] <= 12:
                if smdata < 1000.0:
                    smdata4 = smdata / 100.0
                else:
                    smdata4 = smdata / 1000.0
                self.Frequency = str(int(1000.0 * smdata4) / 1000.0) + "KHz"
            elif self.databuf[3] <= 14:
                self.Frequency = str(int(100.0 * (smdata / 10.0)) / 100.0) + "KHz"
            elif self.databuf[3] <= 15:
                if smdata < 1000.0:
                    smdata3 = smdata / 1000.0
                else:
                    smdata3 = smdata / 10000.0
                self.Frequency = str(int(10000.0 * smdata3) / 10000.0) + "MHz"
            else:
                if smdata < 1000.0:
                    smdata2 = smdata / 10.0
                else:
                    smdata2 = smdata / 100.0
                self.Frequency = str(int(1000.0 * smdata2) / 1000.0) + "MHz"

            self.SamplingRate = sm[self.databuf[3]]
            self.TriggerIco = self.databuf[21]

            if self.databuf[13] == 0:
                self.SpeedSign = "Fast"
            else:
                self.SpeedSign = "Slow"

            for i in range(82, 382):
                try:
                    tempmaindata = float(self.databuf[i] - 135) * (maindatavpp[self.databuf[4]] / 25.0)
                    self.maindata[i - 82] = tempmaindata
                except Exception:
                    return

            if self.databuf[2] == 3:
                j = 0
                for i2 in range(392, 512):
                    tempFFTdata = float(self.databuf[i2] - 58) * (maindatavpp[self.databuf[4]] / 25.0)
                    self.FFTdata[i2 - 392] = tempFFTdata
                    tempFrepdata = frepdata[self.databuf[3]] * j
                    j += 1
                    if self.databuf[3] <= 2:
                        tempstr = str(int(tempFrepdata)) + "Hz"
                    elif self.databuf[3] <= 7:
                        tempstr = str(int(100.0 * (tempFrepdata / 100.0)) / 100.0) + "KHz"
                    elif self.databuf[3] <= 12:
                        tempstr = str(int(10.0 * (tempFrepdata / 10.0)) / 10.0) + "KHz"
                    else:
                        tempstr = str(int(1000.0 * (tempFrepdata / 1000.0)) / 1000.0) + "MHz"
                    self.Fret[i2 - 392] = tempstr

    def AnalyzeLogMsg(self):
        self.logtimelist.clear()
        self.logdatalist.clear()

        self.strfun = self.arrayfun[self.databuf[2]]
        self.strunit = self.arrayunit[self.databuf[2]]

        self.logstarttime = "%04d-%02d-%02d %02d:%02d:%02d" % (
            (self.databuf[3] // 16) * 10 + (self.databuf[3] % 16) + 2000,
            (self.databuf[4] // 16) * 10 + (self.databuf[4] % 16),
            (self.databuf[5] // 16) * 10 + (self.databuf[5] % 16),
            (self.databuf[6] // 16) * 10 + (self.databuf[6] % 16),
            (self.databuf[7] // 16) * 10 + (self.databuf[7] % 16),
            (self.databuf[8] // 16) * 10 + (self.databuf[8] % 16),
        )

        rate = [0] * 3
        for j in range(3):
            for i in range(4):
                rate[j] = rate[j] << 8
                rate[j] = rate[j] | self.databuf[(j * 4 + 12) - i]

        self.logsamprate = rate[0]
        self.logrectime = rate[1]
        self.logdatanum = rate[2]

        self.logpacketnum = 0
        for i2 in range(2):
            self.logpacketnum <<= 8
            self.logpacketnum |= self.databuf[22 - i2]

    def AnalyzeLogData(self):
        for i in range(len(self.databuf) // 8):
            b = bytes([
                self.databuf[(i * 8) + 3] & 0xFF,
                self.databuf[(i * 8) + 2] & 0xFF,
                self.databuf[(i * 8) + 1] & 0xFF,
                self.databuf[i * 8] & 0xFF,
            ])
            second = 0
            for j in range(4):
                second = (second << 8) | self.databuf[((i * 8) + 7) - j]

            data = self._ByteToFloat(b)
            strdata = str(data)

            date = datetime.strptime(self.logstarttime, self.DATE_FORMAT)
            date2 = date + timedelta(seconds=second)
            strtime = date2.strftime(self.DATE_FORMAT)

            self.logdatalist.append(strdata)
            self.logtimelist.append(strtime)

    # --- Utility methods ---

    @staticmethod
    def _int2byte(self, iarr):
        return bytes([v & 0xFF for v in iarr])

    def _ByteToFloat(self, b):
        return struct.unpack('>f', b[:4])[0]

    def _ByteToString(self, b):
        chars = []
        for i in range(4):
            chars.append(chr(b[i] & 0xFF))
        return "".join(chars)

    def _FloatToString(self, data, point):
        plusdata = 0.0
        if point == 0:
            plusdata = 0.5
        elif point == 1:
            plusdata = 0.05
        elif point == 2:
            plusdata = 0.005
        elif point == 3:
            plusdata = 0.0005
        elif point == 4:
            plusdata = 0.00005

        if -plusdata <= data <= plusdata:
            data = 0.0
            plusdata = 0.0

        if data < 0.0:
            plusdata *= -1.0

        fmt = "%%.%df" % point
        result = fmt % (data - plusdata)

        m_num = 7 - len(result)
        for _ in range(m_num):
            result = " " + result

        return result

    def CorrectUnitShow(self):
        if self.strunit == "s":
            self.strunit = "°C"
            if self.measuretype == DT99Sprotocol.MEASURE_MAXMIN:
                self.strmaxunit = self.strunit
                self.strminunit = self.strunit
                self.stravgunit = self.strunit
        elif self.strunit == "h":
            self.strunit = "°F"
            if self.measuretype == DT99Sprotocol.MEASURE_MAXMIN:
                self.strmaxunit = self.strunit
                self.strminunit = self.strunit
                self.stravgunit = self.strunit
        elif self.strunit == "o":
            self.strunit = "Ω"
        elif self.strunit == "ko":
            self.strunit = "KΩ"
            self.m_coef = 1000.0
        elif self.strunit == "Mo":
            self.strunit = "MΩ"
            self.m_coef = 1000000.0
        elif self.strunit == "VE":
            self.strunit = "V"
            self.flag_diodesign = True
        elif self.strunit == "uF":
            self.m_coef = 1000.0
            self.point -= 1
        elif self.strunit == "mF":
            self.m_coef = 1000000.0
            self.point -= 1
        elif self.strunit == "nF":
            self.point -= 1
        elif self.strunit == "o@":
            self.strunit = "Ω"
        elif self.strunit == "kHZ":
            self.m_coef = 1000.0
        elif self.strunit == "MHZ":
            self.m_coef = 1000000.0

        if self.strmaxunit == "o":
            self.strmaxunit = "Ω"
        elif self.strmaxunit == "ko":
            self.strmaxunit = "KΩ"
            self.m_coefmax = 1000.0
        elif self.strmaxunit == "Mo":
            self.strmaxunit = "MΩ"
            self.m_coefmax = 1000000.0
        elif self.strmaxunit == "kHZ":
            self.m_coefmax = 1000.0
        elif self.strmaxunit == "MHZ":
            self.m_coefmax = 1000000.0

        if self.strminunit == "o":
            self.strminunit = "Ω"
        elif self.strminunit == "ko":
            self.strminunit = "KΩ"
            self.m_coefmin = 1000.0
        elif self.strminunit == "Mo":
            self.strminunit = "MΩ"
            self.m_coefmin = 1000000.0
        elif self.strminunit == "kHZ":
            self.m_coefmin = 1000.0
        elif self.strminunit == "MHZ":
            self.m_coefmin = 1000000.0

        if self.stravgunit == "o":
            self.stravgunit = "Ω"
        elif self.stravgunit == "ko":
            self.stravgunit = "KΩ"
            self.m_coefavg = 1000.0
        elif self.stravgunit == "Mo":
            self.stravgunit = "MΩ"
            self.m_coefavg = 1000000.0
        elif self.stravgunit == "kHZ":
            self.m_coefavg = 1000.0
        elif self.stravgunit == "MHZ":
            self.m_coefavg = 1000000.0

    # --- Getters ---

    def GetStrDatavalue(self):
        return self.strdatavalue

    def GetStrMaxvalue(self):
        return self.strmaxvalue

    def GetStrMinvalue(self):
        return self.strminvalue

    def GetStrAvgvalue(self):
        return self.stravgvalue

    def GetUnit(self):
        return self.strunit

    def GetMaxUnit(self):
        return self.strmaxunit

    def GetMinUnit(self):
        return self.strminunit

    def GetAvgUnit(self):
        return self.stravgunit

    def GetMainData(self):
        return self.m_mainvalue

    def GetMaxData(self):
        return self.m_maxvalue

    def GetMinData(self):
        return self.m_minvalue

    def GetAvgData(self):
        return self.m_avgvalue

    def GetrangeData(self):
        return self.m_range

    def GetFun(self):
        return self.strfun

    def GetAutosign(self):
        return self.strautosign

    def GetPeaksign(self):
        return self.strpeaksign

    def GetMaxminsign(self):
        return self.strmaxminsign

    def GetMaximumsign(self):
        return self.maximumsign

    def GetMinimumsign(self):
        return self.minimumsign

    def GeAveragesign(self):
        return self.averagesign

    def GetHoldsign(self):
        return self.strholdsign

    def GetFlagDiode(self):
        return self.flag_diodesign

    def GetStartRecTime(self):
        return self.startrectime

    def GetMaxTime(self):
        return self.strmaxtime

    def GetMinTime(self):
        return self.strmintime

    def GetAvgTime(self):
        return self.stravgtime

    def GetRelSign(self):
        return self.strrelsign

    def GetRefSign(self):
        return self.strrefsign

    def GetRelData(self):
        return self.m_relvalue

    def GetRefData(self):
        return self.m_refvalue

    def GetStrRefvalue(self):
        return self.strrefvalue

    def GetStrRelvalue(self):
        return self.strrelvalue

    def GetRelunit(self):
        return self.strrelunit

    def GetACunit(self):
        return self.stracunit

    def GetStrACValue(self):
        return self.stracvalue

    def GetACDCSign(self):
        return self.stracdcsign

    def GetDBValue(self):
        return self.strdbvalue

    def GetDBUnit(self):
        return self.strdbunit

    def GetHZValue(self):
        return self.strhzvalue

    def GetHZUnit(self):
        return self.strhzunit

    def GetStrfun(self):
        return self.strfun

    def GetLogSamprate(self):
        return self.logsamprate

    def GetLogRectime(self):
        return self.logrectime

    def GetLogDataNum(self):
        return self.logdatanum

    def GetLogPacketNum(self):
        return self.logpacketnum

    def GetFlagLoZ(self):
        return self.flag_lo
        
    def GetCrestFactor(self):
        return self.flag_cf
