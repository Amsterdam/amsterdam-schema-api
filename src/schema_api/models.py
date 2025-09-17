from schematools.contrib.django.models import (
    Dataset,
    DatasetTable,
    DatasetVersion,
)


class Dataset(Dataset):

    class Meta:
        proxy = True
        db_table = "datasets_dataset"


class DatasetVersion(DatasetVersion):

    class Meta:
        proxy = True
        db_table = "datasets_datasetversion"


class DatasetTable(DatasetTable):

    class Meta:
        proxy = True
        db_table = "datasets_datasettable"
