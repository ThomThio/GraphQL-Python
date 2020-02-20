import graphene
import django_filters
from graphene_django import DjangoObjectType
from graphene_django.filter import DjangoFilterConnectionField

from .models import Link, Vote


#1  Relay allows you to use django-filter for filtering data. 
# Here, you’ve defined a FilterSet, with the url and description fields.
class LinkFilter(django_filters.FilterSet):
    class Meta:
        model = Link
        fields = ['url', 'description']


#2 The data is exposed in Nodes, so you must create one for the links.
class LinkNode(DjangoObjectType):
    class Meta:
        model = Link
        #3 Each node implements an interface with an unique ID (you’ll see the result of this in a bit).
        interfaces = (graphene.relay.Node, )

class VoteNode(DjangoObjectType):
    class Meta:
        model = Vote
        interfaces = (graphene.relay.Node,)


class RelayQuery(graphene.ObjectType):
    #4 Uses the LinkNode with the relay_link field inside your new query.
    relay_link = graphene.relay.Node.Field(LinkNode)
    #5  Defines the relay_links field as a Connection, which implements the pagination structure.
    relay_links = DjangoFilterConnectionField(LinkNode, filterset_class=LinkFilter)



class RelayCreateLink(graphene.relay.ClientIDMutation):
    link = graphene.Field(LinkNode)

    class Input:
        url = graphene.String()
        description = graphene.String()

    def mutate_and_get_payload(root, info, **input):
        user = info.context.user or None

        link = Link(
            url=input.get('url'),
            description=input.get('description'),
            posted_by=user,
        )
        link.save()

        return RelayCreateLink(link=link)


class RelayMutation(graphene.AbstractType):
    relay_create_link = RelayCreateLink.Field()