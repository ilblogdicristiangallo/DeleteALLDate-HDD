# DeleteALLDate-HDD
Erase selected disk with zeros
This script allows you to permanently erase data from a disk or partition by overwriting every single bit with 0.
After the operation, if you run:

xxd /dev/device
you will see only zeros, meaning the data has been completely wiped.

# EXECUTE:
python 2.7 or python3

# Boot:
python delete_date.py
