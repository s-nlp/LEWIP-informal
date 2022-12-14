import re
from string import punctuation
from itertools import groupby
MASK_TEMPLATE = " <extra_id_{}> "

EMOJI_PATTERN = re.compile(
    "(["
    "\U0001F1E0-\U0001F1FF"  # flags (iOS)
    "\U0001F300-\U0001F5FF"  # symbols & pictographs
    "\U0001F600-\U0001F64F"  # emoticons
    "\U0001F680-\U0001F6FF"  # transport & map symbols
    "\U0001F700-\U0001F77F"  # alchemical symbols
    "\U0001F780-\U0001F7FF"  # Geometric Shapes Extended
    "\U0001F800-\U0001F8FF"  # Supplemental Arrows-C
    "\U0001F900-\U0001F9FF"  # Supplemental Symbols and Pictographs
    "\U0001FA00-\U0001FA6F"  # Chess Symbols
    "\U0001FA70-\U0001FAFF"  # Symbols and Pictographs Extended-A
    "\U00002600-\U00002B55"
    "])", \
    flags=re.UNICODE
)
URL_PATTERN = re.compile(r"(http\S+|www\.\S+)", flags=re.UNICODE)
USERS_PATTERN = re.compile(r"@(\w+)", flags=re.UNICODE)
HASHTAG_PATTERN = re.compile(r"#(\w+)", flags=re.UNICODE)


def remove_emoji(text):
    return EMOJI_PATTERN.sub(r'', text)


def remove_hashtags(text):
    return HASHTAG_PATTERN.sub(r'', text)


def remove_urls(text):
    return URL_PATTERN.sub(r'', text)


def remove_users(text):
    return USERS_PATTERN.sub(r'', text)


def remove_multispaces(text):
    return " ".join(text.split()).strip()


def fix_punct(text):
    punct = set(punctuation)
    fixed_text = []
    for k, g in groupby(text):
        if k in punct:
            fixed_text.append(k)
        else:
            fixed_text.extend(g)
    text = "".join(fixed_text)
    text = text.replace(" ,", ", ").replace(" .", ".")
    text = text.replace(" !", "!").replace(" ?", "?")
    text = text.replace("…", "...")
    return text


PIPELINE = (
    remove_emoji,
    remove_users,
    remove_urls,
    remove_multispaces,
    fix_punct,
    remove_multispaces
)


def preprocess_text(text, max_words=100):
    for step in PIPELINE:
        text = step(text)
    text = " ".join(text.split(" ")[:max_words])
    return text


def convert_template_to_t5(template, orig_mask_token):
    current_pos = 0
    mask_pos = template.find(orig_mask_token, current_pos)
    mask_num = 0
    while mask_pos != -1:
        end_mask_pos = mask_pos + len(orig_mask_token)
        template = template[:mask_pos] + MASK_TEMPLATE.format(mask_num) + template[end_mask_pos:]
        template = " ".join(template.split())
        current_pos = end_mask_pos
        mask_pos = template.find(orig_mask_token, current_pos)
        mask_num += 1
    return template