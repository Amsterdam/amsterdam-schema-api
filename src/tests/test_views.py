def test_root_view(client):
    response = client.get("/status/")
    assert response.status_code == 200
    assert response.json() == {
        "status": "online"
    }
