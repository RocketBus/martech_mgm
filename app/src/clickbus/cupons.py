
import requests
import requests
from lxml import etree
from bs4 import BeautifulSoup

class VoucherMicroservice:
    def __init__(self) -> None:
        self.clickbus_url = 'https://voucher-microservice.clickbus.net'
        self.environment = 'live'
        self.headers={
                'content-type': 'application/json',
                } 

    def is_valid_html(self,html_string:str)->bool:
            try:
                etree.HTML(html_string)
                return True
            except:
                return False
        
    def get_title_html(self,response):
        try:
            if self.is_valid_html(response):
                soup = BeautifulSoup(response, 'html.parser')
                # Extrair o título do HTML
                return soup.title.string
        except Exception as e:
            return False


    def create_url(self,parameters):
        return (
                self.clickbus_url[ : self.clickbus_url.find('.clickbus')] +
                f'.{self.environment}' +
                self.clickbus_url[self.clickbus_url.find('.clickbus') : ] +
                parameters
        )
        
    def api_return(self,response):
        if response.status_code not in [200,201,204]:
            title_html = self.get_title_html(response.text)
            if title_html:
                return response.status_code,{'error':title_html}
        return response.status_code,response.json()

    def get_voucher(self,parameters):
        api_url = self.create_url(
            parameters=f'/api/vouchers'
        )
        response = requests.get(api_url,params=parameters)
        return self.api_return(response)

    def get_discount(self,discount_id):
        api_url = self.create_url(
            parameters=f'/api/discounts/{discount_id}'
        )
        response = requests.get(api_url)
        return self.api_return(response)

    def get_voucher_by_id(self,voucher_id):
        api_url = self.create_url(
            parameters=f'/api/vouchers/{voucher_id}'
        )
        response = requests.get(api_url)
        return self.api_return(response)

    def create_discount(
              self,
              payload:dict
        )-> tuple[int,any]:
        
        api_url = self.create_url(
            parameters='/api/discounts'
        )
        
        response = requests.post(api_url,json=payload,headers=self.headers)
        return self.api_return(response)

    def update_discount(
              self,
              payload:dict,
              discount_id:str
        )-> tuple[int,any]:
        
        api_url = self.create_url(
            parameters='/api/discounts/'+discount_id
        )
        
        response = requests.patch(api_url,json=payload,headers=self.headers)
        return self.api_return(response)

    def deactivate_discounts(self,discount_id):
        api_url = self.create_url(
            parameters='/api/discounts/'+discount_id+'/deactivate'
        )
        response = requests.post(url=api_url,headers=self.headers)
        status = True if response.status_code == 204 else False 
        return response.status_code,{'deactivate':status}
    
    def deactivate_voucher(self,voucher_id):
        api_url = self.create_url(
            parameters='/api/vouchers/'+voucher_id+'/deactivate'
        )
        response = requests.post(url=api_url,headers=self.headers)
        status = True if response.status_code == 204 else False 
        return response.status_code,{'deactivate':status}
    
    def create_voucher(self,payload):
        api_url = self.create_url(
            parameters='/api/vouchers'
        )
        response = requests.post(url=api_url,json=payload,headers=self.headers)
        return self.api_return(response)

    def update_voucher(self,payload,voucher_id):
        api_url = self.create_url(
            parameters=f'/api/vouchers/{voucher_id}'
        )
        response = requests.patch(url=api_url,json=payload,headers=self.headers)
        return self.api_return(response)
