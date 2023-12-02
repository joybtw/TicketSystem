import json
from discord import Member
from config import Config as cfg


def has_perm(member: Member, perm: str):
    with open("permissions.json", "r", encoding="utf-8") as file:
        perms = json.load(file)
    for role in member.roles: 
        role_id = role.id
        if role_id != cfg.EVERYONE:
            try: 
                role_perms = perms[str(role_id)]
                
                for permission in role_perms: 
                    if permission == "command.command": 
                        print(role.name)
                        return True
                    elif permission == f"command.{perm}": 
                        print(role.name)
                        return True
            except Exception as e: 
                pass
    return False