# Regex Search Utility

This is a command-line tool written in Python that mimics the behavior of `grep` by matching text against regular expressions. It implements its own custom regex engine that supports a subset of perl-style regular expressions and has the ability to search for patterns in files or from standard input.

The regex engine can also be imported as a standalone package. Info on the API the can be found [here](#Using-Package).

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

- `PTRN1|PTRN2`: Matches either `PTRN1` or `PTRN2`
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
perl_ext           := '(?' (':' | '=' | '!') regex ')'
backref            := '\' number
meta_sequence      := '\' ('d' | 'D'| 'w' | 'W' | 's' | 'S' | 'b')
escape             := '\' ('.' | '^' | '$' | '*' | '+' | '?' | '{' | '}' | '(' | ')' | '[' | ']' | '\' | '|')
```


## Using Program

The program is run from the command-line and has the following usage:

```
usage: grep.py [-h] [-r] [-o] [-n] [--color {always,never,auto}] PATTERN [FILE ...]

A regular expression pattern matching tool.
Search for PATTERN in each FILE. If no FILE is given
read from stdin or search files in '.' if -r is specified.

positional arguments:
  PATTERN               regular expression pattern
  FILE                  Search for PATTERN in each FILE

options:
  -h, --help            show this help message and exit
  -r, --recursive       if FILE is a directory, recursively search each
                        file in the directory for PATTERN
  -o, --only-matching   print only the matching text
  -n, --line-number     print line number with output lines
  --color {always,never,auto}
                        always: Always highlight matches in output
                        auto: Highlight matches only when outputing to a TTY
                        never: Never highlight matches in output
```

Ex:

1. Searching standard input:

```bash
python3 grep.py '(\d{3}-){2}\d{4}' < foo.txt
```

2. Searching files:

```bash
python3 grep.py '(\d{3}-){2}\d{4}' foo.txt bar.txt
```

3. Searching directory

```bash
python3 grep.py -r '(\d{3}-){2}\d{4}' dir/
```

> [!note]
> By default matches are highlighted when outputting to a TTY. To disable highlighting pass the `--color=never` option argument to the program.


## Using Package

You can import the regex engine to match strings against regular expressions in your own python programs. It follows a similar API to Python's standard library module `re`.  To use simply import `regex` and call the `compile()` function with your desired regular expression. The function returns a `Pattern` object that can be used to match strings against the regex pattern. 

Ex:

```python
import regex

pattern = regex.compile(r"(\d{3}-){2}\d{4}")
m = pattern.search("My number is 123-456-7890")

print(m) # Match(match='123-456-7890', span=(13, 25), captures={1: (17, 21)})
```

### API 

#### Functions

- `regex.compile(pattern)`: Returns a `Pattern` object that is used to match the pattern against strings

#### Pattern Object

- `Pattern.search(str)`: Will scan the entire string for the first location where the regular expression pattern produces a match and returns a corresponding `Match` object. If no match is found `None` is returned
- `Pattern.match(str)`: Will return a `Match` object if zero or more characters at the beginning of string match the regular expression pattern. If no match is found `None` is returned
- `Pattern.fullmatch(str)`:  Will return a `Match` object only if the **whole** string matches the regular expression pattern. If no match is found `None` is returned
- `Pattern.findall(str)`: Will scan the entire string and return all non-overlapping matches of pattern in string as a list of`Match` objects. The string is scanned left-to-right, and matches are returned in the order found. If no match is found and empty list is returned

#### Match Object

- `Match.match`: The substring that matched the pattern
- `Match.span`: A 2-tuple containing the start and end index of the matched substring
- `Match.captures`: A dictionary where the keys are group id's and values are 2-tuples containing the start and end index of the captured group
- `Match.group(int, ...)`: If there is a single argument, the result is the string that was captured by the corresponding group id. If there are multiple arguments, the result is a tuple of strings with one string per argument


## Requirements

- Python `v3.12+`