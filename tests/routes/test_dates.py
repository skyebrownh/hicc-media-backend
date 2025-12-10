# def test_get_all_dates(test_client, setup_date):
#     response = test_client.get("/dates")
#     assert response.status_code == 200

#     response_json = response.json()
#     assert len(response_json) > 0
#     assert response_json[0].get("date") == setup_date.get("date")

# def test_get_single_date(test_client, setup_date):
#     response = test_client.get(f"/dates/{setup_date.get("date")}")
#     assert response.status_code == 200

#     response_json = response.json()
#     assert response_json.get("date") == setup_date.get("date")

# def test_post_date(test_client, clean_dates_table):
#     invalid_json1 = {}
#     invalid_json2 = {"date": "INVALID DATE"}
#     valid_json = {"date": "2025-01-01"}

#     response1 = test_client.post("/dates", json=invalid_json1)
#     assert response1.status_code == 422 

#     response2 = test_client.post("/dates", json=invalid_json2)
#     assert response2.status_code == 422 

#     response = test_client.post("/dates", json=valid_json)
#     response_json = response.json()
#     assert response.status_code == 201
#     assert response_json.get("date") == "2025-01-01"

# def test_update_date(test_client, setup_date):
#     empty_json = {}
#     invalid_json2 = {"date": "2012-01-01"}
#     valid_json = {"is_holiday": True, "weekday_of_month": 1}

#     response1 = test_client.patch(f"/dates/{setup_date.get("date")}", json=empty_json)
#     assert response1.status_code == 404 
#     assert setup_date.get("date") == "2000-01-01"

#     response2 = test_client.patch(f"/dates/{setup_date.get("date")}", json=invalid_json2)
#     assert response2.status_code == 404

#     response3 = test_client.patch(f"/dates/2001-01-01", json=valid_json)
#     assert response3.status_code == 404
    
#     response = test_client.patch(f"/dates/{setup_date.get("date")}", json=valid_json)
#     response_json = response.json()
#     assert response.status_code == 200
#     assert response_json.get("is_holiday") == True 
#     assert response_json.get("weekday_of_month") == 1

# def test_delete_date(test_client, setup_date):
#     response1 = test_client.delete(f"/dates/2001-01-01")
#     assert response1.status_code == 404

#     response = test_client.delete(f"/dates/{setup_date.get("date")}")
#     response_json = response.json()
#     assert response.status_code == 200
#     assert response_json.get("date") == setup_date.get("date")
#     assert test_client.get(f"/dates/{setup_date.get("date")}").status_code == 404