from __future__ import annotations

from app.schemas.risk import RiskPolicyResponse

_STATIC_POLICY = RiskPolicyResponse()


class RiskPolicyService:
    def get_policy(self) -> RiskPolicyResponse:
        return _STATIC_POLICY
