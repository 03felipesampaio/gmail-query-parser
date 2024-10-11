# gmail-query-parser
A Python module to parse Gmail queries and match it with messages 

## What is a Gmail Query?

Gmail Queries are used to search for messages in Gmail. Gmail has a special syntax to define specif filters to apply to the messages. Is a nice way to interact with your emails.
If you have a Gmail account you can try it out in the search bar.

### How does it looks like?

The syntax is very simple. The most basic query is just a word that you want to search for. For example, if you want to search for all the emails that contains the word "Hello" you just need to type `Hello` in the search bar. But we can get more advanced than that. For example:

- `from:Uber subject:Ride older:2024/09/25 newer:09/23/2024` will search for all the emails from Uber with a subject that contains "Ride" that are older than 2024/09/25 and newer than 09/23/2024.
- `from:"American Airlines" subject:(ticket flight) has:attachment` will search for all the emails from American Airlines with a subject that contains "ticket" or "flight" that has an attachment.

There are many more filters that you can use. You can check the full list in Google's official documentation, avaliable [here](https://support.google.com/mail/answer/7190?hl=en).


## What is this module for?

This module is a parser for Gmail Queries. It will take a string as input and return a dictionary with the filters that the query contains. For example, if you pass the string `from:Uber subject:Ride older:2024/09/25 newer:09/23/2024` to the parser, it will return the following dictionary:

```python
{
    'from': 'Uber',
    'subject': 'Ride',
    'older': '2024/09/25',
    'newer': '09/23/2024'
}
```