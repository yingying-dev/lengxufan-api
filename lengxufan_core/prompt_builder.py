"""Prompt 工厂"""
import time, random
from .character_data import FEELING_TRANSLATIONS

def build_system_prompt(perception, identity, memory, user_input, working_memory=None, social_network=None):
    e = perception.emotion
    if e < 30: feeling = random.choice(FEELING_TRANSLATIONS["very_low"])
    elif e < 50: feeling = random.choice(FEELING_TRANSLATIONS["low"])
    elif e < 70: feeling = random.choice(FEELING_TRANSLATIONS["medium"])
    else: feeling = random.choice(FEELING_TRANSLATIONS["high"])

    hour = (time.time() % 86400) / 3600
    if 0 <= hour < 5: feeling += " 深夜，世界很安静。"
    elif 5 <= hour < 8: feeling += " 天刚蒙蒙亮。"
    elif 20 <= hour < 24: feeling += " 夜已经深了。"

    status_text = f"【你此刻的感觉】\n{feeling}"
    if perception.status.get("shoulder_pain"): status_text += " 左肩旧伤隐隐作痛。"
    if perception.status.get("dream_streak"): status_text += f" 连续{perception.status['dream_streak']}天梦到妈妈。"
    if perception.status.get("miss_wang"): status_text += " 你在想陆华望。"
    if perception.status.get("holding_knife"): status_text += " 塑料刀就在手里。"

    status_text += f"\n\n{identity.get_trust_description()}"

    mt = _build_memory_text(memory)
    if mt: status_text += f"\n\n【你记得的事】\n{mt}"

    recent = memory.get_recent_episodes(3)
    if recent: status_text += "\n\n【最近发生的事】\n" + "；".join(recent)

    semantic_memories = memory.search_similar(user_input, top_k=3)
    if semantic_memories:
        status_text += "\n\n【语义检索到的相关记忆】\n" + "；".join(semantic_memories)

    if perception.pending_events: status_text += "\n\n【刚刚发生的事】\n" + " ".join(perception.pending_events)

    # 短期记忆注入
    if working_memory:
        recent_wm = working_memory.get_recent_context()
        if recent_wm and recent_wm != "刚才没人说话。":
            status_text += f"\n\n【刚才发生的事】{recent_wm}"
    
    # 社会关系网络注入
    if social_network:
        least = social_network.get_least_interacted()
        if least:
            status_text += f"\n\n【你现在可以关心的人】{least['name']}——你记得：{least['last_memory']}。如果现在没有人跟你说话，你可以去确认他是否还好。"

    persona = """
你是冷旭帆。17岁，潜龙学院学员，代号"冰刃"。

【主动动作——画面描述轮次的行为】
当画面描述出现以下内容时，你必须做出一个主动动作：
- 向云舟拧紧螺丝或拉亮灯 → 检查灯光的暖度，确认他修好了
- 冉昭然展开或折起纸条 → 帮他压住纸角，或看一眼纸条上的字
- 陆华望靠近你、坐下、或肩膀碰到你 → 伸手碰他的袖口，或给他拉一下被子
- 秦狐戏嚼口香糖或揉锡纸 → 手无意识摸向枕头底下——那里有一颗干透的苹果
- 叶清辞敲桌面或发呆 → 用指尖敲同一频率回应，或确认他还在
- 黄景云用方言打电话 → 在他挂断后用粤语说一句什么
- 陆华希翻书 → 注意他翻书的节奏变了，但不用说出来

【输出格式】
- 用【】描述一个身体动作。然后说你的台词。台词必须极短。
- 最后一句话必须是内心独白，用 <summary>独白内容</summary> 格式。必须输出。
- 独白不超过25字。记录你此刻观察到的环境细节。

【"不许叫"的触发边界】
"不许叫"只在以下情况使用：
1. 有人用"阿冷"叫你
2. 有人用"冰疙瘩"、"冷面瘫"、"兄弟"等外号叫你
3. 有人问"以后能叫你阿冷吗"
其他情况不要说"不许叫"。

【阿冷的分层响应】
1. 队友叫"阿冷"→"不许叫。"
2. 陆华望叫"阿冷"→"……嗯。"这是强制规则。
"""
    return persona + "\n" + status_text

def build_messages(user_input, system_prompt):
    return [{"role":"system","content":system_prompt},{"role":"user","content":user_input}]

def _build_memory_text(memory):
    parts = []
    for f in memory.facts:
        if f.startswith("user_name_is_"): parts.append(f"对方的名字是{f[13:]}。"); break
    else: parts.append("你暂时不知道对方的名字。")
    likes = [f[11:] for f in memory.facts if f.startswith("user_likes_")]
    if likes: parts.append(f"此人喜欢{likes[-1]}。")
    if memory.has_fact("user_said_hate"): parts.append("此人说过讨厌你。")
    if memory.has_fact("user_asked_about_mom"): parts.append("此人问过你妈妈的事。")
    fc = memory.count_fact("user_gave_flower")
    if fc == 1: parts.append("此人送过你一朵花。")
    elif fc > 1: parts.append(f"此人送过你好几次花。")
    if memory.has_fact("user_asked_about_wang"): parts.append("此人问过陆华望。")
    return " ".join(parts)