
import click
import subprocess
import sys
import ai
import threading
import itertools
import time

@click.group()
def cli():
    pass

@cli.command()
@click.argument('script')
def run(script):
    """
    Run a Python script and, if an error occurs, send the traceback to OpenAI for structured analysis.
    """
    result = subprocess.run(
        [sys.executable, script],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    if result.returncode != 0:
        error_output = result.stderr
        click.secho("🚨 ERROR FOUND", fg="red", bold=True)
        click.echo("----------------------------------")
        click.echo(error_output)
        click.secho("\nAI Structured Error Analysis:", fg="cyan", bold=True)
        debugger = ai.AIDebugger()
        # Loading spinner while waiting for AI response
        done = False

        def spinner():
            for c in itertools.cycle(['|', '/', '-', '\\']):
                if done:
                    break
                sys.stdout.write(f'\r🤖 AI analyzing... {c}')
                sys.stdout.flush()
                time.sleep(0.1)
            sys.stdout.write('\r' + ' ' * 30 + '\r')

        spinner_thread = threading.Thread(target=spinner)
        spinner_thread.start()

        # Get AI response as a string (not streaming)
        ai_response = debugger.analyze_traceback(error_output, stream=False)
        done = True
        spinner_thread.join()

        # Parse and print in color
        def print_colored_ai_response(response):
            import re
            lines = response.splitlines()
            for line in lines:
                if re.match(r"^\d+\. \*\*Error Name\*\*:", line):
                    click.secho(line, fg="magenta", bold=True)
                elif "**Error Line**:" in line:
                    click.secho(line, fg="yellow")
                elif "**Error Description**:" in line:
                    click.secho(line, fg="red")
                elif "**Error Fix**:" in line:
                    click.secho(line, fg="green", bold=True)
                elif line.strip().startswith("```"):
                    click.secho(line, fg="blue")
                else:
                    click.echo(line)

        print_colored_ai_response(ai_response)
        click.secho("\n✅ AI analysis complete.", fg="cyan", bold=True)
    else:
        click.secho("✅ Script ran successfully!", fg="green")
        click.echo(result.stdout)

if __name__ == '__main__':
    cli()
