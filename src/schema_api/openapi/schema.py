import json

from drf_spectacular.openapi import AutoSchema as _AutoSchema
from drf_spectacular.utils import OpenApiExample, OpenApiParameter, OpenApiResponse, extend_schema
from schematools.types import DatasetSchema

from schema_api.utils import simplify_json


class AutoSchema(_AutoSchema):
    global_params = [
        OpenApiParameter(
            name="API-Version",
            type=str,
            location=OpenApiParameter.HEADER,
            description="",
            required=True,
            style="simple",
            explode=False,
            examples=[
                OpenApiExample(
                    name="API-Version",
                    value="1.0.0",
                    description="Geeft een specifieke API-versie aan in de context van "
                    "een specifieke aanroep.",
                )
            ],
            response=True,
        )
    ]

    def get_override_parameters(self):
        params = super().get_override_parameters()
        return params + self.global_params


# Dataset example is loaded as type Datasetschema to apply version and table filtering
with open("schema_api/openapi/dataset_example.json") as file:
    dataset_example = json.load(file)
    DATASET_EXAMPLE_SCHEMA = DatasetSchema.from_dict(dataset_example)


list_datasets_schema = extend_schema(
    description="Vraag alle datasets op",
    summary="Alle datasets",
    responses={
        200: OpenApiResponse(
            response={"type": "array", "properties": {}},
            examples=[
                OpenApiExample(
                    DATASET_EXAMPLE_SCHEMA.title,
                    value=simplify_json(DATASET_EXAMPLE_SCHEMA),
                )
            ],
        )
    },
    tags=["Dataset"],
)


retrieve_datasets_schema = extend_schema(
    description="Vraag een specifieke dataset op",
    summary="Opgevraagde dataset",
    responses={
        200: OpenApiResponse(
            response={"type": "object", "properties": {}},
            examples=[
                OpenApiExample(
                    DATASET_EXAMPLE_SCHEMA.title,
                    value=DATASET_EXAMPLE_SCHEMA.json_data(),
                )
            ],
        )
    },
    tags=["Dataset"],
)

retrieve_datasets_schema_v = extend_schema(
    description="Vraag een specifieke versie van een dataset op",
    summary="Opgevraagde dataset versie",
    responses={
        200: OpenApiResponse(
            response={"type": "object", "properties": {}},
            examples=[
                OpenApiExample(
                    DATASET_EXAMPLE_SCHEMA.title,
                    value=DATASET_EXAMPLE_SCHEMA.get_version("v1").json_data(),
                )
            ],
        )
    },
    tags=["Dataset"],
)

retrieve_datasets_schema_v_t = extend_schema(
    description="Vraag een tabel van een specifieke versie van een dataset op",
    summary="Opgevraagde tabel",
    responses={
        200: OpenApiResponse(
            response={"type": "object", "properties": {}},
            examples=[
                OpenApiExample(
                    "mraLiander",
                    value=DATASET_EXAMPLE_SCHEMA.get_version("v1")
                    .get_table_by_id("mraLiander")
                    .json_data(),
                )
            ],
        )
    },
    tags=["Dataset"],
)

# Load example Scope json response
with open("schema_api/openapi/scope_example.json") as file:
    scope_example = json.load(file)


list_scope_schema = extend_schema(
    description="Vraag alle scopes op",
    summary="Alle scopes",
    responses={
        200: OpenApiResponse(
            response={"type": "array", "properties": {}},
            examples=[
                OpenApiExample(scope_example["id"], value=scope_example),
            ],
        )
    },
    tags=["Scope"],
)

retrieve_scope_schema = extend_schema(
    description="Vraag een specifieke dataset op",
    summary="Scope",
    responses={
        200: OpenApiResponse(
            response={"type": "object", "properties": {}},
            examples=[
                OpenApiExample(scope_example["id"], value=scope_example),
            ],
        )
    },
    tags=["Scope"],
)

# Load example Publisher json response
with open("schema_api/openapi/publisher_example.json") as file:
    publisher_example = json.load(file)

list_publisher_schema = extend_schema(
    description="Vraag alle publishers op",
    summary="Alle publishers",
    responses={
        200: OpenApiResponse(
            response={"type": "array", "properties": {}},
            examples=[
                OpenApiExample(publisher_example["id"], value=publisher_example),
            ],
        )
    },
    tags=["Publisher"],
)


retrieve_publisher_schema = extend_schema(
    description="Vraag een publisher op",
    summary="Publisher",
    responses={
        200: OpenApiResponse(
            response={"type": "object", "properties": {}},
            examples=[
                OpenApiExample(publisher_example["id"], value=publisher_example),
            ],
        )
    },
    tags=["Publisher"],
)

# Load example Profile json response
with open("schema_api/openapi/profile_example.json") as file:
    profile_example = json.load(file)

list_profile_schema = extend_schema(
    description="Vraag alle profielen op",
    summary="Alle profielen",
    responses={
        200: OpenApiResponse(
            response={"type": "array", "properties": {}},
            examples=[
                OpenApiExample(profile_example["id"], value=profile_example),
            ],
        )
    },
    tags=["Profiel"],
)

retrieve_profile_schema = extend_schema(
    description="Vraag een profiel op",
    summary="Profiel",
    responses={
        200: OpenApiResponse(
            response={"type": "object", "properties": {}},
            examples=[
                OpenApiExample(profile_example["id"], value=profile_example),
            ],
        )
    },
    tags=["Profiel"],
)
