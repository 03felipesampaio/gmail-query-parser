import pyparsing as pp
import re
import json
import copy
from datetime import date


def parsed_result_to_dict(parsed_result: list) -> dict:
    return {
        parsed_values[0]: (
            remove_quotes_from_list(parsed_values[1])
            if isinstance(parsed_values[1], list)
            else remove_quotes_from_string(parsed_values[1])
        )
        for parsed_values in parsed_result
    }


def transform_email_size_to_bytes(token: list[str]) -> int:
    """Transform email size to bytes.

    Args:
        token (list[str]): Token with the email size and the unit of measure.

    Returns:
        int: Email size in bytes.
    """
    token = token[0]

    if token.endswith('K'):
        return int(token[:-1]) * 1024
    elif token.endswith('M'):
        return int(token[:-1]) * (1024**2)

    return int(token)


quoted_value = pp.quotedString.setParseAction(pp.removeQuotes)
# Allow multiple values inside parentheses and store them in a list
parenthesis_value = pp.nested_expr(
    "(", ")", content=quoted_value | pp.Word(pp.alphanums + "/" + "@" + ".")
)

@parenthesis_value.set_parse_action
def parse_parentheses(values: list[list[str]]) -> re.Pattern:
    """Parse parentheses. If there is a parentheses inside a string, it will be parsed to a regex pattern with the following format: "(word1|word2|word3)".

    The parentheses works as an OR operator, it will match any of the words inside the parentheses.

    Ex.: subject:(hello oi ciao "bon soir") will create the pattern r'hello|oi|ciao|bon soir'. Matching 'hello Julia', 'Julia, oi', 'ciao, io sono Julia' or 'bon soir Julia'.
    """
    # print('values:', values)
    return  re.compile('|'.join(remove_quotes_from_list(values[0])))


# Keywords that accept strings
string_keywords = pp.one_of(
    "from to subject cc bcc label list deliveredto filename rfc822msgid"
)

string_keywords_values = (
    parenthesis_value | quoted_value | pp.Word(pp.alphanums + "/" + "@" + ".")
)

@string_keywords_values.set_parse_action
def parse_string_values(values: list[str]) -> re.Pattern:
    """Parse string values. If there is a string inside a string, it will be parsed to a regex pattern with the following format: "word1 word2 word3".

    The string values works as an AND operator, it will match all the words inside the string.

    Ex.: subject:"hello world" will create the pattern r'hello world'. Matching 'hello world', 'hello my dear world', 'hello my dear amazing world', etc.
    """
    value = None

    if isinstance(values[0], str):
        value = re.compile(values[0])
    elif isinstance(values[0], re.Pattern):
        value = values[0]
    else:
        raise ValueError(f"When converting string value to pattern, found this invalid data type: {type(values[0])}")
    
    return value

string_keywords_pair = pp.Group(
    string_keywords + pp.Suppress(":") + string_keywords_values
)

# Keywords that accept strings, but the values have a limited set of options
KEYWORDS_WITH_OPTIONS = (
    pp.Group(
        pp.Literal("category")
        + pp.Suppress(":")
        + pp.one_of(
            [
                "primary",
                "social",
                "promotions",
                "updates",
                "forums",
                "reservations",
                "purchases",
            ]
        ),
    )
    | pp.Group(
        pp.Literal("has")
        + pp.Suppress(":")
        + pp.one_of(
            [
                "attachment",
                "drive",
                "document",
                "spreadsheet",
                "presentation",
                "youtube",
                "link",
                "userlabels",
                "nouserlabels",
                "yellow-star",
                "orange-star",
                "red-star",
                "purple-star",
                "blue-star",
                "green-star",
                "red-bang",
                "orange-guillemet",
                "yellow-bang",
                "green-check",
                "blue-info",
                "purple-question",
            ]
        ),
    )
    | pp.Group(
        pp.Literal("in") + pp.Suppress(":") + pp.one_of(["anywhere", "snoozed"]),
    )
    | pp.Group(
        pp.Literal("is")
        + pp.Suppress(":")
        + pp.one_of(["muted", "important", "starred", "unread", "read"]),
    )
)


# Keywords that accept dates
year_first_date = pp.Group(pp.Word(pp.nums, exact=4) + pp.Suppress("/") + pp.Word(pp.nums, exact=2) + pp.Suppress("/") + pp.Word(pp.nums, exact=2)).set_parse_action(lambda t: date(int(t[0][0]), int(t[0][1]), int(t[0][2])))
month_first_date = pp.Group(pp.Word(pp.nums, exact=2) + pp.Suppress("/") + pp.Word(pp.nums, exact=2) + pp.Suppress("/") + pp.Word(pp.nums, exact=4)).set_parse_action(lambda t: date(int(t[0][2]), int(t[0][0]), int(t[0][1])))
relative_date = pp.Word(pp.nums)

date_keywords_values = year_first_date | month_first_date | relative_date

pp.Word(
    pp.nums + "/"
)  # TODO: Add date validation, the tags accept dates in the format YYYY/MM/DD and MM/DD/YYYY
DATE_KEYWORDS = pp.Group(pp.one_of("after before older newer") + pp.Suppress(":") + date_keywords_values)

# Keywords that accept a specific format
than_keywords_values = pp.Combine(pp.Word(pp.nums) + pp.one_of("d m y")[1])
than_keywords_pair = pp.Group(pp.one_of("older_than newer_than") + pp.Suppress(":") + than_keywords_values)

size_keywords_values = pp.Combine(pp.Word(pp.nums) + pp.one_of("K M")[0, 1]).set_parse_action(transform_email_size_to_bytes)
size_keywords_pair = pp.Group(pp.one_of("larger smaller size") + pp.Suppress(":") + size_keywords_values)

KEYWORDS = (
    string_keywords_pair
    | DATE_KEYWORDS
    | than_keywords_pair
    | size_keywords_pair
    | KEYWORDS_WITH_OPTIONS
)

NOT_KEYWORD = pp.Group(pp.Literal("-") + KEYWORDS)#.set_parse_action(lambda t: (t[0], t[1][0]))
@NOT_KEYWORD.setParseAction
def not_tag_parse_action(t):
    print('t:', type(t))
    return t


pair = pp.ZeroOrMore(KEYWORDS | NOT_KEYWORD).set_parse_action(lambda t: parsed_result_to_dict(t))


def remove_quotes_from_string(string: str):
    if isinstance(string, str) and string.startswith('"') and string.endswith('"'):
        return string[1:-1]

    return string


def remove_quotes_from_list(strings: list[str]):
    return [remove_quotes_from_string(s) for s in strings]


# def parse_around_tag(string: str) -> str:
#     """Parse AROUND tag. If there is a AROUND tag inside a string, it will be parsed to a regex pattern with the following format: "pre_around_string (\w+\s+){0, AROUND_NUM} post_around_string".

#     The AROUND tag works as a proximity search, it will match the words that are around the specified number of words.

#     Ex.: "hello AROUND 3 world" will match "hello world", "hello my dear world", "hello my dear amazing world", etc.
#     """
#     # FIXME: This raises a SyntaxWarning: invalid escape sequence \w
#     return re.sub(
#         r"\s+AROUND\s+(\d+)\s+",
#         lambda m: r'\s+(\w+\s+){{1,{}}}'.format(int(m.group(1))),
#         string,
#         1,
#     )


def match_message(message: dict, query: str, labels: dict = None) -> bool:
    """Match a message with a query.

    Args:
        message (dict): Message to be matched.
        query (str): Query to be used to match the message.
        labels (dict, optional): Gmail messages only have labels ids, 
            so when matching labels this argument should receive a dict with format:
            {label_1_id: label_1_name, ...}. 
            Defaults to None.

    Returns:
        bool: True if the message matches the query, False otherwise.
    """
    message = copy.deepcopy(message)
    message['payload']['headers'] = {header['name']: header['value'] for header in message['payload']['headers']}
    filter_params = pair.parse_string(query, parse_all=True)[0]
    results = []

    for key, value in filter_params.items():
        if key == 'from':
            # message_from = [header['value'] for header in message['payload']['headers'] if header['name'] == 'From'][0]
            message_from = message['payload']['headers']['From']
            print(f"Matching '{value}' with '{message_from}'. Result: {bool(re.search(value, message_from))}")
            results.append(re.search(value, message_from))
        if key == 'subject':
            # message_subject = [header['value'] for header in message['payload']['headers'] if header['name'] == 'Subject'][0]
            message_subject = message['payload']['headers']['Subject']
            print(f"Matching '{value}' with '{message_subject}'. Result: {bool(re.search(value, message_subject))}")
            results.append(re.search(value, message_subject))
        if key == 'label':
            # TODO: The message only receives the label id, we need to get the label name
            results.append(True)
        if key == 'size':
            # TODO Apparently the size tag has a tolerace. I need to discover the percentage.
            message_size = int(message['sizeEstimate'])
            print(f"Matching '{value}' with '{message_size}'. Result: {message_size == value}")
            results.append(message_size == value)
        if key == 'smaller':
            message_size = int(message['sizeEstimate'])
            print(f"Matching '{value}' with '{message_size}'. Result: {message_size < value}")
            results.append(message_size < value)
        if key == 'larger':
            message_size = int(message['sizeEstimate'])
            print(f"Matching '{value}' with '{message_size}'. Result: {message_size > value}")
            results.append(message_size > value)
        if key == 'is':
            if value == 'unread':
                message_is_unread = 'UNREAD' in message['labelIds']
                print(f"Matching '{value}' with '{message_is_unread}'. Result: {message_is_unread}")
                results.append(message_is_unread)
            if value == 'read':
                message_is_read = 'UNREAD' not in message['labelIds']
                print(f"Matching '{value}' with '{message_is_read}'. Result: {message_is_read}")
                results.append(message_is_read)
            # TODO Implement important and unread
        if key == 'filename':
            match_files = []
            if '.' not in value: # That means that we only look for the file extension
                extension = value
                for part in message['payload']['parts']: # TODO Check if all messages parts have a filename key
                    filename = part['filename']
                    print(f"Matching '{extension}' with '{filename}'. Result: {bool(filename.endswith(extension))}")
                    match_files.append(filename.endswith(extension))
            else:
                for part in message['payload']['parts']:
                    filename = part['filename']
                    print(f"Matching '{value}' with '{filename}'. Result: {filename == value}")
                    match_files.append(filename == value)
            results.append(any(match_files))

    return all(results)

if __name__ == "__main__":
    for param in [
        'from:"me@gmail.com" subject:("hello world" world) older_than:1m larger:1M category:primary newer:2021/01/01 older:12/31/2021',
        # 'subject:("hello world")',
    ]:
        parsed = pair.parse_string(param)
        print(parsed)


    # print(parse_around('subject:"Hello AROUND 2 World AROUND 1"'))

    # with open('messages/uber/recibos/19254d1fef585a1b.json', 'r') as f:
    #     message = json.load(f)
    
    # match_message(message, 'from:"Recibos da Uber" subject:(viagem "a Uber") size:94045 larger:10K smaller:1M')