import os
import xbmcaddon

addon = xbmcaddon.Addon(id='plugin.video.xstream')

class cGuiElement:

    DEFAULT_FOLDER_ICON = 'DefaultFolder.png'

    def __init__(self, sTitle = '', sSite = None, sFunction = None):
        self.__sType = 'video'
        self.__sMediaUrl = ''
        self.__sTitle = sTitle
        self.__sTitleSecond = ''
        self.__sDescription = ''
        self.__sThumbnail = ''
        self.__sIcon = self.DEFAULT_FOLDER_ICON
        self.__aItemValues = {}
        self.__aProperties = {}
        self.__aContextElements = []
        self.__sFanart = os.path.join(addon.getAddonInfo('path'),'fanart.jpg')
        self.__sSiteName = sSite
        self.__sFunctionName = sFunction
        self._sLanguage = ''
        self._sQuality = ''

    def setType(self, sType):
        self.__sType = sType

    def getType(self):
        return self.__sType

    def setMediaUrl(self, sMediaUrl):
        self.__sMediaUrl = sMediaUrl

    def getMediaUrl(self):
        return self.__sMediaUrl

    def setSiteName(self, sSiteName):
        self.__sSiteName = sSiteName

    def getSiteName(self):
        return self.__sSiteName

    def setFunction(self, sFunctionName):
        self.__sFunctionName = sFunctionName

    def getFunction(self):
        return self.__sFunctionName

    def setTitle(self, sTitle):
        self.__sTitle = sTitle;

    def getTitle(self):
        return self.__sTitle

    def setTitleSecond(self, sTitleSecond):
        self.__sTitleSecond = str(sTitleSecond)

    def getTitleSecond(self):
        return self.__sTitleSecond

    def setDescription(self, sDescription):
        self.__sDescription = sDescription
        self.__aItemValues['plot'] = sDescription

    def getDescription(self):
        return self.__sDescription

    def setThumbnail(self, sThumbnail):
        self.__sThumbnail = sThumbnail

    def getThumbnail(self):
        return self.__sThumbnail

    def setIcon(self, sIcon):
        self.__sIcon = sIcon

    def getIcon(self):
        return self.__sIcon
    
    def setFanart(self, sFanart):
        self.__sFanart = sFanart

    def getFanart(self):
        return self.__sFanart

    def addItemValue(self, sItemKey, sItemValue):
        self.__aItemValues[sItemKey] = sItemValue
        
    def setItemValues(self, aValueList):
        self.__aItemValues = aValueList

    def getItemValues(self):
        self.__aItemValues['title'] = self.getTitle()
        if self.getDescription() != '':
            self.__aItemValues['plot'] = self.getDescription()
        for sPropertyKey in self.__aProperties.keys():
            self.__aItemValues[sPropertyKey]=self.__aProperties[sPropertyKey]
        return self.__aItemValues
    
    def addItemProperties(self, sPropertyKey, sPropertyValue):
        self.__aProperties[sPropertyKey] = sPropertyValue
  
    def getItemProperties(self):
        for sItemValueKey in self.__aItemValues.keys():
            if not self.__aItemValues[sItemValueKey]=='':
                try:
                    self.__aProperties[sItemValueKey]=str(self.__aItemValues[sItemValueKey])
                except:
                    pass
        return self.__aProperties

    def addContextItem(self, oContextElement):
        self.__aContextElements.append(oContextElement)

    def getContextItems(self):
        return self.__aContextElements

    def setLanguage(self, sLang):
        self._sLanguage = sLang


