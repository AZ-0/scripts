from typing import Union
from vm import ProxyVal, VM

class Breakpoint:
    def __init__(self, vm: VM, ref: Union[str, int]) -> None:
        self.vm = vm
        self.addr = ref if isinstance(ref, int) else ProxyVal(vm, ref).eval().val 
        self.label = ref if ref in vm.labels else None

    def is_hit(self) -> bool:
        return self.vm.rip == self.addr % len(self.vm.ops)

    def __repr__(self) -> str:
        return f'Breakpoint({hex(self.addr % len(self.vm.ops))}: {self.vm.ops[self.addr]})'
