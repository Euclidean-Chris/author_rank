import math
import re
import numpy
from collections import Counter

# Libraries for calculating NGD
import requests
from bs4 import BeautifulSoup
from django.contrib import admin

from .models import Author
from .models import AuthorStatus, AuthorStatusList, PaperAuthor
from .models import Paper
from .models import PaperRank


# Register your models here.


class PaperAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'abstract', 'keyphrases', 'cited_num')
    search_fields = ('title', 'author', 'abstract', 'keyphrases')
    list_per_page = 50


class AuthorAdmin(admin.ModelAdmin):
    list_display = ('a_id', 'author_name', 'affiliation', 'publication', 'h_index')
    search_fields = ('a_id', 'author_name', 'affiliation', 'publication')
    list_per_page = 20


@admin.register(AuthorStatus)
class MaliciousAuthorAdmin(admin.ModelAdmin):
    change_list_template = 'admin/malicious_author.html'

    @staticmethod
    def paperScore(author_id):
        field_score = {}
        paper_author = PaperAuthor.objects.filter(a_id=author_id)
        for paper in paper_author:
            paper_fields = Paper.objects.filter(doi=paper.doi).first()
            field_score.setdefault(paper_fields.paper_field, []).append(1 / int(paper.collaboration_level))
        return field_score

    @staticmethod
    def authors():
        authors = Author.objects.only('a_id', 'author_name')
        return authors

    @staticmethod
    def authors_name():
        authors = Author.objects.only('author_name')
        return authors

    @staticmethod
    def paperField():
        paper_field_filter = []
        paper_fields = Paper.objects.order_by('paper_field').values('paper_field').distinct()
        for paper_field in paper_fields:
            paper_field_filter.append(paper_field['paper_field'])
        return ' '.join(paper_field_filter).split()

    def calculateFieldScore(self):
        field_score = {}
        for author in self.authors():
            for index, scores in self.paperScore(author.a_id).items():
                field_score.setdefault(author.author_name, []).append({index: numpy.mean(scores).round(decimals=4)})
        return field_score

    @staticmethod
    def flattenFieldScore(fields):
        field_score = {}
        new_field_score = []
        for score in fields:
            field_score.update(score)
        for key, new_score in field_score.items():
            new_field_score.append(new_score)
        return new_field_score

    def maliciousAuthor(self):
        a = 0.3 #mean 1
        b = 0.5 #mean 2
        c = 0.2 #std
        d = 5 #number of fields
        author_score = {}
        print("getting something here")
        print(self.calculateFieldScore())
        for author, fields in self.calculateFieldScore().items():
            mean = numpy.mean(self.flattenFieldScore(fields)).round(decimals=4)
            std = numpy.std(self.flattenFieldScore(fields)).round(decimals=4)
            if mean < a and len(self.flattenFieldScore(fields)) > d:
                remarks = "Malicious"
            elif a < mean < b and std > c and len(self.flattenFieldScore(fields))>d:
                remarks = "Malicious 2"
            else:
                remarks = "Good Standing"
            author_score.setdefault(author, []).append(
                {'mean': numpy.mean(self.flattenFieldScore(fields)).round(decimals=4),
                 'std': numpy.std(self.flattenFieldScore(fields)).round(decimals=4),
                 'remark': remarks, 'numberField': len(fields)})
        return author_score

    def changelist_view(self, request, extra_context=None):
        response = super(MaliciousAuthorAdmin, self).changelist_view(request, extra_context=extra_context)
        response.context_data['author_score'] = self.maliciousAuthor()
        response.context_data['authors'] = self.calculateFieldScore()
        response.context_data['paper_field'] = self.paperField()
        response.context_data['author_name'] = self.authors_name()

        return response


@admin.register(AuthorStatusList)
class MaliciousAuthorListAdmin(admin.ModelAdmin):
    change_list_template = 'admin/malicious_author_list.html'

    @staticmethod
    def paperScore(author_id):
        field_score = {}
        paper_author = PaperAuthor.objects.filter(a_id=author_id)
        for paper in paper_author:
            paper_fields = Paper.objects.filter(doi=paper.doi).first()
            field_score.setdefault(paper_fields.paper_field, []).append(1 / int(paper.collaboration_level))
        return field_score

    @staticmethod
    def authors():
        authors = Author.objects.only('a_id', 'author_name')
        return authors

    @staticmethod
    def authors_name():
        authors = Author.objects.only('author_name')
        return authors

    @staticmethod
    def paperField():
        paper_field_filter = []
        paper_fields = Paper.objects.order_by('paper_field').values('paper_field').distinct()
        for paper_field in paper_fields:
            paper_field_filter.append(paper_field['paper_field'])
        return ' '.join(paper_field_filter).split()

    def calculateFieldScore(self):
        field_score = {}
        for author in self.authors():
            for index, scores in self.paperScore(author.a_id).items():
                field_score.setdefault(author.author_name, []).append({index: numpy.mean(scores).round(decimals=4)})
        return field_score

    @staticmethod
    def flattenFieldScore(fields):
        field_score = {}
        new_field_score = []
        for score in fields:
            field_score.update(score)
        for key, new_score in field_score.items():
            new_field_score.append(new_score)
        return new_field_score

    def maliciousAuthor(self):
        a = 0.3 #mean 1
        b = 0.5 #mean 2
        c = 0.2 #std
        d = 5 #number of fields
        author_score = {}
        for author, fields in self.calculateFieldScore().items():
            mean = numpy.mean(self.flattenFieldScore(fields)).round(decimals=4)
            std = numpy.std(self.flattenFieldScore(fields)).round(decimals=4)
            if mean < a and len(self.flattenFieldScore(fields)) > d:
                remarks = "Malicious"
            elif a < mean < b and std > c and len(self.flattenFieldScore(fields))>d:
                remarks = "Malicious 2"
            else:
                remarks = "Good Standing"
            author_score.setdefault(author, []).append(
                {'num':len(fields), 'mean': numpy.mean(self.flattenFieldScore(fields)).round(decimals=4),
                 'std': numpy.std(self.flattenFieldScore(fields)).round(decimals=4),
                 'remark': remarks, 'numberField': len(fields)})
        return author_score

    def changelist_view(self, request, extra_context=None):
        response = super(MaliciousAuthorListAdmin, self).changelist_view(request, extra_context=extra_context)
        response.context_data['author_score'] = self.maliciousAuthor()
        response.context_data['author_name'] = self.authors_name()
        return response


@admin.register(PaperRank)
class PaperRankingAdmin(admin.ModelAdmin):
    change_list_template = 'admin/paper_title_simulation.html'
    WORD = re.compile(r'\w+')

    # FETCH AND PREP DATA
    def get_hits(self, term):
        term = {'q': term, 'tbs': 'li:1'}
        google_result = requests.get('http://citeseerx.ist.psu.edu/search', params=term)

        soup = BeautifulSoup(google_result.text, 'html.parser')
        result = soup.find('div', {'id': 'result_info'}).text

        return int("".join(_ for _ in result if _ in ".1234567890"))

    # DISTANCE MEASURE
    def normalized_google_distance(self, nr_results_x, nr_results_y, nr_results_x_y, index_size=1120000000):
        c_x = math.log(nr_results_x)
        c_y = math.log(nr_results_y)
        c_x_y = math.log(nr_results_x_y)
        c_m = math.log(index_size)
        return (max(c_x, c_y) - c_x_y) / (c_m - min(c_x, c_y))

    # COSINE SIMILARITY
    def get_cosine(self, vec1, vec2):
        intersection = set(vec1.keys()) & set(vec2.keys())
        numerator = sum([vec1[x] * vec2[x] for x in intersection])

        sum1 = sum([vec1[x] ** 2 for x in vec1.keys()])
        sum2 = sum([vec2[x] ** 2 for x in vec2.keys()])
        denominator = math.sqrt(sum1) * math.sqrt(sum2)

        if not denominator:
            return 0.0
        else:
            return float(numerator) / denominator

    def text_to_vector(self, text):
        words = self.WORD.findall(text)
        return Counter(words)

    def changelist_view(self, request, extra_context=None):
        response = super(PaperRankingAdmin, self).changelist_view(request, extra_context=extra_context)
        try:
            qs = response.context_data['cl'].queryset
        except (AttributeError, KeyError):
            return response

        response.context_data['papers'] = list(
            qs.order_by('?').values_list('title', flat=True)[:20]
        )

        paper_list = response.context_data['papers']
        print(paper_list)

        hits = []

        for paper_title in paper_list:
            paper_titles = []
            title1 = self.text_to_vector(paper_title)
            for paper_title2 in paper_list:
                title2 = self.text_to_vector(paper_title2)
                cosine = self.get_cosine(title1, title2)
                paper_titles.append(round(cosine, 2))
            hits.append(paper_titles)

        # print(paper_list)
        # print(hits)
        # print(zip_longest(paper_list,hits))

        response.context_data['hits'] = hits
        response.context_data['paper_titles'] = zip(paper_list, hits)

        # hits = {}
        # index1 = 0
        # index2 = 0
        #
        # for paper_side in paper_lists:
        #     hits[paper_side] = []
        #     index1 = index1 + 1
        #
        #     for paper_head in paper_list:
        #         index2 = index2 + 1
        #
        #         hits[paper_side] = self.normalized_google_distance(self.get_hits(paper_lists[index1-1]),
        #                                         self.get_hits(paper_list[index2-1]),
        #                                         self.get_hits(paper_side + '+' + paper_head))
        #
        #         # hits.update(hits[paper_side])
        #
        #     index2 = 0
        #     hits.update(hits[paper_side])
        # response.context_data['hits'] = hits
        # print(hits)
        return response


admin.site.register(Paper, PaperAdmin)
admin.site.register(Author, AuthorAdmin)
