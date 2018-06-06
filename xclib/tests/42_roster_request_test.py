# Exercises the roster_cloud() request
# Test when replacing request.session
import requests
from xclib.sigcloud import sigcloud
from xclib import xcauth
from xclib.check import assertEqual

class fakeResponse:
    # Will be called as follows:
    # r = self.ctx.session.post(self.url, data=payload, headers=headers,
    #               allow_redirects=False, timeout=self.ctx.timeout)
    # r.status_code
    # r.json()
    # r.text
    def __init__(self, status, json, text):
        self.status_code = status
        self._json = json
        self.text = text

    def json(self):
        return self._json

def post_timeout(url, data='', headers='', allow_redirects=False,
        timeout=5):
    raise requests.exceptions.ConnectTimeout("Connection timed out")

def post_404(url, data='', headers='', allow_redirects=False,
        timeout=5):
    return fakeResponse(404, None, '404 Not found')

def post_200_empty(url, data='', headers='', allow_redirects=False,
        timeout=5):
    return fakeResponse(200, None, '200 Success')

def post_200_ok(url, data='', headers='', allow_redirects=False,
        timeout=5):
    return fakeResponse(200, {
        'result': 'success',
        'data': {
            'sharedRoster': {'user1@domain1':{'name':'Ah Be','groups':['Lonely']}}
        }}, 'fake body')

def setup_module():
    global xc, sc
    xc = xcauth(domain_db={
            'xdomain': '99999\thttps://remotehost\tydomain\t',
            'udomain': '8888\thttps://oldhost\t',
        },
        default_url='https://localhost', default_secret='01234')
    sc = sigcloud(xc, 'user1', 'domain1')

def teardown_module():
    pass

def test_timeout():
    xc.session.post = post_timeout
    assertEqual(sc.roster_cloud(), (False, None))

def test_http404():
    xc.session.post = post_404
    assertEqual(sc.roster_cloud(), (False, None))

def test_http200_empty():
    xc.session.post = post_200_empty
    roster, body = sc.roster_cloud()
    assertEqual(roster, None)
    assertEqual(body, '200 Success')

def test_success():
    xc.session.post = post_200_ok
    roster, body = sc.roster_cloud()
    assertEqual(roster, {'user1@domain1':{'name':'Ah Be','groups':['Lonely']}})
    assertEqual(body, 'fake body')

