"""
Lightweight NLP helpers used to pre-process uploaded notes before sending
them to Gemini, and to provide an offline fallback (extractive summary,
keyword frequency) when no Gemini API key is configured.

Deliberately dependency-light (pure Python + regex) so the project runs
anywhere without extra downloads (no NLTK corpora required).
"""

import re
from collections import Counter

STOPWORDS = set("""
a about above after again against all am an and any are aren't as at be
because been before being below between both but by can't cannot could
couldn't did didn't do does doesn't doing don't down during each few for
from further had hadn't has hasn't have haven't having he he'd he'll he's
her here here's hers herself him himself his how how's i i'd i'll i'm i've
if in into is isn't it it's its itself let's me more most mustn't my myself
no nor not of off on once only or other ought our ours ourselves out over
own same shan't she she'd she'll she's should shouldn't so some such than
that that's the their theirs them themselves then there there's these they
they'd they'll they're they've this those through to too under until up
very was wasn't we we'd we'll we're we've were weren't what what's when
when's where where's which while who who's whom why why's with won't would
wouldn't you you'd you'll you're you've your yours yourself yourselves
""".split())


def clean_text(text: str) -> str:
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def split_sentences(text: str) -> list:
    text = clean_text(text)
    sentences = re.split(r"(?<=[.!?])\s+", text)
    return [s.strip() for s in sentences if len(s.strip()) > 3]


def extract_keywords(text: str, top_n: int = 10) -> list:
    words = re.findall(r"[A-Za-z][A-Za-z'-]{2,}", text.lower())
    words = [w for w in words if w not in STOPWORDS]
    freq = Counter(words)
    return [w for w, _ in freq.most_common(top_n)]


def extractive_summary(text: str, num_sentences: int = 4) -> str:
    """Simple frequency-based extractive summarizer used as an offline
    fallback when no Gemini API key is available."""
    sentences = split_sentences(text)
    if len(sentences) <= num_sentences:
        return " ".join(sentences)

    words = re.findall(r"[A-Za-z][A-Za-z'-]{2,}", text.lower())
    words = [w for w in words if w not in STOPWORDS]
    freq = Counter(words)
    if not freq:
        return " ".join(sentences[:num_sentences])
    max_freq = max(freq.values())
    for w in freq:
        freq[w] = freq[w] / max_freq

    scores = []
    for i, sent in enumerate(sentences):
        sent_words = re.findall(r"[A-Za-z][A-Za-z'-]{2,}", sent.lower())
        score = sum(freq.get(w, 0) for w in sent_words)
        scores.append((score, i, sent))

    top = sorted(scores, reverse=True)[:num_sentences]
    top_in_order = [s for _, _, s in sorted(top, key=lambda x: x[1])]
    return " ".join(top_in_order)


def word_count(text: str) -> int:
    return len(re.findall(r"\S+", text))
