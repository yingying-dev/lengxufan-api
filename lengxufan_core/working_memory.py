"""短期记忆缓冲区 - 动态窗口版本"""
from collections import deque

class WorkingMemory:
    def __init__(self):
        self.recent_turns = deque(maxlen=3)
    
    def add_turn(self, speaker, content, mentioned_entities=None):
        self.recent_turns.append({
            "speaker": speaker,
            "content": content[:50],
            "entities": mentioned_entities or []
        })
    
    def adjust_window(self, reply_length):
        if reply_length > 10:
            new_maxlen = 5
        elif reply_length < 3:
            new_maxlen = 2
        else:
            new_maxlen = 3
        if new_maxlen != self.recent_turns.maxlen:
            old_turns = list(self.recent_turns)
            self.recent_turns = deque(old_turns, maxlen=new_maxlen)
    
    def get_recent_context(self):
        if not self.recent_turns:
            return "刚才没人说话。"
        lines = []
        for turn in self.recent_turns:
            speaker = turn["speaker"] or "有人"
            content = turn["content"]
            entities = "、".join(turn["entities"]) if turn["entities"] else ""
            if entities:
                lines.append(speaker + "说:" + content + "，提到了" + entities)
            else:
                lines.append(speaker + "说:" + content)
        return "；".join(lines)