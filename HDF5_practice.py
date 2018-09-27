import pandas as pd
import serialMonitor as sm
import os
import tables
import csv

CACHE = {}
STORE = 'store.h5'   # Note: another option is to keep the actual file open

os.system('sudo chmod 666 /dev/ttyS7')

newMonitor = sm.SerialMonitor('/dev/ttyS7')
newMonitor.start()

def process_row(d, key, max_len=5, _cache=CACHE):
	"""
	Append row d to the store 'key'.

	When the number of items in the key's cache reaches max_len,
	append the list of rows to the HDF5 store and clear the list.

	"""
	# keep the rows for each key separate.
	lst = _cache.setdefault(key, [])
	if len(lst) >= max_len:
		store_and_clear(lst, key)
	lst.append(d)

def store_and_clear(lst, key):
	"""
	Convert key's cache list to a DataFrame and append that to HDF5.
	"""
	df = pd.DataFrame(lst)
	with pd.HDFStore(STORE) as store:
		store.append(key, df)
	lst.clear()

while True:
	if newMonitor.lineReady:
		new = newMonitor.getCurrentLine()
		new = new.split(',')
		new = [float(i) for i in new]
		process_row(new, key="test")

		for k, lst in CACHE.items():  # you can instead use .iteritems() in python 2
			store_and_clear(lst, k)

		with pd.HDFStore(STORE) as store:
			df = store["test"]
			print(len(df))
			if len(df) >= 100:
				df.to_csv('hdf5test.txt', sep='\t')
				break
