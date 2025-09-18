from schematools.naming import to_snake_case
from schematools.types import DatasetSchema


def simplify_json(schema: DatasetSchema):
    """Constructs reference to replace inlined table"""

    # Schema data to dict
    schema_json = schema.json_data()

    for vmajor, vdata in schema_json["versions"].items():
        tables_ref = []
        for table in vdata["tables"]:

            # Construct reference to replace inlined table
            table_ref = f"{to_snake_case(table["id"])}/{vmajor}"
            tables_ref.append({"id": table["id"], "$ref": table_ref})
        schema_json["versions"][vmajor]["tables"] = tables_ref

    return schema_json


def filter_on_scope(schema: DatasetSchema, scope: str):
    schema_data = schema.json_data()
    scoped_tables = []

    for table in schema_data["tables"]:
        scoped_fields = {}
        for field, data in table["schema"]["properties"].items():

            # Only keep fields when there is no auth, or scope has valid auth
            auth = data.get("auth")
            if not auth or scope == auth:
                scoped_fields[field] = data

        # Replace original fields in table with scope filtered fields
        table["schema"]["properties"] = scoped_fields
        scoped_tables.append(table)

    schema_data["tables"] = scoped_tables
    return schema_data
