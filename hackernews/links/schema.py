import graphene
from graphene_django import DjangoObjectType
from users.schema import UserType

from .models import Link, Vote
from django.db.models import Q



class LinkType(DjangoObjectType):
    class Meta:
        model = Link

class VoteType(DjangoObjectType):
    class Meta:
        model = Vote


#Filter demonstration
# class Query(graphene.ObjectType):
#     links = graphene.List(LinkType, search=graphene.String())
#     votes = graphene.List(VoteType)

#     # Change the resolver
#     def resolve_links(self, info, search=None, **kwargs):
#         # The value sent with the search parameter will be in the args variable
#         if search:
#             filter = (
#                 Q(url__icontains=search) |
#                 Q(description__icontains=search)
#             )
#             return Link.objects.filter(filter)

#         return Link.objects.all()

#     def resolve_votes(self, info, **kwargs):
#         return Vote.objects.all()

#Pagination Demonstration
class Query(graphene.ObjectType):
    # Add the first and skip parameters
    links = graphene.List(
        LinkType,
        search=graphene.String(),
        first=graphene.Int(),
        skip=graphene.Int(),
    )
    votes = graphene.List(VoteType)

    # Use them to slice the Django queryset
    def resolve_links(self, info, search=None, first=None, skip=None, **kwargs):
        qs = Link.objects.all()

        if search:
            filter = (
                Q(url__icontains=search) |
                Q(description__icontains=search)
            )
            qs = qs.filter(filter)

        if skip:
            qs = qs[skip:]

        if first:
            qs = qs[:first]

        return qs

    def resolve_votes(self, info, **kwargs):
        return Vote.objects.all()



#1 Defines a mutation class, and outputs of mutation i.e. what the server sends back to client
class CreateLink(graphene.Mutation):
    id = graphene.Int()
    url = graphene.String()
    description = graphene.String()
    posted_by = graphene.Field(UserType)

    #2 Defines data sending to server. Links' url and description
    class Arguments:
        url = graphene.String()
        description = graphene.String()

    #3 Creates link in database using data sent by user, through url and description parameters
    def mutate(self, info, url, description):
        user = info.context.user or None

        link = Link(
            url=url,
            description=description,
            posted_by=user,
        )
        link.save()

        return CreateLink(
            id=link.id,
            url=link.url,
            description=link.description,
            posted_by=link.posted_by,
        )


class CreateVote(graphene.Mutation):
    user = graphene.Field(UserType)
    link = graphene.Field(LinkType)

    class Arguments:
        link_id = graphene.Int()

    def mutate(self, info, link_id):
        user = info.context.user
        if user.is_anonymous:
           #1
           raise GraphQLError('GraphQL: You must be logged to vote!')


        if user.is_anonymous:
            raise Exception('You must be logged to vote!')

        link = Link.objects.filter(id=link_id).first()
        if not link:
            raise Exception('Invalid Link!')

        Vote.objects.create(
            user=user,
            link=link,
        )

        return CreateVote(user=user, link=link)





#4 Creates mutation class with a field to be resolved, which points to mutation defined before
class Mutation(graphene.ObjectType):
    create_link = CreateLink.Field()
    create_vote = CreateVote.Field()