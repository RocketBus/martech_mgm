import logging
# Import WebClient from Python SDK (github.com/slackapi/python-slack-sdk)
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from datetime import datetime
from app.config.settings import environment_secrets



class SlackAlerts:
    oauthToken = environment_secrets['SLACK_OAUTH_TOKEN']
    # WebClient instantiates a client that can call API methods
    # When using Bolt, you can use either `app.client` or the `client` passed to listeners.
    client = WebClient(token=oauthToken)
    logger = logging.getLogger(__name__)

    async def alert_msg(self,msg : str, channel_id : str, app : str):
        try:
            # Call the conversations.list method using the WebClient
            result = self.client.chat_postMessage(
                channel=channel_id,
                text=f"""
                        :warning: *{app}*
                        \n<!here> {msg}
                        \n*Data*: {datetime.now().strftime("%d/%m/%y %H:%M:%S")}
                        """
                # You could also use a blocks[] array to send richer content
            )
            # Print result, which includes information about the message (like TS)
            return result

        except SlackApiError as e:
            print(f"Error: {e}")