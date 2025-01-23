from datetime import datetime, timedelta
from fastapi import HTTPException

request_counts = {}

MAX_REQUESTS = 20
TIME_WINDOW = 60


def rate_limit(user_ip: str):
    current_time = datetime.now()

    if user_ip in request_counts:
        request_counts[user_ip] = [
            timestamp for timestamp in request_counts[user_ip] if
            current_time - timestamp < timedelta(seconds=TIME_WINDOW)
        ]
        if len(request_counts[user_ip]) >= MAX_REQUESTS:
            raise HTTPException(
                status_code=429,
                detail="Too many requests. Please try again later."
            )

    request_counts.setdefault(user_ip, []).append(current_time)
