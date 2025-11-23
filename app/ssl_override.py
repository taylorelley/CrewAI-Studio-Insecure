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

    if requests:
        try:
            original_init = requests.sessions.Session.__init__

            def insecure_init(self, *args, **kwargs):  # type: ignore[override]
                original_init(self, *args, **kwargs)
                # Ensure all sessions skip certificate verification by default
                self.verify = False

            requests.sessions.Session.__init__ = insecure_init  # type: ignore[assignment]
        except Exception:
            # If monkeypatching fails, fall back to setting the module-level default
            # which still covers top-level helpers like requests.get
            requests.sessions.Session.verify = False  # type: ignore[assignment]

        if InsecureRequestWarning:
            requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

    if extra_warning:
        print(extra_warning)
