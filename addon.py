"""
AIS playbox TV addon for kodi.

This Kodi addon allows you to play the free TV channels provided by the AIS
playbox device.
"""
import json
import random
import re
import requests
import sys
import xbmcaddon
import xbmcgui
import xbmcplugin
import zlib
from base64 import b64encode
from time import strftime
from urlparse import parse_qsl

AISWEB = "https://playbox.ais.co.th/AISWeb/"
# Without SSL GET_DEVICE_OWNER = "http://stbbe.ais.co.th:8080/getDeviceOwner"
GET_DEVICE_OWNER = "https://stbbe.ais.co.th:8443/getDeviceOwner"
TV_CHANNELS = "https://sifvideostore.s3.amazonaws.com/AIS/json/Page/NewTV.json.gz"
GET_USER_ID = AISWEB + "ServiceGetUserIdFromPrivateId.aspx"
CHECK_ENTITLEMENT = AISWEB + "ServiceCheckAssetEntitlementByUserId.aspx"
PLAYBOX_APP_KEY = "UHgZAVpacCXP/spFoX+S7Pwt/sM="
HEADERS = {
    'User-Agent': 'Dalvik/1.6.0 (Linux; U; Android 4.4.2; n200 Build/KOT49H)'}

plugin_url = sys.argv[0]
plugin_handle = int(sys.argv[1])


def get_tv_channels():
    """Retrieve the current list of TV Channels"""
    response = requests.get(TV_CHANNELS, headers=HEADERS)
    data = json.loads(zlib.decompress(response.content, 16+zlib.MAX_WBITS))
    flatten = [item for x in data['SubPage'] for item in x['Items']]
    unique = dict((i['ItemID'], i) for i in flatten).values()
    return sorted(unique, key=lambda item: item['ItemName'])


def map_channels(channels):
    """Creates a xbmc list of playable TV channels"""
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
    """Request the final playable URL
    This url contains a playlist with SQ and HQ streams.
    """
    parameters = {
        'appId': 'AND',
        'assetId': assetId,
        'assetType': 'CHANNEL',
        'deviceType': 'STB',
        'userId': xbmcplugin.getSetting(plugin_handle, 'userId'),
        'lang': 'en',
        'appKey': PLAYBOX_APP_KEY}
    data = {'JSONtext': json.dumps(parameters)}
    # Verify false due to problems in kodi v16 in macos with old python
    res = requests.post(CHECK_ENTITLEMENT, headers=HEADERS, data=data,
                        verify=False)
    return res.json()["StreamingInfo"][0]["URLInfo"]


def play_channel(channel):
    """Make kodi play a TV channel"""
    url = get_channel_url(channel)
    play_item = xbmcgui.ListItem("Channel")
    play_item.setPath(url)
    play_item.setInfo(type='Video', infoLabels={'Title': 'Channel'})
    play_item.setProperty("IsPlayable", "true")
    xbmcplugin.setResolvedUrl(plugin_handle, True, listitem=play_item)


def generate_command_id(serial):
    """AIS command ids"""
    timestamp = strftime('%m%d%Y%H%M%S')
    options = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    rand_ending = "".join([random.choice(options) for _ in range(4)])
    return "{0}-{1}{2}".format(serial, timestamp, rand_ending)


def get_device_owner(mac, serial):
    """Gets the internal/private/email id of the device owner"""
    device_id = b64encode('n200|null|{0}|{1}'.format(mac, serial))
    command_id = generate_command_id(serial)
    parameters = {
        'commandId': command_id,
        'deviceId': device_id}
    res = requests.get(GET_DEVICE_OWNER, params=parameters, headers=HEADERS,
                       verify=False)
    return res.json()["ownerId"]


def get_user_id_from_email(email):
    """Converts the email/private id to the user id used in channels"""
    parameters = {
        'PrivateId': email,
        # Not needed but just in case
        'appKey': PLAYBOX_APP_KEY}
    data = {'JSONtext': json.dumps(parameters)}
    res = requests.post(GET_USER_ID, headers=HEADERS, data=data,
                        verify=False)
    return res.json()["UserId"]


def get_user_id():
    """Get and save AIS user id and email/private id."""
    mac = xbmcplugin.getSetting(plugin_handle, 'playboxMAC').strip().upper()
    if re.match('^([0-9A-F]{2}[:]){5}([0-9A-F]{2})$', mac) is None:
        xbmcgui.Dialog().ok('AIS', 'Wrong MAC address')
        return
    serial = xbmcplugin.getSetting(plugin_handle, 'playboxSerial').strip()

    email = get_device_owner(mac, serial)
    user_id = get_user_id_from_email(email)

    myself = xbmcaddon.Addon()
    myself.setSetting('privateId', email)
    myself.setSetting('userId', user_id)


def check_settings():
    """Checks if there is a user id needed to play TV"""
    user_id = xbmcplugin.getSetting(plugin_handle, 'userId')
    if user_id:
        return
    get_user_id()


def router(paramstring):
    """Decides what to do based on script parameters"""
    check_settings()
    params = dict(parse_qsl(paramstring))
    # Nothing to do yet with those
    if not params:
        # Demo channel list
        channels = map_channels(get_tv_channels())
        xbmcplugin.addDirectoryItems(plugin_handle, channels, len(channels))
        xbmcplugin.addSortMethod(
                plugin_handle, xbmcplugin.SORT_METHOD_LABEL_IGNORE_THE)
        xbmcplugin.endOfDirectory(plugin_handle)
    elif params['action'] == 'play':
        play_channel(params['channel'])
    elif params['action'] == 'get_user_id':
        get_user_id()


if __name__ == '__main__':
    router(sys.argv[2][1:])
