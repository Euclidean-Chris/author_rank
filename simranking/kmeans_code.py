from __future__ import print_function
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans, MiniBatchKMeans
from sklearn.metrics import adjusted_rand_score
from sklearn.decomposition import TruncatedSVD
from sklearn.feature_extraction.text import HashingVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import Normalizer
from sklearn import preprocessing  # to normalise existing X
from sklearn import metrics
from sklearn.metrics.pairwise import cosine_similarity
import logging
from optparse import OptionParser
import sys
from time import time
import numpy as np
import json
from pprint import pprint
import re
import pprint
import nltk.classify
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import pandas as pd
# multidimensional scaling
import os  # for os.path.basename
import matplotlib.pyplot as plt
import matplotlib as mpl
from sklearn.manifold import MDS
import itertools
from sklearn.metrics import silhouette_samples, silhouette_score


import matplotlib.cm as cm


print(__doc__)

# Display progress logs on stdout
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(levelname)s %(message)s')

# parse commandline arguments
op = OptionParser()
op.add_option("--lsa",
              dest="n_components", type="int",
              help="Preprocess documents with latent semantic analysis.")
op.add_option("--no-minibatch",
              action="store_false", dest="minibatch", default=True,
              help="Use ordinary k-means algorithm (in batch mode).")
op.add_option("--no-idf",
              action="store_false", dest="use_idf", default=True,
              help="Disable Inverse Document Frequency feature weighting.")
op.add_option("--use-hashing",
              action="store_true", default=False,
              help="Use a hashing feature vectorizer")
op.add_option("--n-features", type=int, default=10000,
              help="Maximum number of features (dimensions)"
                   " to extract from text.")
op.add_option("--verbose",
              action="store_true", dest="verbose", default=False,
              help="Print progress reports inside k-means algorithm.")

print(__doc__)
op.print_help()


def is_interactive():
    return not hasattr(sys.modules['__main__'], '__file__')


# work-around for Jupyter notebook and IPython console
argv = [] if is_interactive() else sys.argv[1:]
(opts, args) = op.parse_args(argv)
if len(args) > 0:
    op.error("this script takes no arguments.")
    sys.exit(1)
# output = re.sub(r'\d+', '', '123hello 456world')
# documents=list()
documents = []
# list(itertools.chain.from_iterable(a))
with open('one_million.json') as f:
    data = json.load(f)
    for d in data:
    	documents.append(re.sub(r'\d+', '', ' '.join(d['title'])))  #remove numbers in title
      # documents.extend(d['title'])  #with numbers
      # documents.append(' '.join(d['Keywords']))

#print(documents)
documents_labels = []
with open('one_million.json') as g:
    data2 = json.load(g)
    for s in data2:
        documents_labels.append(s['Labels'])
# print(documents_labels)

# categories = [
#     'security privacy',
#     'algorithm theory',
#     'computer graphics',
#     'computer vision',
#     'multimedia',
#     'operating systems',
#     'computer education',
#     'human computer interaction',
#     'artificial intelligence',
#     'database',
#     'natural language processing',
#     'intelligent agents',
#     'semantic web',
#     'data mining',
#     'programming languages',
#     'information retrieval',
#     'hardware architecture',
#     'network communication',
#     'software engineering',
#     'blockchain',
# ]
# print(categories)
# print("%d categories" % len(categories))
labels = documents_labels
# print(len(documents_labels))
true_k = 20

print("Extracting features from the training dataset "
      "using a sparse vectorizer")
t0 = time()

vectorizer = TfidfVectorizer(max_features=opts.n_features,
                                 stop_words='english',
                                 use_idf=opts.use_idf)
tfidf_matrix = vectorizer.fit_transform(documents)  # fit the vectorizer to documents

z = vectorizer.fit_transform(documents)
X = preprocessing.normalize(z)

print("done in %fs" % (time() - t0))
print("n_samples: %d, n_features: %d" % X.shape)
print()

# #############################################################################
# Do the actual clustering
km = KMeans(n_clusters=true_k, init='k-means++', max_iter=100, n_init=1,
                verbose=opts.verbose, random_state=3425)


print("Clustering sparse data with %s" % km)
t0 = time()
km.fit(X)
print("done in %0.3fs" % (time() - t0))
print()

##################################################################################################
##################################################################################################
clusters = km.labels_.tolist()


#########################################################################################################################
#########################################################################################################################


print("Homogeneity: %0.3f" % metrics.homogeneity_score(labels, km.labels_))
print("Completeness: %0.3f" % metrics.completeness_score(labels, km.labels_))
print("V-measure: %0.3f" % metrics.v_measure_score(labels, km.labels_))
print("Adjusted Rand-Index: %.3f"
      % metrics.adjusted_rand_score(labels, km.labels_))
print("Silhouette Coefficient: %0.3f"
      % metrics.silhouette_score(X, km.labels_, sample_size=1000))
# print("Homogeneity: %0.3f" % metrics.homogeneity_score(labels, km.labels_))
# print("Completeness: %0.3f" % metrics.completeness_score(labels, km.labels_))
# print("V-measure: %0.3f" % metrics.v_measure_score(labels, km.labels_))
# print("Adjusted Rand-Index: %.3f"
#       % metrics.adjusted_rand_score(labels, km.labels_))
# print("Silhouette Coefficient: %0.3f"
#       % metrics.silhouette_score(X, km.labels_, sample_size=1000))

print()


print("Top terms per cluster:")

order_centroids = km.cluster_centers_.argsort()[:, ::-1]
print("\n")
terms = vectorizer.get_feature_names()
for i in range(true_k):
    print("Cluster %d:" % i, end='')
    print("\n")
    for ind in order_centroids[i, :10]:
        print(' %s' % terms[ind], end='')
print()

print("\n")
print("Prediction")

Y = vectorizer.transform(["Privacy preserving"])
prediction = km.predict(Y)
print(prediction)

Y = vectorizer.transform(["semantic web"])
prediction = km.predict(Y)
print(prediction)

print("\n")
print("More Predictions")
testdocuments = []
with open('test.json') as f:
    testdata = json.load(f)
    for td in testdata:
        testdocuments.extend(td['title'])


for i in range(len(testdocuments)):
    M = vectorizer.transform(testdocuments)
    test_prediction = km.predict(M)
    # print(i)
    print("paper %s : %s "%(i+1, test_prediction[i]))
    # print(test_prediction[i])

################################################################################################################
################################################################################################################