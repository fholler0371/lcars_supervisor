import pydantic


class CliStatus(pydantic.BaseModel):
    name : str
    docker_name : str
    python : bool = False
    lcars : bool = False
    status : str = 'unbekannt'
    network : str = ''
    ip : str = ''
    start : int = 0
    created : int = 0
    
class CliContainer(pydantic.BaseModel):
    name : str
    label : str
    