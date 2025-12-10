# def test_get_all_schedule_dates(test_client, setup_schedule_date):
#     schedule_date, schedule, date, type, type2 = setup_schedule_date
#     response = test_client.get("/schedule_dates")
#     assert response.status_code == 200

#     response_json = response.json()
#     assert len(response_json) > 0
#     assert response_json[0].get("schedule_date_id") == schedule_date.get("schedule_date_id")

# def test_get_single_schedule_date(test_client, setup_schedule_date):
#     schedule_date, schedule, date, type, type2 = setup_schedule_date
#     response = test_client.get(f"/schedule_dates/{schedule_date.get("schedule_date_id")}")
#     assert response.status_code == 200

#     response_json = response.json()
#     assert response_json.get("schedule_date_id") == schedule_date.get("schedule_date_id")
#     assert response_json.get("schedule_date_type_id") == type.get("schedule_date_type_id")

# def test_post_schedule_dates(test_client, setup_schedule_date):
#     schedule_date, schedule, date, type, type2 = setup_schedule_date
#     invalid_json1 = {}
#     invalid_json2 = {"schedule_date_type_id": type.get("schedule_date_type_id")}
#     valid_json = {
#         "schedule_id": schedule.get("schedule_id"),
#         "date": date.get("date"),
#         "schedule_date_type_id": type2.get("schedule_date_type_id")
#     }

#     response1 = test_client.post("/schedule_dates", json=invalid_json1)
#     assert response1.status_code == 422 

#     response2 = test_client.post("/schedule_dates", json=invalid_json2)
#     assert response2.status_code == 422 

#     response = test_client.post("/schedule_dates", json=valid_json)
#     response_json = response.json()
#     assert response.status_code == 201
#     assert response_json.get("schedule_date_type_id") == type2.get("schedule_date_type_id")
#     assert response_json.get("schedule_id") == schedule.get("schedule_id") 

# def test_update_schedule_dates(test_client, setup_schedule_date):
#     schedule_date, schedule, date, type, type2 = setup_schedule_date
#     schedule_date_id = schedule_date.get("schedule_date_id")

#     empty_json = {}
#     invalid_json2 = {"schedule_date_id": "00000000-0000-0000-0000-000000000000"}
#     valid_json = {"schedule_date_type_id": type2.get("schedule_date_type_id")}

#     response1 = test_client.patch(f"/schedule_dates/{schedule_date_id}", json=empty_json)
#     assert response1.status_code == 404 
#     assert schedule_date.get("schedule_date_type_id") == type.get("schedule_date_type_id")

#     response2 = test_client.patch(f"/schedule_dates/{schedule_date_id}", json=invalid_json2)
#     assert response2.status_code == 404

#     response3 = test_client.patch(f"/schedule_dates/00000000-0000-0000-0000-000000000000", json=valid_json)
#     assert response3.status_code == 404
    
#     response = test_client.patch(f"/schedule_dates/{schedule_date_id}", json=valid_json)
#     response_json = response.json()
#     assert response.status_code == 200
#     assert response_json.get("schedule_date_type_id") == type2.get("schedule_date_type_id")

# def test_delete_schedule_dates(test_client, setup_schedule_date):
#     schedule_date, schedule, date, type, type2 = setup_schedule_date
#     response1 = test_client.delete(f"/schedule_dates/00000000-0000-0000-0000-000000000000")
#     assert response1.status_code == 404

#     response = test_client.delete(f"/schedule_dates/{schedule_date.get("schedule_date_id")}")
#     response_json = response.json()
#     assert response.status_code == 200
#     assert response_json.get("schedule_date_id") == schedule_date.get("schedule_date_id")
#     assert test_client.get(f"/schedule_dates/{schedule_date.get("schedule_date_id")}").status_code == 404