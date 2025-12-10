import pytest

@pytest.mark.asyncio
async def test_create_team(async_client):
    payload = {
        "team_name": "New Team",
        "team_code": "new_team"
    }

    response = await async_client.post("/teams", json=payload)
    assert response.status_code == 201

    response_json = response.json()
    assert response_json["team_id"] is not None
    assert response_json["team_name"] == "New Team"
    assert response_json["team_code"] == "new_team"
    assert response_json["is_active"] is True

# def test_get_all_teams(test_client, setup_team):
#     response = test_client.get("/teams")
#     assert response.status_code == 200

#     response_json = response.json()
#     assert len(response_json) > 0
#     assert response_json[0].get("team_id") == setup_team.get("team_id")

# def test_get_single_team(test_client, setup_team):
#     response = test_client.get(f"/teams/{setup_team.get("team_id")}")
#     assert response.status_code == 200

#     response_json = response.json()
#     assert response_json.get("team_id") == setup_team.get("team_id")
#     assert response_json.get("team_name") == "TEST TEAM"

# def test_post_team(test_client, clean_teams_table):
#     invalid_json1 = {}
#     invalid_json2 = {"team_name": "INVALID TEAM"}
#     valid_json = {"team_name": "NEW TEAM", "lookup": "newteam"}

#     response1 = test_client.post("/teams", json=invalid_json1)
#     assert response1.status_code == 422 

#     response2 = test_client.post("/teams", json=invalid_json2)
#     assert response2.status_code == 422 

#     response = test_client.post("/teams", json=valid_json)
#     response_json = response.json()
#     assert response.status_code == 201
#     assert response_json.get("team_name") == "NEW TEAM"
#     assert response_json.get("is_active") == True 

# def test_update_team(test_client, setup_team):
#     setup_team_id = setup_team.get("team_id")

#     empty_json = {}
#     invalid_json2 = {"team_id": "00000000-0000-0000-0000-000000000000"}
#     valid_json = {"team_name": "UPDATED", "lookup": "updated"}

#     response1 = test_client.patch(f"/teams/{setup_team_id}", json=empty_json)
#     assert response1.status_code == 404 
#     assert setup_team.get("team_name") == "TEST TEAM"

#     response2 = test_client.patch(f"/teams/{setup_team_id}", json=invalid_json2)
#     assert response2.status_code == 404

#     response3 = test_client.patch(f"/teams/00000000-0000-0000-0000-000000000000", json=valid_json)
#     assert response3.status_code == 404
    
#     response = test_client.patch(f"/teams/{setup_team_id}", json=valid_json)
#     response_json = response.json()
#     assert response.status_code == 200
#     assert response_json.get("team_name") == "UPDATED"
#     assert response_json.get("lookup") == "updated"

# def test_delete_team(test_client, setup_team):
#     response1 = test_client.delete(f"/teams/00000000-0000-0000-0000-000000000000")
#     assert response1.status_code == 404

#     response = test_client.delete(f"/teams/{setup_team.get("team_id")}")
#     response_json = response.json()
#     assert response.status_code == 200
#     assert response_json.get("team_id") == setup_team.get("team_id")
#     assert test_client.get(f"/teams/{setup_team.get("team_id")}").status_code == 404