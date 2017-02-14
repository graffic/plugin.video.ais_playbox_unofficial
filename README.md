# AIS Playbox for Kodi - Unofficial

Kodi plugin to enjoy AIS playbox content. For now it only has free TV.

## Settings

You're gonna need your playbox mac address and serial number.

The first time you use the plugin, it will retrieve the `userId` needed to open
the streams. After the first time you can check your user id in the settings.

## Reverse engineering notes

### UserId

It is retrieved in two steps. First we find the owner of the playbox and then
we retrieve the userId from that owner id (called PrivateId).

### UserId in the device

The only setting needed is a `userId`. One easy way to obtain it is to open
a shell (adb shell) in your **rooted** playbox system and get it from this
file: `/data/data/com.ais.mimo.AISOnAirTV/shared_prefs/MioTVGOPref.xml`

Take the value from the entry: `<string name="PREF_USERID">...</string>`

### UserId as the device gets it.

When the device register itself, the backend returns the user id. This method
requires to fake the password registration step the device does and since the
security is not really good (there is no password), I decided not to use the
`ServiceAISLogin.aspx` endpoint.

If the current endpoint stops working, the Login endpoint is a viable
alternative to get the userId

