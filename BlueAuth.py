from atproto_client import Client


# stolen from https://github.com/MarshalX/atproto/discussions/167#discussioncomment-8579573
class RateLimitedClient(Client):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        
        self._limit = self._remaining = self._reset = None
    
    def get_rate_limit(self):
        return self._limit, self._remaining, self._reset
    
    def _invoke(self, *args, **kwargs):
        response = super()._invoke(*args, **kwargs)
        
        self._limit = response.headers.get('ratelimit-limit')
        self._remaining = response.headers.get('ratelimit-remaining')
        self._reset = response.headers.get('ratelimit-reset')
        
        return response


def Login(APU, AP):
    client = RateLimitedClient()
    client.login(login=APU, password=AP)
    return client
