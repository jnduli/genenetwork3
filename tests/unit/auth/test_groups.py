"""Test functions dealing with group management."""
from uuid import UUID

import pytest

from gn3.auth import db
from gn3.auth.authentication.users import User
from gn3.auth.authorisation.roles import Role
from gn3.auth.authorisation.privileges import Privilege
from gn3.auth.authorisation.groups import (
    Group, GroupRole, create_group, MembershipError, create_group_role)

create_group_failure = {
    "status": "error",
    "message": "Unauthorised: Failed to create group."
}

uuid_fn = lambda : UUID("d32611e3-07fc-4564-b56c-786c6db6de2b")

GROUP = Group(UUID("9988c21d-f02f-4d45-8966-22c968ac2fbf"), "TheTestGroup")
PRIVILEGES = (
    Privilege(
        UUID("7f261757-3211-4f28-a43f-a09b800b164d"), "view-resource"),
    Privilege(
        UUID("2f980855-959b-4339-b80e-25d1ec286e21"), "edit-resource"))

@pytest.mark.unit_test
@pytest.mark.parametrize(
    "user_id,expected", (
    ("ecb52977-3004-469e-9428-2a1856725c7f", Group(
        UUID("d32611e3-07fc-4564-b56c-786c6db6de2b"), "a_test_group")),
    ("21351b66-8aad-475b-84ac-53ce528451e3", create_group_failure),
    ("ae9c6245-0966-41a5-9a5e-20885a96bea7", create_group_failure),
    ("9a0c7ce5-2f40-4e78-979e-bf3527a59579", create_group_failure),
    ("e614247d-84d2-491d-a048-f80b578216cb", create_group_failure)))
def test_create_group(# pylint: disable=[too-many-arguments]
        test_app, auth_testdb_path, mocker, test_users, user_id, expected):# pylint: disable=[unused-argument]
    """
    GIVEN: an authenticated user
    WHEN: the user attempts to create a group
    THEN: verify they are only able to create the group if they have the
          appropriate privileges
    """
    mocker.patch("gn3.auth.authorisation.groups.uuid4", uuid_fn)
    with test_app.app_context() as flask_context:
        flask_context.g.user_id = UUID(user_id)
        with db.connection(auth_testdb_path) as conn:
            assert create_group(conn, "a_test_group", User(
                UUID(user_id), "some@email.address", "a_test_user")) == expected

create_role_failure = {
    "status": "error",
    "message": "Unauthorised: Could not create the group role"
}

@pytest.mark.unit_test
@pytest.mark.parametrize(
    "user_id,expected", (
    ("ecb52977-3004-469e-9428-2a1856725c7f", GroupRole(
        UUID("d32611e3-07fc-4564-b56c-786c6db6de2b"),
        Role(UUID("d32611e3-07fc-4564-b56c-786c6db6de2b"),
             "ResourceEditor", PRIVILEGES))),
    ("21351b66-8aad-475b-84ac-53ce528451e3", create_role_failure),
    ("ae9c6245-0966-41a5-9a5e-20885a96bea7", create_role_failure),
    ("9a0c7ce5-2f40-4e78-979e-bf3527a59579", create_role_failure),
    ("e614247d-84d2-491d-a048-f80b578216cb", create_role_failure)))
def test_create_group_role(mocker, test_users_in_group, test_app, user_id, expected):
    """
    GIVEN: an authenticated user
    WHEN: the user attempts to create a role, attached to a group
    THEN: verify they are only able to create the role if they have the
        appropriate privileges and that the role is attached to the given group
    """
    mocker.patch("gn3.auth.authorisation.groups.uuid4", uuid_fn)
    mocker.patch("gn3.auth.authorisation.roles.uuid4", uuid_fn)
    conn, _group, _users = test_users_in_group
    with test_app.app_context() as flask_context:
        flask_context.g.user_id = UUID(user_id)
        assert create_group_role(
            conn, GROUP, "ResourceEditor", PRIVILEGES) == expected

@pytest.mark.unit_test
def test_create_multiple_groups(mocker, test_app, test_users):
    """
    GIVEN: An authenticated user with appropriate authorisation
    WHEN: The user attempts to create a new group, while being a member of an
      existing group
    THEN: The system should prevent that, and respond with an appropriate error
      message
    """
    mocker.patch("gn3.auth.authorisation.groups.uuid4", uuid_fn)
    user_id = UUID("ecb52977-3004-469e-9428-2a1856725c7f")
    conn, _test_users = test_users
    with test_app.app_context() as flask_context:
        flask_context.g.user_id = user_id
        user = User(user_id, "some@email.address", "a_test_user")
        # First time, successfully creates the group
        assert create_group(conn, "a_test_group", user) == Group(
            UUID("d32611e3-07fc-4564-b56c-786c6db6de2b"), "a_test_group")
        # subsequent attempts should fail
        with pytest.raises(MembershipError):
            create_group(conn, "another_test_group", user)
