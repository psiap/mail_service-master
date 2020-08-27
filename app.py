# -*- coding: utf-8 -*-
import json

from socks import ProxyConnectionError, GeneralProxyError
from proxy import SocksIMAP4SSL

from flask import Flask, request
from instance import ParseMail

app = Flask(__name__)


@app.route('/api/mailbox/fetch-letters', methods=['POST'])
def fetch_letters():
    """
    {
        "email": "test@test.test",
        "password": "testPassword",
        "host": "imap.test.test",
        "port": 993,
        "toDeleteLetters": false,
        "proxy": "socks5://204.155.31.170:625vXR25@204.155.31.18:4353"
    }

    для гугла нужно разрешить - https://myaccount.google.com/lesssecureapps :: https://accounts.google.com/b/4/DisplayUnlockCaptcha
    """

    proxy = request.json['proxy'].split('/')
    try:
        mail = SocksIMAP4SSL(host=request.json['host'],
                             port=request.json['port'],
                             proxy_type=proxy[0],
                             proxy_addr=proxy[1],
                             proxy_port=int(proxy[2]))
        mail.login(request.json['email'], request.json['password'])
    except (ProxyConnectionError, GeneralProxyError) as error:
        return json.dumps({"status": str(error)}, ensure_ascii=False), 200

    mail.list()
    mail.select("inbox")
    result, data = mail.search(None, "UNSEEN")
    unread_msg_nums = data[0].split()

    messageList = []
    for uid in unread_msg_nums[:10]:
        uid = uid.decode('utf-8')
        _, response = mail.fetch(uid, '(RFC822)')
        messageList.append(ParseMail(response).data)


    if request.json['toDeleteLetters']:
        for msg_id in unread_msg_nums[:10]:
            print(msg_id)
            mail.uid('STORE', msg_id, '+FLAGS', '(\Flagged)' + "\r\n")
            mail.uid('STORE', msg_id, '+FLAGS', '(\Deleted)' + "\r\n")
            mail.expunge()

    mail.close()
    mail.logout()

    return json.dumps({"letters": messageList}, ensure_ascii=False), 200

@app.route('/api/letters/send', methods=['POST'])
def send():
    pass

if __name__ == '__main__':
    app.run('0.0.0.0', 5002)