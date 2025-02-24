"""
Test module for margin position CRUD operations.
Contains tests for opening, closing, and managing margin positions.
"""

import uuid
from decimal import Decimal
from unittest.mock import AsyncMock, Mock

import pytest
from app.crud.margin_position import MarginPositionCRUD, MarginPositionStatus
from app.models.margin_position import MarginPosition


@pytest.mark.asyncio
async def test_open_margin_position_success():
    """
    Test successful opening of a margin position.
    Verifies that a new position is created with correct parameters and OPEN status.
    """
    user_id = uuid.uuid4()
    borrowed_amount = Decimal("5000.00")
    multiplier = 2
    transaction_id = "tx_12345"

    crud = MarginPositionCRUD()
    mock_position = MarginPosition(
        user_id=user_id,
        borrowed_amount=borrowed_amount,
        multiplier=multiplier,
        transaction_id=transaction_id,
        status=MarginPositionStatus.OPEN,
    )
    crud.write_to_db = AsyncMock(return_value=mock_position)

    result = await crud.open_margin_position(user_id, borrowed_amount, multiplier, transaction_id)

    crud.write_to_db.assert_awaited_once()
    passed_position = crud.write_to_db.call_args.args[0]
    assert passed_position.user_id == user_id
    assert passed_position.borrowed_amount == borrowed_amount
    assert passed_position.multiplier == multiplier
    assert passed_position.transaction_id == transaction_id
    assert passed_position.status == MarginPositionStatus.OPEN
    assert result == mock_position


@pytest.mark.asyncio
async def test_close_margin_position_success():
    """
    Test successful closing of a margin position.
    Verifies that an existing position can be closed and its status updated to CLOSED.
    """
    position_id = uuid.uuid4()
    mock_position = MarginPosition(
        id=position_id,
        user_id=uuid.uuid4(),
        borrowed_amount=Decimal("1000.00"),
        multiplier=3,
        transaction_id="tx_67890",
        status=MarginPositionStatus.OPEN,
    )

    crud = MarginPositionCRUD()
    crud.get_object = AsyncMock(return_value=mock_position)
    crud.write_to_db = AsyncMock(return_value=mock_position)

    result = await crud.close_margin_position(position_id)

    assert result == MarginPositionStatus.CLOSED
    crud.get_object.assert_awaited_once_with(MarginPosition, position_id)
    crud.write_to_db.assert_awaited_once_with(mock_position)
    assert mock_position.status == MarginPositionStatus.CLOSED


@pytest.mark.asyncio
async def test_close_margin_position_not_found():
    """
    Test attempting to close a non-existent margin position.
    Verifies that the operation returns None when position is not found.
    """
    position_id = uuid.uuid4()
    
    crud = MarginPositionCRUD()
    crud.get_object = AsyncMock(return_value=None)
    crud.write_to_db = AsyncMock()
    
    result = await crud.close_margin_position(position_id)
    
    assert result is None
    crud.get_object.assert_awaited_once_with(MarginPosition, position_id)
    crud.write_to_db.assert_not_awaited()


@pytest.mark.asyncio
async def test_close_already_closed_position():
    """
    Test attempting to close an already closed margin position.
    Verifies that closing a closed position maintains the CLOSED status.
    """
    position_id = uuid.uuid4()
    mock_position = MarginPosition(
        id=position_id,
        user_id=uuid.uuid4(),
        borrowed_amount=Decimal("2000.00"),
        multiplier=2,
        transaction_id="tx_98765",
        status=MarginPositionStatus.CLOSED,
    )

    crud = MarginPositionCRUD()
    crud.get_object = AsyncMock(return_value=mock_position)
    crud.write_to_db = AsyncMock(return_value=mock_position)

    result = await crud.close_margin_position(position_id)

    assert result == MarginPositionStatus.CLOSED
    crud.write_to_db.assert_awaited_once_with(mock_position)
    assert mock_position.status == MarginPositionStatus.CLOSED