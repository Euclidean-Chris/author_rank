import requests
from bs4 import BeautifulSoup

term = {'q': 'The quick brown fox jumps over the lazy dog'+'+'+'Good', 'tbs': 'li:1'}

r = requests.get('http://citeseerx.ist.psu.edu/search', params=term)
# r = requests.get('https://www.google.com.gh/search', params=term)

soup = BeautifulSoup(r.text, 'html.parser')
result = soup.find('div', {'id': 'result_info'}).text

resultNumber = int("".join(_ for _ in result if _ in ".1234567890"))

print(resultNumber)


