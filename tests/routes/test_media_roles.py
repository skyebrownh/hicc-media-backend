# def test_get_all_media_roles(test_client, setup_media_role):
#     response = test_client.get("/media_roles")
#     assert response.status_code == 200

#     response_json = response.json()
#     assert len(response_json) > 0
#     assert response_json[0].get("media_role_id") == setup_media_role.get("media_role_id")

# def test_get_single_media_role(test_client, setup_media_role):
#     response = test_client.get(f"/media_roles/{setup_media_role.get("media_role_id")}")
#     assert response.status_code == 200

#     response_json = response.json()
#     assert response_json.get("media_role_id") == setup_media_role.get("media_role_id")
#     assert response_json.get("media_role_name") == "TEST MEDIA ROLE"

# def test_post_media_role(test_client, clean_media_roles_table):
#     invalid_json1 = {}
#     invalid_json2 = {"media_role_name": "INVALID MEDIA ROLE"}
#     valid_json = {"media_role_name": "NEW MEDIA ROLE", "sort": 10, "lookup": "newmediarole"}

#     response1 = test_client.post("/media_roles", json=invalid_json1)
#     assert response1.status_code == 422 

#     response2 = test_client.post("/media_roles", json=invalid_json2)
#     assert response2.status_code == 422 

#     response = test_client.post("/media_roles", json=valid_json)
#     response_json = response.json()
#     assert response.status_code == 201
#     assert response_json.get("media_role_name") == "NEW MEDIA ROLE"
#     assert response_json.get("is_active") == True 

# def test_update_media_role(test_client, setup_media_role):
#     setup_media_role_id = setup_media_role.get("media_role_id")

#     empty_json = {}
#     invalid_json2 = {"media_role_id": "00000000-0000-0000-0000-000000000000"}
#     valid_json = {"media_role_name": "UPDATED", "lookup": "updated"}

#     response1 = test_client.patch(f"/media_roles/{setup_media_role_id}", json=empty_json)
#     assert response1.status_code == 404 
#     assert setup_media_role.get("media_role_name") == "TEST MEDIA ROLE"

#     response2 = test_client.patch(f"/media_roles/{setup_media_role_id}", json=invalid_json2)
#     assert response2.status_code == 404

#     response3 = test_client.patch(f"/media_roles/00000000-0000-0000-0000-000000000000", json=valid_json)
#     assert response3.status_code == 404
    
#     response = test_client.patch(f"/media_roles/{setup_media_role_id}", json=valid_json)
#     response_json = response.json()
#     assert response.status_code == 200
#     assert response_json.get("media_role_name") == "UPDATED"
#     assert response_json.get("lookup") == "updated"

# def test_delete_media_role(test_client, setup_media_role):
#     response1 = test_client.delete(f"/media_roles/00000000-0000-0000-0000-000000000000")
#     assert response1.status_code == 404

#     response = test_client.delete(f"/media_roles/{setup_media_role.get("media_role_id")}")
#     response_json = response.json()
#     assert response.status_code == 200
#     assert response_json.get("media_role_id") == setup_media_role.get("media_role_id")
#     assert test_client.get(f"/media_roles/{setup_media_role.get("media_role_id")}").status_code == 404