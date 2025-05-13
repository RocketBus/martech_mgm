import requests
import json
from datetime import datetime, timedelta
from fastapi import HTTPException, status

class Phoenix:
    def __init__(self) -> None:
        self.base_url = 'https://api.clickbus.com/api/v3'
    
    def get_url(self,url:str)->str:
        return self.base_url + url
    

class Orders(Phoenix):
    def __init__(self) -> None:
        super().__init__()
        self.status_accepted = [
            'completed',
            'partially canceled'
        ]
        self.departure_status = 'departure_type'
        self.item_type = 'ticket'
    
    async def get_order(self,order_id:str,client_id:int = 1):
        url = self.get_url(
            url=f'/order/{order_id}'
        )
        params = {"clientId": client_id}
        headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.0.0 Safari/537.36",
            
        }
        return requests.get(url=url,params=params,headers=headers)
    
    async def status_order_is_valid(self,order_response:dict)->bool:
        order_status = order_response['status']
        return order_status in self.status_accepted
    
    async def get_departure_date(self, order_response: dict):
        itemDetails = [
            item.get('itemDetails',[]) 
            for item in order_response.get('itemsDetails', []) 
            if item['type']==self.item_type
        ]
        departures = [
            item.get('departure',[]).get('schedule') 
            for item in itemDetails if item['tripType'] == self.departure_status
        ]
        return await self.adjust_departure_time(
            departure_time=departures[0]
        )

    async def adjust_departure_time(self,departure_time: dict):
        # Constrói o datetime com a data e hora fornecidas
        dt_str = f"{departure_time['date']} {departure_time['time']}"
        dt = datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S")
        
        # Subtrai 3 horas
        adjusted_dt = dt - timedelta(hours=3)
        
        return adjusted_dt

    async def cancellation_settings(self,itemsDetails):
        for items in itemsDetails:
            if items['type'] == 'fine':
                results = {}
                results['maximumDiscountValue'] = round(float(items['amount']),2)
                results['periodEnd'] = datetime.strptime(items['createdAt'], '%Y-%m-%d %H:%M:%S')
                return results
            else:
                continue
            # ordemId out of the parameters
        return False