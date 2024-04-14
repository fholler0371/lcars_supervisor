class Container:
    def __init__(self, core: any, client: any) -> None:
        self.core = core
        self.client = client
        
    async def get(self, name: str) -> None:
        try:
            return await self.core.const.loop.run_in_executor(None, self.client.containers.get, name)
        except Exception as e:
            return None

    async def list(self) -> None:
        try:
            return await self.core.const.loop.run_in_executor(None, self.client.containers.list, True)
        except Exception as e:
            print(e)
            return None
