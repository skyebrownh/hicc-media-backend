# from fastapi import HTTPException
# from supabase import create_client, Client, PostgrestAPIError

# from app.utils.helpers import table_id

# class SupabaseService():
#     def __init__(self, url, key):
#         self.client: Client = create_client(url, key)

#     def get_all(self, table: str):
#         query = self.client.table(table).select("*")
#         response = validate(query)
#         return response.data

#     def get_single(self, table: str, id: str):
#         query = self.client.table(table).select("*").eq(table_id(table), id)
#         response = validate(query)
#         return response.data[0]

#     def post(self, table: str, body: dict):
#         query = self.client.table(table).insert(body)
#         response = validate(query)
#         return response.data[0]

#     def update(self, table: str, body: dict, id: str):
#         # only applies to direct calls, not through FastAPI
#         if table_id(table) in body:
#             raise HTTPException(status_code=400, detail="Primary Key/ID cannot be updated")

#         query = self.client.table(table).update(body).eq(table_id(table), id)
#         response = validate(query)
#         return response.data[0]

#     def delete(self, table: str, id: str):
#         query = self.client.table(table).delete().eq(table_id(table), id)
#         response = validate(query)
#         return response.data[0]

# def validate(query):
#     try:
#         response = query.execute()
#     except PostgrestAPIError as e:
#         raise handle_supabase_error(e)

#     if len(response.data) == 0:
#         raise HTTPException(status_code=404, detail="Resource not found")
    
#     return response

# def handle_supabase_error(error: PostgrestAPIError) -> HTTPException:
#     code = error.code if hasattr(error, "code") else None
#     message = error.message if hasattr(error, "message") else str(error)

#     match code: 
#         case "23505":
#             return HTTPException(status_code=409, detail="Duplicate entry")
#         case "23503":
#             return HTTPException(status_code=400, detail="Invalid foreign key reference")
#         case "23502":
#             return HTTPException(status_code=400, detail=f"Not null violation: {message}")
#         case "PGRST100":
#             return HTTPException(status_code=400, detail="Failed to parse parameters")
#         case "42P01":
#             return HTTPException(status_code=404, detail="Requested resource does not exist")
#         case 404:
#             return HTTPException(status_code=404, detail="Requested resource does not exist")
#         case _:
#             return HTTPException(status_code=500, detail=message)