import pytest

from src import parser_gmail


@pytest.mark.parametrize(
    'query, expected',
    [
        ('from:me', {'from': 'me'}),
        ('from:me@gmail.com', {'from': 'me@gmail.com'}),
        ('to:me', {'to': 'me'}),
        ('subject:hello', {'subject': 'hello'}),
        ('after:2021/01/01', {'after': '2021/01/01'}),
        ('older_than:1m', {'older_than': '1m'}),

        # Quoted values
        ('from:"me@gmail.com"', {'from': 'me@gmail.com'}),
        ('from:"me_1@gmail.com"', {'from': 'me_1@gmail.com'}),
        ('from:"1.me@gmail.com"', {'from': '1.me@gmail.com'}),

        # Parenthesis values
        ('subject:(hello)', {'subject': ['hello']}),
        ('subject:("hello world")', {'subject': ['hello world']}),
        # ('subject:(dinner movie)', {'subject': ['dinner', 'movie']}),

        # Composed queries
        ('from:me to:you', {'from': 'me', 'to': 'you'}),
        ('from:me subject:hello', {'from': 'me', 'subject': 'hello'}),
        ('to:me subject:hello', {'to': 'me', 'subject': 'hello'}),
        ('from:me to:you subject:hello', {'from': 'me', 'to': 'you', 'subject': 'hello'}),
        ('from:me to:you subject:hello after:2021/01/01', {'from': 'me', 'to': 'you', 'subject': 'hello', 'after': '2021/01/01'}),
        ('from:me to:you subject:hello before:2021/01/01', {'from': 'me', 'to': 'you', 'subject': 'hello', 'before': '2021/01/01'}),
        # ('from:me to:you subject:hello after:2021/01/01 before:2021/01/02', {'from': 'me', 'to': 'you', 'subject': 'hello', 'after': '2021/01/01', 'before': '2021/01/02'}),
        # ('from:me to:you subject:hello after:2021/01/01 before:2021/01/02 is:unread', {'from': 'me', 'to': 'you', 'subject': 'hello', 'after': '2021/01/01', 'before': '2021/01/02', 'is': 'unread'}),
        # ('from:me to:you subject:hello after:2021/01/01 before:2021/01/02 is:read', {'from': 'me', 'to': 'you', 'subject': 'hello', 'after': '2021/01/01', 'before': '2021/01/02', 'is': 'read'}),
        # ('from:me to:you subject:hello after:2021/01/01 before:2021/01/02 is:starred', {'from': 'me', 'to': 'you', 'subject': 'hello', 'after': '2021/01/01', 'before': '2021/01/02', 'is': 'starred'}),
    ]
)
def test_parse_gmail_query(query, expected):
    assert parser_gmail.parse_string(query) == expected



@pytest.mark.parametrize(
    'query, expected',
    [
        ('from:"me"', 'from:"me"'),
        ('subject:"Hello AROUND 1 World"', 'subject:"Hello\s+(\w+\s+){0,1}World"'),
    ]
)
def test_parse_around(query, expected):
    assert parser_gmail.parse_around_tag(query) == expected