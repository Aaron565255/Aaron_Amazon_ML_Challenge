import re
import unicodedata


def clean_text(value):
    if value is None:
        return ""

    value = str(value)

    if value.lower() == "nan":
        return ""

    value = unicodedata.normalize("NFKD", value)

    value = "".join(
        c for c in value
        if not unicodedata.combining(c)
    )

    value = value.lower()

    value = re.sub(r"[^a-z0-9\s]", " ", value)

    value = re.sub(r"\s+", " ", value).strip()

    return value


def compact_text(value):
    return re.sub(
        r"[^a-z0-9]",
        "",
        clean_text(value)
    )


def name_key(value):
    text = clean_text(value)

    suffixes = [
        "private limited",
        "pvt ltd",
        "pvt limited",
        "private ltd",
        "limited",
        "ltd",
        "llc",
        "incorporated",
        "inc",
        "corp",
        "corporation",
        "company",
        "co"
    ]

    for suffix in suffixes:
        text = re.sub(
            rf"\b{re.escape(suffix)}\b",
            " ",
            text
        )

    text = re.sub(
        r"\s+",
        " ",
        text
    ).strip()

    return text


def address_key(value):
    return clean_text(value)


def name_prefix(value):
    text = name_key(value)

    if not text:
        return ""

    return compact_text(text)[:8]


def address_prefix(value):
    text = address_key(value)

    if not text:
        return ""

    return compact_text(text)[:10]


def make_name_tokens(value):
    text = name_key(value)

    if not text:
        return []

    return [
        token
        for token in text.split()
        if len(token) >= 3
    ]


def make_block_key(value):
    tokens = make_name_tokens(value)

    if not tokens:
        return ""

    tokens = sorted(set(tokens))

    return "|".join(tokens[:4])


def country_key(value):
    return clean_text(value)