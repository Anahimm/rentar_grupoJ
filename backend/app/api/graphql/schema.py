import strawberry

@strawberry.type
class Query:
    @strawberry.field
    def ping(self) -> str:
        return "GraphQL configurado para agregar las consultas"

# Esto empaqueta todas las consultas para que FastAPI las lea
schema = strawberry.Schema(query=Query)