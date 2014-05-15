#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
Todo
- Acrescentar Listas de Veículos
- Acrescentar Lista de Reporter
- Colocar os idiomas de acordo com o presente no Settings.xml
- Permitir escolher o formato de reprodução
- Colocar os cinco videos mais recentes no menu principal, juntamente com uma opção
- Corrigir o Google Analytics, para permitir a contagem de todos os videos vistos (verificar)
"""

import xbmc, xbmcaddon, xbmcplugin, xbmcgui, urllib, urllib2, sys, json, re, time, datetime, HTMLParser, os, binascii, httplib, urlparse
local = xbmcaddon.Addon(id='plugin.video.mbtv')
#print os.path.join( local.getAddonInfo('path'), 'resources', 'lib' )
sys.path.append( os.path.join( local.getAddonInfo('path'), 'resources', 'lib' )) 

from ga import *

h = HTMLParser.HTMLParser()

addon_id='plugin.video.mbtv'
selfAddon = xbmcaddon.Addon(id=addon_id)
addonfolder = selfAddon.getAddonInfo('path')
title = selfAddon.getAddonInfo('name')
icon = selfAddon.getAddonInfo('icon')
ADDON = selfAddon
menuescolha = xbmcgui.Dialog().select
mensagemok = xbmcgui.Dialog().ok
mensagemprogresso = xbmcgui.DialogProgress()

ficheiroglobal="http://www5.mercedes-benz.com/en/tv/tv.json"
videourl="http://www5.mercedes-benz.com/media/video/%s_en_560p.mov"
videobaseurl="http://www5.mercedes-benz.com/en/tv/%s/video.json"



def playMedia(title, thumbnail, link, mediaType='Video') :
    """Plays a video

    Arguments:
    title: the title to be displayed
    thumbnail: the thumbnail to be used as an icon and thumbnail
    link: the link to the media to be played
    mediaType: the type of media to play, defaults to Video. Known values are Video, Pictures, Music and Programs
    """
    li = xbmcgui.ListItem(label=title, iconImage=thumbnail, thumbnailImage=thumbnail, path=link)
    li.setInfo(type=mediaType, infoLabels={ "Title": title })
    xbmcPlayer = xbmc.Player(xbmc.PLAYER_CORE_AUTO)
    xbmcPlayer.play(item=link, listitem=li)

def exists(url):
    host, path = urlparse.urlparse(url)[1:3]    # elems [1] and [2]
    conn = httplib.HTTPConnection(host)
    conn.request('HEAD', path)
    response = conn.getresponse()
    conn.close()
    return response.status == 200

def get_params():
    param=[]
    paramstring=sys.argv[2]
    if len(paramstring)>=2:
        params=sys.argv[2]
        cleanedparams=params.replace('?','')
        if (params[len(params)-1]=='/'):
                params=params[0:len(params)-2]
        pairsofparams=cleanedparams.split('&')
        param={}
        for i in range(len(pairsofparams)):
            splitparams={}
            splitparams=pairsofparams[i].split('=')
            if (len(splitparams))==2:
                param[splitparams[0]]=splitparams[1]
    return param
    
    
def json_get(url):
    req = urllib2.Request(url)
    req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
    req.add_header('Accept', 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8')
    data = json.load(urllib2.urlopen(req))
    return data

def eliminatags(valor):
    texto = re.sub('<[^>]*>', '', valor)
    return texto

def json_post(data,url):
    data = json.dumps(data)
    req = urllib2.Request(url, data, {'Content-Type': 'application/json'})
    f = urllib2.urlopen(req)
    response = f.read()
    f.close()

def addDir(name,url,mode,iconimage,pasta):
    u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)+"&name="+urllib.quote_plus(name)
    #print u
    if pasta == False:
        contextmen = []
        contextmen.append(('Information', 'XBMC.RunPlugin(%s?mode=10&url=%s)' % (sys.argv[0], url)))
    ok=True
    liz=xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=iconimage)
    liz.setProperty('fanart_image', addonfolder + '/fanart.jpg')
    if pasta == False:
        liz.addContextMenuItems(contextmen, replaceItems=True)
    ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=pasta)
    return ok

def listaelementostodos():
    js= json_get(ficheiroglobal)
    for i in js["clips"]:
        addDir(eliminatags(i["title"].encode('utf-8')),i["slug"],2, i["thumbnail_url_large"], False)

def listaelementosReporter():
    js= json_get(ficheiroglobal)
    for i in js["clips"]:
        if i["reporter"] == True:
            addDir(eliminatags(i["title"].encode('utf-8')),i["slug"],2, i["thumbnail_url_large"], False)

def listaelementosfiltro(url):
    js= json_get(ficheiroglobal)
    for i in js["clips"]:
        if i["resortText"] == url:
            addDir(eliminatags(i["title"].encode('utf-8')),i["slug"],2, i["thumbnail_url_large"], False)

def listaelementosvehicles():
    js= json_get(ficheiroglobal)
    addDir("All","All",4,addonfolder+'/fanart.jpg',True)
    for i in js["filter"]["series"]:
        addDir(i["en"],i["en"],4,addonfolder + '/fanart.jpg',True)

def listatodosveiculos():
    js= json_get(ficheiroglobal)
    for i in js["clips"]:
        if i["resortText"] == "Vehicles":
            addDir(eliminatags(i["title"].encode('utf-8')),i["slug"],2, i["thumbnail_url_large"], False)

def listacategoriaveiculos(url):
    js= json_get(ficheiroglobal)
    for i in js["clips"]:
        if i["seriesText"] == url:
            addDir(eliminatags(i["title"].encode('utf-8')),i["slug"],2, i["thumbnail_url_large"], False)

def listaelementoinicial():
    reporter = False
    js= json_get(ficheiroglobal)
    addDir("All","All",3,addonfolder+'/fanart.jpg',True)
    for i in js["filter"]["resorts"]:
        if i["en"]=="Reporter":
            reporter = True
        addDir(i["en"],i["en"],3,addonfolder + '/fanart.jpg',True)
    if reporter == False:
        addDir("Reporter","Reporter",4,addonfolder + '/fanart.jpg',True)

def mostralateral(url):
    js2=json_get(videobaseurl % url)
    textojanela=eliminatags(js2["teaser"][0]["copy"].encode('utf-8'))
    titulojanela = eliminatags(js2["teaser"][0]["head"].encode('utf-8'))
    duration = js2["duration"]
    durationtext = time.strftime('%H:%M:%S', time.gmtime(duration))
    textojanela+= ("\n\nDuration: %s" % durationtext)
    janela_lateral(titulojanela, textojanela)

def janela_lateral(label,texto):
    xbmc.executebuiltin("ActivateWindow(10147)")
    window = xbmcgui.Window(10147)
    xbmc.sleep(100)
    window.getControl(1).setLabel(label)
    window.getControl(5).setText(texto)

def reproduzficheiro(url):
    js2=json_get(videobaseurl % url)
    GA("none",url)
    qualidade = int(selfAddon.getSetting('format'))
    if qualidade == 3:
        dadosescolha=['Try 1080p','Highest Original (hd)','Lowest Original (sd)']
        index = menuescolha("Quality:", dadosescolha)
        if index > -1:
            qualidade = index
        else:
            return
    if qualidade == 1:
        urldovideoultra=js2["rendition"]["hd"]
    elif qualidade == 2:
        urldovideoultra=js2["rendition"]["sd"]
    elif qualidade == 0:
        #urldovideoultra = urldovideo.replace("_720p", "_1080p")
        valorvideohd = js2["rendition"]["hd"]
        urldovideoultra = valorvideohd.replace("_720p", "_1080p")
        if not exists(urldovideoultra):
            urldovideoultra=valorvideohd
    else:
        return
    playMedia(eliminatags(js2["title"].encode('utf-8')),js2["poster"]["embed"],urldovideoultra)


#########################################################################################################
#NAVEGAÇÃO                                                                                              #
#########################################################################################################




params=get_params()
url=None
name=None
mode=None
iconimage=None

try:
    url=urllib.unquote_plus(params["url"])
except:
    pass
try:
    name=urllib.unquote_plus(params["name"])
except:
    pass
try:
    mode=int(params["mode"])
except:
    pass
try:
    iconimage=urllib.unquote_plus(params["iconimage"])
except:
    pass

#print "Mode: "+str(mode)
#print "URL: "+str(url)
#print "Name: "+str(name)
#print "Iconimage: "+str(iconimage)

###############################################################################################################
#                                                   MODOS                                                     #
###############################################################################################################

if mode==None or url==None or len(url)<1:
#inicial, carrega a lista de todos os videos ou categorias conforme as definições
    if selfAddon.getSetting('start') == "1":
        listaelementostodos()
    else:
        listaelementoinicial()
elif mode==1:
#Não utilizado
    #listar_videos(url)
    print url
elif mode==2:
#Reproduz o ficheiro que vem no url
    reproduzficheiro(url)
    mode=None

elif mode==3:
#Ou carrega o ficheiro ou carrega as categorias "all"- todos os videos (categoria All), url os videos da categoria
    if url == "All":
        listaelementostodos()
    elif url == "Vehicles":
        listaelementosvehicles()
    else: 
        listaelementosfiltro(url) 

elif mode==4:
#Carrega lista referente ao Reporter
    if url == "All":
        listatodosveiculos()
    elif url == "Reporter":
        listaelementosReporter()
    else:
        listacategoriaveiculos(url)      
    
    #selfAddon.openSettings()
elif mode== 10: mostralateral(url)

xbmcplugin.endOfDirectory(int(sys.argv[1]))



