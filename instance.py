import base64
import email


class ParseMail:
    def __init__(self, response):
        html = response[0][1].decode('utf-8')
        self.message = email.message_from_string(html)
        self.data = {}

        self.getFrom()
        self.getName()
        self.getTitle()
        self.getDate()

    def getFrom(self):
        fromMsg = email.utils.parseaddr(self.message['From'])
        self.data['senderEmail'] = str(fromMsg[1])
        
    def getName(self):
        name = email.utils.parseaddr(self.message['From'])[0].split(' ')
        self.data['firstName'] = str(name[0])
        self.data['lastName'] = ''
        if len(name) > 1:
            self.data['lastName'] = str(name[1])
            
    def getTitle(self):
        title = ''

        for item in self.message['subject'].split('\n'):
            try:
                _, charset, _, text, _ = item.split('?', maxsplit=4)
            except:
                title += item
                continue
            try:
                title += base64.b64decode(text).decode(charset)
            except:
                title += text
        self.data['header'] = str(title)

    def getDate(self):
        date = email.utils.parsedate_tz(self.message['Date'])
        self.data['postDate'] = str(
            str(date[0]) + '-' + str(date[1]) + '-' + str(date[2]) + ' ' + str(date[3]) + ':' + str(
                date[4]) + ':' + str(date[5]))
