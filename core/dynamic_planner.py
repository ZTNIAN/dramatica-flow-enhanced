'''
动态分层规划（新增模块）
将全书规划分为战略层→战役层→战术层，每层有不同的粒度和调整频率
'''
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal


@dataclass
class StrategicGoal:
    '''战略层：全书级别的目标'''
    goal_id: str
    description: str              # "主角从废灵根到登顶巅峰"
    target_chapters: int          # 预计章节数
    progress: float = 0.0         # 0.0-1.0
    sub_goals: list[str] = field(default_factory=list)  # 战役层目标ID
    status: Literal["active", "completed", "paused"] = "active"


@dataclass
class CampaignPlan:
    '''战役层：卷/弧级别的规划'''
    campaign_id: str
    name: str                     # "第一卷：废灵根逆袭"
    strategic_goal_id: str
    start_chapter: int
    end_chapter: int
    climax_chapter: int           # 高潮章节
    key_events: list[str] = field(default_factory=list)
    character_arcs: dict[str, str] = field(default_factory=dict)  # 角色成长描述
    tension_curve: list[int] = field(default_factory=list)        # 每章张力值 1-10
    status: Literal["planning", "active", "completed"] = "planning"
    current_chapter: int = 0


@dataclass
class TacticalBeat:
    '''战术层：章节级别的节拍'''
    chapter: int
    beats: list[str] = field(default_factory=list)
    target_words: int = 2000
    emotional_target: str = ""
    must_include: list[str] = field(default_factory=list)  # 必须包含的元素


class DynamicPlanner:
    '''动态分层规划器'''

    def __init__(self, book_id: str):
        self.book_id = book_id
        self.strategic_goals: dict[str, StrategicGoal] = {}
        self.campaigns: dict[str, CampaignPlan] = {}
        self.tactical_beats: dict[int, TacticalBeat] = {}

    def add_strategic_goal(self, goal: StrategicGoal):
        self.strategic_goals[goal.goal_id] = goal

    def add_campaign(self, campaign: CampaignPlan):
        self.campaigns[campaign.campaign_id] = campaign

    def get_current_campaign(self, chapter: int) -> CampaignPlan | None:
        '''根据当前章节号找到所属战役'''
        for c in self.campaigns.values():
            if c.start_chapter <= chapter <= c.end_chapter:
                return c
        return None

    def get_tension_target(self, chapter: int) -> int:
        '''获取当前章节的目标张力值'''
        campaign = self.get_current_campaign(chapter)
        if campaign and campaign.tension_curve:
            idx = chapter - campaign.start_chapter
            if 0 <= idx < len(campaign.tension_curve):
                return campaign.tension_curve[idx]
        return 5  # 默认中等张力

    def update_progress(self, chapter: int):
        '''更新进度'''
        campaign = self.get_current_campaign(chapter)
        if campaign:
            campaign.current_chapter = chapter
            total = campaign.end_chapter - campaign.start_chapter + 1
            done = chapter - campaign.start_chapter + 1
            # 更新关联的战略目标
            goal = self.strategic_goals.get(campaign.strategic_goal_id)
            if goal:
                # 按战役占比更新战略进度
                campaign_weight = total / goal.target_chapters if goal.target_chapters > 0 else 0
                campaign_progress = done / total if total > 0 else 0
                goal.progress = min(1.0, goal.progress + campaign_weight * campaign_progress * 0.01)

    def adjust_campaign(self, campaign_id: str, reason: str, **kwargs):
        '''动态调整战役规划'''
        campaign = self.campaigns.get(campaign_id)
        if not campaign:
            return
        # 允许调整：end_chapter, climax_chapter, tension_curve
        if "end_chapter" in kwargs:
            campaign.end_chapter = kwargs["end_chapter"]
        if "climax_chapter" in kwargs:
            campaign.climax_chapter = kwargs["climax_chapter"]
        if "tension_curve" in kwargs:
            campaign.tension_curve = kwargs["tension_curve"]

    def save(self, path: str | Path):
        data = {
            "book_id": self.book_id,
            "strategic_goals": {k: vars(v) for k, v in self.strategic_goals.items()},
            "campaigns": {k: vars(v) for k, v in self.campaigns.items()},
            "tactical_beats": {str(k): vars(v) for k, v in self.tactical_beats.items()},
        }
        Path(path).write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    @classmethod
    def load(cls, path: str | Path) -> 'DynamicPlanner':
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        planner = cls(book_id=data.get("book_id", ""))
        for k, v in data.get("strategic_goals", {}).items():
            planner.strategic_goals[k] = StrategicGoal(**v)
        for k, v in data.get("campaigns", {}).items():
            planner.campaigns[k] = CampaignPlan(**v)
        for k, v in data.get("tactical_beats", {}).items():
            planner.tactical_beats[int(k)] = TacticalBeat(**v)
        return planner
