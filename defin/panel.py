import sys,os
import curses
import select
import time
from SDP import *
from SatRegister import *

class Panel:
	
	_SATNAME_COLS=12
	_DATETIME_COLS=30
	_DATETIME_FMT="%a %b %d %H:%M:%S %Z %Y"
	_FIELDSEP=5
	_MainPanel = -1
	_InfoPanel = 0
	_StatusBar = "Press 'q' to exit | STATUS BAR | "
	_StatusInfo = None

	def __init__(self, SatReg):
		self.satreg = SatReg
		self.wobj = curses.initscr()
		#self.drawMainPanel()
		self.active = self._MainPanel
		


	def drawMainPanel(self, statusinfo = None):
		k = 0
		cursor_x = 0
		cursor_y = 0
		
		stdscr = self.wobj
		
		curses.noecho()
		curses.cbreak()
		stdscr.keypad(1)
		
		
		# Clear and refresh the screen for a blank canvas
		stdscr.clear()
		stdscr.refresh()
		
		# Start colors in curses
		curses.start_color()
		curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)
		curses.init_pair(2, curses.COLOR_YELLOW, curses.COLOR_CYAN)
		curses.init_pair(3, curses.COLOR_BLACK, curses.COLOR_WHITE)	
		
		# Initialization
		stdscr.clear()
		height, width = stdscr.getmaxyx()	
		
		# Declaration of strings
		title_text = "Next multicast transmission of satellite passes"[:width-1]
		number_blanks = (width-len(title_text))//2
		titlebar = '{message: <{fill}}'.format(message=title_text, fill=len(title_text)+number_blanks)
		titlebar = '{message: >{fill}}'.format(message=titlebar, fill=len(titlebar)+number_blanks)
		

		
		# Render status bar
		if statusinfo is None:
			statusinfo = self._StatusInfo

		if statusinfo is None:
			statusbarstr = self._StatusBar 
		else:
			statusbarstr = self._StatusBar + statusinfo


		stdscr.attron(curses.color_pair(3))
		stdscr.addstr(height-1, 0, statusbarstr)
		stdscr.addstr(height-1, len(statusbarstr), " " * (width - len(statusbarstr) - 1))
		stdscr.attroff(curses.color_pair(3))

		
		# Turning on attributes for title
		stdscr.attron(curses.color_pair(2))
		stdscr.attron(curses.A_BOLD)
		
		# Rendering title
		
		# Centering calculations
		#start_x_title = int((width // 2) - (len(title) // 2) - len(title) % 2)
		start_x_title = 0
		start_y_title = 0
		stdscr.addstr(start_y_title, start_x_title, titlebar)
		
		# Turning off attributes for title
		stdscr.attroff(curses.color_pair(2))
		stdscr.attroff(curses.A_BOLD)

		# Print satellite summary
		self._FIELDSEP=(width-(self._SATNAME_COLS + 2 * self._DATETIME_COLS))//3
		for i in self.satreg._SatRegister.keys():
			
			# Render line
			index = '{message: >{fill}}'.format(message=i, fill=2)
			satname = self.satreg._SatRegister[i].sessionname
			satname = '{message: >{fill}}'.format(message=satname, fill=self._SATNAME_COLS)
			starttime = time.strftime(self._DATETIME_FMT,time.gmtime(self.satreg._SatRegister[i].time[0][0]))
			starttime = '{message: <{fill}}'.format(message=starttime, fill=self._DATETIME_COLS)
			endtime = time.strftime(self._DATETIME_FMT,time.gmtime(self.satreg._SatRegister[i].time[0][1]))
			endtime = '{message: <{fill}}'.format(message=endtime, fill=self._DATETIME_COLS)
			FS = " "*self._FIELDSEP
			satline = index + FS + satname + FS + starttime + FS + endtime
			
			stdscr.attron(curses.color_pair(1))
			stdscr.addstr(i+1, 0, satline[:width-1])
			#stdscr.addstr(i+1, len(satline), " " * (width - len(satline) - 1))
			stdscr.attroff(curses.color_pair(1))

		stdscr.move(height-1, width-1)
		# Refresh the screen
		stdscr.refresh()
		self.active = self._MainPanel
				
	
	def drawInfoPanel(self, satidx):
		cursor_x = 0
		cursor_y = 0
		
		stdscr = self.wobj
		
		curses.noecho()
		curses.cbreak()
		stdscr.keypad(1)
		
		
		# Clear and refresh the screen for a blank canvas
		stdscr.clear()
		stdscr.refresh()
		
		# Start colors in curses
		curses.start_color()
		curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)
		curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)
		curses.init_pair(3, curses.COLOR_BLACK, curses.COLOR_WHITE)	
		
		# Initialization
		stdscr.clear()
		height, width = stdscr.getmaxyx()	
		
		# Declaration of strings
		title_text = "Next multicast transmission of satellite passes"[:width-1]
		number_blanks = (width-len(title_text))//2
		titlebar = '{message: <{fill}}'.format(message=title_text, fill=len(title_text)+number_blanks)
		titlebar = '{message: >{fill}}'.format(message=titlebar, fill=len(titlebar)+number_blanks)
		
		# Render status bar
		if self._StatusInfo is None:
			statusbarstr = self._StatusBar
		else:
			statusbarstr = self._StatusBar + self._StatusInfo
		
		
		# Render status bar
		stdscr.attron(curses.color_pair(3))
		stdscr.addstr(height-1, 0, statusbarstr)
		stdscr.addstr(height-1, len(statusbarstr), " " * (width - len(statusbarstr) - 1))
		stdscr.attroff(curses.color_pair(3))
		
		# Turning on attributes for title
		stdscr.attron(curses.color_pair(2))
		stdscr.attron(curses.A_BOLD)

		
		# Centering calculations
		#start_x_title = int((width // 2) - (len(title) // 2) - len(title) % 2)
		start_x_title = 0
		start_y_title = 0
		
		# Rendering title
		stdscr.addstr(start_y_title, start_x_title, titlebar)
		
		# Turning off attributes for title
		stdscr.attroff(curses.color_pair(2))
		stdscr.attroff(curses.A_BOLD)

		if satidx > len(self.satreg._SatRegister) -1:
			return 0
		SDPobj = self.satreg._SatRegister[satidx]
		
		title_text = "Satellite : "
		title_text = '{message: <{fill}}'.format(message = title_text, fill=len(title_text))
		stdscr.attron(curses.color_pair(2))
		stdscr.addstr(1, 5, title_text[:width-1])		
		
		panel_text = '{message: <{fill}}'.format(message = SDPobj.sessionname, fill=width)	
		stdscr.attron(curses.color_pair(1))
		stdscr.addstr(1, 20, panel_text[:width-1])
		
		
		title_text = "Information : "
		title_text = '{message: <{fill}}'.format(message = title_text, fill=len(title_text))
		stdscr.attron(curses.color_pair(2))
		stdscr.addstr(2, 5, title_text[:width-1])			
		
		panel_text = '{message: <{fill}}'.format(message = SDPobj.information, fill=width)	
		stdscr.attron(curses.color_pair(1))
		stdscr.addstr(2, 20, panel_text[:width-1])
		
		title_text = "URL : "
		title_text = '{message: <{fill}}'.format(message = title_text, fill=len(title_text))
		stdscr.attron(curses.color_pair(2))
		stdscr.addstr(3, 5, title_text[:width-1])		
		
		panel_text = '{message: <{fill}}'.format(message = SDPobj.URI, fill=width)	
		stdscr.attron(curses.color_pair(1))
		stdscr.addstr(3, 20, panel_text[:width-1])
		
		
		title_text = "Start Time : "
		title_text = '{message: <{fill}}'.format(message = title_text, fill=len(title_text))
		stdscr.attron(curses.color_pair(2))
		stdscr.addstr(4, 5, title_text[:width-1])		

		starttime = time.strftime(self._DATETIME_FMT,time.gmtime(SDPobj.time[0][0]))
		starttime = '{message: <{fill}}'.format(message = starttime, fill=self._DATETIME_COLS)
		stdscr.attron(curses.color_pair(1))
		stdscr.addstr(4, 20, starttime[:width-1])

		title_text = "End Time : "
		title_text = '{message: <{fill}}'.format(message = title_text, fill=len(title_text))
		stdscr.attron(curses.color_pair(2))
		stdscr.addstr(5, 5, title_text[:width-1])
						
		endtime = time.strftime(self._DATETIME_FMT,time.gmtime(SDPobj.time[0][1]))
		endtime = '{message: <{fill}}'.format(message = endtime, fill=self._DATETIME_COLS)	
		stdscr.attron(curses.color_pair(1))
		stdscr.addstr(5, 20, endtime[:width-1])

		title_text = "Multicast IP : "
		title_text = '{message: <{fill}}'.format(message = title_text, fill=len(title_text))
		stdscr.attron(curses.color_pair(2))
		stdscr.addstr(6, 5, title_text[:width-1])
						
		ipmcast = '{message: <{fill}}'.format(message = SDPobj.connection[2], fill=15)
		stdscr.attron(curses.color_pair(1))
		stdscr.addstr(6, 20, ipmcast[:width-1])
		
		for media in SDPobj.media_list:

			panel_text = "media"
			panel_text = '{message: <{fill}}'.format(message = panel_text, fill=len(panel_text))
			stdscr.attron(curses.color_pair(2))
			stdscr.addstr(8, 5, panel_text[:width-1])
						
			panel_text = '{message: <{fill}}'.format(message = media.media, fill=len(str(media.media)))
			stdscr.attron(curses.color_pair(1))
			stdscr.addstr(9, 5, panel_text[:width-1])		
			
			panel_text = "port"
			panel_text = '{message: <{fill}}'.format(message = panel_text, fill=len(panel_text))
			stdscr.attron(curses.color_pair(2))
			stdscr.addstr(8, 20, panel_text[:width-1])
						
			panel_text = '{message: <{fill}}'.format(message = media.port, fill=len(str(media.port)))
			stdscr.attron(curses.color_pair(1))
			stdscr.addstr(9, 20, panel_text[:width-1])
			
			panel_text = "protocol"
			panel_text = '{message: <{fill}}'.format(message = panel_text, fill=len(panel_text))
			stdscr.attron(curses.color_pair(2))
			stdscr.addstr(8, 35, panel_text[:width-1])
						
			panel_text = '{message: <{fill}}'.format(message = media.transport, fill=len(str(media.transport)))
			stdscr.attron(curses.color_pair(1))
			stdscr.addstr(9, 35, panel_text[:width-1])			
				
			panel_text = "format"
			panel_text = '{message: <{fill}}'.format(message = panel_text, fill=len(panel_text))
			stdscr.attron(curses.color_pair(2))
			stdscr.addstr(8, 50, panel_text[:width-1])
						
			panel_text = '{message: <{fill}}'.format(message = media.formats, fill=len(str(media.formats)))
			stdscr.attron(curses.color_pair(1))
			stdscr.addstr(9, 50, panel_text[:width-1])								
			
			if len(media.attributes) > 0:
				i = 0
				for att in media.attributes:
					if len(att.split(':'))	== 2:
						attname, value = att.split(':')
						panel_text =  attname +  " : "
						panel_text = '{message: <{fill}}'.format(message = panel_text, fill=len(panel_text))
						stdscr.attron(curses.color_pair(2))
						stdscr.addstr(12 + i, 5, panel_text[:width-1])
						panel_text = value			
						panel_text = '{message: >{fill}}'.format(message = panel_text, fill=len(panel_text))
						stdscr.attron(curses.color_pair(1))
						stdscr.addstr(12 + i, 25, panel_text[:width-1])	
						i = i + 1							



		stdscr.move(height-1, width-1)
		# Refresh the screen
		stdscr.refresh()
		self._InfoPanel = satidx
		self.active = self._InfoPanel
				

	def StatusInfo(self, text):
		self._StatusInfo = str(text)
		
		
			
			

def main():
	
	
	sdp1 = """\
v=0
o=mhandley 2890844526 2890842807 IN IP4 tgs.upc.edu
s=OSCAR-7
i=OSCAR-7 data multicasting
u=http://tgs.upc.edu/oscar7
e=mjh@isi.edu (Mark Handley)
c=IN IP4 239.10.10.9/127
t=1552557431 1552558031
a=recvonly
m=application 5500 udp GNURadio
a=BkName: USRP Source
a=SampleFmt: Complex
a=SampleRate: 6.25Msps
a=Carrier:1.961GHz
a=Antenna Gain: 25dB
""".splitlines()


	sdp2 = """\
v=0
o=mhandley 1345678931 1838482808 IN IP4 tgs.upc.edu
s=ISS
i=ISS data multicasting
u=http://tgs.upc.edu/iss
e=mjh@isi.edu (Mark Handley)
c=IN IP4 239.10.10.10/127
t=1552562431 1552563031
a=recvonly
m=application 5000 udp GNURadio
a=BkName: USRP Source
a=SampleFmt: Complex
a=SampleRate: 6.25Msps
a=Carrier:1.951GHz
a=Antenna Gain: 25dB
""".splitlines()


	sdp3 = """\
v=0
o=mhandley 4000441234 401032110 IN IP4 tgs.upc.edu
s=HUBBLE
i=HUBBLE data multicasting
u=http://tgs.upc.edu/hubble
e=mjh@isi.edu (Mark Handley)
c=IN IP4 239.10.10.12/127
t=1552565431 1552566031
a=recvonly
m=application 4500 udp GNURadio
a=BkName: USRP Source
a=SampleFmt: Complex
a=SampleRate: 6.25Msps
a=Carrier:1.931GHz
a=Antenna Gain: 25dB
""".splitlines()



	# Build some imaginary passing dates
	sdp_parser = SDPParser(sdp1)
	sdp_parser.run()
	sdpsession1 = SDPSession(sdp_parser.outbox)
	sdp_parser = SDPParser(sdp2)
	sdp_parser.run()
	sdpsession2 = SDPSession(sdp_parser.outbox)
	sdp_parser = SDPParser(sdp3)
	sdp_parser.run()
	sdpsession3 = SDPSession(sdp_parser.outbox)	
	sdp_parser = SDPParser(sdp1)
	sdp_parser.run()
	sdpsessionN = SDPSession(sdp_parser.outbox)
	
	#summary1 = (sdpsession1.sessionname, sdpsession1.time[0][0], sdpsession1.time[0][1])
	#summary2 = (sdpsession2.sessionname, sdpsession2.time[0][0], sdpsession2.time[0][1])
	#summary3 = (sdpsession3.sessionname, sdpsession3.time[0][0], sdpsession3.time[0][1])
	
	SatR = SatRegister()
	
	a = Panel(SatR)
	
	SatR.add_satellite(sdpsession1)
	SatR.add_satellite(sdpsession2)
	SatR.add_satellite(sdpsession3)
	a.drawMainPanel("MainPanel")
	


	while True:
		# inputs: The list of file descriptors (also socket descriptors) that we want the SO watch for them for reading (input events)
		# for example: 
		# inputs = [sys.stdin, socket_tcp_listen, socket_tcp_client ]
		inputs = [sys.stdin]
		try:
			# Select return 3 lists. read_rdy, write_rdy and except_rdy.
			# For read_dry: This list holds the file descriptors which were in "inputs" list and now they are ready to be read
			# This list can have:
			#   0 elements ([]) because select exits due to other event (for example timeout)
			#   1 element: any of sys.stdin, socket_tcp_listen or socket_tcp_client. The one that is ready to be read
			#   2 elements: any set of two elements from "inputs": They are the two elemnents that are ready to be read
			#   3 elements: .....

			read_rdy, write_rdy, except_rdy = select.select(inputs,[],[], 5.0)

			# Check if there are some file descritor ready to be read:
			if len(read_rdy) > 0:
				# In this case, due to inputs has only one element, if read_rdy is not None it can only because the sys.stdin is ready for reading
				# If we have several file descriptors in "inputs" list, then, we have to check for anyone in the read_rdy list:
				# if sys.stdin in read_rdy:
				# 	......
				# if socket_tcp_listen in read_rdy:
				#   ........
				#
				# in this case we call getch() blocking function that will NOT block beacause there is a "key code" waiting to be read 
				k = a.wobj.getch()
				# Check if key pressed was 'q'
				if k == ord('q'):
					curses.endwin()
					break 
				# Check if we are showing the mainPanel with the summary list of satellites
				if a.active == a._MainPanel:
					maxsats = len(a.satreg._SatRegister)
					# Check if key ascii code is in the range from '0' (ascii 48) to ascii maxsats + 48:
					# In other words ... check if keypressed a number between 0  and maxsats-1
					if (k-48) > -1 and (k-48) < maxsats :
						# Display Detailed information of satellite indexed by the keypressed
						a.StatusInfo("Satellite idx %s" % (k-48))
						a.drawInfoPanel(k-48)
				# If we are showind Satellite Details Panel, then go back to the MainPanel
				elif a.active == a._InfoPanel:
					a.drawMainPanel("MainPanel")
			# Check if ready list is []. It means select exited due to timeout
			if len(read_rdy) == 0:
				# Time out: In the case we code an silly example
				# Every time a timeout occurs, a sessionN satellite is deleted from the system
				if len(a.satreg._SatRegister) != 0:
					for i in a.satreg._SatRegister.keys():
						SDPSessionObj = a.satreg._SatRegister[i]
						if SDPSessionObj == sdpsessionN:
							SatR.del_satellite(SDPSessionObj)
							a.drawMainPanel("MainPanel")
							break
			
		except:
			if a.active == a._MainPanel: 
				a.drawMainPanel("MainPanel")
			elif a.active == a._InfoPanel:
				a.drawInfoPanel(a._InfoPanel)
		

if __name__ == "__main__":
    main()

