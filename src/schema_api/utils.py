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
            table_ref = f"{to_snake_case(table['id'])}/{vmajor}"
            tables_ref.append({"id": table["id"], "$ref": table_ref})
        schema_json["versions"][vmajor]["tables"] = tables_ref

    return schema_json
