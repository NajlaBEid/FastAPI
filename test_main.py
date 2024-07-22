from fastapi.testclient import TestClient
from main import app





client = TestClient(app)


#Successful Cases 


def test_create_user():

    user = {
        "firstName": "Amal",
        "lastName": "A",
        "mobile": "0505303827",
        "email": "amal@gmail.com"
    }

    response = client.post("/users/", json=user)

  
    assert response.status_code == 200  
    created_user = response.json()

  
    assert created_user["firstName"] == "Amal"
    assert created_user["lastName"] == "A"
    assert created_user["email"] == "amal@gmail.com"
    assert created_user["mobile"] == "0505303827"


def test_get_user():
    response = client.get(f"/users/1")
    assert response.status_code == 200
    assert response.json() == {"id": 1, "firstName": "Amal", "lastName": "A", "mobile": "0505303827", "email": "amal@gmail.com"}



def test_delete_user():
    response = client.delete("/users/1")
    assert response.status_code == 200


def test_update_user():
   
    user_data = {
        "firstName": "Najla",  
        "lastName": "Bin Eid",
        "mobile": "05050000",  
        "email": "najla@ringneck.ai",  
    }


    response = client.post("/users/", json=user_data)
    assert response.status_code == 200
    created_user = response.json()
    user_id = created_user["id"]

    #
    update_data = {
        "firstName": "Najlaa",
        "lastName": "Eid",
        "mobile": "05050000",  
        "email": "najla@ringneck.ai",  
    }

    response = client.put(f"/users/{user_id}", json=update_data)

   
    assert response.status_code == 200

    updated_user = response.json()
    assert updated_user["firstName"] == update_data["firstName"]
    assert updated_user["lastName"] == update_data["lastName"]



#Faied Cases 

def test_create_user_missing_field():
    user_data = {
        "lastName": "Reema",
        "mobile": "05000",
        "email": "Reema@gmail.com",
    }
    response = client.post("/users/", json=user_data)
    assert response.status_code == 422


def test_create_user_invalid_format():
    user_data = {
        "lastName": 11,
        "mobile": "00009",
        "email": "Reema@gmail.com",
    }
    response = client.post("/users/", json=user_data)
    assert response.status_code == 422


def test_get_user_not_found():

    response = client.get(f"/users/200")
    assert response.status_code == 404


def test_delete_user_not_found():
    response = client.delete("/users/199")
    assert response.status_code == 404


def test_update_user_missing_field():

    user_data = {
        "firstName": "Amal",
        "lastName": "A",
        "mobile": "05051234",
        "email": "amal@gmail.com",
    }

    response = client.post("/users/", json=user_data)
    assert response.status_code == 200
    created_user = response.json()
    user_id = created_user["id"]

    update_data = {
        "lastName": "Sarah", 
        "mobile": "B",
        "email": "amal@gmail.com",
    }

    response = client.put(f"/users/{user_id}", json=update_data)

    assert response.status_code == 422



def test_update_user_invalid_field():

    user_data = {
        "firstName": "Reema",
        "lastName": "Bin Eid",
        "mobile": "0509999",
        "email": "reema@gmail.com",
    }

    response = client.post("/users/", json=user_data)
    assert response.status_code == 200
    created_user = response.json()
    user_id = created_user["id"]

    update_data = {
        "firstName": 111,
        "lastName": "Bin Eid", 
        "mobile": "0509999",
        "email": "reema@gmail.com",
    }

    response = client.put(f"/users/{user_id}", json=update_data)

    assert response.status_code == 422









