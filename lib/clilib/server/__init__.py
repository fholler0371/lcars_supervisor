from aiohttp import web

from corelib import BaseObj, Core


class Server(BaseObj):
    def __init__(self, core: Core) -> None:
        BaseObj.__init__(self, core)
        
    async def _ainit(self):
        await self.core.web.add_handler('/cli/', self.handler)
        
    async def handler(self, request: web.Request) -> bool:
        print(request)
        try:
            version = int(request.path.split('/')[2])
        except:
            self.core.log.error('Keine gültige Version im Pfad')
            version = 0
        if 'Authorization' in request.headers:
            header = request.headers['Authorization']
            print(self.core.web.local_keys.local)
        else:
            self.core.log.error('Kein Autorisation Handler')
            return (True, web.Response(status=403, text='Nicht erlaubt'))
        return False
#Authorization: Bearer <token>