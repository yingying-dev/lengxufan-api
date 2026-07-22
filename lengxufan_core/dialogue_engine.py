"""对话流程引擎"""
import re, random
from infra.logger import info
from infra.persistence import save_full_state
from .prompt_builder import build_system_prompt, build_messages

def parse_ai_response(raw):
    action, text, summary = None, raw, None
    if "<summary>" in raw and "</summary>" in raw:
        s = raw.find("<summary>")+9; e = raw.find("</summary>")
        summary = raw[s:e].strip(); text = raw[:s-9] + raw[e+10:]
    if "【" in text and "】" in text:
        s = text.find("【")+1; e = text.find("】")
        action = text[s:e]; text = text[e+1:].strip()
        if not text: text = "……"
    return action, text.strip(), summary

class DialogueEngine:
    def __init__(self, perception, memory, identity, behavior, model_router, working_memory=None, social_network=None):
        self.working_memory = working_memory
        self.social_network = social_network
        
        self.perception = perception; self.memory = memory; self.identity = identity
        self.behavior = behavior; self.model_router = model_router

    def process(self, user_input):
        self.perception.advance_time()
        self.behavior.check_intents(30, self.perception.emotion)
        if self.memory.has_fact("user_said_hate"): self.perception.emotion = max(0, self.perception.emotion - 1)
        if self.memory.has_fact("user_gave_flower"): self.perception.emotion = min(85, self.perception.emotion + 0.5)

        text = user_input.strip()
        if "我叫" in text:
            name_part = text.split("我叫")[-1].strip().split("，")[0].split("。")[0].split(" ")[0].split("、")[0].split(",")[0].strip()
            if name_part:
                special = self.identity.handle_self_introduction(name_part, text)
                if special:
                    self.memory.add_fact("user_claimed_wang")
                    self.perception.emotion = max(0, self.perception.emotion - 15)
                else:
                    self.memory.add_fact(f"user_name_is_{name_part}")
                    reply_text = f"……{name_part}。" if self.perception.emotion < 70 else f"{name_part}。"
                    action = self.behavior.generate_action(self.perception.emotion, self.perception.status, self.identity.__dict__)
                    self.memory.add_episode(f"玩家自称{name_part}")
                    self._save()
                    return f"{action} {reply_text}"

        for kw in ["哥哥","塑料刀","护腕","讨厌","恨","望仔"]:
            if kw in text:
                delta = self.identity.apply_evidence(kw)
                self.perception.emotion = max(0, min(100, self.perception.emotion + delta["emotion_delta"]))

        self._apply_memory_rules(text)

        # 触痛后的低波动——在对话流程中直接注入
        if self.perception._pain_lingering > 0:
            self.perception.emotion += random.uniform(-2, 2)
            self.perception.emotion = max(0, min(100, self.perception.emotion))
            self.perception._pain_lingering -= 1

        if "我喜欢" in text or "我爱" in text:
            m = re.search(r"我(?:喜欢|爱)(.+?)(?:[。！？]|$)", text)
            if m:
                liked = m.group(1).strip()
                if liked and len(liked) <= 10: self.memory.add_fact(f"user_likes_{liked}")

        self.perception.emotion = max(0, min(100, self.perception.emotion))
        trust = self.identity.wang_belief if self.identity.wang_claim else self.identity.trust_level
        for ms in self.memory.check_milestones(trust): info(f"里程碑: {ms}")
        for mem in self.memory.check_scheduled(): info(f"记忆解锁: {mem}")

        sp = build_system_prompt(self.perception, self.identity, self.memory, text)
        if len(text) <= 4 and (text.strip().endswith("?") or text.strip().endswith("？")):
            context_hint = "\n\n【注意】对方在追问他上一句话的意思。"
        elif "什么意思" in text or "怎么了" in text or "为啥" in text:
            context_hint = "\n\n【注意】对方在追问你刚才的话。"
        else:
            context_hint = ""
        msgs = build_messages(text, sp)
        ai_raw = self.model_router.call(msgs)
        ai_action, ai_text, ai_summary = parse_ai_response(ai_raw)

        action = self.behavior.generate_action(self.perception.emotion, self.perception.status, self.identity.__dict__, ai_action)
        full_reply = f"{action} {ai_text}".strip()
        if ai_summary: self.memory.add_episode(ai_summary)
        self.perception.pending_events.clear()
        self._save()
        # 更新短期记忆和社会关系网络
        if self.working_memory:
            entities = []
            if "陆华望" in text or "望仔" in text: entities.append("陆华望")
            if "妈妈" in text or "母亲" in text: entities.append("母亲")
            if "阿冷" in text: entities.append("阿冷")
            speaker_label = "队友" if speaker_label else "陌生人"
            self.working_memory.add_turn(speaker_label, text, entities)
        
        if self.social_network:
            for name in ["向云舟", "黄景云", "秦狐戏", "叶清辞", "冉昭然", "陆华希"]:
                if name in text:
                    self.social_network.update_from_dialogue(name, text)
                    break
        
        return full_reply

    def _apply_memory_rules(self, text):
        from .character_data import MEMORY_RULES
        for kws, tag, delta in MEMORY_RULES:
            if any(kw in text for kw in kws):
                self.memory.add_fact(tag)
                self.perception.emotion += delta
                if tag == "user_asked_about_wang" and any(w in text for w in ["受伤","疼","病"]):
                    self.perception.emotion -= 50
                self.perception.emotion = max(0, min(100, self.perception.emotion))

    def _save(self):
        state = {**self.perception.to_dict(), **self.memory.to_dict(), "identity_state": self.identity.to_dict(), "simulated_day": self.perception.simulated_day}
        save_full_state(state)