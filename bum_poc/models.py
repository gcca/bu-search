from django.contrib.postgres.fields import JSONField
from django.db.models import (
    CASCADE,
    CharField,
    DateTimeField,
    ForeignKey,
    Index,
    JSONField,
    Model,
    TextField,
    URLField,
)


class GithubUser(Model):

    name = CharField(max_length=63)


class GithubRepo(Model):

    full_name = CharField(max_length=255)
    description = TextField(null=True)
    html_url = URLField(max_length=511)
    readme = TextField(null=True)
    github_user = ForeignKey(GithubUser, on_delete=CASCADE)


class GithubLake(Model):

    data = JSONField()


class OSMPlace(Model):

    entry = CharField(max_length=511)
    data = JSONField(default=dict)
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)

    class Meta:
        indexes = [Index(fields=["entry"])]
