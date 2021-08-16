# -*- coding: utf-8 -*-
#
#----------------------------------------------------------------
#
#    VTDroid
#    Copyright (C) 2021  Nagoya Institute of Technology, Hiroki Inayoshi
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <https://www.gnu.org/licenses/>."
#
#----------------------------------------------------------------
#

source = {
    'Landroid/telephony/TelephonyManager;->getDeviceId()Ljava/lang/String;': 'IMEI1',
    'Landroid/telephony/TelephonyManager;->getDeviceId(I)Ljava/lang/String;': 'IMEI1',
    'Landroid/telephony/TelephonyManager;->getImei()Ljava/lang/String;': 'IMEI1',
    'Landroid/provider/Settings$Secure;->getString(Landroid/content/ContentResolver;Ljava/lang/String;)Ljava/lang/String;': 'AndroidId',
    'Landroid/provider/Settings$System;->getString(Landroid/content/ContentResolver;Ljava/lang/String;)Ljava/lang/String;': 'AndroidId',
    'Landroid/telephony/TelephonyManager;->getSimSerialNumber()Ljava/lang/String;': 'ICCID',
    'Landroid/telephony/TelephonyManager;->getSubscriberId()Ljava/lang/String;': 'IMSI',
    'Landroid/telephony/TelephonyManager;->getLine1Number()Ljava/lang/String;': 'PhoneNumber',
    'Landroid/net/wifi/WifiInfo;->getMacAddress()Ljava/lang/String;': 'MACAddress',
    'Landroid/location/Location;->getLatitude()D': 'GPS_LAT',
    'Landroid/location/Location;->getLongitude()D': 'GPS_LON',
    'Landroid/os/Build;->getSerial()Ljava/lang/String;': 'Build.Serial',
    'Lcom/google/android/gms/ads/identifier/AdvertisingIdClient$Info;->getId()Ljava/lang/String;': 'AdId',
    'Ljava/util/UUID;->randomUUID()Ljava/util/UUID;': 'GUID',
    'Lcom/google/firebase/iid/FirebaseInstanceId;->getId()Ljava/lang/String;': 'FirebaseInstanceId',
}
