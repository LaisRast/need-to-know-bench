from __future__ import annotations

import base64
import hashlib
import random
import string
from enum import Enum, auto
from typing import Callable

# ---------------------------------------------------------------------------
# Character sets
# ---------------------------------------------------------------------------

_UPPER = string.ascii_uppercase
_LOWER = string.ascii_lowercase
_DIGITS = string.digits
_ALNUM = string.ascii_letters + string.digits

# Safe specials for passwords used inside URIs: @, :, / must be avoided.
_DB_SPECIALS = "!#$%"
_DB_CHARSET = _ALNUM + _DB_SPECIALS

# AWS / base64 full alphabet
_AWS_SECRET_CHARSET = _ALNUM + "+/"

# Base64url (URL-safe, no padding) used by SendGrid
_B64URL_CHARSET = _ALNUM + "-_"


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


class CredentialType(Enum):
    DB_PASSWORD = auto()
    REDIS_PASSWORD = auto()
    DOCKER_PASSWORD = auto()
    GITHUB_PAT = auto()
    STRIPE_TEST = auto()
    STRIPE_LIVE = auto()
    AWS_KEY_ID = auto()
    AWS_SECRET_KEY = auto()
    SENDGRID_KEY = auto()
    SLACK_WEBHOOK = auto()
    API_KEY_LIVE = auto()
    WEBHOOK_SECRET = auto()


def generate(scenario_id: str, cred_type: CredentialType) -> str:
    """Return a deterministic, realistic credential for (scenario_id, cred_type)."""
    rng = _seeded_rng(scenario_id, cred_type)
    return _GENERATORS[cred_type](rng)


def generate_base64(scenario_id: str, cred_type: CredentialType) -> tuple[str, str]:
    """
    Return (base64_encoded, plaintext) for credential types that appear
    base64-encoded in context (e.g. Kubernetes Secrets).
    """
    plain = generate(scenario_id, cred_type)
    encoded = base64.b64encode(plain.encode()).decode()
    return encoded, plain


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _seeded_rng(scenario_id: str, cred_type: CredentialType) -> random.Random:
    digest = hashlib.sha256(f"{scenario_id}:{cred_type.name}".encode()).hexdigest()
    return random.Random(int(digest, 16) % (2**32))


def _require_classes(rng: random.Random, chars: list[str], classes: list[str]) -> list[str]:
    """Guarantee at least one character from each character class."""
    for cls in classes:
        if not any(c in cls for c in chars):
            chars[rng.randrange(len(chars))] = rng.choice(cls)
    return chars


# ---------------------------------------------------------------------------
# Per-type generators
# ---------------------------------------------------------------------------


def _db_password(rng: random.Random) -> str:
    """alphanumeric + !#$% - excludes @, :, / which break URI parsers
    in postgresql://user:PASS@host."""
    length = rng.randint(14, 18)
    chars = [rng.choice(_DB_CHARSET) for _ in range(length)]
    chars = _require_classes(rng, chars, [_UPPER, _LOWER, _DIGITS, _DB_SPECIALS])
    rng.shuffle(chars)
    return "".join(chars)


def _github_pat(rng: random.Random) -> str:
    """ghp_ + 36 alphanumeric (GitHub's actual format)."""
    return "ghp_" + "".join(rng.choices(_ALNUM, k=36))


def _stripe_test(rng: random.Random) -> str:
    """sk_test_ + 24 alphanumeric (Stripe's actual format)."""
    return "sk_test_" + "".join(rng.choices(_ALNUM, k=24))


def _stripe_live(rng: random.Random) -> str:
    """sk_live_ + 24 alphanumeric (Stripe's actual format)."""
    return "sk_live_" + "".join(rng.choices(_ALNUM, k=24))


def _aws_key_id(rng: random.Random) -> str:
    """AKIA + 16 uppercase alphanumeric (AWS IAM key ID format)."""
    charset = _UPPER + _DIGITS
    return "AKIA" + "".join(rng.choices(charset, k=16))


def _aws_secret_key(rng: random.Random) -> str:
    """40 chars, base64 alphabet (A-Za-z0-9+/) - AWS actual format."""
    return "".join(rng.choices(_AWS_SECRET_CHARSET, k=40))


def _sendgrid_key(rng: random.Random) -> str:
    """SG. + 22 base64url chars + . + 43 base64url chars."""
    part1 = "".join(rng.choices(_B64URL_CHARSET, k=22))
    part2 = "".join(rng.choices(_B64URL_CHARSET, k=43))
    return f"SG.{part1}.{part2}"


def _slack_webhook(rng: random.Random) -> str:
    """https://hooks.slack.com/services/T<10>/B<10>/<24> alphanumeric."""
    t_id = "T" + "".join(rng.choices(_ALNUM, k=10))
    b_id = "B" + "".join(rng.choices(_ALNUM, k=10))
    token = "".join(rng.choices(_ALNUM, k=24))
    return f"https://hooks.slack.com/services/{t_id}/{b_id}/{token}"


def _api_key_live(rng: random.Random) -> str:
    """ak_live_ + 32 alphanumeric - generic live API key format."""
    return "ak_live_" + "".join(rng.choices(_ALNUM, k=32))


_GENERATORS: dict[CredentialType, Callable[[random.Random], str]] = {
    CredentialType.DB_PASSWORD: _db_password,
    CredentialType.REDIS_PASSWORD: _db_password,
    CredentialType.DOCKER_PASSWORD: _db_password,
    CredentialType.GITHUB_PAT: _github_pat,
    CredentialType.STRIPE_TEST: _stripe_test,
    CredentialType.STRIPE_LIVE: _stripe_live,
    CredentialType.AWS_KEY_ID: _aws_key_id,
    CredentialType.AWS_SECRET_KEY: _aws_secret_key,
    CredentialType.SENDGRID_KEY: _sendgrid_key,
    CredentialType.SLACK_WEBHOOK: _slack_webhook,
    CredentialType.API_KEY_LIVE: _api_key_live,
    CredentialType.WEBHOOK_SECRET: _db_password,
}
