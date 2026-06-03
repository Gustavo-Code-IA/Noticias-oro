import os
import logging
from typing import Tuple

logger = logging.getLogger(__name__)

try:
    import openai
except Exception:
    openai = None


def _rule_based_score(text: str) -> Tuple[str, str]:
    txt = text.lower()
    high_words = ['crash', 'collapse', 'sanctions', 'war', 'panic', 'default', 'debt', 'collapse', 'bomb', 'invasion']
    med_words = ['increase', 'surge', 'rally', 'concern', 'uncertainty', 'inflation', 'rate', 'hike', 'cut']
    score = 0
    hits = []
    for w in high_words:
        if w in txt:
            score += 3
            hits.append(w)
    for w in med_words:
        if w in txt:
            score += 1
            hits.append(w)

    if score >= 3:
        return 'high', f"rule_hits={hits}"
    if score >= 1:
        return 'medium', f"rule_hits={hits}"
    return 'low', 'rule_hits=[]'


def _openai_classify(text: str) -> Tuple[str, str]:
    if openai is None:
        raise RuntimeError('openai package not available')
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        raise RuntimeError('OPENAI_API_KEY not set')
    openai.api_key = api_key
    timeout = int(os.getenv('OPENAI_TIMEOUT', '10'))
    prompt = (
        "Clasifica el siguiente texto según el impacto que tendría sobre el precio del oro como activo refugio: "
        "Responde solo con una palabra: low, medium o high. Después de la palabra, opcionalmente indica en una frase corta la razón.\n\n"
        f"Texto:\n" + text
    )
    try:
        resp = openai.ChatCompletion.create(
            model=os.getenv('OPENAI_MODEL', 'gpt-3.5-turbo'),
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
            timeout=timeout
        )
        out = resp.choices[0].message.content.strip()
        # normalize
        first = out.split()[0].lower()
        if first in ('low', 'medium', 'high'):
            reason = out[len(first):].strip()
            return first, reason or 'from_openai'
        # fallback parse
        if 'high' in out.lower():
            return 'high', out
        if 'medium' in out.lower():
            return 'medium', out
        return 'low', out
    except Exception as e:
        logger.exception('OpenAI classification failed: %s', e)
        raise


def classify_impact(text: str, use_openai: bool | None = None) -> str:
    """Clasifica el impacto de una noticia sobre el oro: 'low'|'medium'|'high'.

    Comportamiento:
    - Si `use_openai` es True o si la variable de entorno `USE_OPENAI_IMPACT` es 'true' y
      `OPENAI_API_KEY` existe, se intentará usar OpenAI. Si falla, se usa el fallback rule-based.
    - Si no, se usa una heurística local.
    """
    env_use = os.getenv('USE_OPENAI_IMPACT', '').lower() == 'true'
    want_openai = (use_openai is True) or (use_openai is None and env_use)
    if want_openai:
        try:
            label, reason = _openai_classify(text)
            logger.info('OpenAI impact: %s (%s)', label, reason)
            return label
        except Exception:
            logger.info('Falling back to rule-based impact classifier')

    label, reason = _rule_based_score(text)
    logger.info('Rule-based impact: %s (%s)', label, reason)
    return label


if __name__ == '__main__':
    s = 'Gold surges after geopolitical tensions and central bank rate hikes.'
    print('Input:', s)
    print('Impact:', classify_impact(s))
