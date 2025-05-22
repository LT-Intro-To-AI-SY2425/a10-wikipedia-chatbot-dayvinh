#Davin and Adrian
import re, string, calendar
from wikipedia import WikipediaPage
import wikipedia
from bs4 import BeautifulSoup
from match import match
from typing import List, Callable, Tuple, Any, Match


def get_page_html(title: str) -> str:
    """Gets html of a wikipedia page

    Args:
        title - title of the page

    Returns:
        html of the page
    """
    results = wikipedia.search(title)
    return WikipediaPage(results[0]).html()


def get_first_infobox_text(html: str) -> str:
    """Gets first infobox html from a Wikipedia page (summary box)

    Args:
        html - the full html of the page

    Returns:
        html of just the first infobox
    """
    soup = BeautifulSoup(html, "html.parser")
    results = soup.find_all(class_="infobox")

    if not results:
        raise LookupError("Page has no infobox")
    return results[0].text

def convert_to_float(number_str):
    return float(number_str.replace(',', ''))

def clean_text(text: str) -> str:
    """Cleans given text removing non-ASCII characters and duplicate spaces & newlines

    Args:
        text - text to clean

    Returns:
        cleaned text
    """
    only_ascii = "".join([char if char in string.printable else " " for char in text])
    no_dup_spaces = re.sub(" +", " ", only_ascii)
    no_dup_newlines = re.sub("\n+", "\n", no_dup_spaces)
    return no_dup_newlines


def get_match(
    text: str,
    pattern: str,
    error_text: str = "Page doesn't appear to have the property you're expecting",
) -> Match:
    """Finds regex matches for a pattern

    Args:
        text - text to search within
        pattern - pattern to attempt to find within text
        error_text - text to display if pattern fails to match

    Returns:
        text that matches
    """
    p = re.compile(pattern, re.DOTALL | re.IGNORECASE)
    match = p.search(text)

    if not match:
        raise AttributeError(error_text)
    return match


def get_percentage(country_name: str) -> str:
    infobox_text = clean_text(get_first_infobox_text(get_page_html(country_name)))
    pattern = r"Water\s*\(%\)\s*(?P<perc>[0-9]+(?:\.[0-9]+)?)"
    error_text = "Page infobox has no water information"
    match = get_match(infobox_text, pattern, error_text)
    return(match.group("perc"))

def get_area(country_name: str) -> str:
    infobox_text = clean_text(get_first_infobox_text(get_page_html(country_name)))
    pattern = r"(?:Area Total)(?: ?[\d]+ )?(?P<area>[\d,.]+)"
    error_text = "Page infobox has no area information"
    match = get_match(infobox_text, pattern, error_text)
    return(match.group("area"))

def get_population(country_name: str) -> str:
    infobox_text = clean_text(get_first_infobox_text(get_page_html(country_name)))
    pattern = r"Population(?: [^\n\r]*)?[:\s]+(?P<population>[\d,]+)"
    error_text = "Page infobox has no population information"
    match = get_match(infobox_text, pattern, error_text)
    return match.group("population")

def get_water_amount(country_name: str) -> str:
    
    infobox_text = clean_text(get_first_infobox_text(get_page_html(country_name)))
    pattern_a = r"(?:Area Total)(?: ?[\d]+ )?(?P<area>[\d,.]+)"
    error_text_a = "Page infobox has no area information"
    match_a = get_match(infobox_text, pattern_a, error_text_a)

    pattern_p = r"Water\s*\(%\)\s*(?P<perc>[0-9]+(?:\.[0-9]+)?)"
    error_text_p = "Page infobox has no water information"
    match_p = get_match(infobox_text, pattern_p, error_text_p)

    return (round(convert_to_float(match_a.group("area"))*(convert_to_float(match_p.group("perc"))/100)))

def water_amount(matches: List[str]) -> List[str]:

    return [get_water_amount(matches[0])]

def water_percentage(matches: List[str]) -> List[str]:
    return [get_percentage(matches[0])]

def country_population(matches: List[str]) -> List[str]:
    return [get_population(matches[0])]

def country_area(matches: List[str]) -> List[str]:
    return [get_area(matches[0])]



# dummy argument is ignored and doesn't matter
def bye_action(dummy: List[str]) -> None:
    raise KeyboardInterrupt


# type aliases to make pa_list type more readable, could also have written:
# pa_list: List[Tuple[List[str], Callable[[List[str]], List[Any]]]] = [...]
Pattern = List[str]
Action = Callable[[List[str]], List[Any]]

# The pattern-action list for the natural language query system. It must be declared
# here, after all of the function definitions
pa_list: List[Tuple[Pattern, Action]] = [
    ("how much of % is water".split(), water_amount),
    ("what percentage of % is water".split(), water_percentage),
    ("what is the area of %".split(), country_area),
    ("what is the population of %".split(), country_population),
    (["bye"], bye_action)
]


def search_pa_list(src: List[str]) -> List[str]:
    """Takes source, finds matching pattern and calls corresponding action. If it finds
    a match but has no answers it returns ["No answers"]. If it finds no match it
    returns ["I don't understand"].

    Args:
        source - a phrase represented as a list of words (strings)

    Returns:
        a list of answers. Will be ["I don't understand"] if it finds no matches and
        ["No answers"] if it finds a match but no answers
    """
    for pat, act in pa_list:
        mat = match(pat, src)
        if mat is not None:
            answer = act(mat)
            return answer if answer else ["No answers"]

    return ["I don't understand"]


def query_loop() -> None:
    """The simple query loop. The try/except structure is to catch Ctrl-C or Ctrl-D
    characters and exit gracefully"""
    print("Welcome to the movie database!\n")
    while True:
        try:
            print()
            query = input("Your query? ").replace("?", "").lower().split()
            answers = search_pa_list(query)
            for ans in answers:
                print(ans)

        except (KeyboardInterrupt, EOFError):
            break

    print("\nSo long!\n")


# uncomment the next line once you've implemented everything are ready to try it out
query_loop()