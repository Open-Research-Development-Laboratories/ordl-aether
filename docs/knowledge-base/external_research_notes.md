# External Research Notes

- Generated: `2026-03-08T03:44:58.878435+00:00`

## FastAPI References Used

- Handling errors guide: https://fastapi.tiangolo.com/tutorial/handling-errors/
- CORS guide: https://fastapi.tiangolo.com/tutorial/cors/

## Key Guidance Applied

- `HTTPException` should propagate with its intended status code instead of being wrapped into generic 500 responses.
- With `allow_credentials=True`, wildcard (`*`) should not be used for `allow_origins`.
