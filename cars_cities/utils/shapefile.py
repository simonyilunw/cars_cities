from __future__ import absolute_import
from shapefile import Reader as UnsafeReader
from shapefile import unpack, b, u


class Reader(UnsafeReader):
	
	def __record(self):
		"""
		Overrides the __record method of the original shapefile Reader so that interpreting
		floats as ints will not throw exception
		"""
		f = self.__getFileObj(self.dbf)
		recFmt = self.__recordFmt()
		recordContents = unpack(recFmt[0], f.read(recFmt[1]))
	 	if recordContents[0] != b(' '):
			return None
		
		record = []
		for (name, typ, size, deci), value in zip(self.fields, recordContents):
		    if name == 'DeletionFlag':
		        continue
		    elif not value.strip():
		        record.append(value)
		        continue
		    elif typ == "N":
		        value = value.replace(b('\0'), b('')).strip()
		        if value == b(''):
		            value = 0
		        elif deci:
		            value = float(value)
		        else:
		        	try:
		        		value = int(float(value or 0))  # THIS is the change required, was just int(value)
		        	except ValueError:
		        		value = 0
		    elif typ == b('D'):
		        try:
		            y, m, d = int(value[:4]), int(value[4:6]), int(value[6:8])
		            value = [y, m, d]
		        except:
		            value = value.strip()
		    elif typ == b('L'):
		        value = (value in b('YyTt') and b('T')) or \
		                                (value in b('NnFf') and b('F')) or b('?')
		    else:
		        value = u(value)
		        value = value.strip()
		    record.append(value)
		return record
	