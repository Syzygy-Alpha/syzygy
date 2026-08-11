from pydantic import BaseModel, Field

from syzygy_observatory.foundation_client import FoundationClient, FoundationModuleDescriptor
from syzygy_observatory.health_observations import (
    HealthObservationRecord,
    HealthObservationRequest,
    HealthObservationStore,
)


class FoundationModuleIngestRequest(BaseModel):
    confirm: bool = Field(default=False)


class FoundationModuleIngestResult(BaseModel):
    observed: int
    observations: list[HealthObservationRecord] = Field(default_factory=list)


class FoundationModuleIngestionError(ValueError):
    pass


class FoundationModuleIngestor:
    def __init__(
        self,
        foundation_client: FoundationClient,
        health_observations: HealthObservationStore,
    ) -> None:
        self.foundation_client = foundation_client
        self.health_observations = health_observations

    async def ingest(self, request: FoundationModuleIngestRequest) -> FoundationModuleIngestResult:
        if not request.confirm:
            msg = "Foundation module ingestion requires confirm=true"
            raise FoundationModuleIngestionError(msg)

        modules = await self.foundation_client.list_modules()
        observations = [
            self.health_observations.record(self._observation_request(module))
            for module in modules
        ]
        return FoundationModuleIngestResult(
            observed=len(observations),
            observations=observations,
        )

    def _observation_request(
        self,
        module: FoundationModuleDescriptor,
    ) -> HealthObservationRequest:
        details = {
            "module_status": module.status,
            "version": module.version,
        }
        if module.capabilities:
            details["capabilities"] = ",".join(module.capabilities)
        if module.dependencies:
            details["dependencies"] = ",".join(module.dependencies)
        details.update(module.health.details)
        return HealthObservationRequest(
            name=module.name,
            status=module.health.status,
            source="foundation.modules",
            details=details,
        )
