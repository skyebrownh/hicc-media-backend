# def test_get_all_schedules(test_client, setup_schedule):
#     response = test_client.get("/schedules")
#     assert response.status_code == 200

#     response_json = response.json()
#     assert len(response_json) > 0
#     assert response_json[0].get("schedule_id") == setup_schedule.get("schedule_id")

# def test_get_single_schedule(test_client, setup_schedule):
#     response = test_client.get(f"/schedules/{setup_schedule.get("schedule_id")}")
#     assert response.status_code == 200

#     response_json = response.json()
#     assert response_json.get("schedule_id") == setup_schedule.get("schedule_id")
#     assert response_json.get("month_start_date") == "2000-01-01" 

# def test_post_schedule(test_client, setup_schedule):
#     invalid_json1 = {}
#     invalid_json2 = {"month_start_date": "INVALID"}
#     valid_json = {"month_start_date": "2000-01-01", "is_active": False, "notes": "post schedule test"}

#     response1 = test_client.post("/schedules", json=invalid_json1)
#     assert response1.status_code == 422 

#     response2 = test_client.post("/schedules", json=invalid_json2)
#     assert response2.status_code == 422 

#     response = test_client.post("/schedules", json=valid_json)
#     response_json = response.json()
#     assert response.status_code == 201
#     assert response_json.get("month_start_date") == "2000-01-01"
#     assert response_json.get("is_active") == False 

# def test_update_schedule(test_client, setup_schedule):
#     setup_schedule_id = setup_schedule.get("schedule_id")

#     empty_json = {}
#     invalid_json2 = {"schedule_id": "00000000-0000-0000-0000-000000000000"}
#     valid_json = {"notes": "updated"}

#     response1 = test_client.patch(f"/schedules/{setup_schedule_id}", json=empty_json)
#     assert response1.status_code == 404 
#     assert setup_schedule.get("notes") == None 

#     response2 = test_client.patch(f"/schedules/{setup_schedule_id}", json=invalid_json2)
#     assert response2.status_code == 404

#     response3 = test_client.patch(f"/schedules/00000000-0000-0000-0000-000000000000", json=valid_json)
#     assert response3.status_code == 404
    
#     response = test_client.patch(f"/schedules/{setup_schedule_id}", json=valid_json)
#     response_json = response.json()
#     assert response.status_code == 200
#     assert response_json.get("notes") == "updated"

# def test_delete_schedule(test_client, setup_schedule):
#     response1 = test_client.delete(f"/schedules/00000000-0000-0000-0000-000000000000")
#     assert response1.status_code == 404

#     response = test_client.delete(f"/schedules/{setup_schedule.get("schedule_id")}")
#     response_json = response.json()
#     assert response.status_code == 200
#     assert response_json.get("schedule_id") == setup_schedule.get("schedule_id")
#     assert test_client.get(f"/schedules/{setup_schedule.get("schedule_id")}").status_code == 404
