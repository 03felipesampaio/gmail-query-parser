import pyparsing as pp

greet = pp.Word(pp.alphas) + ',' + pp.Word(pp.alphas) + '!'

for greeting_str in ['Hello, Felipe!', 'Oi, Felipe!', 'Ciao, Leticia!']:
    greeting = greet.parse_string(greeting_str)
    print(greeting)