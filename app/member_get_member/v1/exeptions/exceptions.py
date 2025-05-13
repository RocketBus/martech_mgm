from app.config.settings import environment_secrets,ENVIRONMENT_LOCAL
from app.services.slack.slack import SlackAlerts
from fastapi import HTTPException, status, Request
import asyncio

class MemberGetMemberException(Exception):
    def __init__(self, message:str,request:Request=False):
        super().__init__(message)
        self.slack = SlackAlerts()
        self.message = message
        self.request = request
        self.main()

    async def execute_additional_code(self):
        endpoint = str(self.request.url)
        if self.request:
           msg = f"\n:house: *Ambiente:* ( {ENVIRONMENT_LOCAL} )\n:motorway: *Endpoint:* ( {endpoint} )\n:construction: *Erro:* ( {self.message} )"
        else:
            msg = self.message
        
        await self.slack.alert_msg(
            msg=msg,
            channel_id=environment_secrets['MARTECH_ALERT_CHANNEL_ID'],
            app="Member get member"
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=self.message
        )

    def main(self):
        # Executa a corrotina em segundo plano
        asyncio.create_task(self.execute_additional_code())

class MemberGetMemberUserDoesExists(HTTPException):
    def __init__(self, status_code, detail = None, headers = None):
        super().__init__(status_code, detail, headers)

class MemberGetMemberInvitedExist(HTTPException):
    def __init__(self, status_code, detail = None, headers = None):
        super().__init__(status_code, detail, headers)