# AIS Playbox for Kodi - Unofficial

Kodi plugin to enjoy AIS playbox content. For now it only has free TV.

## Settings

The only setting needed is a `userId`. One easy way to obtain it is to open
a shell (adb shell) in your **rooted** playbox system and get it from this
file: `/data/data/com.ais.mimo.AISOnAirTV/shared_prefs/MioTVGOPref.xml`

Take the value from the entry: `<string name="PREF_USERID">...</string>`

It is possible to obtain the `userId` with code, but it is in the ToDo list.
