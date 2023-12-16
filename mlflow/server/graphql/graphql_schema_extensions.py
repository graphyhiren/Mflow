# This file uses autogenerated_graphql_schema.py as the base and applies manual extensions on top of that.
import graphene
from mlflow.server.graphql.autogenerated_graphql_schema import QueryType, MutationType, MlflowExperiment


class Test(graphene.ObjectType):
    output = graphene.String(description="Echoes the input string")

# DO NOT MERGE THIS - this is to demonstrate the ability to extend an autogenerated type
class ExtendedExperiment(MlflowExperiment):
    output = graphene.String(description="Echoes the input string")
class Query(QueryType):
    test = graphene.Field(Test, input_string=graphene.String(), description="Simple echoing field")

    def resolve_test(self, info, input_string):
        return {"output": input_string}

class Mutation(MutationType):
    pass

schema = graphene.Schema(query=Query, mutation=Mutation)
