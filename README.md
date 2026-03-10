# CEM-DMM-sniffer
Chinese CEM Multimeters protocol parsers in Python

# How to use
1. clone repository
2. get CEM DMM that is supported currently
3. enable bluetooth function on it
4. connect to PC (default PIN 1234). Ensure COM ports are exposed (two ports , one in , other out)
5. launch script: python cem-dt-dmm-sniff.py COMx 9600

in Windows OS there will be COM[1-...] ports to use, in Linux /dev/ttyS[0-...] 

Data will be output in various CSV-files each 2 seconds (hardcoded in CEM DMM and not available to change).
on console there will be informational log.

# Supported multimeters
CEM DT-9979 (tested), DT-9989, DT99s, FI279MG models.
