# utf-8
from typing import Union
from urllib.parse import ParseResult, urlparse

IMPROPER_KEYWORDS = (
    'adult',
    'porn',
    'xxx',
    '18+',
    'nsfw',
    'sex',
    'erotica',
    'xvideos',
    'localhost',
    ' torrent',
    'Bit.ly',
    ' pornografia',
    ' vazados',
    'pornographic',
)


def validate_links(github: str, linkedin: str, site: str):
    """
    Valida os links fornecidos (GitHub, LinkedIn e site pessoal) com base em
     urlparse.
    Retorna um dicionário indicando quais links são válidos.
    """
    github_url, linkedin_url, site_url = map(
        urlparse, (github, linkedin, site)
    )

    for text_in_link in IMPROPER_KEYWORDS:
        if any(map(lambda x: text_in_link in x, (github, linkedin, site))):
            return {
                'github_valid': False,
                'linkedin_valid': False,
                'site_regex': False,
            }

    results = {
        'github_valid': validate_url(github_url, 'github.com'),
        'linkedin_valid': validate_url(linkedin_url, 'linkedin.com'),
        'site_regex': validate_url(site_url),
    }

    return results


def validate_url(url: ParseResult, netloc: Union[str, None] = None):
    if url.scheme != 'https':
        return False
    return url.netloc.lstrip('www.') == netloc if netloc else bool(url.netloc)
