from aiohttp import web
import tomllib
import time

import clilib.data as cd
from corelib import BaseObj, Core
from models.network import IpData
from httplib.models import HttpMsgData

import boto3

class Com(BaseObj):
    def __init__(self, core: Core) -> None:
        BaseObj.__init__(self, core)
        
    async def do_check_records(self):
        await self.core.call_random(60, self.do_check_records)
        zones = {}
        with open("/lcars/config/secret.toml", "rb") as f:
            secret = tomllib.load(f)
        with open("/lcars/data/entries.toml", "rb") as f:
            records = tomllib.load(f).get('records', [])
        session = boto3.Session(aws_access_key_id=secret['aws']['key'], aws_secret_access_key=secret['aws']['secret'])
        try:
            resp = await self.core.web_l.msg_send(HttpMsgData(dest='avm', type='get_all_ip'))
            ip_data = IpData.model_validate(resp)
            ip_data = ip_data.model_dump()
            r53 = session.client('route53')
            domains = secret['aws'].get('domains', [])
            for record in records:
                for domain in domains:
                    if domain['domain'] in record['domain']:
                        zone_id = domain['zone_id']
                        reload = False #Lade Zonendaten
                        if zone_id not in zones:
                            reload = True
                        elif zones[zone_id]['timestamp'] + 10800 < time.time():
                            reload = True
                        if reload:
                            zone_data = r53.list_resource_record_sets(HostedZoneId=zone_id)
                            if zone_data['ResponseMetadata']['HTTPStatusCode'] == 200:
                                zones[zone_id] = {'timestamp': int(time.time()), 'data': zone_data['ResourceRecordSets']}
                            elif zone_id  in zones:
                                del zones[zone_id]
                        if zone_id in zones:
                            for entry in  zones[zone_id]['data']:
                                if entry['Name'] == f'{record['domain']}.' and entry['Type'] == record['type']:
                                    value = ip_data.get(record['entry'])
                                    if value != entry['ResourceRecords'][0]['Value']:
                                        batch = [{'Action': 'UPSERT', 'ResourceRecordSet': {'Name': entry['Name'], 'Type': 'AAAA', 'TTL': 300,
                                                  'ResourceRecords': [{'Value': value}]}}]
                                        resp = r53.change_resource_record_sets(HostedZoneId=zone_id, ChangeBatch={'Comment': 'changed by lcars', 'Changes': batch})
        except Exception as e:
            self.core.log.error(repr(e))
                
    async def _ainit(self):
        self.core.log.debug('Initaliesiere com')

    async def _astart(self):
        self.core.log.debug('Starte com')
        await self.core.call_random(30, self.do_check_records)