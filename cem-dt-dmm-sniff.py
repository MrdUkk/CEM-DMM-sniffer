#!/usr/bin/env python3

# (c) dUkk 2026  https://blog.softdev.online
# CEM DT-9979, DT-9989, DT-99S, FI279MG digital multimeters (DMM) protocol sniffer and parser
# How to use:
# 1. power on DMM and enable Bluetooth
# 2. open bluetooth on PC and search for device
# 3. pair it (use pincode 1234)
# 4. there should be exposed two COM ports
# 5. get one that is feeding bytestream one at a time (every second) and pass it to this script


import serial
import argparse
import structlog
import sys
import logging
import dt99s_proto
from datetime import datetime
from struct import pack,unpack
from binascii import hexlify

LOG_LEVEL_NAMES = [logging.getLevelName(v) for v in
                   sorted(getattr(logging, '_levelToName', None) or logging._levelNames) if getattr(v, "real", 0)]

log = structlog.get_logger()


def DoNormalRun(serial_port, baud_rate):
    do_work = True
    payload_len = 20
    buffer = bytes()
    
    log.info('opening serial port', port=serial_port, baud=baud_rate)
    with serial.serial_for_url(serial_port, int(baud_rate),  bytesize=serial.EIGHTBITS, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE, timeout=5) as ser:       
        while do_work:
                try:
                    buffer += ser.read(ser.inWaiting())
                except KeyboardInterrupt:
                    log.info('stopped')
                    break;
                
                while len(buffer) > payload_len:                    
                    (leadin, measuretype) = unpack('BB', buffer[:2])
                    if leadin != 0xA0:
                        log.error('invalid start frame header! trying refill buffer', header=hexlify(buffer[:1]))
                        buffer = buffer[1:] # make single byte step (probably lost sync)
                        break
                        
                    # search to leadout
                    idx_leadout = buffer.find(0xA1, 0)
                    if idx_leadout == -1:
                        log.error('cant find leadout! trying refill buffer')
                        break;
                    
                    # rotary selector of measurement type
                    match measuretype:
                        case 0x80:
                            measuretype = dt99s_proto.DT99Sprotocol.MEASURE_CURRENT
                            payload_len = 20
                        case 0x81:
                            measuretype = dt99s_proto.DT99Sprotocol.MEASURE_MAXMIN
                            payload_len = 59
                        case 0x82:
                            measuretype = dt99s_proto.DT99Sprotocol.MEASURE_REL
                            payload_len = 28
                        case 0x83:
                            measuretype = dt99s_proto.DT99Sprotocol.MEASURE_PEAK
                            payload_len = 47
                        case 0x84:
                            measuretype = dt99s_proto.DT99Sprotocol.MEASURE_DCAC
                            payload_len = 29
                        case 0x85:
                            measuretype = dt99s_proto.DT99Sprotocol.MEASURE_ACDB
                            payload_len = 27
                        case 0x86:
                            measuretype = dt99s_proto.DT99Sprotocol.MEASURE_HZ
                            payload_len = 14
                        # todo: handle MEASURE_OSC, MEASURE_LOGMSG, MEASURE_LOGDATA types of packets but i didnt catch it
                        case _:
                            log.error('encoutered non valid measuretype, trying refill buffer', HEXpacket=hexlify(buffer[:idx_leadout]))
                            buffer=buffer[idx_leadout:] # eat all such packet data
                            payload_len=20 # reset required minimal buffer size
                            continue;
                    
                    if payload_len > len(buffer):
                        log.warn('buffer too short for this measurement data, refilling')
                        continue;
                    
                    dmm = dt99s_proto.DT99Sprotocol(buffer, measuretype)
                    dmm.ProcessPacket()
                    
                    mainvalue=dmm.GetStrDatavalue()
                    mainunit=dmm.GetUnit()
                    funcused=dmm.GetStrfun()
                    log.debug('measure sub data', function=funcused, autosign=dmm.GetAutosign(), peaksign=dmm.GetPeaksign(), holdsign=dmm.GetHoldsign(), flagdiode=dmm.GetFlagDiode(), rangedata=dmm.GetrangeData(), startrectime=dmm.GetStartRecTime(), maxminsign=dmm.GetMaxminsign(), max_value=dmm.GetStrMaxvalue(), maxunit=dmm.GetMaxUnit(), maxtime=dmm.GetMaxTime(), maxsign=dmm.GetMaximumsign(), min_value=dmm.GetStrMinvalue(), minunit=dmm.GetMinUnit(), mintime=dmm.GetMinTime(), minsign=dmm.GetMinimumsign(), stravg_value=dmm.GetStrAvgvalue(), avgunit=dmm.GetAvgUnit(), avgtime=dmm.GetAvgTime(), avgsign=dmm.GeAveragesign(), relvalue=dmm.GetStrRelvalue(), relsign=dmm.GetRelSign(), relunit=dmm.GetRelunit(), refvalue=dmm.GetStrRefvalue(), refsign=dmm.GetRefSign(), acvalue=dmm.GetStrACValue(), acunit=dmm.GetACunit(), acdcsign=dmm.GetACDCSign(), dbvalue=dmm.GetDBValue(), dbunit=dmm.GetDBUnit(), hzvalue=dmm.GetHZValue(), hzunit=dmm.GetHZUnit())
                    
                    if "@" in mainunit:
                        mainunit = mainunit.replace("@", "")
                    elif "E" in mainunit:
                        mainunit = mainunit.replace("E", "")
                    
                    datalength = 6
                    if "-" in mainvalue:
                        datalength+=1
                    if "." in mainvalue:
                        datalength+=1
                    if funcused is not None and (funcused == "4-20mA" or funcused == "Temp"):
                        datalength-=1
                    if len(mainvalue) > datalength:
                        mainvalue = mainvalue.substring(0, datalength)
                    
                    log.debug('measure main data', main_value=dmm.GetMainData(), main_unit=mainunit)
                    
                    # log to CSV format file in append mode
                    file_path = "currentdata-{0}{1}{2}-log.csv".format(funcused, dmm.GetRelSign(),dmm.GetMaxminsign())
                    with open(file_path, 'a', encoding='utf-8') as file:
                        match measuretype:
                            case dt99s_proto.DT99Sprotocol.MEASURE_CURRENT:
                                file.write("{0};{1};{2};{3};{4};{5};{6};{7}\n".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S"),dmm.GetHoldsign(),dmm.GetAutosign(),dmm.GetFlagLoZ(),dmm.GetFlagDiode(),dmm.GetStrDatavalue(),dmm.GetUnit(),dmm.GetrangeData()))
                            case dt99s_proto.DT99Sprotocol.MEASURE_HZ:
                                file.write("{0};{1};{2};{3};{4};{5};{6}\n".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S"),dmm.GetHoldsign(),dmm.GetAutosign(),dmm.GetStrDatavalue(),dmm.GetUnit(),dmm.GetHZValue(),dmm.GetHZUnit()))
                            case dt99s_proto.DT99Sprotocol.MEASURE_ACDB:
                                file.write("{0};{1};{2};{3};{4};{5};{6};{7}\n".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S"),dmm.GetHoldsign(),dmm.GetAutosign(),dmm.GetStrDatavalue(),dmm.GetUnit(),dmm.GetDBValue(),dmm.GetDBUnit(),dmm.GetrangeData()))
                            case dt99s_proto.DT99Sprotocol.MEASURE_REL:
                                file.write("{0};{1};{2};{3};{4};{5};{6};{7};{8};{9}\n".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S"),dmm.GetHoldsign(),dmm.GetAutosign(),dmm.GetFlagLoZ(),dmm.GetStrDatavalue(),dmm.GetUnit(),dmm.GetStrRelvalue(),dmm.GetRelunit(),dmm.GetStrRefvalue(),dmm.GetrangeData()))                            
                            case dt99s_proto.DT99Sprotocol.MEASURE_MAXMIN:
                                file.write("{0};{1};{2};{3};{4};{5};{6};{7};{8};{9};{10};{11};{12};{13};{14};{15};{16}\n".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S"),dmm.GetHoldsign(),dmm.GetAutosign(),dmm.GetFlagLoZ(),dmm.GetStrDatavalue(),dmm.GetUnit(),dmm.GetStrMaxvalue(),dmm.GetMaxUnit(),dmm.GetMaxTime(),dmm.GetStrMinvalue(),dmm.GetMinUnit(),dmm.GetMinTime(),dmm.GetStrAvgvalue(),dmm.GetAvgUnit(),dmm.GetAvgTime(),dmm.GetrangeData(),dmm.GetStartRecTime()))
                            case dt99s_proto.DT99Sprotocol.MEASURE_PEAK:
                                file.write("{0};{1};{2};{3};{4};{5};{6};{7};{8};{9};{10};{11};{12};{13};{14};{15}\n".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S"),dmm.GetHoldsign(),dmm.GetAutosign(),dmm.GetCrestFactor(),dmm.GetStrDatavalue(),dmm.GetUnit(),dmm.GetStrMaxvalue(),dmm.GetMaxUnit(),dmm.GetMaxTime(),dmm.GetStrMinvalue(),dmm.GetMinUnit(),dmm.GetMinTime(),dmm.GetStrAvgvalue(),dmm.GetAvgUnit(),dmm.GetAvgTime(),dmm.GetrangeData()))                            
                            case dt99s_proto.DT99Sprotocol.MEASURE_DCAC:
                                file.write("{0};{1};{2};{3};{4};{5};{6};{7}\n".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S"),dmm.GetHoldsign(),dmm.GetAutosign(),dmm.GetStrDatavalue(),dmm.GetUnit(),dmm.GetStrACValue(),dmm.GetACunit(),dmm.GetrangeData()))

                    buffer = buffer[payload_len:] # remove processed bytes from circular buffer 



def DoBinfileCapture(serial_port, baud_rate):
    do_work = True
    buffer = bytes()

    log.info('opening serial port', port=serial_port, baud=baud_rate)
    with serial.serial_for_url(serial_port, int(baud_rate),  bytesize=serial.EIGHTBITS, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE, timeout=5) as ser:        
        bd = open("cem-dump.bin", "wb")        
        while do_work:
                try:
                    buffer = ser.read(ser.inWaiting())
                except KeyboardInterrupt:
                    log.info('stopped')
                    do_work = False
                    break;
                if len(buffer) > 0:
                    log.debug('writing', bytes=len(buffer))
                    bd.write(buffer)
        
        bd.close()



def DoBinfileReplay():
    buffer = bytes()
    payload_len = 20
    
    bd = open("cem-dump.bin", "rb")
    while True:
        try:
            curbuf = bd.read(21)
            if not curbuf:
                log.info("ended file processing with remaining unparsed", bytes=len(buffer))
                break;
            buffer += curbuf
        except KeyboardInterrupt:
            log.info('stopped')
            break;

        while len(buffer) > payload_len:                    
            (leadin, measuretype) = unpack('BB', buffer[:2])
            if leadin != 0xA0:
                log.error('invalid start frame header! trying refill buffer', header=hexlify(buffer[:1]))
                buffer = buffer[1:] # make single byte step (probably lost sync)
                break
                
            # search to leadout
            idx_leadout = buffer.find(0xA1, 0)
            if idx_leadout == -1:
                log.error('cant find leadout! trying refill buffer')
                break;
            
            # rotary selector of measurement type
            match measuretype:
                case 0x80:
                    measuretype = dt99s_proto.DT99Sprotocol.MEASURE_CURRENT
                    payload_len = 20
                case 0x81:
                    measuretype = dt99s_proto.DT99Sprotocol.MEASURE_MAXMIN
                    payload_len = 59
                case 0x82:
                    measuretype = dt99s_proto.DT99Sprotocol.MEASURE_REL
                    payload_len = 28
                case 0x83:
                    measuretype = dt99s_proto.DT99Sprotocol.MEASURE_PEAK
                    payload_len = 47
                case 0x84:
                    measuretype = dt99s_proto.DT99Sprotocol.MEASURE_DCAC
                    payload_len = 29
                case 0x85:
                    measuretype = dt99s_proto.DT99Sprotocol.MEASURE_ACDB
                    payload_len = 27
                case 0x86:
                    measuretype = dt99s_proto.DT99Sprotocol.MEASURE_HZ
                    payload_len = 14
                # todo: handle MEASURE_OSC, MEASURE_LOGMSG, MEASURE_LOGDATA types of packets but i didnt catch it
                case _:
                    log.error('encoutered non valid measuretype, trying refill buffer', HEXpacket=hexlify(buffer[:idx_leadout]))
                    buffer=buffer[idx_leadout:] # eat all such packet data
                    payload_len=20 # reset required minimal buffer size
                    continue;
            
            if payload_len > len(buffer):
                log.warn('buffer too short for this measurement data, refilling')
                continue;
            
            dmm = dt99s_proto.DT99Sprotocol(buffer, measuretype)
            dmm.ProcessPacket()
            
            mainvalue=dmm.GetStrDatavalue()
            mainunit=dmm.GetUnit()
            funcused=dmm.GetStrfun()
            log.debug('measure sub data', function=funcused, autosign=dmm.GetAutosign(), peaksign=dmm.GetPeaksign(), holdsign=dmm.GetHoldsign(), flagdiode=dmm.GetFlagDiode(), rangedata=dmm.GetrangeData(), startrectime=dmm.GetStartRecTime(), maxminsign=dmm.GetMaxminsign(), max_value=dmm.GetStrMaxvalue(), maxunit=dmm.GetMaxUnit(), maxtime=dmm.GetMaxTime(), maxsign=dmm.GetMaximumsign(), min_value=dmm.GetStrMinvalue(), minunit=dmm.GetMinUnit(), mintime=dmm.GetMinTime(), minsign=dmm.GetMinimumsign(), stravg_value=dmm.GetStrAvgvalue(), avgunit=dmm.GetAvgUnit(), avgtime=dmm.GetAvgTime(), avgsign=dmm.GeAveragesign(), relvalue=dmm.GetStrRelvalue(), relsign=dmm.GetRelSign(), relunit=dmm.GetRelunit(), refvalue=dmm.GetStrRefvalue(), refsign=dmm.GetRefSign(), acvalue=dmm.GetStrACValue(), acunit=dmm.GetACunit(), acdcsign=dmm.GetACDCSign(), dbvalue=dmm.GetDBValue(), dbunit=dmm.GetDBUnit(), hzvalue=dmm.GetHZValue(), hzunit=dmm.GetHZUnit())
            
            if "@" in mainunit:
                mainunit = mainunit.replace("@", "")
            elif "E" in mainunit:
                mainunit = mainunit.replace("E", "")
            
            datalength = 6
            if "-" in mainvalue:
                datalength+=1
            if "." in mainvalue:
                datalength+=1
            if funcused is not None and (funcused == "4-20mA" or funcused == "Temp"):
                datalength-=1
            if len(mainvalue) > datalength:
                mainvalue = mainvalue.substring(0, datalength)
            
            log.debug('measure main data', main_value=dmm.GetMainData(), main_unit=mainunit)
            
            # log to CSV format file in append mode
            file_path = "currentdata-{0}{1}{2}-log.csv".format(funcused, dmm.GetRelSign(),dmm.GetMaxminsign())
            with open(file_path, 'a', encoding='utf-8') as file:
                match measuretype:
                    case dt99s_proto.DT99Sprotocol.MEASURE_CURRENT:
                        file.write("{0};{1};{2};{3};{4};{5};{6};{7}\n".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S"),dmm.GetHoldsign(),dmm.GetAutosign(),dmm.GetFlagLoZ(),dmm.GetFlagDiode(),dmm.GetStrDatavalue(),dmm.GetUnit(),dmm.GetrangeData()))
                    case dt99s_proto.DT99Sprotocol.MEASURE_HZ:
                        file.write("{0};{1};{2};{3};{4};{5};{6}\n".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S"),dmm.GetHoldsign(),dmm.GetAutosign(),dmm.GetStrDatavalue(),dmm.GetUnit(),dmm.GetHZValue(),dmm.GetHZUnit()))
                    case dt99s_proto.DT99Sprotocol.MEASURE_ACDB:
                        file.write("{0};{1};{2};{3};{4};{5};{6};{7}\n".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S"),dmm.GetHoldsign(),dmm.GetAutosign(),dmm.GetStrDatavalue(),dmm.GetUnit(),dmm.GetDBValue(),dmm.GetDBUnit(),dmm.GetrangeData()))
                    case dt99s_proto.DT99Sprotocol.MEASURE_REL:
                        file.write("{0};{1};{2};{3};{4};{5};{6};{7};{8};{9}\n".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S"),dmm.GetHoldsign(),dmm.GetAutosign(),dmm.GetFlagLoZ(),dmm.GetStrDatavalue(),dmm.GetUnit(),dmm.GetStrRelvalue(),dmm.GetRelunit(),dmm.GetStrRefvalue(),dmm.GetrangeData()))                            
                    case dt99s_proto.DT99Sprotocol.MEASURE_MAXMIN:
                        file.write("{0};{1};{2};{3};{4};{5};{6};{7};{8};{9};{10};{11};{12};{13};{14};{15};{16}\n".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S"),dmm.GetHoldsign(),dmm.GetAutosign(),dmm.GetFlagLoZ(),dmm.GetStrDatavalue(),dmm.GetUnit(),dmm.GetStrMaxvalue(),dmm.GetMaxUnit(),dmm.GetMaxTime(),dmm.GetStrMinvalue(),dmm.GetMinUnit(),dmm.GetMinTime(),dmm.GetStrAvgvalue(),dmm.GetAvgUnit(),dmm.GetAvgTime(),dmm.GetrangeData(),dmm.GetStartRecTime()))
                    case dt99s_proto.DT99Sprotocol.MEASURE_PEAK:
                        file.write("{0};{1};{2};{3};{4};{5};{6};{7};{8};{9};{10};{11};{12};{13};{14};{15}\n".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S"),dmm.GetHoldsign(),dmm.GetAutosign(),dmm.GetCrestFactor(),dmm.GetStrDatavalue(),dmm.GetUnit(),dmm.GetStrMaxvalue(),dmm.GetMaxUnit(),dmm.GetMaxTime(),dmm.GetStrMinvalue(),dmm.GetMinUnit(),dmm.GetMinTime(),dmm.GetStrAvgvalue(),dmm.GetAvgUnit(),dmm.GetAvgTime(),dmm.GetrangeData()))                            
                    case dt99s_proto.DT99Sprotocol.MEASURE_DCAC:
                        file.write("{0};{1};{2};{3};{4};{5};{6};{7}\n".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S"),dmm.GetHoldsign(),dmm.GetAutosign(),dmm.GetStrDatavalue(),dmm.GetUnit(),dmm.GetStrACValue(),dmm.GetACunit(),dmm.GetrangeData()))

            buffer = buffer[payload_len:] # remove processed bytes from circular buffer   
        
    bd.close()




if __name__ == "__main__":
    structlog.configure(
        wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
        logger_factory=structlog.PrintLoggerFactory(file=sys.stderr)
    )

    parser = argparse.ArgumentParser(description='CEM DT-99x protocol sniffer')
    parser.add_argument('--loglevel', choices=LOG_LEVEL_NAMES, default='INFO', help='Change log level')
    parser.add_argument('--bincapture', action='store_true', help='capture all binary data coming to file cem-dump.bin')
    parser.add_argument('--binreplay', action='store_true', help='process all binary data from file cem-dump.bin')
    parser.add_argument('serial_port', type=str, nargs='?', help='Serial port. (ex. COM1 on Windows or /dev/ttpys0 on Linux)')
    parser.add_argument('baud_rate', type=int, default=9600, nargs='?', help='baud rate. probably 9600')

    args = parser.parse_args()
    if args.bincapture and args.binreplay:
       print("bincapture and binreplay cant be specified together")
       exit()
    if not args.bincapture and not args.binreplay:
       if not args.serial_port:
          print("serial_port is REQUIRED for this mode")
          exit()       

    # Restrict log message to be above selected level
    structlog.configure( wrapper_class=structlog.make_filtering_bound_logger(getattr(logging, args.loglevel)) )
    
    if args.bincapture:
        print("doing capture from meter to a file on disk....")
        DoBinfileCapture(args.serial_port, args.baud_rate)
    elif args.binreplay:
        print("doing processing from file on disk....")
        DoBinfileReplay()
    else:
        print("doing live processing")
        DoNormalRun(args.serial_port, args.baud_rate)
