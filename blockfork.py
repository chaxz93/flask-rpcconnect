import requests
from base64 import b64encode
import logging
import datetime
import hashlib
import json
from flask import Flask, jsonify, flash, request, redirect, url_for
import os
from werkzeug.utils import secure_filename
import binascii
import codecs
import pprint

log = logging.getLogger('Savoir')

class Savoir():
    __id_count = 0

    def __init__(self,
        rpcuser,
        rpcpasswd,
        rpchost,
        rpcport,
        chainname,
        rpc_call=None
    ):
        self.__rpcuser = rpcuser
        self.__rpcpasswd = rpcpasswd
        self.__rpchost = rpchost
        self.__rpcport = rpcport
        self.__chainname = chainname
        self.__auth_header = ' '.join(
            ['Basic', b64encode(':'.join([rpcuser, rpcpasswd]).encode()).decode()]
        )
        self.__headers = {'Host': self.__rpchost,
            'User-Agent': 'Savoir v0.1',
            'Authorization': self.__auth_header,
            'Content-type': 'application/json'
            }
        self.__rpc_call = rpc_call

    def __getattr__(self, name):
        if name.startswith('__') and name.endswith('__'):
            # Python internal stuff
            raise AttributeError
        if self.__rpc_call is not None:
            name = "%s.%s" % (self.__rpc_call, name)
        return Savoir(self.__rpcuser,
            self.__rpcpasswd,
            self.__rpchost,
            self.__rpcport,
            self.__chainname,
            name)

    def __call__(self, *args):
        Savoir.__id_count += 1
        postdata = {'chain_name': self.__chainname,
            'version': '1.1',
            'params': args,
            'method': self.__rpc_call,
            'id': Savoir.__id_count}
        url = ''.join(['http://', self.__rpchost, ':', self.__rpcport])
        encoded = json.dumps(postdata)
        log.info("Request: %s" % encoded)
        r = requests.post(url, data=encoded, headers=self.__headers)
        if r.status_code == 200:
            log.info("Response: %s" % r.json())
            return r.json()['result']
        else:
            log.error("Error! Status code: %s" % r.status_code)
            log.error("Text: %s" % r.text)
            log.error("Json: %s" % r.json())
            return r.json()

rpcuser = 'multichainrpc'
rpcpasswd = '6rDnQbqPzeM5sBZoxWE6QNcgH69zGVwy5Use2Jhj48PM'
rpchost = '127.0.0.1'
rpcport = '7760'
chainname = 'chain1'

api = Savoir(rpcuser, rpcpasswd, rpchost, rpcport, chainname)

stream_text = 'ifrs2018' 
publisher_text = 'genesis'
key_text = 'sample-gaap'

rand_hex = binascii.b2a_hex(os.urandom(15))
converted_hex = rand_hex.hex()

rpc_getinfo = api.getinfo()
rpc_getpeerinfo = api.getpeerinfo()
rpc_listassets = api.listassets()
rpc_liststreamitems = api.liststreamitems(stream_text)
rpc_liststreamkeys = api.liststreamkeys(stream_text)
rpc_liststreamkeyitems = api.liststreamkeyitems('ifrs2018', 'sample-ifrs')

publish_wizard = api.publish(stream_text, key_text, converted_hex)

app = Flask(__name__)
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True
host = os.environ.get('IP', '127.0.0.1')
port = int(os.environ.get('PORT', 5000))

@app.route('/')
def index():
	return jsonify(rpc_getinfo), 200

@app.route('/getpeerinfo')
def getpeerinfo():
    return jsonify(rpc_getpeerinfo), 200

@app.route('/listassets')
def listassets():
    return jsonify(rpc_listassets), 200


@app.route('/liststreamitems')
def liststreamitems():
    return jsonify(rpc_liststreamitems), 200


@app.route('/liststreamkeys')
def liststreamkeys():
    return jsonify(rpc_liststreamkeys), 200

@app.route('/liststreamkeyitems')
def liststreamkeyitems():
    return jsonify(rpc_liststreamkeyitems), 200

app.run(host=host, port=port)