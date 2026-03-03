"""Broker yönetimi endpoint'leri."""

from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.schemas.broker import (
    BrokerConnectionCreate,
    BrokerConnectionListResponse,
    BrokerConnectionResponse,
    BrokerConnectionUpdate,
    BrokerListInfo,
    BrokerQuoteResponse,
    BrokerTestResult,
)
from app.schemas.common import APIResponse
from app.services.broker_service import BrokerService

router = APIRouter()


def get_broker_service(db: AsyncSession = Depends(get_db)) -> BrokerService:
    return BrokerService(db)


@router.get("/info", response_model=APIResponse[BrokerListInfo])
async def get_available_brokers():
    """Desteklenen broker listesini döner."""
    data = BrokerService.get_available_brokers()
    return APIResponse(success=True, data=data)


@router.get("/connections", response_model=APIResponse[BrokerConnectionListResponse])
async def list_connections(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    user: User = Depends(get_current_user),
    service: BrokerService = Depends(get_broker_service),
):
    """Kullanıcının broker bağlantılarını listeler."""
    data = await service.list_connections(user.id, page=page, per_page=per_page)
    return APIResponse(success=True, data=data)


@router.post("/connections", response_model=APIResponse[BrokerConnectionResponse], status_code=201)
async def create_connection(
    body: BrokerConnectionCreate,
    user: User = Depends(get_current_user),
    service: BrokerService = Depends(get_broker_service),
):
    """Yeni broker bağlantısı oluşturur."""
    data = await service.create_connection(user.id, body)
    return APIResponse(success=True, data=data)


@router.get("/connections/{connection_id}", response_model=APIResponse[BrokerConnectionResponse])
async def get_connection(
    connection_id: UUID,
    user: User = Depends(get_current_user),
    service: BrokerService = Depends(get_broker_service),
):
    """Belirli bir broker bağlantısının detayını getirir."""
    data = await service.get_connection(user.id, connection_id)
    return APIResponse(success=True, data=data)


@router.put("/connections/{connection_id}", response_model=APIResponse[BrokerConnectionResponse])
async def update_connection(
    connection_id: UUID,
    body: BrokerConnectionUpdate,
    user: User = Depends(get_current_user),
    service: BrokerService = Depends(get_broker_service),
):
    """Broker bağlantısını günceller."""
    data = await service.update_connection(user.id, connection_id, body)
    return APIResponse(success=True, data=data)


@router.delete("/connections/{connection_id}", status_code=204)
async def delete_connection(
    connection_id: UUID,
    user: User = Depends(get_current_user),
    service: BrokerService = Depends(get_broker_service),
):
    """Broker bağlantısını siler."""
    await service.delete_connection(user.id, connection_id)


@router.post(
    "/connections/{connection_id}/test",
    response_model=APIResponse[BrokerTestResult],
)
async def test_connection(
    connection_id: UUID,
    user: User = Depends(get_current_user),
    service: BrokerService = Depends(get_broker_service),
):
    """Broker bağlantısını test eder."""
    data = await service.test_connection(user.id, connection_id)
    return APIResponse(success=True, data=data)


@router.get(
    "/connections/{connection_id}/quote/{symbol}",
    response_model=APIResponse[BrokerQuoteResponse],
)
async def get_broker_quote(
    connection_id: UUID,
    symbol: str,
    user: User = Depends(get_current_user),
    service: BrokerService = Depends(get_broker_service),
):
    """Broker üzerinden belirli bir sembolün fiyat bilgisini alır."""
    data = await service.get_quote_via_broker(user.id, connection_id, symbol)
    return APIResponse(success=True, data=data)
