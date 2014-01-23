import sys
import os
import logger
from resources.lib.config import cConfig
from resources.lib import common

class cPluginHandler:

    def __getFileNamesFromFolder(self, sFolder):
        aNameList = []
        items = os.listdir(sFolder)
        for sItemName in items:
            if sItemName.endswith('.py'):
                sItemName = os.path.basename(sItemName[:-3])
                aNameList.append(sItemName)
        return aNameList

    def __importPlugin(self, sName):
        try:
            plugin = __import__(sName, globals(), locals())
            sSiteName = plugin.SITE_NAME
            sPluginSettingsName = 'plugin_' + sName                        
        except Exception, e:
            logger.error("Can't import plugin: %s :%s" % (sName, e))
            return False, None, None, None
        try:
            sSiteIcon = plugin.SITE_ICON
            return True, sSiteName, sPluginSettingsName, sSiteIcon
        except:
            return True, sSiteName, sPluginSettingsName, ''

    def getAvailablePlugins(self):
        oConfig = cConfig()

        sFolder =  common.addonPath
        sIconFolder = os.path.join(sFolder, 'resources','art','sites')
        sFolder = os.path.join(sFolder, 'sites')

        # xbox hack
        sFolder = sFolder.replace('\\', '/')
        logger.info('sites folder: ' + sFolder)

        aFileNames = self.__getFileNamesFromFolder(sFolder)

        aPlugins = []
        for sFileName in aFileNames:
            logger.info('load plugin: '+ str(sFileName))

            # wir versuchen das plugin zu importieren
            aPlugin = self.__importPlugin(sFileName)
            if aPlugin[0]:
                sSiteName = aPlugin[1]
                sPluginSettingsName = aPlugin[2]
                if aPlugin[3] != '':
                    sSiteIcon = os.path.join(sIconFolder, aPlugin[3])
                else:
                    sSiteIcon = ''

                # existieren zu diesem plugin die an/aus settings
                bPlugin = oConfig.getSetting(sPluginSettingsName)
                if (bPlugin != ''):
                    # settings gefunden
                    if (bPlugin == 'true'):
                        aPlugins.append(self.__createAvailablePluginsItem(sSiteName, sFileName, sSiteIcon))
                else:
                   # settings nicht gefunden, also schalten wir es trotzdem sichtbar
                   aPlugins.append(self.__createAvailablePluginsItem(sSiteName, sFileName, sSiteIcon))

        return aPlugins

    def __createAvailablePluginsItem(self, sPluginName, sPluginIdentifier, sPluginIcon):
        aPluginEntry = []
        aPluginEntry.append(sPluginName)
        aPluginEntry.append(sPluginIdentifier)
        aPluginEntry.append(sPluginIcon)
        return aPluginEntry