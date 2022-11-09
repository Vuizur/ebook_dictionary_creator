# A function to extract the languages out of following HTML:
# <li><a href="English/index.html">English (1367202 senses)</a></li>
# <li><a href="Latin/index.html">Latin (968851 senses)</a></li>
# <li><a href="Spanish/index.html">Spanish (829631 senses)</a></li>

import requests
import html




def get_languages_from_html(html_str: str) -> list[str]:
    """
    Gets the languages from the HTML.
    """
    languages = []
    for line in html_str.split("\n"):
        if "<li><a href=" in line:
            lang = html.unescape(line.split('"')[1].split("/")[0])
            if lang.strip() != "All languages combined":
                languages.append(lang)

    return languages

def download_languages_list() -> list[str]:
    # download html from https://kaikki.org/dictionary/
    r = requests.get("https://kaikki.org/dictionary/")
    # Apparently the HTML is encoded in ISO-8859-1
    r.encoding = r.apparent_encoding
    html = r.text
        
    # print html to file
    with open("languages.html", "w", encoding="utf-8") as f:
        f.write(html)
    # delete all text before <h2>Available languages</h2>
    html = html.split("<h2>Available languages</h2>")[1]
    return get_languages_from_html(html)

if __name__ == "__main__":
    # Print all languages to a txt file
    #languages = get_languages_from_html(ALL_LANGUAGES_HTML)
    languages = download_languages_list()
    with open("languages.txt", "w", encoding="utf-8") as f:
        f.write("\n".join(languages))
