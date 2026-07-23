from acf.workspace.project import Project


def test_project_creation():

    project = Project(
        name="ACF Demo",
        author="Sohaib",
    )

    assert project.name == "ACF Demo"
    assert project.author == "Sohaib"
    assert project.version == "0.1.0"


def test_project_to_dict():

    project = Project(name="Demo")

    data = project.to_dict()

    assert data["name"] == "Demo"


def test_project_from_dict():

    data = {
        "name": "Projet Test",
        "author": "ACF",
    }

    project = Project.from_dict(data)

    assert project.name == "Projet Test"
    assert project.author == "ACF"
