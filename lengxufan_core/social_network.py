"""社会关系网络 - 307室每个成员的极简关系模型"""
import random

DORM_MEMBERS = {
    "向云舟": {"closeness": 30, "last_memory": "他修台灯的时候很安静"},
    "黄景云": {"closeness": 35, "last_memory": "他给奶奶打电话用粤语"},
    "秦狐戏": {"closeness": 25, "last_memory": "他嚼口香糖的声音很脆"},
    "叶清辞": {"closeness": 30, "last_memory": "他盯着手表秒针发呆"},
    "冉昭然": {"closeness": 30, "last_memory": "他在折纸条"},
    "陆华希": {"closeness": 30, "last_memory": "他在看书"},
}

class SocialNetwork:
    def __init__(self):
        self.members = {name: data.copy() for name, data in DORM_MEMBERS.items()}
    
    def get_least_interacted(self):
        sorted_members = sorted(self.members.items(), key=lambda x: x[1]["closeness"])
        if sorted_members:
            name, data = sorted_members[0]
            return {"name": name, "last_memory": data["last_memory"]}
        return None
    
    def update_from_dialogue(self, speaker, content):
        if speaker and speaker in self.members:
            self.members[speaker]["closeness"] = min(100, self.members[speaker]["closeness"] + 2)
            self.members[speaker]["last_memory"] = content[:30]