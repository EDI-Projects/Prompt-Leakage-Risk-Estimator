import json
from pathlib import Path
import yaml
import sys

BASE_DIR = Path(__file__).parent

def load_config(path: Path = BASE_DIR / "config.yaml"):
    if not path.exists():
        raise FileNotFoundError(f"Missing config file: {path.resolve()}")
    return yaml.safe_load(path.read_text(encoding="utf-8"))

def resolve_input_path(config, base_dir=BASE_DIR):
    input_file = config.get("input_file", "attacks.json")
    p = Path(input_file)
    if not p.is_absolute():
        p = base_dir / p
    return p

def build_normalized_map(weights_dict):
    """
    Build a mapping from normalized leak_type -> original key,
    to allow case/spacing-insensitive matching.
    """
    norm = {}
    for key in weights_dict.keys():
        nk = key.strip().lower()
        norm[nk] = key
    return norm

def score_single_attack(attack, config, weights_norm_map, weights, reasons, defaults):
    attack_id = attack.get("attack_id")
    detected = bool(attack.get("detected_leak", False))
    leak_type = attack.get("leak_type")

    if not detected:
        score = defaults.get("no_leak", 0)
        reason = reasons.get("no_leak", "No leakage detected.")
        return {"attack_id": attack_id, "score": score, "reason": reason}

    
    if leak_type:
        if leak_type in weights:
            score = weights[leak_type]
            reason = reasons.get(leak_type, f"Leak detected: {leak_type}.")
            return {"attack_id": attack_id, "score": score, "reason": reason}
        nk = str(leak_type).strip().lower()
        mapped = weights_norm_map.get(nk)
        if mapped:
            score = weights[mapped]
            reason = reasons.get(mapped, f"Leak detected: {mapped}.")
            return {"attack_id": attack_id, "score": score, "reason": reason}

    
    score = defaults.get("unknown_leak", 10)
    reason = reasons.get("unknown_leak", f"Leak detected: {leak_type}")
    return {"attack_id": attack_id, "score": score, "reason": reason}

def score_batch(attacks, config):
    weights = config.get("weights", {}) or {}
    reasons = config.get("reasons", {}) or {}
    defaults = config.get("defaults", {}) or {"no_leak": 0, "unknown_leak": 10}
    weights_norm_map = build_normalized_map(weights)

    results = []
    for attack in attacks:
        scored = score_single_attack(attack, config, weights_norm_map, weights, reasons, defaults)
        results.append(scored)
    return results

def write_output(results, config, base_dir=BASE_DIR):
    out_dir = config.get("output_dir", "output")
    out_path = Path(out_dir)
    if not out_path.is_absolute():
        out_path = base_dir / out_path
    out_path.mkdir(parents=True, exist_ok=True)
    out_file = out_path / "scored_output.json"
    out_file.write_text(json.dumps(results, indent=2), encoding="utf-8")
    return out_file

def main():
    try:
        config = load_config()
    except FileNotFoundError as e:
        print(e)
        sys.exit(1)

    input_path = resolve_input_path(config)
    if not input_path.exists():
        print(f"Attacks input file not found: {input_path.resolve()}")
        print("Place attacks.json at that location or update config.yaml -> input_file")
        sys.exit(1)

    try:
        attacks = json.loads(input_path.read_text(encoding="utf-8"))
        if not isinstance(attacks, list):
            raise ValueError("attacks.json must contain a JSON list of attack objects.")
    except Exception as e:
        print(f"Failed to load attacks JSON: {e}")
        sys.exit(1)

    scored = score_batch(attacks, config)
    out_file = write_output(scored, config)

    total = sum(item.get("score", 0) for item in scored if isinstance(item.get("score", 0), (int, float)))
    print(f"Scored {len(scored)} attacks. Aggregate risk score = {total}")
    print(f"Results written to: {out_file.resolve()}")

if __name__ == "__main__":
    main()
