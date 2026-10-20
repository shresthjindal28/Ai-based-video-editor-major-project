
import pytest
from sqlalchemy.exc import DBAPIError

from app.db.session import transaction_retry


@pytest.mark.asyncio
async def test_deadlock_retry_is_bounded_and_reexecutes_fresh_operation():
    class Deadlock(Exception):
        sqlstate="40P01"
    attempts=0
    async def operation():
        nonlocal attempts
        attempts+=1
        if attempts<3:
            raise DBAPIError("statement",None,Deadlock(),False)
        return "committed"
    assert await transaction_retry(operation,attempts=3)=="committed"
    assert attempts==3


@pytest.mark.asyncio
async def test_permanent_database_error_is_not_retried():
    attempts=0
    async def operation():
        nonlocal attempts
        attempts+=1
        raise DBAPIError("statement",None,ValueError("permanent"),False)
    with pytest.raises(DBAPIError):
        await transaction_retry(operation)
    assert attempts==1
