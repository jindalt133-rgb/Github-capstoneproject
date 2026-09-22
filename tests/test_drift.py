import pytest

from doc_sync.drift import detect_drift, has_drift


BASE_REPO = {
    "Application Name": "demo-app",
    "Language/Runtime": "Python 3.11",
    "Frameworks": "fastapi, Flask, django",
    "Deployment Pipeline": "GitHub Actions",
    "GitHub Repository": "https://github.com/example/demo-app",
    "Current Version": "v1.2.3",
    "Service Owner": "Jane Doe",
    "Business Impact": "Medium",
    "Description": "A task management API.",
}

BASE_MANIFEST = {
    "Application Name": "demo-app",
    "Language/Runtime": "Python 3.11",
    "Frameworks": "django, fastapi, Flask",
    "Deployment Pipeline": "GitHub Actions",
    "GitHub Repository": "https://github.com/example/demo-app",
    "Current Version": "1.2.3",
    "Service Owner": "Jane Doe",
    "Business Impact": "Medium",
    "Description": "A task management API.",
}


def test_identical_normalized_values_no_drift():
    result = detect_drift(BASE_REPO, BASE_MANIFEST)

    assert result["has_drift"] is False
    assert result["drifting_fields"] == ()


def test_case_and_whitespace_differences_do_not_create_drift():
    repo = {**BASE_REPO, "Language/Runtime": " python 3.11 "}
    manifest = {**BASE_MANIFEST, "Language/Runtime": "Python 3.11"}

    result = detect_drift(repo, manifest)

    assert result["has_drift"] is False
    assert result["drifting_fields"] == ()


def test_runtime_version_drift_is_detected():
    repo = {**BASE_REPO, "Language/Runtime": " python 3.12 "}
    manifest = {**BASE_MANIFEST, "Language/Runtime": "Python 3.11"}

    result = detect_drift(repo, manifest)

    assert result["has_drift"] is True
    assert result["drifting_fields"] == ("Language/Runtime",)


def test_list_ordering_differences_do_not_create_drift():
    repo = {**BASE_REPO, "Frameworks": "django, fastapi, Flask"}
    manifest = {**BASE_MANIFEST, "Frameworks": "Flask, django, fastapi"}

    result = detect_drift(repo, manifest)

    assert result["has_drift"] is False
    assert result["drifting_fields"] == ()


def test_actual_value_change_detects_drift():
    repo = {**BASE_REPO, "Application Name": "updated-demo-app"}
    manifest = {**BASE_MANIFEST, "Application Name": "demo-app"}

    result = detect_drift(repo, manifest)

    assert result["has_drift"] is True
    assert result["drifting_fields"] == ("Application Name",)


def test_missing_value_and_not_found_match():
    repo = {**BASE_REPO, "GitHub Repository": None}
    manifest = {**BASE_MANIFEST, "GitHub Repository": "Not Found"}

    result = detect_drift(repo, manifest)

    assert result["has_drift"] is False
    assert result["drifting_fields"] == ()


def test_not_found_value_is_treated_as_real_drift():
    repo = {**BASE_REPO, "GitHub Repository": "Not Found"}
    manifest = {**BASE_MANIFEST, "GitHub Repository": "https://github.com/example/demo-app"}

    result = detect_drift(repo, manifest)

    assert result["has_drift"] is True
    assert result["drifting_fields"] == ("GitHub Repository",)

    reverse = detect_drift({**BASE_REPO, "GitHub Repository": "https://github.com/example/demo-app"}, {**BASE_MANIFEST, "GitHub Repository": "Not Found"})
    assert reverse["has_drift"] is True
    assert reverse["drifting_fields"] == ("GitHub Repository",)


def test_multiple_drifting_fields_are_reported():
    repo = {
        **BASE_REPO,
        "Application Name": "new-app",
        "Deployment Pipeline": "Azure Pipelines",
        "Current Version": "v2.0.0",
    }
    manifest = {
        **BASE_MANIFEST,
        "Application Name": "demo-app",
        "Deployment Pipeline": "GitHub Actions",
        "Current Version": "1.2.3",
    }

    result = detect_drift(repo, manifest)

    assert result["has_drift"] is True
    assert result["drifting_fields"] == ("Application Name", "Deployment Pipeline", "Current Version")


def test_protected_human_fields_are_ignored():
    repo = {**BASE_REPO, "Service Owner": "New Owner", "Description": "Updated summary"}
    manifest = {**BASE_MANIFEST, "Service Owner": "Jane Doe", "Description": "A task management API."}

    result = detect_drift(repo, manifest)

    assert result["has_drift"] is False
    assert result["drifting_fields"] == ()


def test_drift_results_are_deterministic():
    repo = {**BASE_REPO, "Application Name": "changed-app"}
    manifest = {**BASE_MANIFEST, "Application Name": "demo-app"}

    first = detect_drift(repo, manifest)
    second = detect_drift(repo, manifest)

    assert first == second
    assert first["drifting_fields"] == ("Application Name",)
    assert has_drift(repo, manifest) is True


def test_manifest_text_input_is_supported():
    manifest_text = """# Technical App Manifest

- Application Name: demo-app
- Service Owner: Jane Doe
- Business Impact: Medium
- Description: A task management API.
- Language/Runtime:  python 3.11
- Frameworks: django, fastapi, Flask
- Deployment Pipeline: GitHub Actions
- JIRA Board: TEAM-123
- On-Call Rotation: Primary On-Call
- GitHub Repository: https://github.com/example/demo-app
- Current Version: v1.2.3
"""

    result = detect_drift(BASE_REPO, manifest_text)

    assert result["has_drift"] is False
    assert result["drifting_fields"] == ()


@pytest.mark.parametrize("field_name", ["Service Owner", "Business Impact", "Description", "JIRA Board", "On-Call Rotation"])
def test_protected_field_names_are_not_part_of_drift_targets(field_name):
    repo = {field_name: "updated value"}
    manifest = {field_name: "original value"}

    result = detect_drift(repo, manifest)

    assert result["has_drift"] is False
    assert result["drifting_fields"] == ()
