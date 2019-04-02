import datetime
import math
import re
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

from django.core import serializers
from django.shortcuts import render
from django.views.generic.base import View
from django.template import loader

from .decorators import template
from django.http import HttpResponse, HttpResponseRedirect, Http404, JsonResponse
from django.template import RequestContext
from django.urls import reverse
from django.shortcuts import get_object_or_404
import logging
import pandas as pd
import numpy as np

from collections import Counter

from .models import Paper, Author, PaperAuthor

# import ssl
# try:
#     _create_unverified_https_context = ssl._create_unverified_context
# except AttributeError:
#     pass
# else:
#     ssl._create_default_https_context = _create_unverified_https_context
#
# nltk.download('punkt')
# nltk.download('stopword')


# Global variables
WORD = re.compile(r'\w+')


# Create your views here.

@template('index.html')
def index(request, a_id):
    return render(request, 'index.html')


def cleanup(a_string):
    filtered_sentence = [w for w in word_tokenize(a_string) if not w in stopwords.words()]
    # print(filtered_sentence)
    return filtered_sentence


def text_to_vector(text):
    words = cleanup(text)
    # words = WORD.findall(text)
    return Counter(words)


# COSINE SIMILARITY
def get_cosine(vec1, vec2):
    vec1 = text_to_vector(vec1.lower())
    vec2 = text_to_vector(vec2.lower())

    intersection = set(vec1.keys()) & set(vec2.keys())

    numerator = sum([vec1[x] * vec2[x] for x in intersection])

    sum1 = sum([vec1[x] ** 2 for x in vec1.keys()])
    sum2 = sum([vec2[x] ** 2 for x in vec2.keys()])

    denominator = math.sqrt(sum1) * math.sqrt(sum2)

    if not denominator:
        return 0.0
    else:
        return float(numerator) / denominator


# QUERY RELEVANCE FOR THE SEARCH QUERY
def get_query_relevance(search_query):
    papers = Paper.objects.all()
    paper_score = {}
    for paper in papers:
        cosine_similarity = get_cosine(search_query, paper.title)
        paper_score.setdefault(paper.doi, []).append(cosine_similarity)
    return paper_score


def author_score(collaboration_level, score):
    return np.exp((1 / int(collaboration_level)) * score[0])


def get_author(author_name):
    author = Author.objects.filter(author_name=author_name).first()
    return author


def publication_count(author_id):
    count = PaperAuthor.objects.filter(a_id=author_id).count()
    return count


def sort_score(author_scores):
    #publication
    #keywords
    new_author_score = {}
    for k, v in sorted(author_scores.items(), reverse=True, key=lambda x: x[1][0]):
        author = get_author(k)
        new_author_score.setdefault(k, []).append({'score': v[0], 'a_id': author.a_id, 'affiliation': author.affiliation,
                                                   'count': publication_count(author.a_id),'h_index': author.h_index,
                                                   'keywords': author.keywords})
    return new_author_score


def check_authors(paper_score):
    author_scores = {}
    author_scores_final = {}
    for idx, score in paper_score.items():
        paper_aut = PaperAuthor.objects.filter(doi=idx)
        if not 0.0 in score:
            for author in paper_aut:
                aut = Author.objects.filter(a_id=author.a_id).first()
                author_scores.setdefault(aut.author_name, []).append(author_score(author.collaboration_level, score))

    for idx2, old_score in author_scores.items():
        get_author(idx2)
        author_scores_final.setdefault(idx2, []).append(sum(old_score))
    return sort_score(author_scores_final)


def search_author(request):
    paper_title = request.GET.get('author_name', None)
    check_authors(get_query_relevance(paper_title))
    data = {
        'available_paper': check_authors(get_query_relevance(paper_title))
    }
    # if data['available_paper']:
    #     data['error_message'] = 'Bad search query.'
    return JsonResponse(data)


def get_publications(author):
    publications = {}
    paperAuthor = PaperAuthor.objects.filter(a_id=author)
    for paper in paperAuthor:
        papers = Paper.objects.filter(doi=paper.doi).first()
        publications[paper.doi] = papers.title
    return publications


# @template('authorDetails.html')
def get_single_author(request, author):
    authord = get_object_or_404(Author, pk=author)
    count = PaperAuthor.objects.filter(a_id=author).count()
    return render(request, './simranking/authorDetails.html', context={'author': authord, 'count': count, 'publications': get_publications(author)})


def upload_csv(request):
    messages = ""
    data = {}
    if "GET" == request.method:
        return render(request, 'simranking/csv_upload.html', data)

    try:
        csv_file = request.FILES["csv_file"]
        # cereal_df = pd.read_csv(csv_file)
        # print(cereal_df)
        if not csv_file.name.endswith('.csv'):
            messages.error(request, 'File is not CSV type')
            return HttpResponseRedirect(reverse("simranking:csv"))

        if csv_file.multiple_chunks():
            messages.error(request, "Uploaded file is too big (%.2f MB)." % (csv_file.size / (1000 * 1000),))
            return HttpResponseRedirect(reverse("simranking:csv"))

        # file_data = csv_file.read().decode("utf-8")
        # print(file_data)
        cereal_df = pd.read_csv(csv_file, skipinitialspace=True)
        # df1 = pd.read_csv('input1.csv', sep=',\s+', delimiter=',', encoding="utf-8", skipinitialspace=True)
        print(cereal_df['Author'].str.strip())

        lines = cereal_df
        # print(lines)

        for line in lines:
            fields = line.split(",")
            data_dict = {}
            print(data_dict)
            data_dict['cid'] = fields[0]
            data_dict['venue'] = fields[1]
            #         # data_dict['title'] = fields[2]
            #         # data_dict['author'] = fields[3]
            #         # data_dict['abstract'] = fields[4]
            #         # data_dict['keyphrases'] = fields[5]
            #         # data_dict['crawl_site_state'] = fields[5]
            #         # data_dict['self_cited_state'] = fields[5]
            #         # data_dict['download_state'] = fields[5]
            #         # data_dict['pdf_save_path'] = fields[5]
            #         # data_dict['citation'] = fields[5]
            #
            try:
                form = Paper(data_dict)
                if form.is_valid():
                    form.save()
                else:
                    logging.getLogger("error_logger").error(form.errors.as_json())
            except Exception as e:
                # logging.getLogger("error_loggger").error(repr(e))
                pass
    except Exception as e:
        logging.getLogger("error_logger").error("Unable to upload file. ")
        # messages.error(request, "Unable to upload file. ")
    return HttpResponseRedirect(reverse("simranking:csv"))
    # return render(request, 'simranking/csv_upload.html', RequestContext(request))
