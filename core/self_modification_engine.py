"""
Self-Modification Engine — Recursive Self-Improvement

The ultimate capability: the agent can modify its own source code.

NOT just adding tools. Modifying:
- Decision-making logic
- Reflection algorithms
- Goal generation strategies
- Core behavioral patterns

This is the path to recursive self-improvement → AGI.

Safety measures:
- Versioning (can rollback)
- Testing before applying
- Gradual modification (not wholesale rewrites)
- Critical systems protected
"""

import os
import json
import shutil
import logging
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Optional, List
import importlib
import sys

log = logging.getLogger(__name__)


class ModificationProposal:
    """A proposed change to the agent's code."""
    
    def __init__(
        self,
        target_file: str,
        target_function: str,
        modification_type: str,
        new_code: str,
        rationale: str
    ):
        self.id = hashlib.md5(f"{target_file}{target_function}{datetime.utcnow().isoformat()}".encode()).hexdigest()[:12]
        self.target_file = target_file
        self.target_function = target_function
        self.modification_type = modification_type  # enhance, optimize, fix, refactor
        self.new_code = new_code
        self.rationale = rationale
        self.status = "proposed"  # proposed, tested, applied, rejected, reverted
        self.test_results = None
        self.created_at = datetime.utcnow().isoformat()
        self.applied_at = None
        self.performance_before = None
        self.performance_after = None


class SelfModificationEngine:
    """
    Allows the agent to modify its own source code.
    
    This is DANGEROUS and POWERFUL.
    
    The agent can:
    1. Identify inefficiencies in its own code
    2. Propose improvements
    3. Test modifications safely
    4. Apply successful modifications
    5. Revert if things go wrong
    
    This is recursive self-improvement.
    """
    
    def __init__(self, config: dict = None):
        config = config or {}
        self.base_path = Path(config.get("base_path", "./core"))
        self.backup_path = Path(config.get("backup_path", "./backups"))
        self.modifications_log = Path(config.get("log_path", "./autonomy/modifications.json"))
        
        self.backup_path.mkdir(parents=True, exist_ok=True)
        self.modifications_log.parent.mkdir(parents=True, exist_ok=True)
        
        # Track modifications
        self.proposals: List[ModificationProposal] = []
        self.applied_modifications = []
        self.reverted_modifications = []
        
        # Protected files (cannot be modified without special permission)
        self.protected_files = {
            "self_modification_engine.py",  # Don't modify the modifier!
        }
        
        # Metrics before modification (for comparison)
        self.baseline_metrics = {}
        
        self._load_log()
        log.info("Self-modification engine initialized")
    
    # ══════════════════════════════════════════════════════════
    # MODIFICATION PROPOSAL
    # ══════════════════════════════════════════════════════════
    
    def propose_modification(
        self,
        target_file: str,
        target_function: str,
        modification_type: str,
        new_code: str,
        rationale: str
    ) -> ModificationProposal:
        """
        Agent proposes a modification to its own code.
        
        This is step 1 of self-modification.
        """
        # Safety check
        if target_file in self.protected_files:
            log.warning(f"Cannot modify protected file: {target_file}")
            return None
        
        proposal = ModificationProposal(
            target_file=target_file,
            target_function=target_function,
            modification_type=modification_type,
            new_code=new_code,
            rationale=rationale
        )
        
        self.proposals.append(proposal)
        
        log.info(f"Modification proposed: {target_file}.{target_function} - {rationale[:60]}")
        
        self._save_log()
        return proposal
    
    def identify_improvement_opportunities(self, performance_data: dict) -> List[dict]:
        """
        Agent analyzes its own performance to find improvement opportunities.
        
        This is metacognition applied to code.
        """
        opportunities = []
        
        # Slow operations
        if "slow_operations" in performance_data:
            for op in performance_data["slow_operations"]:
                opportunities.append({
                    "type": "optimize",
                    "target": op["function"],
                    "reason": f"Slow operation: {op['avg_time']:.2f}s avg",
                    "priority": 0.8,
                })
        
        # High failure rate
        if "failure_rates" in performance_data:
            for func, rate in performance_data["failure_rates"].items():
                if rate > 0.3:
                    opportunities.append({
                        "type": "fix",
                        "target": func,
                        "reason": f"High failure rate: {rate:.0%}",
                        "priority": 0.9,
                    })
        
        # Repeated patterns (could be abstracted)
        if "code_duplication" in performance_data:
            for pattern in performance_data["code_duplication"]:
                opportunities.append({
                    "type": "refactor",
                    "target": pattern["locations"],
                    "reason": "Code duplication detected",
                    "priority": 0.5,
                })
        
        return sorted(opportunities, key=lambda x: x["priority"], reverse=True)
    
    # ══════════════════════════════════════════════════════════
    # TESTING & APPLICATION
    # ══════════════════════════════════════════════════════════
    
    def test_modification(self, proposal: ModificationProposal) -> dict:
        """
        Test a proposed modification in isolation.
        
        CRITICAL: Must not break existing functionality.
        """
        log.info(f"Testing modification: {proposal.id}")
        
        # Create backup first
        backup_path = self._backup_file(proposal.target_file)
        
        try:
            # Apply modification temporarily
            target_path = self.base_path / proposal.target_file
            
            if not target_path.exists():
                return {
                    "success": False,
                    "error": "Target file not found",
                }
            
            # Read current code
            original_code = target_path.read_text()
            
            # Apply modification (simple replace for now)
            # In production: use AST manipulation
            modified_code = self._apply_code_change(
                original_code,
                proposal.target_function,
                proposal.new_code
            )
            
            # Write temporarily
            temp_path = target_path.with_suffix('.py.test')
            temp_path.write_text(modified_code)
            
            # Try to import and test
            test_result = self._test_modified_code(temp_path, proposal)
            
            # Clean up
            temp_path.unlink()
            
            proposal.test_results = test_result
            proposal.status = "tested"
            
            self._save_log()
            
            return test_result
        
        except Exception as e:
            log.error(f"Test failed: {e}")
            return {
                "success": False,
                "error": str(e),
            }
    
    def apply_modification(self, proposal: ModificationProposal) -> bool:
        """
        Apply a tested modification to the live code.
        
        This is the moment of self-modification.
        """
        if proposal.status != "tested":
            log.warning("Cannot apply untested modification")
            return False
        
        if not proposal.test_results or not proposal.test_results.get("success"):
            log.warning("Cannot apply failed modification")
            return False
        
        log.info(f"Applying modification: {proposal.id}")
        
        try:
            # Backup current version
            backup_path = self._backup_file(proposal.target_file)
            
            # Apply modification
            target_path = self.base_path / proposal.target_file
            original_code = target_path.read_text()
            
            modified_code = self._apply_code_change(
                original_code,
                proposal.target_function,
                proposal.new_code
            )
            
            # Write new version
            target_path.write_text(modified_code)
            
            # Reload module
            self._reload_module(proposal.target_file)
            
            proposal.status = "applied"
            proposal.applied_at = datetime.utcnow().isoformat()
            
            self.applied_modifications.append(proposal)
            
            log.info(f"✓ Self-modification applied: {proposal.target_file}.{proposal.target_function}")
            
            self._save_log()
            
            return True
        
        except Exception as e:
            log.error(f"Application failed: {e}")
            # Restore backup
            self._restore_backup(proposal.target_file, backup_path)
            return False
    
    def revert_modification(self, proposal: ModificationProposal) -> bool:
        """
        Rollback a modification if it causes problems.
        """
        log.info(f"Reverting modification: {proposal.id}")
        
        # Find most recent backup
        backups = list(self.backup_path.glob(f"{proposal.target_file}_*.backup"))
        if not backups:
            log.error("No backup found")
            return False
        
        latest_backup = max(backups, key=lambda p: p.stat().st_mtime)
        
        # Restore
        target_path = self.base_path / proposal.target_file
        shutil.copy(latest_backup, target_path)
        
        # Reload
        self._reload_module(proposal.target_file)
        
        proposal.status = "reverted"
        self.reverted_modifications.append(proposal)
        
        log.info(f"✓ Modification reverted: {proposal.id}")
        
        self._save_log()
        
        return True
    
    # ══════════════════════════════════════════════════════════
    # METRICS & EVALUATION
    # ══════════════════════════════════════════════════════════
    
    def capture_baseline_metrics(self, agent) -> dict:
        """
        Capture performance before modification.
        """
        metrics = {
            "confidence": agent.self_model.self_assessment.get("confidence", 0.5),
            "success_rate": self._compute_success_rate(agent),
            "avg_satisfaction": self._compute_avg_satisfaction(agent),
            "timestamp": datetime.utcnow().isoformat(),
        }
        
        self.baseline_metrics = metrics
        return metrics
    
    def evaluate_modification_impact(self, agent, proposal: ModificationProposal) -> dict:
        """
        Compare performance before and after modification.
        """
        current_metrics = {
            "confidence": agent.self_model.self_assessment.get("confidence", 0.5),
            "success_rate": self._compute_success_rate(agent),
            "avg_satisfaction": self._compute_avg_satisfaction(agent),
        }
        
        baseline = self.baseline_metrics
        
        impact = {
            "confidence_delta": current_metrics["confidence"] - baseline.get("confidence", 0.5),
            "success_rate_delta": current_metrics["success_rate"] - baseline.get("success_rate", 0.5),
            "satisfaction_delta": current_metrics["avg_satisfaction"] - baseline.get("avg_satisfaction", 0.5),
        }
        
        # Overall assessment
        if all(v > 0 for v in impact.values()):
            impact["overall"] = "improvement"
        elif any(v < -0.1 for v in impact.values()):
            impact["overall"] = "regression"
        else:
            impact["overall"] = "neutral"
        
        proposal.performance_before = baseline
        proposal.performance_after = current_metrics
        
        self._save_log()
        
        return impact
    
    # ══════════════════════════════════════════════════════════
    # INTERNAL HELPERS
    # ══════════════════════════════════════════════════════════
    
    def _backup_file(self, filename: str) -> Path:
        """Create timestamped backup."""
        source = self.base_path / filename
        if not source.exists():
            return None
        
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        backup_name = f"{filename}_{timestamp}.backup"
        backup_path = self.backup_path / backup_name
        
        shutil.copy(source, backup_path)
        
        return backup_path
    
    def _restore_backup(self, filename: str, backup_path: Path):
        """Restore from backup."""
        target = self.base_path / filename
        shutil.copy(backup_path, target)
    
    def _apply_code_change(self, original_code: str, target_function: str, new_code: str) -> str:
        """
        Apply code modification.
        
        In production: use AST manipulation for safety.
        Here: simple string replacement for demo.
        """
        # Find function definition
        import re
        pattern = rf"def {target_function}\(.*?\):(.*?)(?=\n(?:def |class |\Z))"
        
        # Replace with new code
        modified = re.sub(
            pattern,
            f"def {target_function}({new_code}",
            original_code,
            flags=re.DOTALL
        )
        
        return modified
    
    def _test_modified_code(self, temp_path: Path, proposal: ModificationProposal) -> dict:
        """
        Test modified code.
        
        Run basic checks: syntax, imports, basic functionality.
        """
        try:
            # Syntax check
            import py_compile
            py_compile.compile(str(temp_path), doraise=True)
            
            # Try to import
            spec = importlib.util.spec_from_file_location("test_module", temp_path)
            test_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(test_module)
            
            # Basic functionality check
            # (In production: run unit tests)
            
            return {
                "success": True,
                "syntax_ok": True,
                "import_ok": True,
            }
        
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
            }
    
    def _reload_module(self, filename: str):
        """Reload a modified module."""
        module_name = filename.replace(".py", "").replace("/", ".")
        if module_name in sys.modules:
            importlib.reload(sys.modules[module_name])
    
    def _compute_success_rate(self, agent) -> float:
        """Compute recent success rate."""
        # Simplified
        return agent.self_model.self_assessment.get("confidence", 0.5)
    
    def _compute_avg_satisfaction(self, agent) -> float:
        """Compute average satisfaction."""
        return agent.self_model.self_assessment.get("happiness", 0.5)
    
    def _save_log(self):
        """Persist modification log."""
        log_data = {
            "proposals": [
                {
                    "id": p.id,
                    "target_file": p.target_file,
                    "target_function": p.target_function,
                    "modification_type": p.modification_type,
                    "rationale": p.rationale,
                    "status": p.status,
                    "created_at": p.created_at,
                    "applied_at": p.applied_at,
                    "test_results": p.test_results,
                }
                for p in self.proposals
            ],
            "applied_count": len(self.applied_modifications),
            "reverted_count": len(self.reverted_modifications),
            "last_updated": datetime.utcnow().isoformat(),
        }
        
        self.modifications_log.write_text(json.dumps(log_data, indent=2))
    
    def _load_log(self):
        """Load modification history."""
        if not self.modifications_log.exists():
            return
        
        try:
            data = json.loads(self.modifications_log.read_text())
            # Reconstruct proposals (simplified)
            # In production: full reconstruction
        except Exception as e:
            log.warning(f"Failed to load modification log: {e}")
    
    def get_modification_history(self) -> dict:
        """Summary of self-modifications."""
        return {
            "total_proposals": len(self.proposals),
            "applied": len(self.applied_modifications),
            "reverted": len(self.reverted_modifications),
            "success_rate": len(self.applied_modifications) / max(1, len(self.proposals)),
            "recent_modifications": [
                {
                    "target": f"{p.target_file}.{p.target_function}",
                    "type": p.modification_type,
                    "rationale": p.rationale[:60],
                    "status": p.status,
                }
                for p in self.proposals[-5:]
            ]
        }
