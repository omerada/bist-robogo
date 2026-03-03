# Source: Doc 02 §2.4 — Risk yönetimi servisi (9 kural)
"""Risk yönetimi iş mantığı katmanı."""

import logging
from decimal import Decimal
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.portfolio_repository import (
    PortfolioRepository,
    PositionRepository,
)
from app.repositories.risk_repository import RiskEventRepository, RiskRuleRepository
from app.schemas.risk import (
    RiskEventResponse,
    RiskLevel,
    RiskRuleResponse,
    RiskRuleUpdate,
    RiskStatusResponse,
)

logger = logging.getLogger(__name__)

INITIAL_CASH = 100_000.0


class RiskService:
    """Risk kuralları yönetimi + kural doğrulama."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.rule_repo = RiskRuleRepository(db)
        self.event_repo = RiskEventRepository(db)
        self.portfolio_repo = PortfolioRepository(db)
        self.position_repo = PositionRepository(db)

    # ── Risk Durumu ──

    async def get_status(self, user_id: UUID) -> RiskStatusResponse:
        """Genel risk durumunu hesapla."""
        # Kuralları al (yoksa defaults oluştur)
        rules = await self.rule_repo.ensure_defaults(user_id)
        await self.db.commit()  # varsayılan kurallar oluşturulmuşsa persist et
        active_rules = [r for r in rules if r.is_active]

        # Portföy bilgisi
        portfolio = await self.portfolio_repo.get_or_create(user_id, INITIAL_CASH)
        open_positions = await self.position_repo.count_open(user_id)

        # Günlük kayıp hesapla
        daily_loss = Decimal(str(abs(float(portfolio.daily_pnl)))) if portfolio.daily_pnl < 0 else Decimal("0")
        daily_loss_limit_rule = next(
            (r for r in active_rules if r.rule_type == "daily_loss_limit_pct"), None
        )
        daily_loss_limit_pct = Decimal(str(daily_loss_limit_rule.value.get("limit", 5.0))) if daily_loss_limit_rule else Decimal("5.0")
        daily_loss_limit = Decimal(str(float(portfolio.total_value))) * daily_loss_limit_pct / 100

        # Max pozisyon kuralı
        max_pos_rule = next(
            (r for r in active_rules if r.rule_type == "max_position_count"), None
        )
        max_positions = max_pos_rule.value.get("limit", 10) if max_pos_rule else 10

        # Risk seviyesi hesapla
        risk_level = self._calculate_risk_level(
            daily_loss=float(daily_loss),
            daily_loss_limit=float(daily_loss_limit),
            open_positions=open_positions,
            max_positions=max_positions,
        )

        # Son olaylar
        recent_events = await self.event_repo.get_recent(user_id, limit=5)
        events_data = [
            {"type": e.event_type, "details": e.details, "created_at": str(e.created_at)}
            for e in recent_events
        ]

        return RiskStatusResponse(
            overall_risk=risk_level,
            daily_loss=daily_loss,
            daily_loss_limit=daily_loss_limit,
            open_positions=open_positions,
            max_positions=max_positions,
            rules_active=len(active_rules),
            recent_events=events_data,
        )

    # ── Kurallar ──

    async def list_rules(self, user_id: UUID) -> list[RiskRuleResponse]:
        """Kullanıcının tüm risk kurallarını listele."""
        rules = await self.rule_repo.ensure_defaults(user_id)
        await self.db.commit()  # varsayılan kurallar oluşturulmuşsa persist et
        return [RiskRuleResponse.model_validate(r) for r in rules]

    async def update_rule(
        self, user_id: UUID, rule_id: UUID, data: RiskRuleUpdate
    ) -> RiskRuleResponse:
        """Risk kuralını güncelle."""
        rule = await self.rule_repo.get_by_id(rule_id)
        if not rule or rule.user_id != user_id:
            raise ValueError("Risk kuralı bulunamadı")

        update_data = {}
        if data.value is not None:
            update_data["value"] = data.value
        if data.is_active is not None:
            update_data["is_active"] = data.is_active

        if update_data:
            rule = await self.rule_repo.update(rule, **update_data)
            await self.db.commit()
            await self.db.refresh(rule)  # Fix #24: onupdate alanlarını yenile (MissingGreenlet)

        return RiskRuleResponse.model_validate(rule)

    # ── Olaylar ──

    async def list_events(
        self,
        user_id: UUID,
        event_type: str | None = None,
        skip: int = 0,
        limit: int = 50,
    ) -> tuple[list[RiskEventResponse], int]:
        """Risk olaylarını listele."""
        events = await self.event_repo.get_by_user(
            user_id, event_type=event_type, skip=skip, limit=limit
        )
        total = await self.event_repo.count_by_user(user_id, event_type=event_type)
        return [RiskEventResponse.model_validate(e) for e in events], total

    # ── Kural Doğrulama (9 kural) ──

    async def validate_order(
        self,
        user_id: UUID,
        symbol: str,
        side: str,
        quantity: int,
        price: float,
    ) -> tuple[bool, str | None]:
        """Emir öncesi risk kontrolü yap. (ok, reason) döner."""
        rules = await self.rule_repo.get_active_rules(user_id)
        if not rules:
            return True, None

        portfolio = await self.portfolio_repo.get_or_create(user_id, INITIAL_CASH)
        positions = await self.position_repo.get_open_positions(user_id)
        order_value = quantity * price

        for rule in rules:
            ok, reason = self._check_rule(
                rule=rule,
                portfolio=portfolio,
                positions=positions,
                symbol=symbol,
                side=side,
                order_value=order_value,
            )
            if not ok:
                # Risk olayı kaydet
                await self.event_repo.create(
                    user_id=user_id,
                    event_type="rule_violation",
                    rule_id=rule.id,
                    details={
                        "rule_type": rule.rule_type,
                        "symbol": symbol,
                        "side": side,
                        "order_value": order_value,
                        "reason": reason,
                    },
                )
                await self.db.commit()
                return False, reason

        return True, None

    def _check_rule(
        self,
        rule,
        portfolio,
        positions: list,
        symbol: str,
        side: str,
        order_value: float,
    ) -> tuple[bool, str | None]:
        """Tek bir kuralı kontrol et."""
        rt = rule.rule_type
        v = rule.value

        if rt == "max_position_count" and side == "buy":
            limit = v.get("limit", 10)
            if len(positions) >= limit:
                return False, f"Maksimum pozisyon sayısı ({limit}) aşıldı"

        elif rt == "max_position_size_pct" and side == "buy":
            limit_pct = v.get("limit", 20.0)
            total_value = float(portfolio.total_value) or 1
            ratio = (order_value / total_value) * 100
            if ratio > limit_pct:
                return False, f"Tek pozisyon portföy oranı %{ratio:.1f} > %{limit_pct} limiti"

        elif rt == "daily_loss_limit_pct":
            limit_pct = v.get("limit", 5.0)
            total_value = float(portfolio.total_value) or 1
            daily_loss = abs(float(portfolio.daily_pnl)) if portfolio.daily_pnl < 0 else 0
            daily_loss_pct = (daily_loss / total_value) * 100
            if daily_loss_pct > limit_pct:
                return False, f"Günlük kayıp limiti aşıldı: %{daily_loss_pct:.1f} > %{limit_pct}"

        elif rt == "max_order_value" and side == "buy":
            limit_val = v.get("limit", 50000.0)
            if order_value > limit_val:
                return False, f"Emir değeri {order_value:,.0f} > {limit_val:,.0f} limiti"

        elif rt == "max_sector_exposure_pct" and side == "buy":
            # Sektör bazlı kontrol — basit implementasyon
            limit_pct = v.get("limit", 40.0)
            # İleride sektör bilgisi ile kontrol yapılacak
            pass

        elif rt == "min_cash_reserve_pct" and side == "buy":
            limit_pct = v.get("limit", 10.0)
            total_value = float(portfolio.total_value) or 1
            remaining_cash = float(portfolio.cash_balance) - order_value
            cash_pct = (remaining_cash / total_value) * 100
            if cash_pct < limit_pct:
                return False, f"Nakit rezerv %{cash_pct:.1f} < %{limit_pct} minimum"

        elif rt == "max_daily_trades":
            # Günlük işlem sayısı kontrolü — basit implementasyon
            limit_count = v.get("limit", 20)
            # İleride günlük trade sayısı ile kontrol yapılacak
            pass

        elif rt == "max_leverage":
            limit_leverage = v.get("limit", 1.0)
            total_value = float(portfolio.total_value) or 1
            invested = float(portfolio.invested_value) + (order_value if side == "buy" else 0)
            leverage = invested / total_value
            if leverage > limit_leverage:
                return False, f"Kaldıraç oranı {leverage:.2f} > {limit_leverage} limiti"

        return True, None

    def _calculate_risk_level(
        self,
        daily_loss: float,
        daily_loss_limit: float,
        open_positions: int,
        max_positions: int,
    ) -> RiskLevel:
        """Risk seviyesini hesapla."""
        if daily_loss_limit <= 0:
            return RiskLevel.LOW

        loss_ratio = daily_loss / daily_loss_limit
        pos_ratio = open_positions / max(max_positions, 1)

        if loss_ratio > 0.9 or pos_ratio > 0.9:
            return RiskLevel.CRITICAL
        elif loss_ratio > 0.7 or pos_ratio > 0.7:
            return RiskLevel.HIGH
        elif loss_ratio > 0.4 or pos_ratio > 0.4:
            return RiskLevel.MODERATE
        return RiskLevel.LOW
