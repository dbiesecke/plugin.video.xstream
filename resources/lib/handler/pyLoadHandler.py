from resources.lib.util import cUtil
from resources.lib.config import cConfig
from resources.lib.gui.gui import cGui
from resources.lib.handler.requestHandler import cRequestHandler
from resources.lib.config import cConfig
import logger
import urllib
import urllib2
import sys


class cPyLoadHandler:

	
	def sendToPyLoad(self, sUrl):
		logger.info('PyLoad link: '+str(sUrl))
		if(self.__sendLinkToCore(sUrl)==True):
			cGui().showInfo('PyLoad', 'Link gesendet', 5)
		else:
			cGui().showInfo('PyLoad', 'Fehler beim Senden des Links!', 5)
			
	def __sendLinkToCore(self, sUrl):
		logger.info('Sending link...')
		
		try:
			
			py_host=cConfig().getSetting('pyload_host')
			py_port=cConfig().getSetting('pyload_port')
			py_user=cConfig().getSetting('pyload_user')
			py_passwd=cConfig().getSetting('pyload_passwd')
			mydata=[('username',py_user),('password',py_passwd)]
			mydata=urllib.urlencode(mydata)

			#check if host has a leading http://
			if(py_host.find('http://') != 0):
				logger.info('adding http:// on top of pyload_host')
				py_host = 'http://'+py_host

			req=urllib2.Request(py_host+':'+py_port+'/api/login', mydata)
			req.add_header("Content-type", "application/x-www-form-urlencoded")
			page=urllib2.urlopen(req).read()
			page=page[1:]
			session=page[:-1]
			opener = urllib2.build_opener()
			opener.addheaders.append(('Cookie', 'beaker.session.id='+session))
			sock = opener.open(py_host+':'+py_port+'/api/addPackage?name=""&links=["' + sUrl + '"]')
			logger.info('123')
			content = sock.read()
			sock.close()
			return True
		except urllib2.HTTPError, e:
			logger.info('unable to send link: Error= '+str(sys.exc_info()[0]))
			logger.info(e.code)
			logger.info(e.read())
			try:
				sock.close()
			except:
				logger.info('unable to close socket...')
			return False
