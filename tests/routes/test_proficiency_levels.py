# def test_get_all_proficiency_levels(test_client, setup_proficiency_level):
#     response = test_client.get("/proficiency_levels")
#     assert response.status_code == 200

#     response_json = response.json()
#     assert len(response_json) > 0
#     assert response_json[0].get("proficiency_level_id") == setup_proficiency_level.get("proficiency_level_id")

# def test_get_single_proficiency_level(test_client, setup_proficiency_level):
#     response = test_client.get(f"/proficiency_levels/{setup_proficiency_level.get("proficiency_level_id")}")
#     assert response.status_code == 200

#     response_json = response.json()
#     assert response_json.get("proficiency_level_id") == setup_proficiency_level.get("proficiency_level_id")
#     assert response_json.get("proficiency_level_name") == "TEST PROFICIENCY LEVEL" 

# def test_post_proficiency_level(test_client, clean_proficiency_levels_table):
#     invalid_json1 = {}
#     invalid_json2 = {"proficiency_level_name": "INVALID PROFICIENCY LEVEL"}
#     valid_json = {"proficiency_level_name": "NEW PROFICIENCY LEVEL", "lookup": "newproficiencylevel"}

#     response1 = test_client.post("/proficiency_levels", json=invalid_json1)
#     assert response1.status_code == 422 

#     response2 = test_client.post("/proficiency_levels", json=invalid_json2)
#     assert response2.status_code == 422 

#     response = test_client.post("/proficiency_levels", json=valid_json)
#     response_json = response.json()
#     assert response.status_code == 201
#     assert response_json.get("proficiency_level_name") == "NEW PROFICIENCY LEVEL"
#     assert response_json.get("is_active") == True 

# def test_update_proficiency_level(test_client, setup_proficiency_level):
#     setup_proficiency_level_id = setup_proficiency_level.get("proficiency_level_id")

#     empty_json = {}
#     invalid_json2 = {"proficiency_level_id": "00000000-0000-0000-0000-000000000000"}
#     valid_json = {"proficiency_level_name": "UPDATED", "lookup": "updated"}

#     response1 = test_client.patch(f"/proficiency_levels/{setup_proficiency_level_id}", json=empty_json)
#     assert response1.status_code == 404 
#     assert setup_proficiency_level.get("proficiency_level_name") == "TEST PROFICIENCY LEVEL"

#     response2 = test_client.patch(f"/proficiency_levels/{setup_proficiency_level_id}", json=invalid_json2)
#     assert response2.status_code == 404

#     response3 = test_client.patch(f"/proficiency_levels/00000000-0000-0000-0000-000000000000", json=valid_json)
#     assert response3.status_code == 404
    
#     response = test_client.patch(f"/proficiency_levels/{setup_proficiency_level_id}", json=valid_json)
#     response_json = response.json()
#     assert response.status_code == 200
#     assert response_json.get("proficiency_level_name") == "UPDATED"
#     assert response_json.get("lookup") == "updated"

# def test_delete_proficiency_level(test_client, setup_proficiency_level):
#     response1 = test_client.delete(f"/proficiency_levels/00000000-0000-0000-0000-000000000000")
#     assert response1.status_code == 404

#     response = test_client.delete(f"/proficiency_levels/{setup_proficiency_level.get("proficiency_level_id")}")
#     response_json = response.json()
#     assert response.status_code == 200
#     assert response_json.get("proficiency_level_id") == setup_proficiency_level.get("proficiency_level_id")
#     assert test_client.get(f"/proficiency_levels/{setup_proficiency_level.get("proficiency_level_id")}").status_code == 404