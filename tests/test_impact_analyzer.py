import os
from unittest.mock import patch

import agents.impact_analyzer as ia


def test_rule_based_high():
    text = 'Major war and sanctions cause panic and gold rally.'
    label = ia.classify_impact(text, use_openai=False)
    assert label == 'high'


def test_rule_based_low():
    text = 'Minor market update with low relevance.'
    label = ia.classify_impact(text, use_openai=False)
    assert label == 'low'


def test_openai_mock():
    # Mock OpenAI response
    class Msg:
        def __init__(self, content):
            self.content = content

    class Choice:
        def __init__(self, msg):
            self.message = msg

    class Resp:
        def __init__(self, content):
            self.choices = [Choice(Msg(content))]

    with patch('agents.impact_analyzer.openai.ChatCompletion.create', return_value=Resp('high because major event')):
        os.environ['OPENAI_API_KEY'] = 'dummy'
        os.environ['USE_OPENAI_IMPACT'] = 'true'
        label = ia.classify_impact('irrelevant text', use_openai=True)
        assert label == 'high'
