import logging

from diskcache import Cache
from playwright.sync_api import Page, Response, sync_playwright

import reqs

logger = logging.getLogger(__name__)
cache = Cache("./cagematchcache")
session = reqs.get_session()

@cache.memoize()
def get_text(url:str) -> str:
    """
    Attempts to use requests to get the content at `url`,
    then if requests fails, attempts in Playwright
    """
    raw_html = reqs.get_text(session, url)
    if raw_html is not None:
        return raw_html.decode("ISO-8859-1")
    else:
        content = None
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page()

            document_responses: list[Response] = []
            page.on("response", lambda response: on_response(response, page, document_responses))
            resp = page.goto(url=url,wait_until="domcontentloaded")
            final_response = document_responses[-1]

            if resp is not None and is_good_response(final_response):
                content = page.content()
            browser.close()

        if content is None:
            raise ResponseException("No valid response from Playwright")
        else:
            return content

def is_good_response(resp: Response) -> bool:
    """
    Returns True if the response seems to be HTML, False otherwise.
    """
    content_type = resp.header_value('Content-Type')
    return (resp.ok
            and content_type is not None
            and content_type.lower().find('html') > -1)

def on_response(response:Response, page:Page, document_responses:list[Response]) -> None:
    """
    Callback for Playwright responses. Checks if the type is document, and if so adds it to a list of responses.
    This lets us determine the last response recieved, which lets us check the status of the redirected page.
    """
    if (response.request.resource_type == "document" and response.request.frame == page.main_frame):
        document_responses.append(response)

class ResponseException(Exception):
    pass
