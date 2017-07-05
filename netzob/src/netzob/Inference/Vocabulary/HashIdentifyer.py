# -*- coding: utf-8 -*-

#+---------------------------------------------------------------------------+
#|          01001110 01100101 01110100 01111010 01101111 01100010            |
#|                                                                           |
#|               Netzob : Inferring communication protocols                  |
#+---------------------------------------------------------------------------+
#| Copyright (C) 2011-2017 Georges Bossert and Frédéric Guihéry              |
#| This program is free software: you can redistribute it and/or modify      |
#| it under the terms of the GNU General Public License as published by      |
#| the Free Software Foundation, either version 3 of the License, or         |
#| (at your option) any later version.                                       |
#|                                                                           |
#| This program is distributed in the hope that it will be useful,           |
#| but WITHOUT ANY WARRANTY; without even the implied warranty of            |
#| MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the              |
#| GNU General Public License for more details.                              |
#|                                                                           |
#| You should have received a copy of the GNU General Public License         |
#| along with this program. If not, see <http://www.gnu.org/licenses/>.      |
#+---------------------------------------------------------------------------+
#| @url      : http://www.netzob.org                                         |
#| @contact  : contact@netzob.org                                            |
#| @sponsors : Amossys, http://www.amossys.fr                                |
#|             Supélec, http://www.rennes.supelec.fr/ren/rd/cidre/           |
#+---------------------------------------------------------------------------+

#+---------------------------------------------------------------------------+
#| Standard library imports
#+---------------------------------------------------------------------------+
import re
import binascii
from collections import namedtuple

#+---------------------------------------------------------------------------+
#| Local application imports
#+---------------------------------------------------------------------------+
from netzob.Common.Utils.Decorators import typeCheck, NetzobLogger
from netzob.Model.Vocabulary.AbstractField import AbstractField



@NetzobLogger
class HashIdentifyer(object):
    """Hash identification based on well known regex patterns.

    """
    Prototype = namedtuple('Prototype', ['regex', 'hashes'])

    prototypes = [
        Prototype(
            regex=re.compile(r'^[a-f0-9]{4}$', re.IGNORECASE),
            hashes=[
            'CRC-16',
            'CRC-16-CCITT',
            'FCS-16']),
        Prototype(
            regex=re.compile(r'^[a-f0-9]{8}$', re.IGNORECASE),
            hashes=[
            'Adler-32',
            'CRC-32B',
            'FCS-32',
            'GHash-32-3',
            'GHash-32-5',
            'FNV-132',
            'Fletcher-32',
            'Joaat',
            'ELF-32',
            'XOR-32']),
        Prototype(
            regex=re.compile(r'^[a-f0-9]{6}$', re.IGNORECASE),
            hashes=[
            'CRC-24']),
        Prototype(
            regex=re.compile(r'^(\$crc32\$[a-f0-9]{8}.)?[a-f0-9]{8}$', re.IGNORECASE),
            hashes=[
            'CRC-32']),
        Prototype(
            regex=re.compile(r'^\+[a-z0-9\/.]{12}$', re.IGNORECASE),
            hashes=[
            'Eggdrop IRC Bot']),
        Prototype(
            regex=re.compile(r'^[a-z0-9\/.]{13}$', re.IGNORECASE),
            hashes=[
            'DES(Unix)',
            'Traditional DES',
            'DEScrypt']),
        Prototype(
            regex=re.compile(r'^[a-f0-9]{16}$', re.IGNORECASE),
            hashes=[
            'MySQL323',
            'DES(Oracle)',
            'Half MD5',
            'Oracle 7-10g',
            'FNV-164',
            'CRC-64']),
        Prototype(
            regex=re.compile(r'^[a-z0-9\/.]{16}$', re.IGNORECASE),
            hashes=[
            'Cisco-PIX(MD5)']),
        Prototype(
            regex=re.compile(r'^\([a-z0-9\/+]{20}\)$', re.IGNORECASE),
            hashes=[
            'Lotus Notes/Domino 6']),
        Prototype(
            regex=re.compile(r'^_[a-z0-9\/.]{19}$', re.IGNORECASE),
            hashes=[
            'BSDi Crypt']),
        Prototype(
            regex=re.compile(r'^[a-f0-9]{24}$', re.IGNORECASE),
            hashes=[
            'CRC-96(ZIP)']),
        Prototype(
            regex=re.compile(r'^[a-z0-9\/.]{24}$', re.IGNORECASE),
            hashes=[
            'Crypt16']),
        Prototype(
            regex=re.compile(r'^(\$md2\$)?[a-f0-9]{32}$', re.IGNORECASE),
            hashes=[
            'MD2']),
        Prototype(
            regex=re.compile(r'^[a-f0-9]{32}(:.+)?$', re.IGNORECASE),
            hashes=[
            'MD5',
            'MD4',
            'Double MD5',
            'LM',
            'RIPEMD-128',
            'Haval-128',
            'Tiger-128',
            'Skein-256(128)',
            'Skein-512(128)',
            'Lotus Notes/Domino 5',
            'Skype',
            'ZipMonster',
            'PrestaShop',
            'md5(md5(md5($pass)))',
            'md5(strtoupper(md5($pass)))',
            'md5(sha1($pass))',
            'md5($pass.$salt)',
            'md5($salt.$pass)',
            'md5(unicode($pass).$salt)',
            'md5($salt.unicode($pass))',
            'HMAC-MD5 (key = $pass)',
            'HMAC-MD5 (key = $salt)',
            'md5(md5($salt).$pass)',
            'md5($salt.md5($pass))',
            'md5($pass.md5($salt))',
            'md5($salt.$pass.$salt)',
            'md5(md5($pass).md5($salt))',
            'md5($salt.md5($salt.$pass))',
            'md5($salt.md5($pass.$salt))',
            'md5($username.0.$pass)']),
        Prototype(
            regex=re.compile(r'^(\$snefru\$)?[a-f0-9]{32}$', re.IGNORECASE),
            hashes=[
            'Snefru-128']),
        Prototype(
            regex=re.compile(r'^(\$NT\$)?[a-f0-9]{32}$', re.IGNORECASE),
            hashes=[
            'NTLM']),
        Prototype(
            regex=re.compile(r'^([^\\\/:*?"<>|]{1,20}:)?[a-f0-9]{32}(:[^\\\/:*?"<>|]{1,20})?$', re.IGNORECASE),
            hashes=[
            'Domain Cached Credentials']),
        Prototype(
            regex=re.compile(r'^([^\\\/:*?"<>|]{1,20}:)?(\$DCC2\$10240#[^\\\/:*?"<>|]{1,20}#)?[a-f0-9]{32}$',
                             re.IGNORECASE),
            hashes=[
            'Domain Cached Credentials 2']),
        Prototype(
            regex=re.compile(r'^{SHA}[a-z0-9\/+]{27}=$', re.IGNORECASE),
            hashes=[
            'SHA-1(Base64)',
            'Netscape LDAP SHA']),
        Prototype(
            regex=re.compile(r'^\$1\$[a-z0-9\/.]{0,8}\$[a-z0-9\/.]{22}(:.*)?$', re.IGNORECASE),
            hashes=[
            'MD5 Crypt',
            'Cisco-IOS(MD5)',
            'FreeBSD MD5']),
        Prototype(
            regex=re.compile(r'^0x[a-f0-9]{32}$', re.IGNORECASE),
            hashes=[
            'Lineage II C4']),
        Prototype(
            regex=re.compile(r'^\$H\$[a-z0-9\/.]{31}$', re.IGNORECASE),
            hashes=[
            'phpBB v3.x',
            'Wordpress v2.6.0/2.6.1',
            "PHPass' Portable Hash"]),
        Prototype(
            regex=re.compile(r'^\$P\$[a-z0-9\/.]{31}$', re.IGNORECASE),
            hashes=[
            u'Wordpress ≥ v2.6.2',
            u'Joomla ≥ v2.5.18',
            "PHPass' Portable Hash"]),
        Prototype(
            regex=re.compile(r'^[a-f0-9]{32}:[a-z0-9]{2}$', re.IGNORECASE),
            hashes=[
            'osCommerce',
            'xt:Commerce']),
        Prototype(
            regex=re.compile(r'^\$apr1\$[a-z0-9\/.]{0,8}\$[a-z0-9\/.]{22}$', re.IGNORECASE),
            hashes=[
            'MD5(APR)',
            'Apache MD5',
            'md5apr1']),
        Prototype(
            regex=re.compile(r'^{smd5}[a-z0-9$\/.]{31}$', re.IGNORECASE),
            hashes=[
            'AIX(smd5)']),
        Prototype(
            regex=re.compile(r'^[a-f0-9]{32}:[a-f0-9]{32}$', re.IGNORECASE),
            hashes=[
            'WebEdition CMS']),
        Prototype(
            regex=re.compile(r'^[a-f0-9]{32}:.{5}$', re.IGNORECASE),
            hashes=[
            u'IP.Board ≥ v2+']),
        Prototype(
            regex=re.compile(r'^[a-f0-9]{32}:.{8}$', re.IGNORECASE),
            hashes=[
            u'MyBB ≥ v1.2+']),
        Prototype(
            regex=re.compile(r'^[a-z0-9]{34}$', re.IGNORECASE),
            hashes=[
            'CryptoCurrency(Adress)']),
        Prototype(
            regex=re.compile(r'^[a-f0-9]{40}(:.+)?$', re.IGNORECASE),
            hashes=[
            'SHA-1',
            'Double SHA-1',
            'RIPEMD-160',
            'Haval-160',
            'Tiger-160',
            'HAS-160',
            'LinkedIn',
            'Skein-256(160)',
            'Skein-512(160)',
            'MangosWeb Enhanced CMS',
            'sha1(sha1(sha1($pass)))',
            'sha1(md5($pass))',
            'sha1($pass.$salt)',
            'sha1($salt.$pass)',
            'sha1(unicode($pass).$salt)',
            'sha1($salt.unicode($pass))',
            'HMAC-SHA1 (key = $pass)',
            'HMAC-SHA1 (key = $salt)',
            'sha1($salt.$pass.$salt)']),
        Prototype(
            regex=re.compile(r'^\*[a-f0-9]{40}$', re.IGNORECASE),
            hashes=[
            'MySQL5.x',
            'MySQL4.1']),
        Prototype(
            regex=re.compile(r'^[a-z0-9]{43}$', re.IGNORECASE),
            hashes=[
            'Cisco-IOS(SHA-256)']),
        Prototype(
            regex=re.compile(r'^{SSHA}[a-z0-9\/+]{38}==$', re.IGNORECASE),
            hashes=[
            'SSHA-1(Base64)',
            'Netscape LDAP SSHA',
            'nsldaps']),
        Prototype(
            regex=re.compile(r'^[a-z0-9=]{47}$', re.IGNORECASE),
            hashes=[
            'Fortigate(FortiOS)']),
        Prototype(
            regex=re.compile(r'^[a-f0-9]{48}$', re.IGNORECASE),
            hashes=[
            'Haval-192',
            'Tiger-192',
            'SHA-1(Oracle)',
            'OSX v10.4',
            'OSX v10.5',
            'OSX v10.6']),
        Prototype(
            regex=re.compile(r'^[a-f0-9]{51}$', re.IGNORECASE),
            hashes=[
            'Palshop CMS']),
        Prototype(
            regex=re.compile(r'^[a-z0-9]{51}$', re.IGNORECASE),
            hashes=[
            'CryptoCurrency(PrivateKey)']),
        Prototype(
            regex=re.compile(r'^{ssha1}[0-9]{2}\$[a-z0-9$\/.]{44}$', re.IGNORECASE),
            hashes=[
            'AIX(ssha1)']),
        Prototype(
            regex=re.compile(r'^0x0100[a-f0-9]{48}$', re.IGNORECASE),
            hashes=[
            'MSSQL(2005)',
            'MSSQL(2008)']),
        Prototype(
            regex=re.compile(
                r'^(\$md5,rounds=[0-9]+\$|\$md5\$rounds=[0-9]+\$|\$md5\$)[a-z0-9\/.]{0,16}(\$|\$\$)[a-z0-9\/.]{22}$',
                re.IGNORECASE),
            hashes=[
            'Sun MD5 Crypt']),
        Prototype(
            regex=re.compile(r'^[a-f0-9]{56}$', re.IGNORECASE),
            hashes=[
            'SHA-224',
            'Haval-224',
            'SHA3-224',
            'Skein-256(224)',
            'Skein-512(224)']),
        Prototype(
            regex=re.compile(r'^(\$2[axy]|\$2)\$[0-9]{2}\$[a-z0-9\/.]{53}$', re.IGNORECASE),
            hashes=[
            'Blowfish(OpenBSD)',
            'Woltlab Burning Board 4.x',
            'bcrypt']),
        Prototype(
            regex=re.compile(r'^[a-f0-9]{40}:[a-f0-9]{16}$', re.IGNORECASE),
            hashes=[
            'Android PIN']),
        Prototype(
            regex=re.compile(r'^(S:)?[a-f0-9]{40}(:)?[a-f0-9]{20}$', re.IGNORECASE),
            hashes=[
            'Oracle 11g/12c']),
        Prototype(
            regex=re.compile(r'^\$bcrypt-sha256\$(2[axy]|2)\,[0-9]+\$[a-z0-9\/.]{22}\$[a-z0-9\/.]{31}$', re.IGNORECASE),
            hashes=[
            'bcrypt(SHA-256)']),
        Prototype(
            regex=re.compile(r'^[a-f0-9]{32}:.{3}$', re.IGNORECASE),
            hashes=[
            'vBulletin < v3.8.5']),
        Prototype(
            regex=re.compile(r'^[a-f0-9]{32}:.{30}$', re.IGNORECASE),
            hashes=[
            u'vBulletin ≥ v3.8.5']),
        Prototype(
            regex=re.compile(r'^(\$snefru\$)?[a-f0-9]{64}$', re.IGNORECASE),
            hashes=[
            'Snefru-256']),
        Prototype(
            regex=re.compile(r'^[a-f0-9]{64}(:.+)?$', re.IGNORECASE),
            hashes=[
            'SHA-256',
            'RIPEMD-256',
            'Haval-256',
            'GOST R 34.11-94',
            'GOST CryptoPro S-Box',
            'SHA3-256',
            'Skein-256',
            'Skein-512(256)',
            'Ventrilo',
            'sha256($pass.$salt)',
            'sha256($salt.$pass)',
            'sha256(unicode($pass).$salt)',
            'sha256($salt.unicode($pass))',
            'HMAC-SHA256 (key = $pass)',
            'HMAC-SHA256 (key = $salt)']),
        Prototype(
            regex=re.compile(r'^[a-f0-9]{32}:[a-z0-9]{32}$', re.IGNORECASE),
            hashes=[
            'Joomla < v2.5.18']),
        Prototype(
            regex=re.compile(r'^[a-f-0-9]{32}:[a-f-0-9]{32}$', re.IGNORECASE),
            hashes=[
            'SAM(LM_Hash:NT_Hash)']),
        Prototype(
            regex=re.compile(r'^(\$chap\$0\*)?[a-f0-9]{32}[\*:][a-f0-9]{32}(:[0-9]{2})?$', re.IGNORECASE),
            hashes=[
            'MD5(Chap)',
            'iSCSI CHAP Authentication']),
        Prototype(
            regex=re.compile(r'^\$episerver\$\*0\*[a-z0-9\/=+]+\*[a-z0-9\/=+]{27,28}$', re.IGNORECASE),
            hashes=[
            'EPiServer 6.x < v4']),
        Prototype(
            regex=re.compile(r'^{ssha256}[0-9]{2}\$[a-z0-9$\/.]{60}$', re.IGNORECASE),
            hashes=[
            'AIX(ssha256)']),
        Prototype(
            regex=re.compile(r'^[a-f0-9]{80}$', re.IGNORECASE),
            hashes=[
            'RIPEMD-320']),
        Prototype(
            regex=re.compile(r'^\$episerver\$\*1\*[a-z0-9\/=+]+\*[a-z0-9\/=+]{42,43}$', re.IGNORECASE),
            hashes=[
            u'EPiServer 6.x ≥ v4']),
        Prototype(
            regex=re.compile(r'^0x0100[a-f0-9]{88}$', re.IGNORECASE),
            hashes=[
            'MSSQL(2000)']),
        Prototype(
            regex=re.compile(r'^[a-f0-9]{96}$', re.IGNORECASE),
            hashes=[
            'SHA-384',
            'SHA3-384',
            'Skein-512(384)',
            'Skein-1024(384)']),
        Prototype(
            regex=re.compile(r'^{SSHA512}[a-z0-9\/+]{96}$', re.IGNORECASE),
            hashes=[
            'SSHA-512(Base64)',
            'LDAP(SSHA-512)']),
        Prototype(
            regex=re.compile(r'^{ssha512}[0-9]{2}\$[a-z0-9\/.]{16,48}\$[a-z0-9\/.]{86}$', re.IGNORECASE),
            hashes=[
            'AIX(ssha512)']),
        Prototype(
            regex=re.compile(r'^[a-f0-9]{128}(:.+)?$', re.IGNORECASE),
            hashes=[
            'SHA-512',
            'Whirlpool',
            'Salsa10',
            'Salsa20',
            'SHA3-512',
            'Skein-512',
            'Skein-1024(512)',
            'sha512($pass.$salt)',
            'sha512($salt.$pass)',
            'sha512(unicode($pass).$salt)',
            'sha512($salt.unicode($pass))',
            'HMAC-SHA512 (key = $pass)',
            'HMAC-SHA512 (key = $salt)']),
        Prototype(
            regex=re.compile(r'^[a-f0-9]{136}$', re.IGNORECASE),
            hashes=[
            'OSX v10.7']),
        Prototype(
            regex=re.compile(r'^0x0200[a-f0-9]{136}$', re.IGNORECASE),
            hashes=[
            'MSSQL(2012)',
            'MSSQL(2014)']),
        Prototype(
            regex=re.compile(r'^\$ml\$[0-9]+\$[a-f0-9]{64}\$[a-f0-9]{128}$', re.IGNORECASE),
            hashes=[
            'OSX v10.8',
            'OSX v10.9']),
        Prototype(
            regex=re.compile(r'^[a-f0-9]{256}$', re.IGNORECASE),
            hashes=[
            'Skein-1024']),
        Prototype(
            regex=re.compile(r'^grub\.pbkdf2\.sha512\.[0-9]+\.([a-f0-9]{128,2048}\.|[0-9]+\.)?[a-f0-9]{128}$',
                             re.IGNORECASE),
            hashes=[
            'GRUB 2']),
        Prototype(
            regex=re.compile(r'^sha1\$[a-z0-9]+\$[a-f0-9]{40}$', re.IGNORECASE),
            hashes=[
            'Django(SHA-1)']),
        Prototype(
            regex=re.compile(r'^[a-f0-9]{49}$', re.IGNORECASE),
            hashes=[
            'Citrix Netscaler']),
        Prototype(
            regex=re.compile(r'^\$S\$[a-z0-9\/.]{52}$', re.IGNORECASE),
            hashes=[
            'Drupal > v7.x']),
        Prototype(
            regex=re.compile(r'^\$5\$(rounds=[0-9]+\$)?[a-z0-9\/.]{0,16}\$[a-z0-9\/.]{43}$', re.IGNORECASE),
            hashes=[
            'SHA-256 Crypt']),
        Prototype(
            regex=re.compile(r'^0x[a-f0-9]{4}[a-f0-9]{16}[a-f0-9]{64}$', re.IGNORECASE),
            hashes=[
            'Sybase ASE']),
        Prototype(
            regex=re.compile(r'^\$6\$(rounds=[0-9]+\$)?[a-z0-9\/.]{0,16}\$[a-z0-9\/.]{86}$', re.IGNORECASE),
            hashes=[
            'SHA-512 Crypt']),
        Prototype(
            regex=re.compile(
                r'^\$sha\$[a-z0-9]{1,16}\$([a-f0-9]{32}|[a-f0-9]{40}|[a-f0-9]{64}|[a-f0-9]{128}|[a-f0-9]{140})$',
                re.IGNORECASE),
            hashes=[
            'Minecraft(AuthMe Reloaded)']),
        Prototype(
            regex=re.compile(r'^sha256\$[a-z0-9]+\$[a-f0-9]{64}$', re.IGNORECASE),
            hashes=[
            'Django(SHA-256)']),
        Prototype(
            regex=re.compile(r'^sha384\$[a-z0-9]+\$[a-f0-9]{96}$', re.IGNORECASE),
            hashes=[
            'Django(SHA-384)']),
        Prototype(
            regex=re.compile(r'^crypt1:[a-z0-9+=]{12}:[a-z0-9+=]{12}$', re.IGNORECASE),
            hashes=[
            'Clavister Secure Gateway']),
        Prototype(
            regex=re.compile(r'^[a-f0-9]{112}$', re.IGNORECASE),
            hashes=[
            'Cisco VPN Client(PCF-File)']),
        Prototype(
            regex=re.compile(r'^[a-f0-9]{1329}$', re.IGNORECASE),
            hashes=[
            'Microsoft MSTSC(RDP-File)']),
        Prototype(
            regex=re.compile(
                r'^[^\\\/:*?"<>|]{1,20}[:]{2,3}([^\\\/:*?"<>|]{1,20})?:[a-f0-9]{48}:[a-f0-9]{48}:[a-f0-9]{16}$',
                re.IGNORECASE),
            hashes=[
            'NetNTLMv1-VANILLA / NetNTLMv1+ESS']),
        Prototype(
            regex=re.compile(
                r'^([^\\\/:*?"<>|]{1,20}\\)?[^\\\/:*?"<>|]{1,20}[:]{2,3}([^\\\/:*?"<>|]{1,20}:)?[^\\\/:*?"<>|]{1,20}:[a-f0-9]{32}:[a-f0-9]+$',
                re.IGNORECASE),
            hashes=[
            'NetNTLMv2']),
        Prototype(
            regex=re.compile(r'^\$(krb5pa|mskrb5)\$([0-9]{2})?\$.+\$[a-f0-9]{1,}$', re.IGNORECASE),
            hashes=[
            'Kerberos 5 AS-REQ Pre-Auth']),
        Prototype(
            regex=re.compile(
                r'^\$scram\$[0-9]+\$[a-z0-9\/.]{16}\$sha-1=[a-z0-9\/.]{27},sha-256=[a-z0-9\/.]{43},sha-512=[a-z0-9\/.]{86}$',
                re.IGNORECASE),
            hashes=[
            'SCRAM Hash']),
        Prototype(
            regex=re.compile(r'^[a-f0-9]{40}:[a-f0-9]{0,32}$', re.IGNORECASE),
            hashes=[
            'Redmine Project Management Web App']),
        Prototype(
            regex=re.compile(r'^(.+)?\$[a-f0-9]{16}$', re.IGNORECASE),
            hashes=[
            'SAP CODVN B (BCODE)']),
        Prototype(
            regex=re.compile(r'^(.+)?\$[a-f0-9]{40}$', re.IGNORECASE),
            hashes=[
            'SAP CODVN F/G (PASSCODE)']),
        Prototype(
            regex=re.compile(r'^(.+\$)?[a-z0-9\/.+]{30}(:.+)?$', re.IGNORECASE),
            hashes=[
            'Juniper Netscreen/SSG(ScreenOS)']),
        Prototype(
            regex=re.compile(r'^0x[a-f0-9]{60}\s0x[a-f0-9]{40}$', re.IGNORECASE),
            hashes=[
            'EPi']),
        Prototype(
            regex=re.compile(r'^[a-f0-9]{40}:[^*]{1,25}$', re.IGNORECASE),
            hashes=[
            u'SMF ≥ v1.1']),
        Prototype(
            regex=re.compile(r'^(\$wbb3\$\*1\*)?[a-f0-9]{40}[:*][a-f0-9]{40}$', re.IGNORECASE),
            hashes=[
            'Woltlab Burning Board 3.x']),
        Prototype(
            regex=re.compile(r'^[a-f0-9]{130}(:[a-f0-9]{40})?$', re.IGNORECASE),
            hashes=[
            'IPMI2 RAKP HMAC-SHA1']),
        Prototype(
            regex=re.compile(r'^[a-f0-9]{32}:[0-9]+:[a-z0-9_.+-]+@[a-z0-9-]+\.[a-z0-9-.]+$', re.IGNORECASE),
            hashes=[
            'Lastpass']),
        Prototype(
            regex=re.compile(r'^[a-z0-9\/.]{16}([:$].{1,})?$', re.IGNORECASE),
            hashes=[
            'Cisco-ASA(MD5)']),
        Prototype(
            regex=re.compile(r'^\$vnc\$\*[a-f0-9]{32}\*[a-f0-9]{32}$', re.IGNORECASE),
            hashes=[
            'VNC']),
        Prototype(
            regex=re.compile(r'^[a-z0-9]{32}(:([a-z0-9-]+\.)?[a-z0-9-.]+\.[a-z]{2,7}:.+:[0-9]+)?$', re.IGNORECASE),
            hashes=[
            'DNSSEC(NSEC3)']),
        Prototype(
            regex=re.compile(r'^(user-.+:)?\$racf\$\*.+\*[a-f0-9]{16}$', re.IGNORECASE),
            hashes=[
            'RACF']),
        Prototype(
            regex=re.compile(r'^\$3\$\$[a-f0-9]{32}$', re.IGNORECASE),
            hashes=[
            'NTHash(FreeBSD Variant)']),
        Prototype(
            regex=re.compile(r'^\$sha1\$[0-9]+\$[a-z0-9\/.]{0,64}\$[a-z0-9\/.]{28}$', re.IGNORECASE),
            hashes=[
            'SHA-1 Crypt']),
        Prototype(
            regex=re.compile(r'^[a-f0-9]{70}$', re.IGNORECASE),
            hashes=[
            'hMailServer']),
        Prototype(
            regex=re.compile(r'^[:\$][AB][:\$]([a-f0-9]{1,8}[:\$])?[a-f0-9]{32}$', re.IGNORECASE),
            hashes=[
            'MediaWiki']),
        Prototype(
            regex=re.compile(r'^[a-f0-9]{140}$', re.IGNORECASE),
            hashes=[
            'Minecraft(xAuth)']),
        Prototype(
            regex=re.compile(r'^\$pbkdf2(-sha1)?\$[0-9]+\$[a-z0-9\/.]+\$[a-z0-9\/.]{27}$', re.IGNORECASE),
            hashes=[
            'PBKDF2-SHA1(Generic)']),
        Prototype(
            regex=re.compile(r'^\$pbkdf2-sha256\$[0-9]+\$[a-z0-9\/.]+\$[a-z0-9\/.]{43}$', re.IGNORECASE),
            hashes=[
            'PBKDF2-SHA256(Generic)']),
        Prototype(
            regex=re.compile(r'^\$pbkdf2-sha512\$[0-9]+\$[a-z0-9\/.]+\$[a-z0-9\/.]{86}$', re.IGNORECASE),
            hashes=[
            'PBKDF2-SHA512(Generic)']),
        Prototype(
            regex=re.compile(r'^\$p5k2\$[0-9]+\$[a-z0-9\/+=-]+\$[a-z0-9\/+-]{27}=$', re.IGNORECASE),
            hashes=[
            'PBKDF2(Cryptacular)']),
        Prototype(
            regex=re.compile(r'^\$p5k2\$[0-9]+\$[a-z0-9\/.]+\$[a-z0-9\/.]{32}$', re.IGNORECASE),
            hashes=[
            'PBKDF2(Dwayne Litzenberger)']),
        Prototype(
            regex=re.compile(r'^{FSHP[0123]\|[0-9]+\|[0-9]+}[a-z0-9\/+=]+$', re.IGNORECASE),
            hashes=[
            'Fairly Secure Hashed Password']),
        Prototype(
            regex=re.compile(r'^\$PHPS\$.+\$[a-f0-9]{32}$', re.IGNORECASE),
            hashes=[
            'PHPS']),
        Prototype(
            regex=re.compile(r'^[0-9]{4}:[a-f0-9]{16}:[a-f0-9]{2080}$', re.IGNORECASE),
            hashes=[
            '1Password(Agile Keychain)']),
        Prototype(
            regex=re.compile(r'^[a-f0-9]{64}:[a-f0-9]{32}:[0-9]{5}:[a-f0-9]{608}$', re.IGNORECASE),
            hashes=[
            '1Password(Cloud Keychain)']),
        Prototype(
            regex=re.compile(
                r'^[a-f0-9]{256}:[a-f0-9]{256}:[a-f0-9]{16}:[a-f0-9]{16}:[a-f0-9]{320}:[a-f0-9]{16}:[a-f0-9]{40}:[a-f0-9]{40}:[a-f0-9]{32}$',
                re.IGNORECASE),
            hashes=[
            'IKE-PSK MD5']),
        Prototype(
            regex=re.compile(
                r'^[a-f0-9]{256}:[a-f0-9]{256}:[a-f0-9]{16}:[a-f0-9]{16}:[a-f0-9]{320}:[a-f0-9]{16}:[a-f0-9]{40}:[a-f0-9]{40}:[a-f0-9]{40}$',
                re.IGNORECASE),
            hashes=[
            'IKE-PSK SHA1']),
        Prototype(
            regex=re.compile(r'^[a-z0-9\/+]{27}=$', re.IGNORECASE),
            hashes=[
            'PeopleSoft']),
        Prototype(
            regex=re.compile(r'^crypt\$[a-f0-9]{5}\$[a-z0-9\/.]{13}$', re.IGNORECASE),
            hashes=[
            'Django(DES Crypt Wrapper)']),
        Prototype(
            regex=re.compile(r'^(\$django\$\*1\*)?pbkdf2_sha256\$[0-9]+\$[a-z0-9]+\$[a-z0-9\/+=]{44}$', re.IGNORECASE),
            hashes=[
            'Django(PBKDF2-HMAC-SHA256)']),
        Prototype(
            regex=re.compile(r'^pbkdf2_sha1\$[0-9]+\$[a-z0-9]+\$[a-z0-9\/+=]{28}$', re.IGNORECASE),
            hashes=[
            'Django(PBKDF2-HMAC-SHA1)']),
        Prototype(
            regex=re.compile(r'^bcrypt(\$2[axy]|\$2)\$[0-9]{2}\$[a-z0-9\/.]{53}$', re.IGNORECASE),
            hashes=[
            'Django(bcrypt)']),
        Prototype(
            regex=re.compile(r'^md5\$[a-f0-9]+\$[a-f0-9]{32}$', re.IGNORECASE),
            hashes=[
            'Django(MD5)']),
        Prototype(
            regex=re.compile(r'^\{PKCS5S2\}[a-z0-9\/+]{64}$', re.IGNORECASE),
            hashes=[
            'PBKDF2(Atlassian)']),
        Prototype(
            regex=re.compile(r'^md5[a-f0-9]{32}$', re.IGNORECASE),
            hashes=[
            'PostgreSQL MD5']),
        Prototype(
            regex=re.compile(r'^\([a-z0-9\/+]{49}\)$', re.IGNORECASE),
            hashes=[
            'Lotus Notes/Domino 8']),
        Prototype(
            regex=re.compile(r'^SCRYPT:[0-9]{1,}:[0-9]{1}:[0-9]{1}:[a-z0-9:\/+=]{1,}$', re.IGNORECASE),
            hashes=[
            'scrypt']),
        Prototype(
            regex=re.compile(r'^\$8\$[a-z0-9\/.]{14}\$[a-z0-9\/.]{43}$', re.IGNORECASE),
            hashes=[
            'Cisco Type 8']),
        Prototype(
            regex=re.compile(r'^\$9\$[a-z0-9\/.]{14}\$[a-z0-9\/.]{43}$', re.IGNORECASE),
            hashes=[
            'Cisco Type 9']),
        Prototype(
            regex=re.compile(
                r'^\$office\$\*2007\*[0-9]{2}\*[0-9]{3}\*[0-9]{2}\*[a-z0-9]{32}\*[a-z0-9]{32}\*[a-z0-9]{40}$',
                re.IGNORECASE),
            hashes=[
            'Microsoft Office 2007']),
        Prototype(
            regex=re.compile(
                r'^\$office\$\*2010\*[0-9]{6}\*[0-9]{3}\*[0-9]{2}\*[a-z0-9]{32}\*[a-z0-9]{32}\*[a-z0-9]{64}$',
                re.IGNORECASE),
            hashes=[
            'Microsoft Office 2010']),
        Prototype(
            regex=re.compile(
                r'^\$office\$\*2013\*[0-9]{6}\*[0-9]{3}\*[0-9]{2}\*[a-z0-9]{32}\*[a-z0-9]{32}\*[a-z0-9]{64}$',
                re.IGNORECASE),
            hashes=[
            'Microsoft Office 2013']),
        Prototype(
            regex=re.compile(r'^\$fde\$[0-9]{2}\$[a-f0-9]{32}\$[0-9]{2}\$[a-f0-9]{32}\$[a-f0-9]{3072}$', re.IGNORECASE),
            hashes=[
            u'Android FDE ≤ 4.3']),
        Prototype(
            regex=re.compile(r'^\$oldoffice\$[01]\*[a-f0-9]{32}\*[a-f0-9]{32}\*[a-f0-9]{32}$', re.IGNORECASE),
            hashes=[
            u'Microsoft Office ≤ 2003 (MD5+RC4)',
            u'Microsoft Office ≤ 2003 (MD5+RC4) collider-mode #1',
            u'Microsoft Office ≤ 2003 (MD5+RC4) collider-mode #2']),
        Prototype(
            regex=re.compile(r'^\$oldoffice\$[34]\*[a-f0-9]{32}\*[a-f0-9]{32}\*[a-f0-9]{40}$', re.IGNORECASE),
            hashes=[
            u'Microsoft Office ≤ 2003 (SHA1+RC4)',
            u'Microsoft Office ≤ 2003 (SHA1+RC4) collider-mode #1',
            u'Microsoft Office ≤ 2003 (SHA1+RC4) collider-mode #2']),
        Prototype(
            regex=re.compile(r'^(\$radmin2\$)?[a-f0-9]{32}$', re.IGNORECASE),
            hashes=['RAdmin v2.x']),
        Prototype(
            regex=re.compile(r'^{x-issha,\s[0-9]{4}}[a-z0-9\/+=]+$', re.IGNORECASE),
            hashes=['SAP CODVN H (PWDSALTEDHASH) iSSHA-1']),
        Prototype(
            regex=re.compile(r'^\$cram_md5\$[a-z0-9\/+=-]+\$[a-z0-9\/+=-]{52}$', re.IGNORECASE),
            hashes=['CRAM-MD5']),
        Prototype(
            regex=re.compile(r'^[a-f0-9]{16}:2:4:[a-f0-9]{32}$', re.IGNORECASE),
            hashes=['SipHash']),
        Prototype(
            regex=re.compile(r'^[a-f0-9]{4,}$', re.IGNORECASE),
            hashes=['Cisco Type 7']),
        Prototype(
            regex=re.compile(r'^[a-z0-9\/.]{13,}$', re.IGNORECASE),
            hashes=['BigCrypt']),
        Prototype(
            regex=re.compile(r'^(\$cisco4\$)?[a-z0-9\/.]{43}$', re.IGNORECASE),
            hashes=['Cisco Type 4']),
        Prototype(
            regex=re.compile(r'^bcrypt_sha256\$\$(2[axy]|2)\$[0-9]+\$[a-z0-9\/.]{53}$', re.IGNORECASE),
            hashes=['Django(bcrypt-SHA256)']),
        Prototype(
            regex=re.compile(r'^\$postgres\$.[^\*]+[*:][a-f0-9]{1,32}[*:][a-f0-9]{32}$', re.IGNORECASE),
            hashes=['PostgreSQL Challenge-Response Authentication (MD5)']),
        Prototype(
            regex=re.compile(r'^\$siemens-s7\$[0-9]{1}\$[a-f0-9]{40}\$[a-f0-9]{40}$', re.IGNORECASE),
            hashes=['Siemens-S7']),
        Prototype(
            regex=re.compile(r'^(\$pst\$)?[a-f0-9]{8}$', re.IGNORECASE),
            hashes=['Microsoft Outlook PST']),
        Prototype(
            regex=re.compile(r'^sha256[:$][0-9]+[:$][a-z0-9\/+]+[:$][a-z0-9\/+]{32,128}$', re.IGNORECASE),
            hashes=['PBKDF2-HMAC-SHA256(PHP)']),
        Prototype(
            regex=re.compile(r'^(\$dahua\$)?[a-z0-9]{8}$', re.IGNORECASE),
            hashes=['Dahua']),
        Prototype(
            regex=re.compile(r'^\$mysqlna\$[a-f0-9]{40}[:*][a-f0-9]{40}$', re.IGNORECASE),
            hashes=['MySQL Challenge-Response Authentication (SHA1)']),
        Prototype(
            regex=re.compile(
                r'^\$pdf\$[24]\*[34]\*128\*[0-9-]{1,5}\*1\*(16|32)\*[a-f0-9]{32,64}\*32\*[a-f0-9]{64}\*(8|16|32)\*[a-f0-9]{16,64}$',
                re.IGNORECASE),
            hashes=[
            'PDF 1.4 - 1.6 (Acrobat 5 - 8)']),
        Prototype(
            regex=re.compile(r'^([a-fA-F0-9]{2})+$', re.IGNORECASE),
            hashes=[
            'Hex string'
            ]),
        Prototype(
            regex=re.compile(r'^([a-zA-Z0-9+/]{4})*([a-zA-Z0-9+/]{4}|[a-zA-Z0-9+/]{2}==|[a-zA-Z0-9+/]{3}=)$'),
            hashes=['Base64'
            ])
    ]

    def __init__(self):
        pass

    @staticmethod
    @typeCheck(AbstractField)
    def identify(symbol):
        """
        Identify hash inside fields of a symbol. If there are no encoding functions,
        will transform to HexaString encoding function

        Args:
            symbol:

        Returns:

        """

        hI = HashIdentifyer()
        return hI.execute(symbol)

    @typeCheck(AbstractField)
    def execute(self, symbol):
        for field in symbol.fields:
            all_match = True
            prototypes_matched = []
            if len(field.encodingFunctions) != 0:
                self._logger.warning("You probably want to try this with no encoding functions on!")
                field.clearEncodingFunctions()
            #No encoding value
            for value in field.getValues():
                self._logger.warning("Trying match as ISO-8859-1")
                iso_value = value.decode("ISO-8859-1")
                for prototype in self.prototypes:
                    if not prototype.regex.match(iso_value):
                        all_match = False
                    else:
                        prototypes_matched.append(prototype)
            if all_match:
                self._logger.warning("Hash identifyed:\n"
                                               "Field:" + field.name + "\n"
                                               "Hash:")
                for prototype in prototypes_matched:
                    for hash in prototype.hashes:
                        self._logger.warning(hash + "\n")
            all_match = True
            prototypes_matched = []
            #Encoding value
            for value in field.getValues():
                self._logger.warning("Trying match as HexaString")
                hexa_string_value = str(binascii.hexlify(value))[2:-1] #Convert to HexaString without changing EncodingFunctions from field object
                for prototype in self.prototypes:
                    if not prototype.regex.match(hexa_string_value):
                        all_match = False
                    else:
                        prototypes_matched.append(prototype)
            if all_match:
                self._logger.warning("Hash identifyed:\n"
                                        "Field:" + field.name + "\n"
                                        "Hash:")
                for prototype in prototypes_matched:
                    for hash in prototype.hashes:
                        self._logger.warning(hash + "\n")



