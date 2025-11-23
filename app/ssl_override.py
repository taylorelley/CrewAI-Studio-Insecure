"""Centralized TLS/SSL relaxation utilities.

This module disables certificate verification across the Python runtime so
that the application can operate in environments that perform TLS/SSL
inspection or present untrusted certificates.
"""

import os
import ssl
from typing import Optional

try:  # pragma: no cover - safeguard for missing optional deps
    import requests
    from urllib3.exceptions import InsecureRequestWarning
except ImportError:  # pragma: no cover
    requests = None
    InsecureRequestWarning = None  # type: ignore


def disable_ssl_verification(extra_warning: Optional[str] = None) -> None:
    """Disable certificate verification globally for HTTPS clients.

    This applies to the standard library's TLS context, common environment
    variables used by HTTP clients (requests, httpx, curl), and suppresses
    related warnings when the ``requests`` package is available.
    """

    os.environ.setdefault("PYTHONHTTPSVERIFY", "0")
    os.environ.setdefault("REQUESTS_CA_BUNDLE", "")
    os.environ.setdefault("CURL_CA_BUNDLE", "")
    os.environ.setdefault("SSL_CERT_FILE", "")

    ssl._create_default_https_context = ssl._create_unverified_context

    if requests and InsecureRequestWarning:
        requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

    if extra_warning:
        print(extra_warning)
