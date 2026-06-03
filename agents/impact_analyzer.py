def classify_impact(text: str) -> str:
    """Placeholder: devuelve 'low', 'medium' o 'high' según reglas simples."""
    txt = text.lower()
    if any(k in txt for k in ['crash', 'collapse', 'sanctions', 'war', 'panic']):
        return 'high'
    if any(k in txt for k in ['increase', 'surge', 'rally', 'concern']):
        return 'medium'
    return 'low'

if __name__ == '__main__':
    s = 'Gold surges after geopolitical tensions.'
    print(classify_impact(s))
