"""记忆模块"""
import time
import chromadb
from dataclasses import dataclass, field
from .character_data import AUTOBIOGRAPHICAL_MEMORIES, SCHEDULED_MEMORIES, RELATIONSHIP_MILESTONES

@dataclass
class Memory:
    facts: list = field(default_factory=list)
    episodic: list = field(default_factory=list)
    autobiographical: list = field(default_factory=list)
    relationship_milestones: list = field(default_factory=list)
    scheduled_memories: list = field(default_factory=list)
    simulated_day: int = 1

    def __post_init__(self):
        self.autobiographical = [m.copy() for m in AUTOBIOGRAPHICAL_MEMORIES]
        self.scheduled_memories = [m.copy() for m in SCHEDULED_MEMORIES]
        self.relationship_milestones = [m.copy() for m in RELATIONSHIP_MILESTONES]
        self._init_vector_store()

    def add_fact(self, f):
        if f not in self.facts: self.facts.append(f)
    def has_fact(self, f): return f in self.facts
    def count_fact(self, f): return self.facts.count(f)
    # def add_episode(self, summary, tags=None):
    #     self.episodic.append({"summary":summary,"timestamp":time.time(),"tags":tags or []})
    #     if len(self.episodic) > 50: self.episodic = self.episodic[-50:]
    #     episode_id = f"ep_{int(time.time() * 1000)}"
    #     self.add_episode_to_vector(episode_id, summary, {"tags": ",".join(tags) if tags else ""})

    def add_episode(self, summary, tags=None):
        if tags is None:
            tags = []
        # 自动标签判断
        auto_tags = self._classify_memory(summary)
        tags = list(set(tags + auto_tags))
        
        self.episodic.append({"summary": summary, "timestamp": time.time(), "tags": tags})
        if len(self.episodic) > 50:
            self.episodic = self.episodic[-50:]
        episode_id = f"ep_{int(time.time() * 1000)}"
        self.add_episode_to_vector(episode_id, summary, {"tags": ",".join(tags)})

    def _classify_memory(self, text):
        """自动给记忆打标签"""
        tags = []
        if any(kw in text for kw in ["我叫", "我是", "我哥", "我姐", "我爸", "我妈", "亲哥", "亲姐"]):
            tags.append("人物关系")
        if any(kw in text for kw in ["喜欢", "讨厌", "爱吃", "最怕", "不喜欢"]):
            tags.append("用户喜好")
        if any(kw in text for kw in ["上次", "那天", "记得", "第一次", "之前"]):
            tags.append("重要事件")
        if any(kw in text for kw in ["今天", "食堂", "天气", "刚才", "这会儿"]):
            tags.append("临时话题")
        if any(kw in text for kw in ["不算", "不是的", "我改", "撤回", "收回"]):
            tags.append("被覆盖")
        if not tags:
            tags.append("一般")
        return tags
    def get_recent_episodes(self, n=3):
        return [e["summary"] for e in self.episodic[-n:]]
    def get_active_autobiographical(self, triggered_keywords=None):
        res = []
        for m in self.autobiographical:
            w = m["base_weight"] * (0.9 ** (m["years_ago"] + self.simulated_day//365))
            if triggered_keywords and set(m.get("trigger_keywords",[])) & set(triggered_keywords): w = m["base_weight"] * 2
            if w > 2.0: res.append(m["event"])
        return res[-5:]
    def check_scheduled(self):
        unlocked = []
        for m in self.scheduled_memories[:]:
            if self.simulated_day >= m["unlock_day"]:
                self.autobiographical.append({"event":m["event"],"base_weight":m["base_weight"],"years_ago":0,"trigger_keywords":m.get("trigger_keywords",[])})
                unlocked.append(m["event"]); self.scheduled_memories.remove(m)
        return unlocked
    def check_milestones(self, trust):
        triggered = []
        for ms in self.relationship_milestones:
            if not ms["triggered"] and trust >= ms["trust"]:
                ms["triggered"] = True; triggered.append(ms["description"])
        return triggered
    def get_relevant_memories(self, user_input, limit=5):
        rel = [e["summary"] for e in reversed(self.episodic) if any(kw in user_input for kw in e.get("tags",[]))]
        return rel[:limit]

    def _init_vector_store(self):
        try:
            self.chroma_client = chromadb.PersistentClient(path="data/chroma_db")
            self.collection = self.chroma_client.get_collection("episodic_memories")
        except Exception:
            self.collection = self.chroma_client.create_collection("episodic_memories")

    def add_episode_to_vector(self, episode_id: str, text: str, metadata: dict = None):
        try:
            self.collection.add(
                documents=[text],
                ids=[episode_id],
                metadatas=[metadata or {}]
            )
        except Exception:
            pass

    def search_similar(self, query: str, top_k: int = 3) -> list:
        try:
            results = self.collection.query(query_texts=[query], n_results=top_k)
            if results and results['documents'] and results['documents'][0]:
                return results['documents'][0]
        except Exception:
            pass
        return []

    def to_dict(self):
        return {"facts":self.facts,"episodic":self.episodic,"relationship_milestones":self.relationship_milestones,"scheduled_memories":self.scheduled_memories}
    @classmethod
    def from_dict(cls, d, simulated_day=1):
        m = cls(simulated_day=simulated_day)
        m.facts = d.get("facts",[]); m.episodic = d.get("episodic",[])
        if d.get("relationship_milestones"): m.relationship_milestones = d["relationship_milestones"]
        if d.get("scheduled_memories"): m.scheduled_memories = d["scheduled_memories"]
        return m