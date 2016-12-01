import json
import requests
import sys
import xbmcgui
import xbmcplugin
import zlib
from itertools import chain
from urlparse import parse_qsl

TV_CHANNELS = "https://sifvideostore.s3.amazonaws.com/AIS/json/Page/NewTV.json.gz"
CHECK_ENTITLEMENT = "https://playbox.ais.co.th/AISWeb/ServiceCheckAssetEntitlementByUserId.aspx"
PLAYBOX_APP_KEY = "UHgZAVpacCXP/spFoX+S7Pwt/sM="
HEADERS = {
    'User-Agent': 'Dalvik/1.6.0 (Linux; U; Android 4.4.2; n200 Build/KOT49H)'}

plugin_url = sys.argv[0]
plugin_handle = int(sys.argv[1])
print "HANDLE: ", plugin_handle


def get_tv_channels():
    response = requests.get(TV_CHANNELS, headers=HEADERS)
    data = json.loads(zlib.decompress(response.content, 16+zlib.MAX_WBITS))
    flatten = [item for x in data['SubPage'] for item in x['Items']]
    unique = dict((i['ItemID'], i) for i in flatten).values()
    return sorted(unique, key=lambda item: item['ItemName'])

def map_channels(channels):
    final_list = []
    for channel in channels:
        list_item = xbmcgui.ListItem(label=channel['ItemName'])
        list_item.setArt({'thumb': channel['ItemIcon'],
                          'icon': channel['ItemIcon']})
        list_item.setInfo('video', {'title': channel['ItemName']})
        list_item.setProperty('IsPlayable', 'true')
        url = '{0}?action=play&channel={1}'.format(
                 plugin_url, channel['ItemID'])
        final_list.append((url, list_item, False))
    return final_list

def get_channel_url(assetId):
    parameters = {
        'appId': 'AND',
        'assetId': assetId,
        'assetType': 'CHANNEL',
        'deviceType': 'STB',
        'userId': xbmcplugin.getSetting(plugin_handle, 'userId'),
        'lang': 'en',
        'appKey': 'UHgZAVpacCXP/spFoX+S7Pwt/sM='}
    data = {'JSONtext': json.dumps(parameters)}
    # Verify false due to problems in kodi v16 in macos with old python
    res = requests.post(CHECK_ENTITLEMENT, headers=HEADERS, data=data,
            verify=False)
    return res.json()["StreamingInfo"][0]["URLInfo"]

def play_channel(channel):
    url = get_channel_url(channel)
    print plugin_handle, url
    play_item = xbmcgui.ListItem("Channel")
    play_item.setPath(url)
    play_item.setInfo(type='Video', infoLabels={'Title': 'Channel'})
    play_item.setProperty("IsPlayable", "true")
    xbmcplugin.setResolvedUrl(plugin_handle, True, listitem=play_item)


def router(paramstring):
    params = dict(parse_qsl(paramstring))
    # Nothing to do yet with those
    if not params:
        # Demo channel list
        channels = map_channels(get_tv_channels())
        xbmcplugin.addDirectoryItems(plugin_handle, channels, len(channels))
        xbmcplugin.addSortMethod(plugin_handle, xbmcplugin.SORT_METHOD_LABEL_IGNORE_THE)
        xbmcplugin.endOfDirectory(plugin_handle)
    elif params['action'] == 'play':
        play_channel(params['channel'])


if __name__ == '__main__':
    router(sys.argv[2][1:])
