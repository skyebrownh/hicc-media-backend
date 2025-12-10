# def test_get_all_users(test_client, setup_user):
#     response = test_client.get("/users")
#     assert response.status_code == 200

#     response_json = response.json()
#     assert len(response_json) > 0
#     assert response_json[0].get("user_id") == setup_user.get("user_id")

# def test_get_single_user(test_client, setup_user):
#     response = test_client.get(f"/users/{setup_user.get("user_id")}")
#     assert response.status_code == 200

#     response_json = response.json()
#     assert response_json.get("user_id") == setup_user.get("user_id")
#     assert response_json.get("first_name") == "TEST"

# def test_post_user(test_client, clean_users_table):
#     invalid_json1 = {}
#     invalid_json2 = {"first_name": "INVALID USER"}
#     valid_json = {"first_name": "NEW", "last_name": "USER", "phone": "1235557890"}

#     response1 = test_client.post("/users", json=invalid_json1)
#     assert response1.status_code == 422 

#     response2 = test_client.post("/users", json=invalid_json2)
#     assert response2.status_code == 422 

#     response = test_client.post("/users", json=valid_json)
#     response_json = response.json()
#     assert response.status_code == 201
#     assert response_json.get("first_name") == "NEW"
#     assert response_json.get("is_active") == True 

# def test_update_user(test_client, setup_user):
#     setup_user_id = setup_user.get("user_id")

#     empty_json = {}
#     invalid_json2 = {"user_id": "00000000-0000-0000-0000-000000000000"}
#     valid_json = {"first_name": "UPDATED", "phone": "4565551234"}

#     response1 = test_client.patch(f"/users/{setup_user_id}", json=empty_json)
#     assert response1.status_code == 404 
#     assert setup_user.get("first_name") == "TEST"

#     response2 = test_client.patch(f"/users/{setup_user_id}", json=invalid_json2)
#     assert response2.status_code == 404

#     response3 = test_client.patch(f"/users/00000000-0000-0000-0000-000000000000", json=valid_json)
#     assert response3.status_code == 404
    
#     response = test_client.patch(f"/users/{setup_user_id}", json=valid_json)
#     response_json = response.json()
#     assert response.status_code == 200
#     assert response_json.get("first_name") == "UPDATED"
#     assert response_json.get("last_name") == "USER"
#     assert response_json.get("phone") == "4565551234"

# def test_delete_user(test_client, setup_user):
#     response1 = test_client.delete(f"/users/00000000-0000-0000-0000-000000000000")
#     assert response1.status_code == 404

#     response = test_client.delete(f"/users/{setup_user.get("user_id")}")
#     response_json = response.json()
#     assert response.status_code == 200
#     assert response_json.get("user_id") == setup_user.get("user_id")
#     assert test_client.get(f"/users/{setup_user.get("user_id")}").status_code == 404