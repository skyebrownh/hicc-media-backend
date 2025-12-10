# def test_get_all_schedule_date_roles(test_client, setup_schedule_date_role):
#     schedule_date_role, schedule_date, date, media_role, media_role2 = setup_schedule_date_role
#     response = test_client.get("/schedule_date_roles")
#     assert response.status_code == 200

#     response_json = response.json()
#     assert len(response_json) > 0
#     assert response_json[0].get("schedule_date_role_id") == schedule_date_role.get("schedule_date_role_id")

# def test_get_single_schedule_date_role(test_client, setup_schedule_date_role):
#     schedule_date_role, schedule_date, date, media_role, media_role2 = setup_schedule_date_role
#     response = test_client.get(f"/schedule_date_roles/{schedule_date_role.get("schedule_date_role_id")}")
#     assert response.status_code == 200

#     response_json = response.json()
#     assert response_json.get("schedule_date_role_id") == schedule_date_role.get("schedule_date_role_id")
#     assert response_json.get("media_role_id") == media_role.get("media_role_id")

# def test_post_schedule_date_roles(test_client, setup_schedule_date_role):
#     schedule_date_role, schedule_date, date, media_role, media_role2 = setup_schedule_date_role
#     invalid_json1 = {}
#     invalid_json2 = {"media_role_id": media_role.get("media_role_id")}
#     valid_json = {
#         "schedule_date_id": schedule_date.get("schedule_date_id"),
#         "media_role_id": media_role.get("media_role_id")
#     }

#     response1 = test_client.post("/schedule_date_roles", json=invalid_json1)
#     assert response1.status_code == 422 

#     response2 = test_client.post("/schedule_date_roles", json=invalid_json2)
#     assert response2.status_code == 422 

#     response = test_client.post("/schedule_date_roles", json=valid_json)
#     response_json = response.json()
#     assert response.status_code == 201
#     assert response_json.get("media_role_id") == media_role.get("media_role_id")
#     assert response_json.get("schedule_date_id") == schedule_date.get("schedule_date_id") 

# def test_update_schedule_date_roles(test_client, setup_schedule_date_role):
#     schedule_date_role, schedule_date, date, media_role, media_role2 = setup_schedule_date_role
#     schedule_date_role_id = schedule_date_role.get("schedule_date_role_id")

#     empty_json = {}
#     invalid_json2 = {"schedule_date_role_id": "00000000-0000-0000-0000-000000000000"}
#     valid_json = {"media_role_id": media_role2.get("media_role_id")}

#     response1 = test_client.patch(f"/schedule_date_roles/{schedule_date_role_id}", json=empty_json)
#     assert response1.status_code == 404 
#     assert schedule_date_role.get("media_role_id") == media_role.get("media_role_id")

#     response2 = test_client.patch(f"/schedule_date_roles/{schedule_date_role_id}", json=invalid_json2)
#     assert response2.status_code == 404

#     response3 = test_client.patch(f"/schedule_date_roles/00000000-0000-0000-0000-000000000000", json=valid_json)
#     assert response3.status_code == 404
    
#     response = test_client.patch(f"/schedule_date_roles/{schedule_date_role_id}", json=valid_json)
#     response_json = response.json()
#     assert response.status_code == 200
#     assert response_json.get("media_role_id") == media_role2.get("media_role_id")

# def test_delete_schedule_date_roles(test_client, setup_schedule_date_role):
#     schedule_date_role, schedule_date, date, media_role, media_role2 = setup_schedule_date_role
#     response1 = test_client.delete(f"/schedule_date_roles/00000000-0000-0000-0000-000000000000")
#     assert response1.status_code == 404

#     response = test_client.delete(f"/schedule_date_roles/{schedule_date_role.get("schedule_date_role_id")}")
#     response_json = response.json()
#     assert response.status_code == 200
#     assert response_json.get("schedule_date_role_id") == schedule_date_role.get("schedule_date_role_id")
#     assert test_client.get(f"/schedule_date_roles/{schedule_date_role.get("schedule_date_role_id")}").status_code == 404