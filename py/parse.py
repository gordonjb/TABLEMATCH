import logging
import re
from enum import IntEnum, StrEnum
from urllib.parse import parse_qsl, urlparse

from models.match import Match
from models.wrestler import Wrestler
import reqs
from bs4 import BeautifulSoup
from models.promotion import Promotion
from models.show import Show

logger = logging.getLogger(__name__)

session = reqs.get_session()


class ContentType(IntEnum):
    """
    Enum of Cagematch content types, the database to which the item belongs
    """
    EVENT = 1
    WRESTLER = 2
    TITLE = 5
    PROMOTION = 8
    TAG_TEAM = 28
    STABLE = 29


class ShowType(StrEnum):
    """
    Enum of show types, the keywords used in shows yaml files to identify shows
    that should be processed specially
    """
    TAPING = "taping"
    PARTIAL = "partial"
    SQUASH = "squashmatch"


class CagematchURLFields(StrEnum):
    """
    Enum of keys in Cagematch URLs. 
    
    This looks wrong but *is* the correct way round
    """

    TYPE = "id"
    ID = "nr"
    NAME = "name"


class CagematchShowInfoKeys(StrEnum):
    """
    Enum of keys in show info tables
    """
    ARENA = "Arena:"
    DATE = "Date:"
    NAME = "Name of the event:"
    PROMOTION = "Promotion:"


def parse_show(show) -> Show:
    """
    Parse an entry in YAML input file to a `Show` object representing it.

    :param show: a single entry from the input file, either a URL or a dictionary
    :return: a Show object
    """
    match show:
        case str() as url:
            return handle_show_url(url)
        case {
            ShowType.SQUASH: {
                "url": url,
                "squash": list(squash_matches),
            }
        }:
            return handle_squash_match(url, squash_matches)
        case {
            ShowType.TAPING: {
                "name": str(name),
                "urls": list(taping),
            }
        }:
            taping = handle_taping(taping)
            taping.name = name
            return taping
        case {ShowType.TAPING: (list(taping) | {"urls": list(taping)})}:
            return handle_taping(taping)
        case {
            ShowType.PARTIAL: {
                "url": url,
                "exclude": list(excluded_matches),
                "exclude_from_count": bool(exclude),
            }
        }:
            partial = handle_partial(url, excluded_matches)
            partial.exclude = bool(exclude)
            return partial
        case {
            ShowType.PARTIAL: {
                "url": url,
                "exclude": list(excluded_matches),
            }
        }:
            return handle_partial(url, excluded_matches)
        case _:
            raise ValueError(
                "Unexpected entry type encountered, or bad syntax: " + str(show)
            )


def handle_show_url(url: str) -> Show:
    """
    Request a single show URL

    :param url: Should be a str URL for a Cagematch show page
    :return: a Show object
    """
    raw_html = reqs.get_text(session, url)
    if raw_html is None:
        raise ValueError("No HTML returned: " + url)
    soup = BeautifulSoup(raw_html, "html.parser")
    return html_to_show(soup, url)


def handle_taping(taping: list) -> Show:
    """
    For a list of shows making up a taping, call parse for each entry in the list, then merge them.

    :param taping: a list of shows to be passed to parse_show, each could be str or dict
    :return: a Show object
    """
    taping_parts: list[Show] = list()
    for part in taping:
        taping_parts.append(parse_show(part))
    ret = taping_parts[0]
    ret.name = ret.name + " Taping"
    for part in taping_parts[1:]:
        ret.id.extend(part.id)
        ret.matches.extend(part.matches)
    return ret


def handle_partial(url, excluded_matches: list) -> Show:
    """
    For a partial show, call parse on the show, then remove the specified matches from the match list.

    :param url: a show to be passed to parse_show, could be str or dict
    :param excluded_matches: a list of matches that should be removed from the match array. 
                             Note that indexing starts at 1 (i.e. `1` is match one and will be 
                             interpreted as array index 0)
    :return: a Show object
    """
    partial = parse_show(url)
    # Blank out any matches that are to be excluded
    for x in excluded_matches:
        partial.matches[x-1] = None
    # Remove the matches that were blanked out from the list
    partial.matches = [x for x in partial.matches if x is not None]
    partial.partial = True
    return partial


def handle_squash_match(url, squash_matches: list) -> Show:
    """
    Take ranges of matches, and combine them into single matches.

    :param url: a show to be passed to parse_show, could be str or dict
    :param squash_matches: a list of ranges from the match array, formatted `x-y`, that should be combined. 
                           Multiple ranges can be provided in a list. No checking is done that these ranges
                           are valid or make sense.
                           Note that indexing starts at 1 (i.e. `1` is match one and will be 
                           interpreted as array index 0)
    :return: a Show object
    """
    sh = parse_show(url)
    for sm in squash_matches:
        start, end = sm.split("-")
        start = int(start)
        end = int(end)
        # Get the slice representing the range of matches
        slice = sh.matches[start-1:end]
        # Create aggregation lists and dicts
        results = []
        wrestlers = {}
        teams = {}
        appearances = {}
        for idx, sl in enumerate(slice):
            results.append(sl.result)
            for w in sl.wrestlers:
                wrestlers.update({w.id: w})
            for t in sl.teams:
                teams.update({t.id: t})
            for a in sl.appearances:
                appearances.update({a.id: a})
            # Now blank out the match we just processed from the original list    
            sh.matches[start-1+idx] = None

        # Combine to a new match object, and put it in the index of the start of the range
        m = Match(
            type="",
            result=", ".join(results),
            won=None,
            cagematch=None,
            wrestlers=list(wrestlers.values()),
            teams=list(teams.values()),
            appearances=list(appearances.values()),
        )
        sh.matches[start-1] = m
    
    # Remove the matches that were blanked out from the list
    sh.matches = [x for x in sh.matches if x is not None]
    return sh

def html_to_show(soup: BeautifulSoup, url: str) -> Show:
    """
    From the souped HTML, create a dictionary for the show info table, and extract the relevant portions.

    :param soup: the HTML as passed through BeautifulSoup
    :param url: the show URL
    :return: a Show object
    """
    query_parts = dict(parse_qsl(urlparse(url).query))
    show_id = query_parts.get(CagematchURLFields.ID)
    show_dict = get_show_info(soup)
    show_name = apply_translations(show_dict[CagematchShowInfoKeys.NAME])
    promotion_str = show_dict[CagematchShowInfoKeys.PROMOTION]
    promotion = html_to_promotion(promotion_str)
    arena = show_dict[CagematchShowInfoKeys.ARENA].get_text()
    date_str = show_dict[CagematchShowInfoKeys.DATE].get_text()
    dd, mm, yy = date_str.split(".")
    matches = html_to_matches(soup)
    return Show(
        id=[show_id],
        name=show_name,
        promotion=promotion,
        arena=arena,
        date="-".join([yy,mm,dd]),
        matches=matches,
    )


def get_show_info(soup: BeautifulSoup) -> dict:
    """
    Find the information box from the show page. Essentially treat it as a table:
        find every InformationBoxTitle div, and use the text as a key.
        find every InformationBoxContents div, and use the content as a value.

    :param soup: the show page html, as parsed through Beautiful Soup
    :return: dictionary of the show information box
    """
    show_table = soup.find("div", {"class": "InformationBoxTable"})
    keys = [
        span.get_text()
        for span in show_table.find_all("div", {"class": "InformationBoxTitle"})
    ]
    values = [
        span.contents[0]
        for span in show_table.find_all("div", {"class": "InformationBoxContents"})
    ]
    dictionary = dict(zip(keys, values))
    return dictionary


def html_to_promotion(promotion_str) -> Promotion:
    """
    From the contents of the 'Promotion' infobox, check for a link. If a link exists, and the content type in the URL
    indicates the link is to a Promotion page, parse the promotion information from the text.

    :param promotion_str: The contents of the 'Promotion: ' infobox.
    :return: a Promotion object
    """
    # TODO: what if no promotion link
    query_parts = dict(parse_qsl(urlparse(promotion_str.attrs["href"]).query))
    link_type = int(query_parts.get(CagematchURLFields.TYPE))
    if link_type == ContentType.PROMOTION:
        promotion_id = int(query_parts.get(CagematchURLFields.ID))
        return Promotion(promotion_id, promotion_str.text)


def html_to_matches(soup: BeautifulSoup) -> list:
    """
    From the souped HTML, find all the `Match` divs, and extract the relevant portions to a list
    of Match objects.

    :param soup: the HTML as passed through BeautifulSoup
    :return: a list of Match objects
    """
    # TODO: Could this be neater?
    matches = soup.find_all("div", {"class": "Match"})
    ret = []
    for m in matches:
        scores = m.find("div", {"class": "MatchRecommendedLine"})
        if scores is not None:
            won_score = html_to_won_score(scores)
            cm_score = html_to_cm_score(scores)

        type = m.find("div", {"class": "MatchType"})
        result = m.find("div", {"class": "MatchResults"})

        wrestlers = []
        teams = []
        appearances = []  # https://regex101.com/r/LtwojY/1
        # TODO: Handle wresters without profiles
        with_blocks = []
        if "w/" in str(result):
            with_blocks = re.findall(r"\(w\/([^\)]+)", str(result))
        profiles = result.find_all("a")
        for p in profiles:
            query_parts = dict(parse_qsl(urlparse(p.attrs["href"]).query))
            link_type = int(query_parts.get(CagematchURLFields.TYPE))
            w = Wrestler(
                id=query_parts.get(CagematchURLFields.ID),
                text=p.text.strip(),
            )
            if any(str(p) in w for w in with_blocks):
                appearances.append(w)
            elif link_type == ContentType.WRESTLER:
                wrestlers.append(w)
            elif link_type in [ContentType.STABLE, ContentType.TAG_TEAM]:
                teams.append(w)

        ret.append(
            Match(
                type=type.text,
                result=result.text,
                won=won_score,
                cagematch=cm_score,
                wrestlers=wrestlers,
                teams=teams,
                appearances=appearances,
            )
        )

    return ret


def html_to_won_score(scores) -> float:
    """
    From an input soup, search for the span containing the WON star rating, and
    convert it to a numerical score

    :param scores: expected to be the `MatchRecommendedLine` span from the soup
    :return: the WON star rating in numerical terms, could be positive or negative or None if no score found.
    """
    won = scores.find("span", {"class": "MatchRecommendedWON"})
    if won is not None:
        rating = won.find("span", {"class": "starRating"}).text
        negate = False
        if rating.startswith("-"):
            rest = rating[1:]
            negate = True
        else:
            rest = rating
        if rest.startswith("*"):
            stars = rating.count("*")
        else:
            stars = 0

        rest = rest.replace("*", "")
        match rest:
            case "1/4":
                fraction = 0.25
            case "1/2":
                fraction = 0.5
            case "3/4":
                fraction = 0.75
            case _:
                fraction = 0

        rating = stars + fraction
        if negate:
            rating = -rating
        return rating
    return None


def html_to_cm_score(scores) -> float:
    """
    From an input soup, search for the text of the Cagematch matchguide rating, and
    convert it to a numerical score

    :param scores: expected to be the `MatchRecommendedLine` span from the soup
    :return: the Cagematch rating in numerical terms, or None if no score found.
    """
    search = re.search(r"Matchguide Rating: (.+) based on ", scores.text)
    if search is not None:
        return float(search.group(1))
    return None


def apply_translations(show_name: str) -> str:
    """
    Apply the following translations to strings:
      - 'Tag {x}' to 'Day {x}'

    :param show_name: the input string to translate
    :return: the translated string
    """
    return re.sub(r"(Tag)( [0-9]+)", r"Day\2", show_name)
