from typing import Dict, List

pending_stats = []
approved_stats = []

# Example stat: {"game_id": 1, "stat": {...}, "submitted_by": user_id, "approved": False}

def submit_stat(stat: Dict):
    stat["approved"] = False
    pending_stats.append(stat)
    return True

def approve_stat(stat_idx: int):
    if 0 <= stat_idx < len(pending_stats):
        stat = pending_stats.pop(stat_idx)
        stat["approved"] = True
        approved_stats.append(stat)
        return True
    return False

def reject_stat(stat_idx: int):
    if 0 <= stat_idx < len(pending_stats):
        pending_stats.pop(stat_idx)
        return True
    return False

def get_pending_stats() -> List[Dict]:
    return pending_stats 