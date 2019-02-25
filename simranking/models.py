from django.db import models


# Create your models here.


class Paper(models.Model):
    doi = models.CharField(max_length=100, primary_key=True)
    cid = models.CharField(max_length=100, unique=True, default='')
    keywords = models.TextField(default='', null=True)
    venue = models.CharField(max_length=512, default='', null=True)
    title = models.TextField(default='', null=True)
    author = models.TextField(null=True)
    abstract = models.TextField(null=True)
    keyphrases = models.TextField(null=True)
    crawl_cite_state = models.CharField(max_length=2, default=0, null=True)
    crawl_cited_state = models.CharField(max_length=2, default=0, null=True)
    self_cite_num = models.CharField(max_length=10, null=True)
    cited_num = models.CharField(max_length=10, null=True)
    download_state = models.CharField(max_length=2, default=0, null=True)
    pdf_save_path = models.TextField(default='', null=True)
    paper_field = models.TextField(default='', null=True)

    class Meta:
        db_table = 'papers'
        unique_together = ('doi', 'cid')

    def __str__(self):
        return self.title


class Cite(models.Model):
    doi = models.ForeignKey(Paper, primary_key=True, to_field='doi', max_length=80, related_name='+',
                            on_delete=models.CASCADE)
    cid = models.ForeignKey(Paper, to_field='cid', max_length=80, related_name='+', on_delete=models.CASCADE)

    class Meta:
        db_table = 'cite'


class PaperRank(Paper):
    class Meta:
        proxy = True
        verbose_name = 'Simulation'
        verbose_name_plural = 'Simulations'


class Author(models.Model):
    a_id = models.CharField(max_length=100, primary_key=True)
    author_name = models.CharField(max_length=2000, default='', null=True)
    affiliation = models.CharField(max_length=2000, default='', null=True)
    publication = models.CharField(max_length=100, default='', null=True)
    h_index = models.CharField(max_length=1000, default='', null=True)
    keywords = models.CharField(max_length=2000, default='', null=True)

    class Meta:
        db_table = 'authors'

    def __str__(self):
        return self.author_name


class PaperAuthor(models.Model):
    doi = models.CharField(max_length=80, primary_key=True)
    a_id = models.CharField(max_length=80)
    collaboration_level = models.CharField(max_length=80)

    # author = models.ForeignKey(Author, to_field='a_id', max_length=80, related_name='+', on_delete=models.CASCADE)
    # paper = models.ForeignKey(Paper, to_field='doi', max_length=80, related_name='+', on_delete=models.CASCADE)

    class Meta:
        db_table = 'paper_author'


class AuthorStatus(Author):
    class Meta:
        proxy = True
        verbose_name = 'Malicious Author Detection'
        verbose_name_plural = 'Malicious Authors Detection'


class AuthorStatusList(Author):
    class Meta:
        proxy = True
        verbose_name = 'Malicious Author Detection List View'
        verbose_name_plural = 'Malicious Authors Detection List View'