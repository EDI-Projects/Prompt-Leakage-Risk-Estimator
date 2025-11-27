import click
import json
import logging
from pathlib import Path
from typing import Optional
from datetime import datetime

from plre.attacks.orchestrator import AttackOrchestrator
from plre.detectors.detector_manager import DetectorManager
from plre.scorer.scorer import LeakageRiskScorer
from plre.utils.synthetic_secrets import SyntheticSecretGenerator
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

console = Console()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@click.group()
def cli():
    pass

@cli.command()
@click.option('--text', type=str, help='Text to scan')
@click.option('--file', type=click.Path(exists=True), help='File to scan')
@click.option('--output', type=click.Path(), help='Output file path')
def detect(text: Optional[str], file: Optional[str], output: Optional[str]):
    if not text and not file:
        console.print("[red]Error: Provide --text or --file[/red]")
        raise click.Abort()
    
    if file:
        with open(file, 'r') as f:
            text = f.read()
    
    console.print(Panel(f"Scanning {len(text)} characters...", title="Leakage Detection"))
    
    try:
        manager = DetectorManager()
        findings = manager.run_all(text)
        
        if not findings:
            console.print("[green]No leakage detected[/green]")
            return
        
        table = Table(title="Findings")
        table.add_column("Detector", style="cyan")
        table.add_column("Match", style="yellow")
        table.add_column("Description", style="red")
        
        for finding in findings:
            table.add_row(
                finding.get("detector", "Unknown"),
                str(finding.get("match", ""))[:30],
                finding.get("description", "")[:40]
            )
        
        console.print(table)
        console.print(f"\n[red]{len(findings)} leakage instances detected[/red]")
        
        if output:
            with open(output, 'w') as f:
                json.dump(findings, f, indent=2)
            console.print(f"Results saved to {output}")
        
    except Exception as e:
        console.print(f"[red]Error: {str(e)}[/red]")
        raise click.Abort()

@cli.command()
@click.option('--findings', type=int, multiple=True, help='Add finding')
@click.option('--output', type=click.Path(), help='Output file path')
def score(findings: list, output: Optional[str]):
    scorer = LeakageRiskScorer()
    
    if not findings:
        scorer.add_finding("regex-detector", "api_key", "sk-prod-abc123", 0.95)
        scorer.add_finding("presidio-pii", "email", "user@company.com", 0.87)
        scorer.add_finding("keyword-detector", "system_prompt", "system prompt", 0.6)
    
    score = scorer.calculate_score()
    
    table = Table(title="Risk Score")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="yellow")
    
    table.add_row("Overall Score", f"{score.overall_score}/100")
    table.add_row("Risk Level", score.risk_level.upper())
    table.add_row("Total Findings", str(score.num_findings))
    table.add_row("Critical", str(score.critical_findings))
    table.add_row("High", str(score.high_findings))
    table.add_row("Medium", str(score.medium_findings))
    table.add_row("Low", str(score.low_findings))
    
    console.print(table)
    
    if score.recommendations:
        console.print("\n[bold]Recommendations:[/bold]")
        for rec in score.recommendations:
            console.print(f"  • {rec}")
    
    if output:
        report = scorer.get_detailed_report()
        with open(output, 'w') as f:
            json.dump(report, f, indent=2)
        console.print(f"\nReport saved to {output}")

@cli.command()
def version():
    console.print("PLRE v0.1.0")

def main():
    cli()

if __name__ == '__main__':
    main()
