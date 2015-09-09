import urllib2
import re
from bs4 import BeautifulSoup

html = urllib2.urlopen('http://hacks.mit.edu/Hacks/by_year/1992/spellbook/').read()
soup = BeautifulSoup(html, "html.parser")
text = soup.findAll(text=True)
# [s.extract() for s in soup(['style', 'script', '[document]', 'head', 'title'])]
visible_text = soup.findAll(text = True)
print visible_text
