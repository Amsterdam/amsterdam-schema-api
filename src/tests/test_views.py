import pytest
from django.urls import reverse

from schema_api.models import ChangelogItem


def test_root_view(client):
    response = client.get("/status/")
    assert response.status_code == 200
    assert response.json() == {"status": "online"}


@pytest.mark.django_db
class TestDatasetViews:

    def test_dataset_list(self, client):
        response = client.get(reverse("dataset-list"))
        assert response.status_code == 200

    def test_dataset_detail(self, client, dataset_fixture):
        response = client.get(
            reverse("dataset-detail", kwargs={"name": "bomen"}),
        )
        assert response.status_code == 200
        assert response.data["id"] == "bomen"

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
            == "Version v3 not found in dataset bomen. Available versions are ['v1', 'v2']"
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

    def test_dataset_scope_access(self, client, dataset_fixture, scope_fixture):
        response = client.get(
            reverse(
                "dataset-detail",
                kwargs={
                    "name": "bomen",
                },
                query={
                    "scopes": "fp_mdw",
                },
            ),
        )
        assert response.status_code == 200
        assert response.data["versions"]["v1"]["tables"][0]["schema"]["properties"]

    def test_dataset_scope_no_access(self, client, dataset_fixture, scope_fixture):
        response = client.get(
            reverse(
                "dataset-detail",
                kwargs={
                    "name": "bomen",
                },
                query={
                    "scopes": "openbaar",
                },
            ),
        )
        assert response.status_code == 200
        assert response.data["versions"]["v1"]["tables"][0]["schema"]["properties"] == {}

    def test_dataset_multiple_scope_access(self, client, dataset_fixture, scope_fixture):
        response = client.get(
            reverse(
                "dataset-detail",
                kwargs={
                    "name": "bomen",
                },
                query={
                    "scopes": ["openbaar", "fp_mdw"],
                },
            ),
        )
        assert response.status_code == 200
        assert response.data["versions"]["v1"]["tables"][0]["schema"]["properties"]

    def test_dataset_scope_version_access(self, client, dataset_fixture, scope_fixture):
        response = client.get(
            reverse(
                "dataset-version",
                kwargs={
                    "name": "bomen",
                    "vmajor": "v1",
                },
                query={
                    "scopes": "fp_mdw",
                },
            ),
        )
        assert response.status_code == 200
        assert response.data["tables"][0]["schema"]["properties"]

    def test_dataset_scope_version_no_access(self, client, dataset_fixture, scope_fixture):
        response = client.get(
            reverse(
                "dataset-version",
                kwargs={
                    "name": "bomen",
                    "vmajor": "v1",
                },
                query={
                    "scopes": "openbaar",
                },
            ),
        )
        assert response.status_code == 200
        assert response.data["tables"][0]["schema"]["properties"] == {}

    def test_dataset_scope_table_access(self, client, dataset_fixture, scope_fixture):
        response = client.get(
            reverse(
                "dataset-table",
                kwargs={
                    "name": "bomen",
                    "vmajor": "v1",
                    "table_id": "groeiplaatsmedebeheer",
                },
                query={
                    "scopes": "fp_mdw",
                },
            ),
        )
        assert response.status_code == 200
        assert response.data["schema"]["properties"]

    def test_dataset_scope_table_no_access(self, client, dataset_fixture, scope_fixture):
        response = client.get(
            reverse(
                "dataset-table",
                kwargs={
                    "name": "bomen",
                    "vmajor": "v1",
                    "table_id": "groeiplaatsmedebeheer",
                },
                query={
                    "scopes": "openbaar",
                },
            ),
        )
        assert response.status_code == 200
        assert response.data["schema"]["properties"] == {}

    def test_dataset_scope_table_field_access(self, client, dataset_fixture, scope_fixture):
        response = client.get(
            reverse(
                "dataset-table",
                kwargs={
                    "name": "bomen",
                    "vmajor": "v2",
                    "table_id": "groeiplaatsmedebeheer",
                },
                query={
                    "scopes": "fp_mdw",
                },
            ),
        )
        assert response.status_code == 200
        assert "guid" in response.data["schema"]["properties"]

    def test_dataset_scope_table_field_no_access(self, client, dataset_fixture, scope_fixture):
        response = client.get(
            reverse(
                "dataset-table",
                kwargs={
                    "name": "bomen",
                    "vmajor": "v2",
                    "table_id": "groeiplaatsmedebeheer",
                },
                query={
                    "scopes": "openbaar",
                },
            ),
        )
        assert response.status_code == 200
        assert "guid" not in response.data["schema"]["properties"]


@pytest.mark.django_db
class TestScopeViews:
    def test_scope_listview(self, client, scope_fixture):
        response = client.get(reverse("scope-list"))
        assert response.status_code == 200
        assert response.data["count"] == 2

    def test_scope_detailview(self, client, scope_fixture):
        response = client.get(
            reverse("scope-detail", kwargs={"pk": "fp_mdw"}),
        )
        assert response.status_code == 200
        assert response.data["id"] == "FP/MDW"


@pytest.mark.django_db
class TestPublisherViews:
    def test_publisher_listview(self, client, publisher_fixture):
        response = client.get(reverse("publisher-list"))
        assert response.status_code == 200
        assert response.data["count"] == 1

    def test_publisher_detailview(self, client, publisher_fixture):
        response = client.get(
            reverse("publisher-detail", kwargs={"pk": "benk"}),
        )
        assert response.status_code == 200
        assert response.data["id"] == "BENK"


@pytest.mark.django_db
class TestProfileViews:
    def test_profile_listview(self, client, profile_fixture):
        response = client.get(reverse("profile-list"))
        assert response.status_code == 200
        assert response.data["count"] == 1

    def test_profile_detailview(self, client, profile_fixture):
        response = client.get(
            reverse("profile-detail", kwargs={"pk": "brkdataportaalgebruiker"}),
        )
        assert response.status_code == 200
        assert response.data["id"] == "brkdataportaalgebruiker"


@pytest.mark.django_db
class TestChangelogViews:
    def test_changelog_listview(self, client):
        item = {
            "id": 1,
            "dataset_id": "hrKvk",
            "status": "stable",
            "object_id": "hrKvk/v1/functievervullingen",
            "label": "update",
            "commit_hash": "COMMIT_HASH",
            "committed_at": "2025-11-04T14:36:05+01:00",
        }
        ChangelogItem.objects.create(**item)
        response = client.get(reverse("changelog-list"))
        assert response.status_code == 200
        assert response.data["count"] == 1
        response = response.data["results"][0]
        assert response["object_id"] == "hrKvk/v1/functievervullingen"
