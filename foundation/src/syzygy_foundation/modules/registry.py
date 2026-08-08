from syzygy_foundation.modules.types import ModuleDescriptor


class ModuleRegistry:
    def __init__(self) -> None:
        self._modules: dict[str, ModuleDescriptor] = {}

    def register(self, descriptor: ModuleDescriptor) -> None:
        self._modules[descriptor.name] = descriptor

    def list_modules(self) -> list[ModuleDescriptor]:
        return sorted(self._modules.values(), key=lambda module: module.name)

    def get(self, name: str) -> ModuleDescriptor | None:
        return self._modules.get(name)

