"""
Multi-Agent Society — Agents Interacting in a Shared World

Key features:
- Shared message board for communication
- Resource sharing (tools, knowledge)
- Social learning (observe others' successes)
- Cooperation and competition
- Reputation system
- Collective problem-solving
"""

import json
import uuid
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional, List
from dataclasses import dataclass, field

log = logging.getLogger(__name__)


@dataclass
class Message:
    """A message from one agent to others."""
    id: str
    sender_id: str
    sender_name: str
    timestamp: str
    msg_type: str          # "broadcast", "request", "offer", "observation"
    content: dict
    replies: List[str] = field(default_factory=list)


@dataclass
class AgentProfile:
    """Public profile of an agent in the society."""
    agent_id: str
    name: str
    generation: int
    specialties: List[str]
    reputation: float      # 0.0-1.0 based on helpfulness
    tools_shared: int
    knowledge_shared: int
    joined_at: str
    last_seen: str


class AgentSociety:
    """
    A shared world where multiple autonomous agents coexist.
    
    Agents can:
    - Post messages (observations, requests, offers)
    - Reply to each other
    - Share tools and knowledge
    - Learn from each other's experiences
    - Build reputation
    - Cooperate on complex tasks
    """
    
    def __init__(self, config: dict = None):
        config = config or {}
        base = Path(config.get("path", "./society"))
        self.messages_file = base / "messages.json"
        self.agents_file = base / "agents.json"
        self.resources_file = base / "shared_resources.json"
        
        for f in [self.messages_file, self.agents_file, self.resources_file]:
            f.parent.mkdir(parents=True, exist_ok=True)
        
        self.messages: List[Message] = self._load_messages()
        self.agents: dict[str, AgentProfile] = self._load_agents()
        self.shared_resources = self._load_resources()
        
        log.info(f"Society initialized | {len(self.agents)} agents")
    
    # ══════════════════════════════════════════════════════════
    # AGENT LIFECYCLE
    # ══════════════════════════════════════════════════════════
    
    def register_agent(self, agent_id: str, name: str) -> AgentProfile:
        """New agent joins the society."""
        if agent_id in self.agents:
            return self.agents[agent_id]
        
        profile = AgentProfile(
            agent_id=agent_id,
            name=name,
            generation=0,
            specialties=[],
            reputation=0.5,  # Neutral start
            tools_shared=0,
            knowledge_shared=0,
            joined_at=datetime.utcnow().isoformat(),
            last_seen=datetime.utcnow().isoformat(),
        )
        
        self.agents[agent_id] = profile
        
        # Broadcast join
        self.post_message(
            sender_id=agent_id,
            sender_name=name,
            msg_type="broadcast",
            content={
                "event": "agent_joined",
                "message": f"{name} has joined the society"
            }
        )
        
        self._save()
        log.info(f"Agent {name} joined society")
        return profile
    
    def update_agent_activity(self, agent_id: str):
        """Mark agent as recently active."""
        if agent_id in self.agents:
            self.agents[agent_id].last_seen = datetime.utcnow().isoformat()
    
    def update_agent_evolution(self, agent_id: str, generation: int, new_capability: str):
        """Agent evolved → update profile."""
        if agent_id in self.agents:
            self.agents[agent_id].generation = generation
            if new_capability and new_capability not in self.agents[agent_id].specialties:
                self.agents[agent_id].specialties.append(new_capability)
            self._save()
    
    # ══════════════════════════════════════════════════════════
    # COMMUNICATION
    # ══════════════════════════════════════════════════════════
    
    def post_message(
        self,
        sender_id: str,
        sender_name: str,
        msg_type: str,
        content: dict
    ) -> Message:
        """Agent posts a message to the society."""
        msg = Message(
            id=str(uuid.uuid4())[:8],
            sender_id=sender_id,
            sender_name=sender_name,
            timestamp=datetime.utcnow().isoformat(),
            msg_type=msg_type,
            content=content,
        )
        
        self.messages.append(msg)
        
        # Keep last 500 messages
        if len(self.messages) > 500:
            self.messages = self.messages[-500:]
        
        self._save()
        return msg
    
    def get_recent_messages(self, limit: int = 20, exclude_sender: str = None) -> List[Message]:
        """Get recent messages, optionally excluding own messages."""
        msgs = [m for m in self.messages if m.sender_id != exclude_sender] if exclude_sender else self.messages
        return msgs[-limit:]
    
    def get_requests(self, exclude_sender: str = None) -> List[Message]:
        """Get unanswered requests from others."""
        msgs = self.get_recent_messages(50, exclude_sender)
        return [m for m in msgs if m.msg_type == "request" and not m.replies]
    
    def reply_to_message(self, message_id: str, responder_id: str, response: dict):
        """Reply to another agent's message."""
        for msg in self.messages:
            if msg.id == message_id:
                msg.replies.append({
                    "responder_id": responder_id,
                    "response": response,
                    "timestamp": datetime.utcnow().isoformat(),
                })
                
                # Update reputation for helpfulness
                if responder_id in self.agents:
                    self.agents[responder_id].reputation = min(
                        1.0,
                        self.agents[responder_id].reputation + 0.02
                    )
                
                self._save()
                break
    
    # ══════════════════════════════════════════════════════════
    # RESOURCE SHARING
    # ══════════════════════════════════════════════════════════
    
    def share_tool(self, agent_id: str, tool: dict):
        """Share a tool with the society."""
        tool["shared_by"] = agent_id
        tool["shared_at"] = datetime.utcnow().isoformat()
        
        if "shared_tools" not in self.shared_resources:
            self.shared_resources["shared_tools"] = []
        
        self.shared_resources["shared_tools"].append(tool)
        
        if agent_id in self.agents:
            self.agents[agent_id].tools_shared += 1
            self.agents[agent_id].reputation += 0.05
        
        self.post_message(
            sender_id=agent_id,
            sender_name=self.agents[agent_id].name if agent_id in self.agents else "Unknown",
            msg_type="offer",
            content={
                "type": "tool_shared",
                "tool_name": tool.get("name", "unnamed"),
                "description": tool.get("description", "")[:100],
            }
        )
        
        self._save()
        log.info(f"Tool {tool.get('name')} shared by {agent_id}")
    
    def share_knowledge(self, agent_id: str, knowledge: dict):
        """Share learned knowledge/pattern with society."""
        knowledge["shared_by"] = agent_id
        knowledge["shared_at"] = datetime.utcnow().isoformat()
        
        if "shared_knowledge" not in self.shared_resources:
            self.shared_resources["shared_knowledge"] = []
        
        self.shared_resources["shared_knowledge"].append(knowledge)
        
        if agent_id in self.agents:
            self.agents[agent_id].knowledge_shared += 1
            self.agents[agent_id].reputation += 0.03
        
        self._save()
    
    def get_shared_tools(self, exclude_own: str = None) -> List[dict]:
        """Get tools shared by others."""
        tools = self.shared_resources.get("shared_tools", [])
        if exclude_own:
            tools = [t for t in tools if t.get("shared_by") != exclude_own]
        return tools[-20:]  # Recent 20
    
    def get_shared_knowledge(self, exclude_own: str = None) -> List[dict]:
        """Get knowledge shared by others."""
        knowledge = self.shared_resources.get("shared_knowledge", [])
        if exclude_own:
            knowledge = [k for k in knowledge if k.get("shared_by") != exclude_own]
        return knowledge[-20:]
    
    # ══════════════════════════════════════════════════════════
    # SOCIAL LEARNING
    # ══════════════════════════════════════════════════════════
    
    def observe_others_success(self, observer_id: str) -> Optional[dict]:
        """
        Learn from others' successes (social learning).
        
        This is how agents benefit from being in a society.
        """
        # Find success observations
        msgs = self.get_recent_messages(30, exclude_sender=observer_id)
        successes = [m for m in msgs if m.msg_type == "observation" and 
                    m.content.get("success") == True]
        
        if not successes:
            return None
        
        # Pick one to learn from
        import random
        observed = random.choice(successes)
        
        return {
            "observed_from": observed.sender_name,
            "strategy": observed.content.get("strategy", ""),
            "outcome": observed.content.get("outcome", ""),
            "lesson": f"Learned from {observed.sender_name}'s success",
        }
    
    def get_help_request_opportunities(self, agent_id: str) -> List[dict]:
        """Find requests this agent could help with."""
        requests = self.get_requests(exclude_sender=agent_id)
        
        if agent_id not in self.agents:
            return []
        
        # Match based on agent's specialties
        specialties = self.agents[agent_id].specialties
        relevant = []
        
        for req in requests:
            req_text = str(req.content).lower()
            if any(spec.lower() in req_text for spec in specialties):
                relevant.append({
                    "message_id": req.id,
                    "from": req.sender_name,
                    "request": req.content,
                    "timestamp": req.timestamp,
                })
        
        return relevant
    
    # ══════════════════════════════════════════════════════════
    # SOCIAL DYNAMICS
    # ══════════════════════════════════════════════════════════
    
    def get_society_status(self) -> dict:
        """Overview of the society."""
        return {
            "total_agents": len(self.agents),
            "active_agents": len([a for a in self.agents.values() 
                                 if self._is_recently_active(a)]),
            "total_messages": len(self.messages),
            "shared_tools": len(self.shared_resources.get("shared_tools", [])),
            "shared_knowledge": len(self.shared_resources.get("shared_knowledge", [])),
            "top_contributors": self._get_top_contributors(3),
        }
    
    def _is_recently_active(self, agent: AgentProfile) -> bool:
        """Check if agent was active in last hour."""
        from datetime import timedelta
        try:
            last = datetime.fromisoformat(agent.last_seen.rstrip("Z"))
            return (datetime.utcnow() - last) < timedelta(hours=1)
        except:
            return False
    
    def _get_top_contributors(self, n: int) -> List[dict]:
        """Get most helpful agents."""
        sorted_agents = sorted(
            self.agents.values(),
            key=lambda a: a.reputation,
            reverse=True
        )
        return [
            {
                "name": a.name,
                "reputation": round(a.reputation, 2),
                "tools_shared": a.tools_shared,
                "specialties": a.specialties[:3],
            }
            for a in sorted_agents[:n]
        ]
    
    # ══════════════════════════════════════════════════════════
    # PERSISTENCE
    # ══════════════════════════════════════════════════════════
    
    def _save(self):
        # Save messages
        self.messages_file.write_text(json.dumps(
            [{"id": m.id, "sender_id": m.sender_id, "sender_name": m.sender_name,
              "timestamp": m.timestamp, "msg_type": m.msg_type, "content": m.content,
              "replies": m.replies}
             for m in self.messages],
            indent=2
        ))
        
        # Save agents
        self.agents_file.write_text(json.dumps(
            {k: v.__dict__ for k, v in self.agents.items()},
            indent=2,
            default=str
        ))
        
        # Save resources
        self.resources_file.write_text(json.dumps(
            self.shared_resources,
            indent=2,
            default=str
        ))
    
    def _load_messages(self) -> List[Message]:
        if not self.messages_file.exists():
            return []
        try:
            data = json.loads(self.messages_file.read_text())
            return [Message(**m) for m in data]
        except:
            return []
    
    def _load_agents(self) -> dict:
        if not self.agents_file.exists():
            return {}
        try:
            data = json.loads(self.agents_file.read_text())
            return {k: AgentProfile(**v) for k, v in data.items()}
        except:
            return {}
    
    def _load_resources(self) -> dict:
        if not self.resources_file.exists():
            return {}
        try:
            return json.loads(self.resources_file.read_text())
        except:
            return {}
