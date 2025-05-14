from hashids import Hashids
from typing import Optional,List
from app.config.settings import environment_secrets
import asyncio


class AmplitudeHashGenerator:
    SALT_GENERATOR = environment_secrets['SALT_GENERATOR']
    ALPHABET = environment_secrets['ALPHABET']
    
    def __init__(self):
        self.generator = Hashids(salt=environment_secrets['SALT_GENERATOR'], min_length=8, alphabet=self.ALPHABET)


    async def decode(self, hash: Optional[str]) -> Optional[int]:
       return self.sync_decode(hash)
    
    
    def sync_decode(self,hash):
        if not hash or hash.strip() == "":
            return None

        decoded = self.generator.decode(hash)
        if not decoded or len(decoded) != 1:
            return None

        return decoded[0]


    async def encode(self, id) -> Optional[str]:
        hash = self.generator.encode(id)
        return hash

    
    async def async_encode(self,ids:List[int])-> list:
        tasks = [self.encode(id) for id in ids]
        response = await asyncio.gather(*tasks)
        return response