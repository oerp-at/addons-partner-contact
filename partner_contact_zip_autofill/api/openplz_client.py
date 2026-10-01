# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

"""HTTP client for OpenPLZ API (https://openplzapi.org/swagger/index.html)."""

import logging

import requests

_logger = logging.getLogger(__name__)

BASE_URL = "https://openplzapi.org"
TIMEOUT_SEC = 2


class OpenPlzApiError(Exception):
    """Raised when the OpenPLZ API request fails."""


def normalize_plz(api_code, postal_code):
    """Return stripped digits-only PLZ or empty string if length invalid for country."""
    pc = (postal_code or "").strip().replace(" ", "")
    if api_code == "de":
        if len(pc) == 5 and pc.isdigit():
            return pc
    elif api_code in ("at", "ch", "li"):
        if len(pc) == 4 and pc.isdigit():
            return pc
    return ""


def fetch_fulltext(api_code, search_term):
    """Return street rows from ``GET /{api_code}/FullTextSearch``.

    The ``searchTerm`` is a free-text query; passing ``"<street> <plz>"`` yields
    the streets matching that name in the given postal-code area. Each row
    carries ``postalCode``, ``locality``, ``municipality`` and the federal
    state/province, which is enough to disambiguate an ambiguous postal code.
    """
    term = (search_term or "").strip()
    if not term or api_code not in ("de", "at", "ch", "li"):
        return []
    url = f"{BASE_URL}/{api_code}/FullTextSearch"
    params = {"searchTerm": term, "page": 1, "pageSize": 50}
    headers = {"Accept": "application/json"}
    try:
        response = requests.get(
            url,
            params=params,
            headers=headers,
            timeout=TIMEOUT_SEC,
        )
        response.raise_for_status()
    except requests.RequestException as exc:
        _logger.warning(
            "OpenPLZ full-text search failed for %s %r: %s", api_code, term, exc
        )
        raise OpenPlzApiError from exc
    try:
        data = response.json()
    except ValueError as exc:
        _logger.warning("OpenPLZ invalid JSON for %s %r", api_code, term)
        raise OpenPlzApiError from exc
    if not isinstance(data, list):
        return []
    return data
