from aiohttp import web
import aiohttp
import json
import tomllib
import urllib.parse
import time

from corelib import BaseObj, Core
from httplib.models import HttpHandler, HttpRequestData, SendOk, HttpMsgData
from models.auth import Moduls
from models.sm import HistoryFullOut
import aioauth


PANELS = {'base': {
             'cards' : [{'name': 'withings_body', 'type': 'app'},
                        {'name': 'withings_weight_trend', 'type': 'app'},
                        {'name': 'withings_heart', 'type': 'app'},
                        {'name': 'withings_temp', 'type': 'app'}],
             'items' : [{"label": "Körper", "type": "withings_body"},
                        {'label': 'Gewichtsentwicklung', 'type': 'withings_weight_trend'},       
                        {'label': 'Herz', 'type': 'withings_heart'},     
                        {'label': 'Temperatur', 'type': 'withings_temp'}]       
                  },
          'daily': {
              'cards' : [{'name': 'withings_daily', 'type': 'app'}],
              'items' : [{"label": "Körper (gestern)", "type": "withings_daily"},
                         {"label": "Körper (Woche)", "type": "withings_daily"},
                         {"label": "Körper (Monat)", "type": "withings_daily"},
                         {"label": "Körper (Quartal)", "type": "withings_daily"},
                         {"label": "Körper (Jahr)", "type": "withings_daily"}]       
                   },
          'heart': {
              'cards' : [{'name': 'withings_cardio', 'type': 'app'}],
              'items' : [{"label": "Herz (gestern)", "type": "withings_cardio"},
                         {"label": "Herz (Woche)", "type": "withings_cardio"},
                         {"label": "Herz (Monat)", "type": "withings_cardio"},
                         {"label": "Herz (Quartal)", "type": "withings_cardio"},
                         {"label": "Herz (Jahr)", "type": "withings_cardio"}]       
                   }
         }


CARDS = {'withings_base': [
            {"gewicht": {"source": "withings.body.gewicht"},
             "fett_anteil": {"source": "withings.body.fett_anteil"},
             "muskeln": {"source": "withings.body.muskeln"},
             "wasser": {"source": "withings.body.wasser"},
             "knochen": {"source": "withings.body.knochen"}},
            {'gewicht_month': {"source": "withings.weight_trend.gewicht_month"},
             'gewicht_quartal': {"source": "withings.weight_trend.gewicht_quartal"},
             'gewicht_year': {"source": "withings.weight_trend.gewicht_year"}},
            {'diastole': {"source": "withings.heart.diastole"},
             'systole': {"source": "withings.heart.systole"},
             'gefaess_alter': {"source": "withings.heart.gefaess_alter"},
             'puls': {'source': 'withings.heart.puls'},
             'puls_wellen_elasitzitaet': {'source': 'withings.heart.puls_wellen_elasitzitaet'}},
            {'body_temp': {"source": "withings.temperatur.body_temp"},
             'skin_temp': {"source": "withings.temperatur.skin_temp"}}],
         'withings_daily': [
            {'steps': {'source': 'withings.sum_m.steps', 'label': 'Schritte', 'params': {'hist': True}}, 
             'activ_intense' : {'source': 'withings.sum_m.intense', 'label': 'Aktiv (hoch)', 'unit': 'h'},
             'activ_moderate' : {'source': 'withings.sum_m.moderate', 'label': 'Aktiv (mittlere)', 'unit': 'h'},
             'activ_soft' : {'source': 'withings.sum_m.soft', 'label': 'Aktiv (leicht)', 'unit': 'h', 'params': {'hist': True}},
             'activecalories' : {'source': 'withings.sum_m.calories', 'label': 'Kalorien (aktiv)', 'unit': 'kcal'},
             'totalcalories' : {'source': 'withings.sum_m.totalcalories', 'label': 'Kalorien (gesamt)', 'unit': 'kcal', 'params': {'hist': True}},
             'distance' : {'source': 'withings.sum_m.distance', 'label': 'Strecke', 'unit': 'km'}},
            {'steps': {'source': 'withings.sum_m.steps_w', 'label': 'Schritte'}, 
             'activ_intense' : {'source': 'withings.sum_m.intense_w', 'label': 'Aktiv (hoch)', 'unit': 'h'},
             'activ_moderate' : {'source': 'withings.sum_m.moderate_w', 'label': 'Aktiv (mittlere)', 'unit': 'h'},
             'activ_soft' : {'source': 'withings.sum_m.soft_w', 'label': 'Aktiv (leicht)', 'unit': 'h'},
             'activecalories' : {'source': 'withings.sum_m.calories_w', 'label': 'Kalorien (aktiv)', 'unit': 'kcal'},
             'totalcalories' : {'source': 'withings.sum_m.totalcalories_w', 'label': 'Kalorien (gesamt)', 'unit': 'kcal'},
             'distance' : {'source': 'withings.sum_m.distance_w', 'label': 'Strecke', 'unit': 'km'}},
            {'steps': {'source': 'withings.sum_m.steps_m', 'label': 'Schritte'}, 
             'activ_intense' : {'source': 'withings.sum_m.intense_m', 'label': 'Aktiv (hoch)', 'unit': 'h'},
             'activ_moderate' : {'source': 'withings.sum_m.moderate_m', 'label': 'Aktiv (mittlere)', 'unit': 'h'},
             'activ_soft' : {'source': 'withings.sum_m.soft_m', 'label': 'Aktiv (leicht)', 'unit': 'h'},
             'activecalories' : {'source': 'withings.sum_m.calories_m', 'label': 'Kalorien (aktiv)', 'unit': 'kcal'},
             'totalcalories' : {'source': 'withings.sum_m.totalcalories_m', 'label': 'Kalorien (gesamt)', 'unit': 'kcal'},
             'distance' : {'source': 'withings.sum_m.distance_m', 'label': 'Strecke', 'unit': 'km'}},
            {'steps': {'source': 'withings.sum_m.steps_q', 'label': 'Schritte'}, 
             'activ_intense' : {'source': 'withings.sum_m.intense_q', 'label': 'Aktiv (hoch)', 'unit': 'h'},
             'activ_moderate' : {'source': 'withings.sum_m.moderate_q', 'label': 'Aktiv (mittlere)', 'unit': 'h'},
             'activ_soft' : {'source': 'withings.sum_m.soft_q', 'label': 'Aktiv (leicht)', 'unit': 'h'},
             'activecalories' : {'source': 'withings.sum_m.calories_q', 'label': 'Kalorien (aktiv)', 'unit': 'kcal'},
             'totalcalories' : {'source': 'withings.sum_m.totalcalories_q', 'label': 'Kalorien (gesamt)', 'unit': 'kcal'},
             'distance' : {'source': 'withings.sum_m.distance_q', 'label': 'Strecke', 'unit': 'km'}},
            {'steps': {'source': 'withings.sum_m.steps_y', 'label': 'Schritte'}, 
             'activ_intense' : {'source': 'withings.sum_m.intense_y', 'label': 'Aktiv (hoch)', 'unit': 'h'},
             'activ_moderate' : {'source': 'withings.sum_m.moderate_y', 'label': 'Aktiv (mittlere)', 'unit': 'h'},
             'activ_soft' : {'source': 'withings.sum_m.soft_y', 'label': 'Aktiv (leicht)', 'unit': 'h'},
             'activecalories' : {'source': 'withings.sum_m.calories_y', 'label': 'Kalorien (aktiv)', 'unit': 'kcal'},
             'totalcalories' : {'source': 'withings.sum_m.totalcalories_y', 'label': 'Kalorien (gesamt)', 'unit': 'kcal'},
             'distance' : {'source': 'withings.sum_m.distance_y', 'label': 'Strecke', 'unit': 'km'}}],
         'withings_heart': [ 
            {'average': {'source': 'withings.heart_d.hr_average', 'label': 'mittlre', 'params': {'hist': True}}, 
             'max' : {'source': 'withings.heart_d.hr_max', 'label': 'max'},
             'min' : {'source': 'withings.heart_d.hr_min', 'label': 'min'},
             'zone0' : {'source': 'withings.heart_d.hr_zone_0', 'label': '0-50% Zone', 'unit': 'h', 'params': {'hist': True}},
             'zone1' : {'source': 'withings.heart_d.hr_zone_1', 'label': '50-70% Zone', 'unit': 'h'},
             'zone2' : {'source': 'withings.heart_d.hr_zone_2', 'label': '70-90% Zone', 'unit': 'h'},
             'zone3' : {'source': 'withings.heart_d.hr_zone_3', 'label': '90-100% Zone', 'unit': 'h'}},
            {'average': {'source': 'withings.heart_d.hr_average_w', 'label': 'mittlre'}, 
             'max' : {'source': 'withings.heart_d.hr_max_w', 'label': 'max'},
             'min' : {'source': 'withings.heart_d.hr_min_w', 'label': 'min'},
             'zone0' : {'source': 'withings.heart_d.hr_zone_0_w', 'label': '0-50% Zone', 'unit': 'h'},
             'zone1' : {'source': 'withings.heart_d.hr_zone_1_w', 'label': '50-70% Zone', 'unit': 'h'},
             'zone2' : {'source': 'withings.heart_d.hr_zone_2_w', 'label': '70-90% Zone', 'unit': 'h'},
             'zone3' : {'source': 'withings.heart_d.hr_zone_3_w', 'label': '90-100% Zone', 'unit': 'h'}},
            {'average': {'source': 'withings.heart_d.hr_average_w', 'label': 'mittlre'}, 
             'max' : {'source': 'withings.heart_d.hr_max_m', 'label': 'max'},
             'min' : {'source': 'withings.heart_d.hr_min_m', 'label': 'min'},
             'zone0' : {'source': 'withings.heart_d.hr_zone_0_m', 'label': '0-50% Zone', 'unit': 'h'},
             'zone1' : {'source': 'withings.heart_d.hr_zone_1_m', 'label': '50-70% Zone', 'unit': 'h'},
             'zone2' : {'source': 'withings.heart_d.hr_zone_2_m', 'label': '70-90% Zone', 'unit': 'h'},
             'zone3' : {'source': 'withings.heart_d.hr_zone_3_m', 'label': '90-100% Zone', 'unit': 'h'}},
            {'average': {'source': 'withings.heart_d.hr_average_q', 'label': 'mittlre'}, 
             'max' : {'source': 'withings.heart_d.hr_max_q', 'label': 'max'},
             'min' : {'source': 'withings.heart_d.hr_min_q', 'label': 'min'},
             'zone0' : {'source': 'withings.heart_d.hr_zone_0_q', 'label': '0-50% Zone', 'unit': 'h'},
             'zone1' : {'source': 'withings.heart_d.hr_zone_1_q', 'label': '50-70% Zone', 'unit': 'h'},
             'zone2' : {'source': 'withings.heart_d.hr_zone_2_q', 'label': '70-90% Zone', 'unit': 'h'},
             'zone3' : {'source': 'withings.heart_d.hr_zone_3_q', 'label': '90-100% Zone', 'unit': 'h'}},
            {'average': {'source': 'withings.heart_d.hr_average_y', 'label': 'mittlre'}, 
             'max' : {'source': 'withings.heart_d.hr_max_y', 'label': 'max'},
             'min' : {'source': 'withings.heart_d.hr_min_y', 'label': 'min'},
             'zone0' : {'source': 'withings.heart_d.hr_zone_0_y', 'label': '0-50% Zone', 'unit': 'h'},
             'zone1' : {'source': 'withings.heart_d.hr_zone_1_y', 'label': '50-70% Zone', 'unit': 'h'},
             'zone2' : {'source': 'withings.heart_d.hr_zone_2_y', 'label': '70-90% Zone', 'unit': 'h'},
             'zone3' : {'source': 'withings.heart_d.hr_zone_3_y', 'label': '90-100% Zone', 'unit': 'h'}}]
         }

#"average", "max", "min", "zone0", "zone1", "zone2", "zone3"

# {average: {value: 75, source: "withings.heart_d.hr_average_d", params: []},…}
# average
# : 
# {value: 75, source: "withings.heart_d.hr_average_d", params: []}
# max
# : 
# {value: 140, source: "withings.heart_d.hr_max_d", params: []}
# min
# : 
# {value: 35, source: "withings.heart_d.hr_min_d", params: []}
# zone0
# : 
# {value: 9.97888888888889, source: "withings.heart_d.hr_zone_0_d", params: []}
# zone1
# : 
# {value: 4.296666666666667, source: "withings.heart_d.hr_zone_1_d", params: []}
# zone2
# : 
# {value: 1.0191666666666668, source: "withings.heart_d.hr_zone_2_d", params: []}
# zone3
# : 
# {value: 0, source: "withings.heart_d.hr_zone_3_d", params: []}

HISTORY = {'withings_base': {
               'withings.body.gewicht' : {"label": "Gewicht", "intervalls": "A,Y,Q,M", "style": "line", "interval": "M"},
               'withings.heart.puls' : {"label": "Herzfequenz", "intervalls": "A,Y,Q,M", "style": "line", "interval": "M"},
               'withings.heart.systole' : {"label": "Blutdruck", "intervalls": "A,Y,Q,M", "style": "line", "interval": "M"},
               'withings.heart.puls_wellen_elasitzitaet' : {"label": "Pulswellengeschwindikeit", "intervalls": "A,Y,Q,M", "style": "line", "interval": "M"},
               'withings.heart.gefaess_alter' : {"label": "Gefässalter", "intervalls": "A,Y,Q,M", "style": "line", "interval": "M"},
               'withings.temperatur.body_temp' : {"label": "Gefässalter", "intervalls": "A,Y,Q,M", "style": "line", "interval": "M"}
          },
           'withings_daily': {
               'withings.sum_m.steps' : {"label": "Schritte", "intervalls": "A,Y,Q,M", "style": "line", "interval": "M"},
               'withings.sum_m.soft' : {"label": "Aktivität", "intervalls": "A,Y,Q,M", "style": "line_stack", "interval": "M"},
               'withings.sum_m.totalcalories' : {"label": "Kalorien", "intervalls": "A,Y,Q,M", "style": "line", "interval": "M"}
          },
           'withings_heart': {
               'withings.heart_d.hr_average' : {"label": "Herzfrequenz", "intervalls": "A,Y,Q,M", "style": "line", "interval": "M"},
               'withings.heart_d.hr_zone_0' : {"label": "Herzfrequenz Zonen", "intervalls": "A,Y,Q,M", "style": "line", "interval": "M"}
          }} 
           

HISTORY_DATA = {'withings.body.gewicht': [{'label': 'Gewicht',
                                           'decimal': 2}],
                'withings.heart.puls': [{'label': 'Herzfrequenz',
                                         'decimal': 0}],
                'withings.heart.systole': [{'label': 'Systole',
                                            'decimal': 0},
                                           {'label': 'Diastole',
                                            'decimal': 0,
                                            'source': 'withings.heart.diastole'}],
                'withings.heart.puls_wellen_elasitzitaet': [{'label': 'Pulswellengeschwindikeit',
                                                             'decimal': 2}],
                'withings.heart.gefaess_alter': [{'label': 'Gefässalter',
                                                  'decimal': 1}],
                'withings.temperatur.body_temp': [{'label': 'Temperatur',
                                                  'decimal': 1}],
                'withings.sum_m.steps': [{'label': 'Schritte',
                                          'decimal': 0}],
                'withings.sum_m.soft': [{'label': 'intensiv',
                                         'source': 'withings.sum_m.intense',
                                         'decimal': 1},
                                        {'label': 'mittel',
                                         'source': 'withings.sum_m.moderate',
                                         'decimal': 1},
                                        {'label': 'leicht',
                                         'decimal': 1}],
                'withings.sum_m.totalcalories': [{'label': 'gesamt',
                                                  'decimal': 0},
                                                 {'label': 'aktiv',
                                                  'decimal': 0,
                                                  'source': 'withings.sum_m.totalcalories'}],
                'withings.heart_d.hr_average' : [{'label': 'max',
                                                  'decimal': 0,
                                                  'source': 'withings.heart_d.hr_max'},
                                                 {'label': 'mittlre',
                                                  'decimal': 0},
                                                 {'label': 'min',
                                                  'decimal': 0,
                                                  'source': 'withings.heart_d.hr_min'}],
                'withings.heart_d.hr_zone_0' : [{'label': '0 - 50%',
                                                  'decimal': 2,
                                                  'factor' : 1/3600},
                                                 {'label': '50% - 70%',
                                                  'decimal': 2,
                                                  'factor' : 1/3600,
                                                  'source': 'withings.heart_d.hr_zone_1'},
                                                 {'label': '70% - 90%',
                                                  'decimal': 2,
                                                  'factor' : 1/3600,
                                                  'source': 'withings.heart_d.hr_zone_2'},
                                                 {'label': '90% - 100%',
                                                  'decimal': 2,
                                                  'factor' : 1/3600,
                                                  'source': 'withings.heart_d.hr_zone_3'}]}

class Api(BaseObj):
    def __init__(self, core: Core) -> None:
        BaseObj.__init__(self, core)
        self._state = ''
        self._auth = aioauth.Client(self.core)
                
    async def handler(self, request: web.Request, rd: HttpRequestData) -> bool:
        #prüfen ob einträge für allgemeine auth handler ist
        self.core.log.critical('v2')
        self.core.log.critical(rd)
        auth_resp = await self._auth.handler(request, rd)
        if auth_resp[0]:
            return auth_resp
        #call für dieses Modul
        match '/'.join(rd.path):
            case 'get_allowed_moduls':
                try:
                    rd = HttpMsgData.model_validate(rd.data)
                    rd = HttpRequestData.model_validate(rd.data)
                except:
                    pass
                data = Moduls()
                if rd.open_id and ('withings' in rd.open_id['app'].split(' ') or rd.open_id['app'] == '*'):
                    data.append({'mod': 'withings_base', 'src': '/withings/js/mod/withings_base'})
                    data.append({'mod': 'withings_daily', 'src': '/withings/js/mod/withings_daily'})
                    data.append({'mod': 'withings_heart', 'src': '/withings/js/mod/withings_heart'})
                if rd.open_id and ('withings_sec' in rd.open_id['app'].split(' ') or rd.open_id['app'] == '*'):
                    data.append({'mod': 'withings_setup', 'src': '/withings/js/mod/withings_setup'})
                return (True, web.json_response(data.model_dump()))
            case 'sm/get_cards':
                bc = rd.data.data
                if bc['open_id'] and ('withings' in bc['open_id']['app'].split(' ') or bc['open_id']['app'] == '*'):
                    data = json.loads(bc['data'])
                    return (True, web.json_response(SendOk(data=PANELS[data['panel']]).model_dump()))
            case 'sm/cards_source':
                bc = rd.data.data
                if bc['open_id'] and ('withings' in bc['open_id']['app'].split(' ') or bc['open_id']['app'] == '*'):
                    data = json.loads(bc['data'])
                    out = {}
                    for item in data['items']:
                        panel = CARDS.get(data['panel'], [])
                        self.core.log.critical(panel) 
                        if _item := panel[data['card']].get(item):
                            value = await self.core.cache.get_value(_item['source'])
                            if value is not None:
                                out[item] = _item.copy()
                                out[item]['value'] = value
#                                             'source': _item['source'],
#                                             'params': _item.get('params', [])} 
                    return (True, web.json_response(SendOk(data=out).model_dump()))
            case 'sm/history_chart':
                bc = rd.data.data
                if bc['open_id'] and ('withings' in bc['open_id']['app'].split(' ') or bc['open_id']['app'] == '*'):
                    data = json.loads(bc['data'])
                    if h_data := HISTORY.get(data['panel'], {}).get(data['sensor']):
                        h_data['sensor'] = data['sensor']
                        return (True, web.json_response(SendOk(data=h_data).model_dump()))
                    return (True, web.json_response(SendOk(ok=False).model_dump()))
            case 'sm/history_chart_data':
                bc = rd.data.data
                if bc['open_id'] and ('withings' in bc['open_id']['app'].split(' ') or bc['open_id']['app'] == '*'):
                    data = json.loads(bc['data'])
                    out = []
                    for rec in HISTORY_DATA[data['sensor']]:
                        rec_out = HistoryFullOut(label= rec['label'], decimal= rec['decimal'], factor = rec.get('factor', 1),
                                                 data= await self.core.cache.get_history(rec.get('source', data['sensor']), data['interval']))
                        out.append(rec_out)
                return (True, web.json_response(SendOk(data=out).model_dump()))
            case 'setup/get_url':
                self.core.log.debug('Ask for url')
                bc = rd.data.data
                url = ''
                if bc['open_id'] and ('withings_sec' in bc['open_id']['app'].split(' ') or bc['open_id']['app'] == '*'):
                    with open("/lcars/config/secret.toml", "rb") as f:
                        config = tomllib.load(f).get('withings', {})
                        url = "https://account.withings.com/oauth2_user/authorize2?response_type=code&client_id="
                        url += f"{config['client']}&scope=user.info,user.metrics,user.activity&redirect_uri="
                        url += urllib.parse.quote_plus(config['callback'])
                        self._state = str(int(time.time()))
                        url += f"&state={self._state}"
                    return (True, web.json_response(SendOk(data={'url': url}).model_dump()))
                else:
                    return (True, web.json_response(SendOk(ok=False).model_dump()))
            case _:
                self.core.log.critical('/'.join(rd.path))
                
    async def receive_code(self, code, state):
        if self._state == state:
            async with aiohttp.ClientSession() as session:
                with open("/lcars/config/secret.toml", "rb") as f:
                    config = tomllib.load(f).get('withings', {})
                response = await session.post(url="https://wbsapi.withings.net/v2/oauth2",
                                              data={"action": "requesttoken",
                                              	    "grant_type": "authorization_code",
	                                                "client_id": config['client'],
                                                    "client_secret": config['secret'],
	                                                "code": code,
	                                                "redirect_uri": config['callback']},
                                              headers={"Content-Type": "application/json"})
                data = await response.json()
                data = data['body']
                await self.core.web_l.msg_send(HttpMsgData(dest='withings', 
                                                           type='set_token', 
                                                           data={'refresh_token': data['refresh_token'],
                                                                 'token': data['access_token'],
                                                                 'timeout': int(time.time() + data['expires_in'] - 900)}))
                
    async def add_scopes(self):
        self.core.log.debug('scopes aktualiesieren')
        await self.core.call_random(12*3600 , self.add_scopes) #
        await self.core.web_l.msg_send(HttpMsgData(dest='web_auth', type='set_scopes', data=['withings', 'withings_sec']))
        
    async def _ainit(self):
        self.core.log.debug('Initaliesiere api')
        await self.core.web.add_handler(HttpHandler(domain = 'api', func = self.handler, auth='remote', acl=None))
        
    async def _astart(self):
        self.core.log.debug('starte api')
        await self.core.call_random(30, self.add_scopes)

# [
#     {
#         "label": "Gewicht",
#         "decimal": 2,
#         "data": [
#             {
#                 "value": 87.418,
#                 "date": 1730009445
#             },
#             {
#                 "value": 87.435,
#                 "date": 1730091258
#             },
#             {
#                 "value": 86.083,
#                 "date": 1730167034
#             },
#             {
#                 "value": 85.862,
#                 "date": 1730250611
#             },
#             {
#                 "value": 86.467,
#                 "date": 1730333031
#             },
#             {
#                 "value": 86.227,
#                 "date": 1730444085
#             },
#             {
#                 "value": 86.721,
#                 "date": 1730504801
#             },
#             {
#                 "value": 86.721,
#                 "date": 1730504801
#             },
#             {
#                 "value": 85.59,
#                 "date": 1730789575
#             },
#             {
#                 "value": 86.711,
#                 "date": 1730860030
#             },
#             {
#                 "value": 86.044,
#                 "date": 1730963675
#             },
#             {
#                 "value": 85.81,
#                 "date": 1731038933
#             },
#             {
#                 "value": 86.427,
#                 "date": 1731132596
#             },
#             {
#                 "value": 87.303,
#                 "date": 1731223595
#             },
#             {
#                 "value": 86.95100000000001,
#                 "date": 1731302120
#             },
#             {
#                 "value": 87.761,
#                 "date": 1731374700
#             },
#             {
#                 "value": 87.239,
#                 "date": 1731475634
#             },
#             {
#                 "value": 85.78,
#                 "date": 1731568746
#             },
#             {
#                 "value": 85.381,
#                 "date": 1731649482
#             },
#             {
#                 "value": 87.021,
#                 "date": 1731729899
#             },
#             {
#                 "value": 87.34400000000001,
#                 "date": 1731821200
#             },
#             {
#                 "value": 86.55,
#                 "date": 1731914823
#             },
#             {
#                 "value": 86.671,
#                 "date": 1731997961
#             },
#             {
#                 "value": 86.812,
#                 "date": 1732073816
#             },
#             {
#                 "value": 86.654,
#                 "date": 1732173125
#             },
#             {
#                 "value": 87.014,
#                 "date": 1732266005
#             },
#             {
#                 "value": 87.003,
#                 "date": 1732350934
#             },
#             {
#                 "value": 86.95,
#                 "date": 1732438482
#             }
#         ]
#     }
# ]