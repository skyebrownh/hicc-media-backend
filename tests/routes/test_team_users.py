# def test_get_all_team_users(test_client, setup_team_user):
#     team_user, team, user, team2 = setup_team_user
#     response = test_client.get("/team_users")
#     assert response.status_code == 200

#     response_json = response.json()
#     assert len(response_json) > 0
#     assert response_json[0].get("team_user_id") == team_user.get("team_user_id")

# def test_get_single_team_user(test_client, setup_team_user):
#     team_user, team, user, team2 = setup_team_user
#     response = test_client.get(f"/team_users/{team_user.get("team_user_id")}")
#     assert response.status_code == 200

#     response_json = response.json()
#     assert response_json.get("team_user_id") == team_user.get("team_user_id")
#     assert response_json.get("user_id") == user.get("user_id")

# def test_post_team_users(test_client, setup_team_user):
#     team_user, team, user, team2 = setup_team_user
#     invalid_json1 = {}
#     invalid_json2 = {"team_id": team.get("team_id")}
#     valid_json = {"team_id": team2.get("team_id"), "user_id": user.get("user_id")}

#     response1 = test_client.post("/team_users", json=invalid_json1)
#     assert response1.status_code == 422 

#     response2 = test_client.post("/team_users", json=invalid_json2)
#     assert response2.status_code == 422 

#     response = test_client.post("/team_users", json=valid_json)
#     response_json = response.json()
#     assert response.status_code == 201
#     assert response_json.get("team_id") == team2.get("team_id")
#     assert response_json.get("user_id") == user.get("user_id") 

# def test_update_team_users(test_client, setup_team_user):
#     team_user, team, user, team2 = setup_team_user
#     team_user_id = team_user.get("team_user_id")

#     empty_json = {}
#     invalid_json2 = {"team_user_id": "00000000-0000-0000-0000-000000000000"}
#     valid_json = {"team_id": team2.get("team_id")}

#     response1 = test_client.patch(f"/team_users/{team_user_id}", json=empty_json)
#     assert response1.status_code == 404 
#     assert team_user.get("team_id") == team.get("team_id")

#     response2 = test_client.patch(f"/team_users/{team_user_id}", json=invalid_json2)
#     assert response2.status_code == 404

#     response3 = test_client.patch(f"/team_users/00000000-0000-0000-0000-000000000000", json=valid_json)
#     assert response3.status_code == 404
    
#     response = test_client.patch(f"/team_users/{team_user_id}", json=valid_json)
#     response_json = response.json()
#     assert response.status_code == 200
#     assert response_json.get("team_id") == team2.get("team_id")

# def test_delete_team_users(test_client, setup_team_user):
#     team_user, team, user, team2 = setup_team_user
#     response1 = test_client.delete(f"/team_users/00000000-0000-0000-0000-000000000000")
#     assert response1.status_code == 404

#     response = test_client.delete(f"/team_users/{team_user.get("team_user_id")}")
#     response_json = response.json()
#     assert response.status_code == 200
#     assert response_json.get("team_user_id") == team_user.get("team_user_id")
#     assert test_client.get(f"/team_users/{team_user.get("team_user_id")}").status_code == 404