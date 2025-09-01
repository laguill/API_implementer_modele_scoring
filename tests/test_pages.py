from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_list_dashboards_html_empty():
    from app.api.pages import pages

    pages.clear()
    response = client.get("/pages/index")
    assert response.status_code == 200  # noqa: PLR2004, S101
    assert "<ul>" in response.text  # noqa: S101
    assert "</ul>" in response.text  # noqa: S101
    assert "<li>" not in response.text  # Pas d'éléments  # noqa: S101


def test_list_dashboards_html_with_items():
    from app.api.pages import pages

    pages.extend(["dashboard1", "dashboard2"])
    response = client.get("/pages/index")
    assert response.status_code == 200  # noqa: PLR2004, S101
    assert "<li><a href='/pages/dashboard1'>dashboard1</a></li>" in response.text  # noqa: S101
    assert "<li><a href='/pages/dashboard2'>dashboard2</a></li>" in response.text  # noqa: S101
