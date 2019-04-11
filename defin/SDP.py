import re


class AllDone(Exception):
   pass




class SDPParser:
    """\
    SDPParser() -> new SDPParser component.
    Parses Session Description Protocol data (see RFC 4566)  Outputs a dict
    containing the parsed data from its "outbox" outbox.
    """

    outbox = {}
               
    def __init__(self, str_sdp):
        self.str_sdp = str_sdp
        self.idx = 0


    def readline(self):
        if self.idx == len(self.str_sdp):
            raise AllDone
            return ''
        retval = self.str_sdp[self.idx]
        self.idx = self.idx + 1
        return retval

    def run(self):

        session = {}
        mandatory = "XXX"
        try:
            line = self.readline()
            type,key,value = _parseline(line)

            while 1:
                # begin by parsing the session section
                session = {}
                mandatory = "vost"
                multiple_allowed = "abtr"
                single_allowed = "vosiuepcbzk"
                most_recent_t = None

                while type != "m":

                    # check to see if we've been getting SDP data, then another 'v' has come along
                    # signifying the start of a new one
                    if type=="v" and "v" not in mandatory:
                        break
                    
                    mandatory=mandatory.replace(type,"")
                    assert((type in single_allowed) or (type in multiple_allowed))
                    single_allowed=single_allowed.replace(type,"")

                    if type in multiple_allowed:
                        if type=="r":
                            assert(most_recent_t is not None)
                            most_recent_t[2].append(value)     # tag repeats into list on end of time field
                        else:
                            session[key] = session.get(key,[])
                            session[key].append(value)
                    else:
                        session[key] = value
                
                    line = self.readline() 
                    type,key,value = _parseline(line)

                # we've hit an 'm' so its the end of the session section
                assert(mandatory=="")
                    
                # now move onto media sections
                
                mandatory_additional=""
                if "c" in single_allowed:
                    mandatory_additional+="c"
                    
                session['media'] = []

                # do a media section
                while type=="m":
                    mandatory = "" + mandatory_additional
                    multiple_allowed = "a"
                    single_allowed = "icbk"
                    
                    media={key:value}
                    session['media'].append(media)
                    
                    line = self.readline()
                    type,key,value = _parseline(line)
                    
                    while type != "m" and type != "v":
                        mandatory=mandatory.replace(type,"")
                        assert((type in single_allowed) or (type in multiple_allowed))
                        single_allowed=single_allowed.replace(type,"")
                        
                        if type in multiple_allowed:
                            media[key] = media.get(key,[])
                            media[key].append(value)
                        else:
                            media[key] = value
                    
                        line = self.readline()
                        type,key,value = _parseline(line)

                    # end of media section
                    assert(mandatory=="")
                    
                # end of complete SDP file (we've hit another 'v' signifying the start of a new one)
                self.sendOutParsedSDP(session)
            
        except AllDone:
            if mandatory=="":
                self.sendOutParsedSDP(session)
            
      


    def sendOutParsedSDP(self,session):
        # normalise it a bit first
        if "connection" in session:
            for media in session['media']:
                media['connection'] = session['connection']
                
        #self.send(session,"outbox")
        #print session
        self.outbox = session



class SDPSession:
	def __init__(self, sdp_dict):	
		self.media_list = []
		self._average_time = 0
		self._interval_number = 0
		self._last_timestamp = 0
		self._total_interval_time = 0
        			
		for key in sdp_dict.keys():
			if key != 'media':
				#print "Add Obj attr %s, val %s" % (key, sdp_dict[key])
				setattr(self,key,sdp_dict[key])
			else:
				for idx in range(0,len(sdp_dict['media'])):
					media, port, numports, protocol, fmt = sdp_dict['media'][idx]['media']
					if sdp_dict['media'][idx].has_key('bandwidth'):
						bandwidth = sdp_dict['media'][idx]['bandwidth']
					else:
						bandwidth = None
						
					if sdp_dict['media'][idx].has_key('attribute'):
						attributes = sdp_dict['media'][idx]['attribute']
					else:
						attributes = None
						
					if sdp_dict['media'][idx].has_key('connection'):
						connection = sdp_dict['media'][idx]['connection']
					else:
						connection = None						
						
					self.media_list.append(SDPMedia(media, port, protocol, numports, fmt, connection, attributes, bandwidth))
		#print self
					
	def setLast_timestamp(self, new_time):
		if self._last_timestamp == 0:
			self._interval_number = 1
			self._last_timestamp = new_time

		else:
			interval = new_time - self._last_timestamp
			#print " interval value: ", interval
			# se guarda la hora del ultimo paquete recibido
			self._last_timestamp = new_time
			self._average_time = (interval + self._total_interval_time) / self._interval_number
			# se suma despues el nuevo paquete y se calcula el tiempo total entre intervalos
			self._total_interval_time = self._average_time * self._interval_number
			self._interval_number = self._interval_number + 1
			#print " packet number: ", self._interval_number
	
	
	def intervalPacket(self, new_time):
		interval = new_time - self._last_timestamp
		if self._average_time != 0:
	
			if interval/self._average_time > 10 or interval/self._average_time > 3600:
				# si es mas grande devolvemos 1 para borrar el paquete
				return 1
			else:
				return 0
		else:
			return 0
	
	def __eq__(self, other):
		OtherObjAttrsNames = other.__dict__.keys()
		if len(OtherObjAttrsNames) != len(self.__dict__.keys()):
			return False
		#if len(self.media_list) != len(other.media_list):
		#	print "En __eq__"
		#	print self
		#	print "other"
		#	print other
		#	#print len(self.media_list), len(other.media_list) 
		#	return False
			
		for attr in self.__dict__.keys():
			if attr in ('_average_time','_interval_number','_last_timestamp','_total_interval_time'):
				continue
			if attr not in OtherObjAttrsNames:
				#print "attr %s not in other set" % attr
				return False
			if attr != 'media_list':
				#print "Checking attr %s" % attr
				if getattr(self,attr) != getattr(other,attr):
					#print "False"
					return False
			else:
				pass
				#othermlist = other.media_list
				#for MediaItem in self.media_list:
				#	rv = False
				#	for OtherMedia in othermlist:
				#		if MediaItem == OtherMedia:
				#			othermlist.remove(OtherMedia)
				#			rv = True
				#	rv =  rv & rv
				#if rv == False:
				#	return False					
		return True

	def __str__(self):
		for k,v in self.__dict__.items():
			if k != "media_list":
				print "Session attr %s: %s" % (k,v)
		print "media_list %s" % self.media_list	
		for mediaobj in self.media_list:
			print mediaobj

		return ""				
			
				


class SDPMedia:
	
	def __init__(self, media, port, transport, port_count=1, formats=None, connection=None, attributes=None, bandwidth_info=None):
		
		self.media = media
		self.port = port
		self.transport = transport
		self.port_count = port_count
		self.formats = formats
		self.connection = connection
		self.attributes = attributes if attributes is not None else []
		self.bandwidth_info = bandwidth_info if bandwidth_info is not None else []
		
	def __eq__(self,other):
		result =(self.media == other.media) & \
				(self.port == other.port) & \
                (self.transport == other.transport) & \
                (self.port_count == other.port_count) & \
                (self.formats == other.formats) & \
 				(self.connection == other.connection) & \
                (self.attributes == other.attributes) & \
                (self.port_count == other.port_count) & \
                (self.bandwidth_info == other.bandwidth_info)
                
                return result

	def __str__(self):
		for k,v in self.__dict__.items():
			print "      media attr %s: %s" % (k,v)
		return ""
        
def _parseline(line):
    match = re.match("^(.)=(.*)",line)
    
    type,value = match.group(1), match.group(2)
    
    if type=="v":
        assert(value=="0")
        return type, 'protocol_version', int(value)
                
    elif type=="o":
        user,sid,ver,ntype,atype,addr = re.match("^ *(\S+) +(\d+) +(\d+) +(IN) +(IP[46]) +(.+)",value).groups()
        return type, 'origin', (user,int(sid),int(ver),ntype,atype,addr)
                
    elif type=="s":
        return type, 'sessionname', value
                
    elif type=="i":
        return type, 'information', value
                    
    elif type=="u":
        return type, 'URI', value
                    
    elif type=="e":
        return type, 'email', value
                    
    elif type=="p":
        return type, 'phone', value
                    
    elif type=="c":
        if re.match("^ *IN +IP4 +.*$",value):
            match = re.match("^ *IN +IP4 +([^/]+)(?:/(\d+)(?:/(\d+))?)? *$",value)
            ntype,atype = "IN","IP4"
            addr,ttl,groupsize = match.groups()
            if ttl is None:
                ttl=127
            if groupsize is None:
                groupsize=1
        elif re.match("^ *IN +IP6 +.*$",value):
            match = re.match("^ *IN +IP6 +([abcdefABCDEF0123456789:.]+)(?:/(\d+))? *$")
            ntype,atype = "IN","IP6"
            addr,groupsize = match.groups()
        else:
            assert(False)
        
        return type, 'connection', (ntype,atype,addr,ttl,groupsize)

    elif type=="b":
        mode,rate = \
        re.match("^ *((?:AS)|(?:CT)|(?:X-[^:]+)):(\d+) *$",value).groups()
        bitspersecond=long(rate)*1000
        return type, 'bandwidth', (mode,bitspersecond)
    
    elif type=="t":
        start,stop = [ long(x) for x in re.match("^ *(\d+) +(\d+) *$",value).groups() ]
        repeats = []
        
        return type, 'time', (start,stop,repeats)

    elif type=="r":
        terms=re.split("\s+",value)
        parsedterms = []
        for term in terms:
            value, unit = re.match("^\d+([dhms])?$").groups()
            value = long(value) * {None:1, "s":1, "m":60, "h":3600, "d":86400}[unit]
            parsedterms.append(value)
        
        interval,duration=parsedterms[0], parsedterms[1]
        offsets=parsedterms[2:]
        return type, 'repeats', (interval,duration,offsets)

    elif type=="z":
        adjustments=[]
        while value.strip() != "":
            adjtime,offset,offsetunit,value = re.match("^ *(\d+) +([+-]?\d+)([dhms])? *?(.*)$",value).groups()
            adjtime=long(adjtime)
            offset=long(offset) * {None:1, "s":1, "m":60, "h":3600, "d":86400}[offsetunit]
            adjustments.append((adjtime,offset))

        return type, 'timezone adjustments', adjustments

    elif type=="k":
        method,value = re.match("^(clear|base64|uri|prompt)(?:[:](.*))?$",value).groups()
        return type, "encryption", (method,value)

    elif type=="a":
        return type, 'attribute', value

    elif type=="m":
        media, port, numports, protocol, fmt = re.match("^(audio|video|text|application|message) +(\d+)(?:[/](\d+))? +([^ ]+) +(.+)$",value).groups()
        port=int(port)
        if numports is None:
            numports=1
        else:
            numports=int(numports)
        return type, 'media', (media,port,numports,protocol,fmt)

    else:
		return type, 'unknown', value



if __name__ == "__main__":


    sdp = """\
v=0
o=mhandley 2890844526 2890842807 IN IP4 126.16.64.4
s=SDP Seminar
i=A Seminar on the session description protocol
u=http://www.cs.ucl.ac.uk/staff/M.Handley/sdp.03.ps
e=mjh@isi.edu (Mark Handley)
c=IN IP4 224.2.17.12/127
t=2873397496 2873404696
a=recvonly
m=audio 49170 RTP/AVP 0
m=video 51372 RTP/AVP 31
m=application 32416 udp wb
a=orient:portrait
""".splitlines()

    sdp2 = """\
v=0
o=jonhny 2890844526 2890842807 IN IP4 126.16.64.4
s=SDP Seminar
i=A Seminar on the session description protocol
u=http://www.cs.ucl.ac.uk/staff/M.Handley/sdp.03.ps
e=mjh@isi.edu (Mark Handley)
c=IN IP4 224.2.17.12/127
t=2873397496 2873404696
a=recvonly
m=audio 49170 RTP/AVP 0
m=video 51372 RTP/AVP 31
m=application 32416 udp wb
a=orient:portrait
""".splitlines()

    a = SDPParser(sdp) 
    a.run()
    #print a.outbox
    b=SDPSession(a.outbox)
    
    a = SDPParser(sdp2) 
    a.run()
    #print a.outbox
    c=SDPSession(a.outbox)

    print b.__dict__.keys()
    print len(b.media_list)
    print b.media_list[0].transport
    
    if b == c:
		print "b and c are equal" 
    else:
		print "b and c are different"

 
