from fastapi import APIRouter, status, HTTPException, Depends, Response
import schemas, oauth
from connection import connect_mysql
from icecream import ic
from typing import List

router = APIRouter(
    prefix="/api/records",
    tags=['Records']
)

@router.get("/", response_model = List[schemas.RecordOut])
def get_all_records(cursor = Depends(connect_mysql), user: schemas.UserOut = Depends(oauth.get_current_user_active)):
    if not user.is_auth:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"No authentication for current user to get all record")
    cursor.execute("SELECT * FROM Records;")
    records = cursor.fetchall()
    return records

@router.get("/{username}/{password}")
def get_user_records(username: str, password: str, cursor = Depends(connect_mysql)):
    cursor.execute("SELECT * FROM Users WHERE username = %s;", [username])
    user = cursor.fetchone()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    #if not oauth.verify(password, user["password"]):
    if not password == user["password"]:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    cursor.execute("SELECT * FROM Records WHERE username = %s;", [username])
    records = cursor.fetchall()
    total_exercise = 0
    for r in records:
        total_exercise = total_exercise + r['exercise']
    out = {"records": records, "total_exercise": total_exercise}
    return out

@router.post("/new", response_model = schemas.RecordOut, status_code=status.HTTP_201_CREATED)
def create_new_record(record: schemas.RecordIn, cursor = Depends(connect_mysql), user: schemas.UserOut = Depends(oauth.get_current_user_active)):
    if not user.is_auth:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"No authentication for current user to create record")
    cursor.execute("SELECT * FROM Users WHERE username = %s;", [record.username])
    exist_user = cursor.fetchone()
    if not exist_user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"User id not in database")
    cursor.execute("INSERT INTO Records (username, create_date, exercise) VALUES (%s, %s, %s);", 
                   [record.username, record.create_date, record.exercise])
    cursor.execute("SELECT * FROM Records WHERE record_id = (SELECT max(record_id) FROM Records);")
    new_record = cursor.fetchone()
    return new_record

@router.put("/edit/{record_id}", response_model = schemas.RecordOut)
def edit_record(record_id: int, edited: schemas.RecordIn, cursor = Depends(connect_mysql), user: schemas.UserOut = Depends(oauth.get_current_user_active)):
    if not user.is_auth:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"No authentication for current user to edit record")
    cursor.execute("SELECT * FROM Records WHERE record_id = %s;", [record_id])
    edit_record = cursor.fetchone()
    if not edit_record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Record with id: {record_id} was not found")
    cursor.execute("SELECT * FROM Users WHERE username = %s;", [edited.username])
    old_user = cursor.fetchone()
    if not old_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"User with name: {edited.username} was not found")
    cursor.execute("UPDATE Records SET username = %s WHERE record_id = %s;", [edited.username, record_id])
    cursor.execute("UPDATE Records SET create_date = %s WHERE record_id = %s;", [edited.create_date, record_id])
    cursor.execute("UPDATE Records SET exercise = %s WHERE record_id = %s;", [edited.exercise, record_id])
    cursor.execute("SELECT * FROM Records WHERE record_id = %s;", [record_id])
    edited_record = cursor.fetchone()
    return edited_record

@router.delete("/delete/{record_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_record(record_id: int, cursor = Depends(connect_mysql), user: schemas.UserOut = Depends(oauth.get_current_user_active)):
    if not user.is_auth:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"No authentication for current user to delete record")
    cursor.execute("SELECT * FROM Records WHERE record_id = %s;", [record_id])
    delete_record = cursor.fetchone()
    if not delete_record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                           detail=f"No authentication for current user to edit record")
    cursor.execute("DELETE FROM Records WHERE record_id = %s;", [record_id])
    return Response(status_code=status.HTTP_204_NO_CONTENT)