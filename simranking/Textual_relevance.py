import re, math
from collections import Counter

WORD = re.compile(r'\w+')

def get_cosine(vec1, vec2):
     intersection = set(vec1.keys()) & set(vec2.keys())
     numerator = sum([vec1[x] * vec2[x] for x in intersection])

     sum1 = sum([vec1[x]**2 for x in vec1.keys()])
     sum2 = sum([vec2[x]**2 for x in vec2.keys()])
     denominator = math.sqrt(sum1) * math.sqrt(sum2)

     if not denominator:
        return 0.0
     else:
        return float(numerator) / denominator

def text_to_vector(text):
     words = WORD.findall(text)
     return Counter(words)


def format_matrix(header, matrix, top_format, left_format, cell_format, row_delim, col_delim):

    table = [[''] + header] + [[name] + row for name, row in zip(header, matrix)]

    table_format = [['{:^{}}'] + len(header) * [top_format]] \
                 + len(matrix) * [[left_format] + len(header) * [cell_format]]
    col_widths = [max(len(format.format(cell, 0))
                      for format, cell in zip(col_format, col))
                  for col_format, col in zip(zip(*table_format), zip(*table))]
    return row_delim.join(
               col_delim.join(
                   format.format(cell, width)
                   for format, cell, width in zip(row_format, row, col_widths))
               for row_format, row in zip(table_format, table))

print(format_matrix(['Man Utd', 'Man City', 'T Hotspur', 'Really Long Column'],
                    [[1, 2, 1, -1], [0, 1, 0, 5], [2, 4, 2, 2], [0, 1, 0, 6]],
                    '{:^{}}', '{:<{}}', '{:>{}.3f}', '\n', ' | '))