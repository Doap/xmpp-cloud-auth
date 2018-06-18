import logging
import sys
import requests
from xclib.sigcloud import sigcloud
import xclib.isuser
from xclib.utf8 import utf8, unutf8

def verify_with_isuser(url, secret, domain, user, timeout, hook=None):
    xc = xcauth(default_url=url, default_secret=secret, timeout=timeout)
    sc = sigcloud(xc, user, domain)
    if hook != None: hook(sc) # For automated testing only
    return sc.isuser_verbose()

class xcauth:
    def __init__(self, default_url=None, default_secret=None,
                ejabberdctl=None, shared_roster_db=None,
                domain_db={}, cache_db={},
                ttls={'query': 3600, 'verify': 86400, 'unreach': 7*86400},
                bcrypt_rounds=12, timeout=5):
        self.default_url=default_url
        self.default_secret=default_secret
        self.ejabberdctl_path=ejabberdctl
        self.shared_roster_db=shared_roster_db
        self.domain_db=domain_db
        self.cache_db=cache_db
        self.ttls=ttls
        self.timeout=timeout
        self.bcrypt_rounds=bcrypt_rounds
        self.session=requests.Session()

    def per_domain(self, dom):
        bdom = utf8(dom)
        if bdom in self.domain_db:
            try:
                # Already 4-value database format? Great!
                secret, url, authDomain, extra = unutf8(self.domain_db[bdom]).split('\t', 3)
            except ValueError:
                # No, fall back to 3-value format (and update DB)
                secret, url, extra = unutf8(self.domain_db[bdom]).split('\t', 2)
                authDomain = dom
                self.domain_db[dom] = utf8('\t'.join((secret, url, authDomain, extra)))
            return utf8(secret), url, authDomain
        else:
            return utf8(self.default_secret), self.default_url, dom
