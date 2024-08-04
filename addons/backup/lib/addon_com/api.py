from aiohttp import web
from datetime import datetime as dt
from os import walk
import os
import tomllib
import boto3
import time

import clilib.data as cd
from corelib import BaseObj, Core
from httplib.models import HttpHandler, HttpRequestData, SendOk

BACKUP_FOLDER = '/lcars/backup'

import logging

class Api(BaseObj):
    def __init__(self, core: Core) -> None:
        BaseObj.__init__(self, core)
        self._apps = {}
        
    async def do_scan(self, idx: int, idx_file: str, rem_folder: str):
        count = 0
        with open("/lcars/config/secret.toml", "rb") as f:
            secret = tomllib.load(f)
        session = boto3.Session(aws_access_key_id=secret['aws']['key'], aws_secret_access_key=secret['aws']['secret'],
                                region_name=secret['aws']['region'])
        s3 = session.resource('s3')
        bucket = s3.Bucket(secret['aws']['bucket'])
        try:
            objs = list(bucket.objects.filter(Prefix=idx_file))
            if len(objs) == 1:
                data = objs[0].get()
                if data['Body'].read().decode() == idx:
                    self.core.log.debug(f"Backup ({rem_folder}) ist schon vorhanden")
                    return
        except Exception as e:
            self.core.log.error(e)  
        self.core.log.debug(bucket)    
        for (dirpath, dirnames, filenames) in walk(BACKUP_FOLDER):
            for name in filenames:
                key = os.path.join(dirpath, name)[len(BACKUP_FOLDER):]
                try:
                    logging.getLogger('boto').setLevel(logging.CRITICAL)
                    objs = list(bucket.objects.filter(Prefix=f'{rem_folder}{key}'))
                    if len(objs) == 0:
                        logging.getLogger('boto').setLevel(logging.CRITICAL)
                        s3.meta.client.upload_file(os.path.join(dirpath, name), secret['aws']['bucket'], f'{rem_folder}{key}')
                        count += 1
                    else:
                        logging.getLogger('boto').setLevel(logging.CRITICAL)
                        days = (objs[0].last_modified.replace(tzinfo=None)-dt.fromtimestamp(os.path.getmtime(os.path.join(dirpath, name)))).days
                        if days < 10:
                            logging.getLogger('boto3').setLevel(logging.CRITICAL)
                            s3.meta.client.upload_file(os.path.join(dirpath, name), secret['aws']['bucket'], f'{rem_folder}{key}')
                            count += 1
                except Exception as e:
                    self.core.log.error(e)  
        self.core.log.info(f"{count} Dateien gesichert {rem_folder}")
        try:
            s3.Object(secret['aws']['bucket'], idx_file).put(Body=idx)
        except Exception as e:
            self.core.log.error(e)  
        
    async def do_day(self):
        rem_folder = f'day/{await self.core.web_l.hostname}'
        idx = str(dt.today().day)
        idx_file = f'{rem_folder}/index'
        rem_folder = f'{rem_folder}/{idx}'
        await self.do_scan(idx, idx_file, rem_folder)
        
    async def do_month(self):
        rem_folder = f'month/{await self.core.web_l.hostname}'
        idx = str(dt.today().month)
        idx_file = f'{rem_folder}/index'
        rem_folder = f'{rem_folder}/{idx}'
        await self.do_scan(idx, idx_file, rem_folder)
        
    async def do_backup(self):
        await self.core.call_random(3600, self.do_backup)
        self.core.log.debug('backup loop')
        await self.do_day()
        await self.do_month()
        
    async def _astart(self):
        self.core.log.debug('starte api')
        await self.core.call_random(30, self.do_backup)