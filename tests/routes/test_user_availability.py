# def test_get_all_user_availability(test_client, setup_user_availability):
#     ua, user, date, date2 = setup_user_availability
#     response = test_client.get("/user_availability")
#     assert response.status_code == 200

#     response_json = response.json()
#     assert len(response_json) > 0
#     assert response_json[0].get("user_availability_id") == ua.get("user_availability_id")

# def test_get_single_user_availability(test_client, setup_user_availability):
#     ua, user, date, date2 = setup_user_availability
#     response = test_client.get(f"/user_availability/{ua.get("user_availability_id")}")
#     assert response.status_code == 200

#     response_json = response.json()
#     assert response_json.get("user_availability_id") == ua.get("user_availability_id")
#     assert response_json.get("user_id") == user.get("user_id")

# def test_post_user_availability(test_client, setup_user_availability):
#     ua, user, date, date2 = setup_user_availability
#     invalid_json1 = {}
#     invalid_json2 = {"date": "2000-01-01"}
#     valid_json = {"date": "2000-01-01", "user_id": user.get("user_id")}

#     response1 = test_client.post("/user_availability", json=invalid_json1)
#     assert response1.status_code == 422 

#     response2 = test_client.post("/user_availability", json=invalid_json2)
#     assert response2.status_code == 422 

#     response = test_client.post("/user_availability", json=valid_json)
#     response_json = response.json()
#     assert response.status_code == 201
#     assert response_json.get("date") == "2000-01-01"
#     assert response_json.get("user_id") == user.get("user_id") 

# def test_update_user_availability(test_client, setup_user_availability):
#     ua, user, date, date2 = setup_user_availability
#     ua_id = ua.get("user_availability_id")

#     empty_json = {}
#     invalid_json2 = {"user_availability_id": "00000000-0000-0000-0000-000000000000"}
#     valid_json = {"date": "2010-01-01"}

#     response1 = test_client.patch(f"/user_availability/{ua_id}", json=empty_json)
#     assert response1.status_code == 404 
#     assert ua.get("date") == "2000-01-01"

#     response2 = test_client.patch(f"/user_availability/{ua_id}", json=invalid_json2)
#     assert response2.status_code == 404

#     response3 = test_client.patch(f"/user_availability/00000000-0000-0000-0000-000000000000", json=valid_json)
#     assert response3.status_code == 404
    
#     response = test_client.patch(f"/user_availability/{ua_id}", json=valid_json)
#     response_json = response.json()
#     assert response.status_code == 200
#     assert response_json.get("date") == "2010-01-01"

# def test_delete_user_availability(test_client, setup_user_availability):
#     ua, user, date, date2 = setup_user_availability
#     response1 = test_client.delete(f"/user_availability/00000000-0000-0000-0000-000000000000")
#     assert response1.status_code == 404

#     response = test_client.delete(f"/user_availability/{ua.get("user_availability_id")}")
#     response_json = response.json()
#     assert response.status_code == 200
#     assert response_json.get("user_availability_id") == ua.get("user_availability_id")
#     assert test_client.get(f"/user_availability/{ua.get("user_availability_id")}").status_code == 404