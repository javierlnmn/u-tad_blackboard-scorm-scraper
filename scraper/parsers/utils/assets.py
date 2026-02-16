from __future__ import annotations

import base64
from typing import Any


def safe_basename_from_url(url: str | None) -> str | None:
    if not url:
        return None
    base = url.split('?', 1)[0].split('#', 1)[0].rstrip('/').split('/')[-1]
    return base or None


def safe_filename(name: str) -> str:
    name = (name or '').strip()
    name = ''.join(ch if ch.isalnum() or ch in {'.', '-', '_'} else '_' for ch in name)
    name = name.strip('._-') or 'asset'
    return name


def download_via_fetch(locator: Any, url: str) -> bytes | None:
    """Download a URL using the page context (cookies/session) via fetch().

    `locator` is any Playwright object that supports `.evaluate(js, arg)`.
    """
    js = r"""
async (el, url) => {
  const res = await fetch(url);
  if (!res.ok) return null;
  const buf = await res.arrayBuffer();
  const bytes = new Uint8Array(buf);
  let binary = '';
  const chunk = 0x8000;
  for (let i = 0; i < bytes.length; i += chunk) {
    binary += String.fromCharCode.apply(null, bytes.subarray(i, i + chunk));
  }
  return btoa(binary);
}
"""
    try:
        b64 = locator.evaluate(js, url)
    except Exception:
        return None
    if not b64:
        return None
    try:
        return base64.b64decode(b64)
    except Exception:
        return None

