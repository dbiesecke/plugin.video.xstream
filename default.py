#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-
from os import getcwd
from os.path import join
from sys import path
from xbmc import translatePath
from xbmc import log
import xbmcaddon

__settings__ = xbmcaddon.Addon(id='plugin.video.xstream')
__cwd__ = __settings__.getAddonInfo('path')

# Add different library path
path.append(translatePath(join(__cwd__, "resources", "lib")))
path.append(translatePath(join(__cwd__, "resources", "lib", "gui")))
path.append(translatePath(join(__cwd__, "resources", "lib", "handler")))
path.append(translatePath(join(__cwd__, "resources", "art", "sites")))
path.append(translatePath(join(__cwd__, "sites")))

log("The new sys.path list: %s" % sys.path, level = xbmc.LOGDEBUG)

# Run xstream
from xstream import run
log('*---- Running xStream, version %s ----*' % __settings__.getAddonInfo('version'))
#import cProfile
#cProfile.run('run()',translatePath(join(__cwd__,'xstream.pstats')))
run()