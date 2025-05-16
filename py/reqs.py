from requests.adapters import HTTPAdapter
from requests.exceptions import RequestException
from contextlib import closing
import requests_cache
from urllib3 import Retry
import logging
logger = logging.getLogger(__name__)


def get_session() -> requests_cache.CachedSession:
    session = requests_cache.CachedSession(cache_name='cagematch_cache', backend='sqlite')
    retry_strategy = Retry(
        total = 4,  # maximum number of retries
        backoff_factor = 1,
        status_forcelist = [403, 429, 500, 502],  # the HTTP status codes to retry on
    )
    adapter = HTTPAdapter(max_retries = retry_strategy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    return session

def get_text(session, url) -> bytes:
    """
    Attempts to get the content at `url` by making an HTTP GET request.
    If the content-type of response is some kind of HTML/XML, return the
    text content, otherwise return None.
    """
    try:
        with closing(session.get(url)) as resp:
            logger.info("{cached} URL '{req_url}'".format(req_url=url, cached="Cached" if resp.from_cache else "Uncached"))
            if is_good_response(resp):
                return resp.content
            else:
                return None

    except RequestException as e:
        logger.error('Error during requests to {0} : {1}'.format(url, str(e)))
        return None


def is_good_response(resp) -> bool:
    """
    Returns True if the response seems to be HTML, False otherwise.
    """
    content_type = resp.headers['Content-Type'].lower()
    return (resp.status_code == 200
            and content_type is not None
            and content_type.find('html') > -1)
