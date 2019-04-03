

class SatRegister():
	"""
	An Ordered Dictionary of Satellite SDPObj's
	Order key is pass initial time
	"""
	
	_SatRegister = {}
	def __init__(self):
		pass
		
	def add_satellite(self, SDPobj):
		if len(self._SatRegister) == 0:
			self._SatRegister[0] = SDPobj
			return 1
		else:
			for i in self._SatRegister.keys():
				if self._SatRegister[i] == SDPobj:
					return 0
					
			for i in self._SatRegister.keys():
				if self._SatRegister[i].time[0][0] > SDPobj.time[0][0]:
					for k in range(len(self._SatRegister),i,-1):
						self._SatRegister[k] = self._SatRegister[k-1]
					self._SatRegister[i] = SDPobj
					return 1
			self._SatRegister[i+1] = SDPobj	
			return 1
			
	def del_satellite(self, SDPobj):
		for i in self._SatRegister.keys():
			if self._SatRegister[i] == SDPobj:
				if len(self._SatRegister)-1 == 0:
					self._SatRegister = {}
					return 1					
				for k in range(i,len(self._SatRegister)-1):
					self._SatRegister[k] = self._SatRegister[k+1]
				del self._SatRegister[k+1]
				return 1
		return 0	
		
	def getkey(self, SDPobj):
		for key, val in self._SatRegister.items():
			if SDPobj == val:
				return k
		return -1
				
