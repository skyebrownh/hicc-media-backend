# def test_get_all_schedule_date_types(test_client, setup_schedule_date_type):
#     response = test_client.get("/schedule_date_types")
#     assert response.status_code == 200

#     response_json = response.json()
#     assert len(response_json) > 0
#     assert response_json[0].get("schedule_date_type_id") == setup_schedule_date_type.get("schedule_date_type_id")

# def test_get_single_schedule_date_type(test_client, setup_schedule_date_type):
#     response = test_client.get(f"/schedule_date_types/{setup_schedule_date_type.get("schedule_date_type_id")}")
#     assert response.status_code == 200

#     response_json = response.json()
#     assert response_json.get("schedule_date_type_id") == setup_schedule_date_type.get("schedule_date_type_id")
#     assert response_json.get("schedule_date_type_name") == "TEST SCHEDULE DATE TYPE" 

# def test_post_schedule_date_type(test_client, clean_schedule_date_types_table):
#     invalid_json1 = {}
#     invalid_json2 = {"schedule_date_type_name": "INVALID SCHEDULE DATE TYPE"}
#     valid_json = {"schedule_date_type_name": "NEW SCHEDULE DATE TYPE", "lookup": "newscheduledatetype"}

#     response1 = test_client.post("/schedule_date_types", json=invalid_json1)
#     assert response1.status_code == 422 

#     response2 = test_client.post("/schedule_date_types", json=invalid_json2)
#     assert response2.status_code == 422 

#     response = test_client.post("/schedule_date_types", json=valid_json)
#     response_json = response.json()
#     assert response.status_code == 201
#     assert response_json.get("schedule_date_type_name") == "NEW SCHEDULE DATE TYPE"
#     assert response_json.get("is_active") == True 

# def test_update_schedule_date_type(test_client, setup_schedule_date_type):
#     setup_schedule_date_type_id = setup_schedule_date_type.get("schedule_date_type_id")

#     empty_json = {}
#     invalid_json2 = {"schedule_date_type_id": "00000000-0000-0000-0000-000000000000"}
#     valid_json = {"schedule_date_type_name": "UPDATED", "lookup": "updated"}

#     response1 = test_client.patch(f"/schedule_date_types/{setup_schedule_date_type_id}", json=empty_json)
#     assert response1.status_code == 404 
#     assert setup_schedule_date_type.get("schedule_date_type_name") == "TEST SCHEDULE DATE TYPE"

#     response2 = test_client.patch(f"/schedule_date_types/{setup_schedule_date_type_id}", json=invalid_json2)
#     assert response2.status_code == 404

#     response3 = test_client.patch(f"/schedule_date_types/00000000-0000-0000-0000-000000000000", json=valid_json)
#     assert response3.status_code == 404
    
#     response = test_client.patch(f"/schedule_date_types/{setup_schedule_date_type_id}", json=valid_json)
#     response_json = response.json()
#     assert response.status_code == 200
#     assert response_json.get("schedule_date_type_name") == "UPDATED"
#     assert response_json.get("lookup") == "updated"

# def test_delete_schedule_date_type(test_client, setup_schedule_date_type):
#     response1 = test_client.delete(f"/schedule_date_types/00000000-0000-0000-0000-000000000000")
#     assert response1.status_code == 404

#     response = test_client.delete(f"/schedule_date_types/{setup_schedule_date_type.get("schedule_date_type_id")}")
#     response_json = response.json()
#     assert response.status_code == 200
#     assert response_json.get("schedule_date_type_id") == setup_schedule_date_type.get("schedule_date_type_id")
#     assert test_client.get(f"/schedule_date_types/{setup_schedule_date_type.get("schedule_date_type_id")}").status_code == 404
