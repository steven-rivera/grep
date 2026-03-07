# Regex Search Utility

This is a command-line tool written in Python that mimics the behavior of `grep` by matching text against regular expressions. It implements its own custom regex engine that supports a subset of perl-style regular expressions and has the ability to search for patterns in files or from standard input.

The regex engine can also be imported as a standalone library. More info can be found [here](#As-Module).

<div align="center">  
    <img src="images/example.png" width="75%"/>
</div>

## Supported Tokens

### Dot

- `.`: Matches any character

### Anchors

- `^`: Asserts that the following pattern must match at the start of the input or line
    - Ex: `^World` matches `World` but not `Hello World`
- `$`: Asserts that the preceding pattern must match at the end of the input or line
    - Ex: `World$` matches `Hello World` but not `Worldwide`

### Quantifiers

#### Repetition Operators

- `*`: Greedily matches 0 or more occurrences of the previous element
    - Ex: `ca*t` matches `ct` or `caaat` but not `cut`
- `+`: Greedily matches 1 or more occurrences of the previous element
    - Ex: `do+g` matches `dog` or `dooog` but not `dg`
- `?`: Matches 0 or 1 occurrence of the previous element
    - Ex: `ba?t` matches `bat`or `bt` but not `baat`

#### Ranges

- `{n}`: Matches exactly `n` occurrences of the previous element 
    - Ex: `ca{3}t` matches `caaat` but not `caat`
- `{n,m}`: Greedily matches between `n` and `m` occurrences of the previous element 
    - Ex: `(ha){2,3}` matches `haha` and `hahaha` but not `ha`
- `{n,}`: Greedily matches `n` or more occurrences of the previous element 
    - Ex: `bo{2,}` matches `boooo` but not `bo`

### Lazy Quantifiers

- `*?`: Matches as few characters as possible 
    - Ex: `a*?` will match the empty string in `aaa` rather than the whole string

`?` is supported after **all** quantifiers

### Meta Sequences

- `\d`: Matches any digit (0-9)
    - Ex: `\d apples` matches `5 apples` but not `five apples`
- `\D`: Matches everything that is **not** a digit
- `\w`: Matches any word character (letters, digits, underscores). Same as `[a-zA-Z0-9_]`
    - Ex: `\w\w`matches `hi` but not `h!`
- `\W`: Matches everything that is **not** a word character
- `\s`: Matches any whitespace character (space, tab, newline)
    - Es: `a\s+b` matches `a b`, `a  b`, `a   b` and so on 
- `\S`: Matches everything that is **not** a whitespace character
- `\b`: Matches, without consuming any characters, immediately between a character matched by `\w` and a character not matched by `\w` (in either order) 
    - Ex: `\bcar\b` matches `car` but not `racecar`

### Character Classes

- `[...]`: matches any one of the characters listed
    - Ex: `[bc]at` matches `cat` but not `rat`
- `[^...]`: matches any character except the ones listed
    - Ex: `[^bc]at` matches `rat` but not `cat`
- `[a-f]`: matches any character in the range `a` - `f`
    - Ex: `[a-f]at` matches `bat` but not `hat`

### Alternation

- `PTRN1|PTRN2`: Matches either `PTRN1` or `PATRN2`
    - Ex: `cat|dog` matches `cat` or `dog` but not `bat`

### Grouping

- `(...)`: Isolates part of the full match to be later referred to by ID within the regex. Can also be used in combination with repetition operators or ranges.
    - Ex: `(ab)+` matches `ab`, `abab`, `ababab` and so on

### Backreference

- `\n`: refers to the nth grouped sub pattern, allowing you to reuse the matched text later in the pattern
    - Ex: `(\w+) egg and \1 ham` matches `green eggs and green ham`

### Perl Extensions

- `(?:...)`: Non-capturing group. Allows you to apply quantifiers to part of your regex but does not capture/assign an ID to group
- `(?=...)`: Asserts that the given subpattern can be matched here, without consuming characters
    - Ex: `foo(?=bar)` matches `foo` in `foobar` but not the `foo` in `foobaz`
- `(?!...)`: Asserts that the given subpattern does not match at the current position in the expression, without consuming characters.
    - Ex: `foo(!=bar)` matches `foo` in `foobaz` but not the `foo` in `foobar`


## Regex Grammar

The regex engine supports the following grammar:

```
regex              := sequence ('|' sequence)*
sequence           := repetition+
repetition         := atom (( '*' | '+' | '?' | range ) '?'?)?
range              := '{' number (',' number?)? '}'
number             := ('0' | '1' | ... | '9')+

atom               := '.' | '^' | '$' | literal | char_class | group | backref | meta_sequence | escape | perl_ext
char_class         := '[' '^'? (literal | literal '-' literal)+ ']'
group              := '(' regex ')'
per_lext           := '(?' (':' | '=' | '!') regex ')'
backref            := '\' number
meta_sequence      := '\' ('d' | 'D'| 'w' | 'W' | 's' | 'S' | 'b')
escape             := '\' ('.' | '^' | '$' | '*' | '+' | '?' | '{' | '}' | '(' | ')' | '[' | ']' | '\' | '|')
```


## Usage

### As Program

The program is run from the command-line and has the following usage:

```
usage: main.py [-h] [-f FILE] PATTERN

positional arguments:
  PATTERN               regular expression pattern

options:
  -h, --help            show this help message and exit
  -f FILE, --file FILE  file to search for all occurences of pattern. 
                        If no file is provided read from stdin
```
  
#### Examples

1. Searching a file:

```bash
python3 main.py -f example.txt "(\d{3}-){2}\d{4}"
```

2. Searching standard input:

```bash
cat example.txt | python3 main.py "(\d{3}-){2}\d{4}"
```


### As Module

You can import the regex engine to match strings against regular expressions in your own python programs. It follows a similar API to Python's standard library module `re`.  To use simply import `regex` and call the `compile(regex)` function with your desired regular expression. The function returns a `Pattern` object that can be used to match strings against the regex pattern. `Pattern` supports the following methods:

- `Pattern.search(str)`: Will search the entire string and return the first  substring that matches as a `Match` object or `None` if no match was found
- `Pattern.match(str)`: Will return a `Match` object if the pattern matches at the **beginning** of the string, else `None`
- `Pattern.fullmatch(str)`:  Will return a `Match` object only if the pattern matches the **entire** string, else `None`
- `Pattern.findall(str)`: Will search the entire string and return all substrings that match the pattern and return a list of `Match` objects 


#### Example

```python
import regex

pattern = regex.compile(r"(\d{3}-){2}\d{4}")
m = pattern.search("My number is 123-456-7890")

print(m) # Match(match='123-456-7890', span=(13, 25), captures={1: (17, 21)})
```


## Requirements

- Python `v3.12+`