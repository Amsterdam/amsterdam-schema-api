import pytest
from django.urls import reverse


def test_root_view(client):
    response = client.get("/status/")
    assert response.status_code == 200
    assert response.json() == {"status": "online"}


@pytest.mark.django_db
def test_dataset_listview(client):
    response = client.get(reverse("dataset-list"))
    assert response.status_code == 200


@pytest.mark.django_db
def test_dataset_detailview(client):
    response = client.get(
        reverse("dataset-detail"),
        kwargs={"name": "bomen"},
    )
    assert response.status_code == 200
