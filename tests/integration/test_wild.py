import pytest
requests = pytest.importorskip("requests")

import vcr

import httplib


def test_domain_redirect():
    '''Ensure that redirects across domains are considered unique'''
    # In this example, seomoz.org redirects to moz.com, and if those
    # requests are considered identical, then we'll be stuck in a redirect
    # loop.
    url = 'http://seomoz.org/'
    with vcr.use_cassette('tests/fixtures/wild/domain_redirect.yaml') as cass:
        requests.get(url, headers={'User-Agent': 'vcrpy-test'})
        # Ensure that we've now served two responses. One for the original
        # redirect, and a second for the actual fetch
        assert len(cass) == 2


def test_flickr_multipart_upload():
    """
    The python-flickr-api project does a multipart
    upload that confuses vcrpy
    """
    def _pretend_to_be_flickr_library():
        content_type, body = "text/plain", "HELLO WORLD"
        h = httplib.HTTPConnection("httpbin.org")
        headers = {
            "Content-Type": content_type,
            "content-length": str(len(body))
        }
        h.request("POST", "/post/", headers=headers)
        h.send(body)
        r = h.getresponse()
        data = r.read()
        h.close()

    with vcr.use_cassette('fixtures/vcr_cassettes/flickr.json') as cass:
        _pretend_to_be_flickr_library()
        assert len(cass) == 1

    with vcr.use_cassette('fixtures/vcr_cassettes/flickr.json') as cass:
        assert len(cass) == 1
        _pretend_to_be_flickr_library()
        assert cass.play_count == 1
