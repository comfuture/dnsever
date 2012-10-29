import re
import lxml.html as l
from mechanize import Browser

VERSION = '0.1pre'
DESCRIPTION = 'Unofficial DNSEver python client'

class DNSEver(object):

    ready = False
    nameservers = []

    def __init__(self, username=None, password=None):
        self.browser = Browser()
        if any((username, password,)):
            self.open()
            self.login(username, password)

    def open(self):
        self.browser.open('http://kr.dnsever.com')
        self._open = True

    def login(self, username, password):
        self.browser.select_form(name='form')
        self.browser['login_id'] = username
        self.browser['login_password'] = password
        self.browser.submit()
        self.browser.open('/start.html')
        self.browser.select_form(name='form')
        self.skey = self.browser['skey']
        self.doc = l.document_fromstring(self.browser.response().read())
       
        # get nameservers
        self.nameservers = zip(
            ['{0}dnsever.com'.format(el.text) for el in self.doc.cssselect(
                '#nsinfobox td:not(.mn) > b')],
            [el.text for el in self.doc.cssselect(
                '#nsinfobox td.mn table tr:nth-child(3n-1) td:nth-child(2)')]
        )

        # get domains
        self.domains = DomainCollection(Domain(el.text) for el in self.doc.cssselect('.domainName a'))
        self.ready = True
        self.domains.session = self

    def get_items(menu):
        # TODO: implement
        return menu

    def checked_values(menu, values):
        # TODO: impelement
        return values

    def api(self, command, values=None):
        # TODO: implement
        if command in ['add_a', 'change_a', 'delete_a']:
            selected_menu = 'edita'

        self.browser.post('/start.html', {
            'command': command,
            'selected_menu': selected_menu,
            'skey': self.skey,
            'check[]': self.checked_values(selected_menu, values)
        })

    def __iter__(self):
        return self.domains

    def __getitem__(self, key):
        return self.domains[key]


class DNSEverException(Exception):
    pass


class Domain(object):
    """domain entry"""

    def __init__(self, name, memo=''):
        re_domain = re.compile(r'[a-z0-9]+([\-\.]{1}[a-z0-9]+)*\.[a-z]{2,5}')
        if not re_domain.match(name):
            raise DNSEverException('Not valid domainname')
        self.name = name
        self.memo = memo

    def add_record(self, record):
        pass

    @property
    def records(self):
        return []

    def __repr__(self):
        return '"{0}"'.format(self.name)

    def __unicode__(self):
        return u'{0:<30} {1}'.format(self.name, self.memo)


class DomainCollection(list):
    """domain collection"""

    session = None

    def __getitem__(self, key):
        if type(key) is str:
            for domain in self:
                if domain.name == key:
                    return domain
        return list.__getitem__(self, key)

    def __setitem__(self, key, value):
        if value in self:
            raise DNSEverException('Domain already exists')

        if not issubclass(value, Domain):
            value = Domain(value)

        if self.session and self.session.ready:
            raise DNSEverException('Adding domain can only available at website')

        list.__setitem__(self, key, value)

    def __delitem__(self, key):
        if self.session and self.session.ready:
            self.session.api('delete_bulk_zone', [self[key].name])

    def __contains__(self, item):
        if issubclass(item, Domain):
            item = item.name
        return item in [domain.name for domain in self]


class Record(object):
    """abstract record"""

    type = None
    name = None
    tld = '.'
    ttl = 0
    memo = ''

    def __init__(self, name, tld='.', ttl=14400, memo=''):
        self.name = name
        if not tld.endswith('.'):
            tld = tld + '.'
        self.tld = tld
        self.ttl = ttol
        self.memo = memo


class RecordCollection(list):

    T = Record

    def __getitem__(self, key):
        if key in ['A', 'CNAME', 'MX', 'TXT', 'DDNS']:
            ret = RecordCollection(record for record in self if record.type == key)
            klasses = {'A': ARecord, 'CNAME': CNAMERecord, 'MX': MXRecord,
                    'DDNS': DDNSRecord}
            ret.T = klasses[key]
            return ret

        return list.__getitem__(self, key)

    def __setitem__(self, key, value):
        if self.T and not issubclass(value, T):
            raise DNSEverException('Not valid {0}'.format(self.T.__name__))

        if self.session and self.session.ready:
            # TODO
            self.session.api('add_record', {})

        list.__setitem__(self, key, value)

    def __delitem__(self, key):

        if self.session and self.session.ready:
            # TODO
            self.session.api('delete_record', {})

        list.__delitem__(self, key)


class ARecord(Record):
    """A Record"""

    type = 'A'
    ip = None

    def __init__(self, ip, *args, **kwargs):
        super(ARecord, self).__init__(self, *args, **kwargs)
        self.ip = ip

    def __repr__(self):
        return '<ARecord {0}="{1}">'.format(self.name, self.ip)

    def __unicode__(self):
        return u'{0}{1:<30}\t{2}\tIN\tA\t{3}'.format(
                self.name, self.tld, self.ttl, self.ip)


class CNAMERecord(Record):
    """CNAME Record"""

    type = 'CNAME'
    address = None

    def __init__(self, address, *args, **kwargs):
        super(CNAMERecord, self).__init__(self, *args, **kwargs)
        self.address = address

    def __repr__(self):
        return '<CNAMERecord {0}="{1}">'.format(self.name, self.address)


class MXRecord(Record):
    """MX Record"""

    type = 'MX'
    address = None
    priority = 10

    def __init__(self, address, priority=10, *args, **kwargs):
        super(MXRecord, self).__init__(self, *args, **kwargs)
        self.priority = priority
        self.address = address

    def __repr__(self):
        return '<MXRecord {0}="{1}" priority={2}>'.format(self.name, self.address, self.priority)


class TXTRecord(Record):
    """TXT Record"""

    type = 'TXT'


class SRVRecord(Record):
    """SRV Record"""

    type = 'SRC'


class DDNSRecord(Record):
    """DNSEver specific DDNS Record"""

    type = 'DDNS'
    ttl = 300


