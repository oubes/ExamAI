from fastapi import APIRouter

submit = APIRouter()

@submit.get("")
def submit_handler(data):
    return f"Submitted, {data}"