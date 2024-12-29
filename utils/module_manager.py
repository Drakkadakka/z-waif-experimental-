import asyncio
from typing import Dict, List, Optional
import logging

class ModuleManager:
    def __init__(self):
        self.modules: Dict[str, any] = {}
        self.dependencies: Dict[str, List[str]] = {}
        self.initialized: Dict[str, bool] = {}
        
    async def register_module(self, name: str, module: any, dependencies: List[str] = None):
        self.modules[name] = module
        self.dependencies[name] = dependencies or []
        self.initialized[name] = False
        
    async def initialize_modules(self):
        """Initialize modules in correct dependency order"""
        for module_name in self._get_initialization_order():
            try:
                if hasattr(self.modules[module_name], 'initialize'):
                    await self.modules[module_name].initialize()
                self.initialized[module_name] = True
            except Exception as e:
                logging.error(f"Failed to initialize {module_name}: {e}")
                
    def _get_initialization_order(self) -> List[str]:
        """Get correct module initialization order based on dependencies"""
        visited = set()
        order = []
        
        def visit(name):
            if name in visited:
                return
            visited.add(name)
            for dep in self.dependencies.get(name, []):
                visit(dep)
            order.append(name)
            
        for module in self.modules:
            visit(module)
            
        return order 