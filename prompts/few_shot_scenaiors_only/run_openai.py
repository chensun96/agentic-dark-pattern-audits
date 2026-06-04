import asyncio
from dotenv import load_dotenv
load_dotenv()
import shutil
from browser_use import BrowserSession, Agent, BrowserProfile, Controller
from browser_use.llm import ChatOpenAI

import os
from datetime import datetime
from urllib.parse import urlparse
import json
from string import Template
from pathlib import Path
import pandas as pd
import json, os, traceback
from schema import DarkPatternRunResult 
import shutil, os, glob



class SafeDict(dict):
    def __missing__(self, key):
        return "{" + key + "}"

# --------- CONFIG ---------
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

df = pd.read_csv("broker_dataset/100_annotated_brokers.csv")
URLS = df["url"].dropna().tolist()
ROOT_OUT_DIR = "agent_output"
MODEL = "gpt-5" 
TEMPERATURE = 0
                     
DP_PROMPT_USER_PATH = "prompts/few_shot_scenaiors_only/prompt_regulator_role.txt"
#DP_TAXONOMY_JSON   = "prompts/few_shot_scenaiors_only/sneaking.json"
# --------------------------

def extract_domain(url: str) -> str:
    parsed = urlparse(url)
    return parsed.netloc.replace("www.", "")

def ensure_dir(p: str) -> str:
    os.makedirs(p, exist_ok=True)
    return p

def write_text(path, content):
    """
    Writes either a string OR an iterable of strings.
    If content is a string, write as-is.
    If list/tuple, join with newlines.
    """
    with open(path, "w", encoding="utf-8") as f:
        if isinstance(content, (list, tuple)):
            f.write("\n".join(str(x) for x in content))
        else:
            f.write(str(content))

def write_json(path: str, obj):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2, default=str)

def load_prompt(path: str) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read().strip()

def fill_prompt(template: str, **kwargs) -> str:
    return Template(template).safe_substitute(**kwargs)



def load_dark_pattern_task(
    template_user_path: str,
    taxonomy_json_path: str,
    url: str,
    pretty: bool = True,
) -> str:
    """Return a single filled prompt string with $url and $dark_pattern_definition injected."""
    
    template_user_text = Path(template_user_path).read_text(encoding="utf-8")
    
    try:
        taxonomy_text = Path(taxonomy_json_path).read_text(encoding="utf-8")
    except Exception as e:
        traceback.print_exc()
        raise
    try:
        taxonomy = json.loads(taxonomy_text)
    except Exception as e:
        print("JSON parse error:", e)
        traceback.print_exc()
        
    taxonomy_block = json.dumps(
        taxonomy,
        ensure_ascii=False,
        indent=2 if pretty else None,
        separators=None if pretty else (",", ":"),
    )
    user_prompt = template_user_text.replace("$dark_pattern_taxonomy", taxonomy_block).replace("$url", url)
    return user_prompt


async def process_one(url: str, browser_session: BrowserSession, type: str, model: str):
    """Run the agent on a single URL and save outputs in its own folder."""
    url_domain = extract_domain(url)
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    run_dir = ensure_dir(os.path.join(ROOT_OUT_DIR, url_domain, type, model, stamp))
    shots_dir = ensure_dir(os.path.join(run_dir, "screenshots"))
    video_run_dir = ensure_dir(os.path.join(run_dir, "videos"))


    print("Loading dark pattern task...")
    user_prompt = load_dark_pattern_task(
        template_user_path=DP_PROMPT_USER_PATH,
        taxonomy_json_path=DP_TAXONOMY_JSON,
        url=url,
    )
    

    controller = Controller(output_model=DarkPatternRunResult)

    agent = Agent(
        controller=controller,                               
        task=user_prompt,                                            
        llm=ChatOpenAI(model=MODEL, temperature=TEMPERATURE, api_key=OPENAI_API_KEY, max_completion_tokens=20000),
        use_vision=True,
        llm_timeout=240,      
        step_timeout=240,
        max_failures=5,
        final_response_after_failures=True,
        browser_session=browser_session,
        output_model_schema=DarkPatternRunResult,
        save_conversation_path=os.path.join(run_dir, "conversation_history.json"),
        save_conversation_path_encoding="utf-8",
        #extend_system_message = system_prompt,
        # try to solve Invalid JSON error
        minimum_wait_page_load_time=60.0,
        wait_for_network_idle_page_load_time=60.0,
        wait_between_actions=5.0,
        calculate_cost=True
    )
    # Navigate to target first 
    try:
       
        print("Running agent...")

        raw_output = await agent.run()

       
        #calcuate the cost
        print(f"Token usage_1: {raw_output.usage}")
        usage = await agent.token_cost_service.get_usage_summary()
        print(f"Token usage_2: {usage}")        
        ###usage_summary = await agent.token_cost_service.get_usage_summary()


        if raw_output and raw_output.final_result():
            result = raw_output.final_result()
            print(f"Final result to be parsed as JSON: {result!r}")
            if isinstance(result, str) and result.strip():
                try:
                    parsed: DarkPatternRunResult = DarkPatternRunResult.model_validate_json(result)
                    write_text(
                        os.path.join(run_dir, "final_result.json"),
                        parsed.model_dump_json(indent=2)
                    )
                except Exception as e:
                    print(f"CRITICAL: JSON decode/validation error: {e}")
                    write_text(os.path.join(run_dir, "INVALID_JSON_PAYLOAD.txt"), str(result))
            else:
                print("WARNING: Final result invalid string, skipping final_result.json")
                write_text(os.path.join(run_dir, "FAILURE.txt"), f"Invalid final result: {result!r}")
        else:
            print("WARNING: No final_result available")
            write_text(os.path.join(run_dir, "FAILURE.txt"), "Agent returned no final result.")


        # --- Always save side artifacts, regardless of final_result.json ---
        def _safe(callable_or_list):
            try:
                return callable_or_list() if callable(callable_or_list) else callable_or_list
            except Exception:
                return []

        urls = _safe(raw_output.urls) if raw_output else []
        action_names = _safe(raw_output.action_names) if raw_output else []
        extracted = _safe(raw_output.extracted_content) if raw_output else []
        model_actions = _safe(raw_output.model_actions) if raw_output else []
        errors = [str(e) for e in (_safe(raw_output.errors) if raw_output else [])]
        shots = _safe(raw_output.screenshot_paths) if raw_output else []
        hist_info = {
            "is_done":        _safe(raw_output.is_done) if raw_output else [],
            "is_successful":  _safe(raw_output.is_successful) if raw_output else [],
            "has_errors":     _safe(raw_output.has_errors) if raw_output else [],
            "number_of_steps": _safe(raw_output.number_of_steps) if raw_output else [],
            "total_duration_seconds": _safe(raw_output.total_duration_seconds) if raw_output else [],
            "token_usage": _safe(raw_output.usage) if raw_output else [],
        } 
        action_history = _safe(raw_output.action_history) if raw_output else []
        action_results = _safe(raw_output.action_results) if raw_output else []
        model_thoughts = _safe(raw_output.model_thoughts) if raw_output else []

        # Save artifacts
        write_text(os.path.join(run_dir, "history_summary.json"), hist_info)
        write_text(os.path.join(run_dir, "action_history.json"), action_history)
        write_text(os.path.join(run_dir, "action_results.json"), action_results)
        write_text(os.path.join(run_dir, "model_thoughts.json"), model_thoughts)

        write_text(os.path.join(run_dir, "urls.txt"), urls)
        write_text(os.path.join(run_dir, "action_names.txt"), action_names)
        write_text(os.path.join(run_dir, "extracted_content.txt"), extracted)
        write_text(os.path.join(run_dir, "errors.txt"), errors)
        write_json(os.path.join(run_dir, "model_actions.json"), model_actions)

        # Copy screenshots (best effort)
        for p in shots or []:
            if p and os.path.exists(p):
                try:
                    shutil.copy(p, shots_dir)
                except Exception as e:
                    with open(os.path.join(run_dir, "screenshot_copy_errors.txt"), "a", encoding="utf-8") as f:
                        f.write(f"{p} -> ERROR: {e}\n")

    except json.JSONDecodeError as e:
        print(f"CRITICAL: JSON Decode Error for URL {url}: {e}")
        # Save the invalid string that caused the error for inspection
        write_text(os.path.join(run_dir, "INVALID_JSON_PAYLOAD.txt"), result)
        traceback.print_exc()

    except Exception as e:
        # Catch any other unexpected errors during the process
        print(f"CRITICAL: An unexpected error occurred for URL {url}: {e}")
        write_text(os.path.join(run_dir, "UNEXPECTED_ERROR.txt"), traceback.format_exc())
        traceback.print_exc()
        
    finally:
        
        await asyncio.sleep(0.2)  # tiny flush buffer

        global_videos_dir = os.path.join(ROOT_OUT_DIR, "videos")
        os.makedirs(global_videos_dir, exist_ok=True)

        files = []
        for root, _, fnames in os.walk(global_videos_dir):
            for fname in fnames:
                if fname.lower().endswith((".webm", ".mp4")):
                    files.append(Path(root) / fname)

        # newest first (or reverse if you prefer)
        files.sort(key=lambda p: p.stat().st_mtime)

        moved_count = 0
        for idx, src in enumerate(files, start=1):
            try:
                if not src.is_file() or src.stat().st_size == 0:
                    continue
                ext = src.suffix or ".webm" or ".mp4"
                dest = Path(video_run_dir) / f"{stamp}_{url_domain}_{idx}{ext}"
                ensure_dir(video_run_dir)
                try:
                    shutil.move(str(src), str(dest))
                except Exception:
                    shutil.copy2(str(src), str(dest))
                    try: os.remove(str(src))
                    except Exception: pass
                moved_count += 1
            except Exception:
                pass


        try:
            with open(os.path.join(run_dir, "video_move_summary.txt"), "a", encoding="utf-8") as f:
                f.write(f"Moved {moved_count} video(s) from {global_videos_dir} -> {video_run_dir}\n")
        except Exception:
            pass

        # write a summary
        try:
            summary = [
                f"URL: {url}",
                f"URLs visited: {len(urls)}",
                f"Actions: {len(action_names)}",
                f"Extracted items: {len(extracted)}",
                f"Errors: {len(errors)}",
                f"Model actions: {len(model_actions)}",
                f"Screenshots copied: {len([p for p in (shots or []) if p and os.path.exists(p)])}",
                f"Videos moved: {len(list(Path(video_run_dir).glob('*')))}",
            ]
            write_text(os.path.join(run_dir, "SUMMARY.txt"), summary)
        except Exception:
            pass

    print(f"[{url}] History + structured report saved to: {run_dir}")


async def main(type: str, model: str):

    # ---- One persistent browser session for all URLs (recommended)
    ROOT = Path(ROOT_OUT_DIR).expanduser().resolve()
    profile_dir = (ROOT / "chromedata").expanduser().resolve()
    profile_dir.mkdir(parents=True, exist_ok=True)

    SYSTEM_CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
    assert Path(SYSTEM_CHROME).exists(), "Install Chrome or fix SYSTEM_CHROME path."

    browser_profile = BrowserProfile(
        headless=True,
        stealth=True,
        storage_state=None,  # rely on persistent user_data_dir
        viewport={"width": 1920, "height": 1080},
        locale="en-US",
        user_agent=("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/126.0.0.0 Safari/537.36"),
        wait_for_network_idle_page_load_time=10.0,
    )


    # SERIAL processing (safer vs bot checks).
    for url in URLS:
        browser_session = BrowserSession(
            browser_profile=browser_profile,
            headless=True,
            user_data_dir=str(profile_dir),  # Persistent profile to store all session data
            #keep_user_data_dir=True,         # Persistent profile
            executable_path=SYSTEM_CHROME,   
            enable_default_extensions=False,
            record_video_dir=str(ROOT / "videos"),  
            record_video_size={"width": 1920, "height": 1080},
            args=[
                "--disable-blink-features=AutomationControlled",
                "--disable-background-networking",
                "--disable-renderer-backgrounding",
                "--disable-component-extensions-with-background-pages",
                "--no-first-run",
                "--no-default-browser-check",
                "--disable-dev-shm-usage",
                "--disable-infobars",
                "--disable-features=IsolateOrigins,site-per-process",
                "--mute-audio",
                "--password-store=basic",
                "--use-mock-keychain",
                "--lang=en-US,en",
                "--window-size=1920,1080",
                "--new-window",
            ],
        )

        # Start once and reuse
        await browser_session.start()
        try:
            await process_one(url, browser_session,type, model)
            await asyncio.sleep(2)
        except Exception as e:
            # Keep going even if one site fails
            err_dir = ensure_dir(os.path.join(ROOT_OUT_DIR, "failures"))
            with open(os.path.join(err_dir, "failures.log"), "a", encoding="utf-8") as f:
                f.write(f"{datetime.now().isoformat()} :: {url} :: {e}\n")
        finally:
            try:
                await browser_session.close()
            except Exception:
                pass

    print("✅ All URLs processed successfully.")

if __name__ == "__main__":

    DP_TAXONOMY_JSONS = [
        "prompts/few_shot_scenaiors_only/sneaking.json",
        "prompts/few_shot_scenaiors_only/interface_interference.json",
        "prompts/few_shot_scenaiors_only/obstruction.json",
    ]
    taxonomy_to_type = {
        "prompts/few_shot_scenaiors_only/sneaking.json":
            "sneaking_regulator_role_few_shot_scenarios",

        "prompts/few_shot_scenaiors_only/interface_interference.json":
            "interface_interference_regulator_role_few_shot_scenarios",

        "prompts/few_shot_scenaiors_only/obstruction.json":
            "obstruction_regulator_role_few_shot_scenarios",
    }

    for taxonomy_path in DP_TAXONOMY_JSONS:

        DP_TAXONOMY_JSON = taxonomy_path

        type = taxonomy_to_type[taxonomy_path]

        print(f"\n{'='*80}")
        print(f"Running taxonomy: {taxonomy_path}")
        print(f"Output type: {type}")
        print(f"{'='*80}\n")

        asyncio.run(main(type, MODEL))
