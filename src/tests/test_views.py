import pytest
from django.urls import reverse


def test_root_view(client):
    response = client.get("/status/")
    assert response.status_code == 200
    assert response.json() == {"status": "online"}


@pytest.mark.django_db
class TestDatasetViews:

    def test_dataset_list(self, client):
        response = client.get(reverse("dataset-list"))
        assert response.status_code == 200

    # TODO: Is there a way to add this fixture to the whole class?
    def test_dataset_detail(self, client, dataset_fixture):
        response = client.get(
            reverse("dataset-detail", kwargs={"name": "bomen"}),
        )
        assert response.status_code == 200

    def test_dataset_version(self, client, dataset_fixture):
        response = client.get(
            reverse("dataset-version", kwargs={"name": "bomen", "vmajor": "v1"}),
        )
        assert response.status_code == 200
        assert response.data["version"] == "1.3.5"

    def test_dataset_version_not_found(self, client, dataset_fixture):
        response = client.get(
            reverse("dataset-version", kwargs={"name": "bomen", "vmajor": "v3"}),
        )
        assert response.status_code == 404
        assert (
            response.data["detail"]
            == "Version v3 not found in dataset bomen. Available versions are ['v1']"
        )

    def test_dataset_table(self, client, dataset_fixture):
        response = client.get(
            reverse(
                "dataset-table",
                kwargs={"name": "bomen", "vmajor": "v1", "table_id": "groeiplaatsmedebeheer"},
            ),
        )
        assert response.status_code == 200
        assert response.data["id"] == "groeiplaatsmedebeheer"

    def test_dataset_table_not_found(self, client, dataset_fixture):
        response = client.get(
            reverse(
                "dataset-table",
                kwargs={"name": "bomen", "vmajor": "v1", "table_id": "groeiplaats"},
            ),
        )
        assert response.status_code == 404
        assert response.data["detail"] == "Table 'groeiplaats' not found."


@pytest.mark.django_db
class TestScopeViews:
    def test_scope_listview(self, client):
        response = client.get(reverse("scope-list"))
        assert response.status_code == 200

    def test_scope_detailview(self, client, scope_fixture):
        response = client.get(
            reverse("scope-detail", kwargs={"pk": "fp_mdw"}),
        )
        assert response.status_code == 200


@pytest.mark.django_db
class TestPublisherViews:
    def test_publisher_listview(self, client):
        response = client.get(reverse("publisher-list"))
        assert response.status_code == 200

    def test_publisher_detailview(self, client, publisher_fixture):
        response = client.get(
            reverse("publisher-detail", kwargs={"pk": "benk"}),
        )
        assert response.status_code == 200


@pytest.mark.django_db
class TestProfileViews:
    def test_profile_listview(self, client):
        response = client.get(reverse("profile-list"))
        assert response.status_code == 200

    def test_profile_detailview(self, client, profile_fixture):
        response = client.get(
            reverse("profile-detail", kwargs={"pk": "brkdataportaalgebruiker"}),
        )
        assert response.status_code == 200
