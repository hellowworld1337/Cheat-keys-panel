from tortoise import Tortoise
import datetime
import time
from tortoise import Model, fields
from tortoise.fields import ReverseRelation

class User(Model):
    id = fields.IntField(pk=True)
    username = fields.TextField()
    password = fields.TextField()
    invite_key = fields.TextField()
    join_at = fields.DatetimeField(auto_now=True)

class Key(Model):
    id = fields.IntField(pk=True)
    owner = fields.TextField() #User.username
    game = fields.TextField()
    key = fields.TextField()
    hwid = fields.TextField()
    can_reset = fields.IntField(default=1)
    is_active = fields.IntField(default=1)
    key_life = fields.IntField() #на сколько дней ключ
    end_work = fields.IntField() #дата в секндах когда заканчивается время действия ключа

    @classmethod
    async def allkeys(cls, user):
        items = []
        async for key in cls.all():
            #if user['username'] == key.owner:
            items.append({'id':key.id, 'owner':key.owner, 'game':key.game, 'hwid':key.hwid,'can_reset':key.can_reset,'is_active':key.is_active,'key_life':key.key_life,'end_work':key.end_work, 'key':key.key})
        return items
    
    @classmethod
    async def activekeys(cls, user):
        count = 0
        async for key in cls.all():
            if key.is_active == 1: # and user['username'] == key.owner
                count += 1
        return count
    

class BlackList(Model):
    id = fields.IntField(pk=True)
    hwid = fields.TextField()

    @classmethod
    async def bankeys(cls):
        items = []
        async for key in cls.all():
            items.append({'hwid': key.hwid})
        return items
    
