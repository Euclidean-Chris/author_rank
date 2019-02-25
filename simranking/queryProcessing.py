# -*- coding: utf-8 -*-
"""
Created on Wed Oct 18 11:41:32 2017

@author: Isaac
"""
import Textual_relevance as  texRel
 
 
# words = {1: 'bar', 2: 'restuarance: rice and jollof', 3: 'motel', 4: 'noodles: rice and beans', 5: 'hot dog', 6: 'rice', 7: 'restaurant',}

# import heap
# h = heap.Heap()
# for keys, values in words.items():
#     h.push(keys)
#
# while len(h) > 0:
#     print(words[h.pop()])

""" computing the textual relevance for query keywords"""
text1 = 'hotel noodle, rice.'
text2 = 'hotel'

vector1 = texRel.text_to_vector(text1)
vector2 = texRel.text_to_vector(text2)
cosine = texRel.get_cosine(vector1, vector2)


print ('Cosine:', cosine)
