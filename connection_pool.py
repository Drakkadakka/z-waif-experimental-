from typing import Dict, Any, Optional
import asyncio
import logging
from contextlib import asynccontextmanager

class ConnectionPool:
    def __init__(self, max_size: int = 10):
        self.pool: Dict[str, list] = {}
        self.max_size = max_size
        self.locks: Dict[str, asyncio.Lock] = {}
        
    async def get_connection(self, pool_name: str, create_func):
        if pool_name not in self.pool:
            self.pool[pool_name] = []
            self.locks[pool_name] = asyncio.Lock()
            
        async with self.locks[pool_name]:
            if not self.pool[pool_name]:
                if len(self.pool[pool_name]) < self.max_size:
                    conn = await create_func()
                    self.pool[pool_name].append(conn)
                else:
                    raise RuntimeError(f"Connection pool {pool_name} exhausted")
            return self.pool[pool_name].pop()
            
    async def return_connection(self, pool_name: str, connection):
        async with self.locks[pool_name]:
            self.pool[pool_name].append(connection)

    @asynccontextmanager
    async def connection(self, pool_name: str, create_func):
        conn = await self.get_connection(pool_name, create_func)
        try:
            yield conn
        finally:
            await self.return_connection(pool_name, conn) 