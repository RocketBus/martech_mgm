from app.config.settings import environment_secrets,ENVIRONMENT_LOCAL
from app.src.slack.slack import SlackAlerts
from fastapi import HTTPException, status, Request
import asyncio

class MemberGetMemberException(Exception):
    def __init__(self, message:str,request:Request=False,status_code:int=status.HTTP_500_INTERNAL_SERVER_ERROR,notify_slack:bool=False):
        super().__init__(message)
        self.slack = SlackAlerts()
        self.message = message
        self.status_code = status_code
        self.request = request
        self.notify_slack = notify_slack
        self.main()
        
    def main(self):
        # if self.notify_slack:
        #     endpoint = str(self.request.url)
        #     if self.request:
        #         msg = f"\n:house: *Ambiente:* ( {ENVIRONMENT_LOCAL} )\n:motorway: *Endpoint:* ( {endpoint} )\n:construction: *Erro:* ( {self.message} )"
        #     else:
        #         msg = self.message
            
        #     self.slack.alert_msg(
        #         msg=msg,
        #         channel_id=environment_secrets['MARTECH_ALERT_CHANNEL_ID'],
        #         app="Member get member"
        #     )
        raise HTTPException(
            status_code=self.status_code,
            detail=self.message
        )

class MemberAlreadyExists(MemberGetMemberException):
    def __init__(self,error_message:str, request:Request=False, notify_slack:bool=False):
        super().__init__(
            message=error_message,
            request=request,
            status_code=status.HTTP_400_BAD_REQUEST,
            notify_slack=notify_slack
        )
        self.duplicated_errors = ['duplicate key', 'unique constraint', 'duplicate entry']
        self.error_message = error_message
        self.notify_slack = notify_slack
        self.additional_code()
    
    def additional_code(self):

        if any(self.error_message.find(keyword) != -1 for keyword in self.duplicated_errors):
            self.message = "Member already exists"
        self.main()
