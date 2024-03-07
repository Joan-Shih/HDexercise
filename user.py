from typing import Annotated
from fastapi import APIRouter, status, HTTPException, Depends, Response
from fastapi.security import OAuth2PasswordRequestForm
import schemas, oauth
from connection import connect_mysql
from icecream import ic

router = APIRouter(
    prefix="/api",
    tags=['Users']
)

@router.get("/users")
def get_all_users(cursor = Depends(connect_mysql), user: schemas.UserOut = Depends(oauth.get_current_user_active)):
    if not user.is_auth:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"No authentication for get all users")
    cursor.execute("SELECT * FROM Users")
    users = cursor.fetchall()
    return users

'''
@router.post("/authuser", response_model = schemas.UserOut, status_code=status.HTTP_201_CREATED)
def create_new_authuser(new_user: schemas.UserIn, cursor = Depends(connect_mysql)):
    cursor.execute("SELECT * FROM Users WHERE username = %s;", [new_user.username])
    exist_user = cursor.fetchone()
    if exist_user:
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE,
                            detail=f"Username with {new_user.username} already exist")
    cursor.execute("INSERT INTO Users (username, password, is_auth) VALUES (%s, %s, %s);", 
                   [new_user.username, oauth.hash(new_user.password), new_user.is_auth])
    cursor.execute("SELECT * FROM Users WHERE username = %s;", [new_user.username])
    created_user = cursor.fetchone()
    return created_user
'''

@router.post("/users", response_model = schemas.UserOut, status_code=status.HTTP_201_CREATED)
def create_new_user(new_user: schemas.UserIn, user: schemas.UserOut = Depends(oauth.get_current_user_active), cursor = Depends(connect_mysql)):
    if not user.is_auth:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"No authentication for create user")
    cursor.execute("SELECT * FROM Users WHERE username = %s;", [new_user.username])
    exist_user = cursor.fetchone()
    if exist_user:
        raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE,
                            detail=f"Username with {new_user.username} already exist")
    #cursor.execute("INSERT INTO Users (username, password, is_auth) VALUES (%s, %s, %s);", 
    #               [new_user.username, oauth.hash(new_user.password), new_user.is_auth])
    cursor.execute("INSERT INTO Users (username, password, is_auth) VALUES (%s, %s, %s);", 
                   [new_user.username, new_user.password, new_user.is_auth])
    cursor.execute("SELECT * FROM Users WHERE username = %s;", [new_user.username])
    created_user = cursor.fetchone()
    return created_user

@router.put("/edit/{username}", response_model = schemas.UserOut)
def edit_user(username: str, edited: schemas.UserIn, cursor = Depends(connect_mysql), user: schemas.UserOut = Depends(oauth.get_current_user_active)):
    if not user.is_auth:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"No authentication for edit user")
    cursor.execute("SELECT * FROM Users WHERE username = %s;", [username])
    edit_user = cursor.fetchone()
    if not edit_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"User with name: {username} was not found")
    cursor.execute("SELECT * FROM Users WHERE username = %s;", [edited.username])
    old_user = cursor.fetchone()
    if old_user and edited.username != username:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"User with name: {edited.username} already exist")
    #cursor.execute("UPDATE Users SET password = %s WHERE username = %s;", [oauth.hash(edited.password), username])
    cursor.execute("UPDATE Users SET password = %s WHERE username = %s;", [edited.password, username])
    cursor.execute("UPDATE Users SET username = %s WHERE username = %s;", [edited.username, username])
    cursor.execute("SELECT * FROM Users WHERE username = %s;", [edited.username])
    edited_user = cursor.fetchone()
    return edited_user

@router.delete("/delete/{username}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(username: str, cursor = Depends(connect_mysql), user: schemas.UserOut = Depends(oauth.get_current_user_active)):
    if not user.is_auth:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"No authentication for delete user")
    cursor.execute("SELECT * FROM Users WHERE username = %s;", [username])
    delete_user = cursor.fetchone()
    if not delete_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"User with name: {username} was not found")
    cursor.execute("DELETE FROM Users WHERE username = %s;", [username])
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@router.post("/login", response_model=schemas.Token)
def login(login_user: Annotated[OAuth2PasswordRequestForm, Depends()], cursor = Depends(connect_mysql)):
    cursor.execute("SELECT * FROM Users WHERE username = %s;", [login_user.username])
    user = cursor.fetchone()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    #if not oauth.verify(login_user.password, user["password"]):
    if not login_user.password == user["password"]:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user["is_auth"]:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not auth user",
            headers={"WWW-Authenticate": "Bearer"},
        )
    cursor.execute("UPDATE Users SET is_login = %s WHERE username = %s;", [True, user["username"]])
    token = oauth.create_access_token({"username": user["username"], "is_auth": user["is_auth"]})
    return {"access_token": token, "token_type": "bearer"}

"""
@router.put("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(cursor = Depends(connect_mysql), user: schemas.UserOut = Depends(oauth.get_current_user_active)):
    cursor.execute("UPDATE Users SET is_login = %s WHERE username = %s;", [False, user.username])
    return Response(status_code=status.HTTP_204_NO_CONTENT)
"""