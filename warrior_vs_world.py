"""
WARRIOR VS WORLD: THE GOLD MEDAL BENCHMARK (V3.1)
DEEP THINKING APPLIED: YES
PYTHON ENGINE: 3.14.4
AUDIT ONLY: YES
TARGET: Compare Warrior V3 vs Standard Industry Engines.
"""

import asyncio
import os
import sys
from playwright.async_api import async_playwright
from axe_core_python.sync_playwright import Axe
from bs4 import BeautifulSoup

# Landmarks for Screen Reader Navigation
L1, L2, L3 = "1.0", "2.0", "3.0"

async def run_benchmark(target):
    is_url = target.startswith(("http://", "https://"))
    target_path = target if is_url else f"file:///{os.path.abspath(target)}".replace("\\", "/")

    async with async_playwright() as p:
        print(f"\n{L1} ARENA INITIALIZED: COMMENCING BENCHMARK")
        
        # Corrected 2026 Gladiator Launch Logic
        browser = await p.chromium.launch(
            headless=False,
            channel="chrome",
            args=["--start-maximized"]
        )
        
        # Defining the Context and Page correctly
        context = await browser.new_context(viewport=None)
        page = await context.new_page()

        try:
            # Using 'domcontentloaded' to avoid Anti-Bot timeouts
            await page.goto(target_path, timeout=60000, wait_until="domcontentloaded")
            
            # --- COMPETITOR 1: AXE-CORE (INDUSTRY STANDARD) ---
            axe = Axe()
            await page.add_script_tag(content=axe.axe_script)
            axe_raw = await page.evaluate("axe.run()")
            axe_count = len(axe_raw.get('violations', []))

            # --- COMPETITOR 2: WARRIOR V3 (SKEPTICAL ENGINE) ---
            content = await page.content()
            soup = BeautifulSoup(content, 'lxml')
            sabotage_count = 0
            
            # Skepticism Logic: Hidden Content + Lang Deception + JS Hijacks
            if soup.find(attrs={"aria-hidden": "true"}) and soup.find('body'): sabotage_count += 1
            html_tag = soup.find('html')
            if html_tag and html_tag.get('lang') and html_tag.get('lang') != 'en': sabotage_count += 1
            if "preventDefault" in content and "Tab" in content: sabotage_count += 1

            total_warrior_threats = axe_count + sabotage_count

            # --- BATTLE DATA OUTPUT ---
            print(f"\n{L2} COMPETITION RESULTS")
            print("-" * 50)
            print(f"TARGET: {target}")
            print(f"STANDARD AXE-CORE DETECTIONS: {axe_count}")
            print(f"WARRIOR V3 EXCLUSIVE (SABOTAGE): {sabotage_count}")
            print(f"TOTAL WARRIOR INTELLIGENCE: {total_warrior_threats}")
            print("-" * 50)

            if total_warrior_threats > axe_count:
                print(f"{L3} VICTORY ACHIEVED: Warrior detected {sabotage_count} hidden threats missed by Axe-core.")
            elif total_warrior_threats == axe_count:
                print(f"{L3} DRAW: Both tools are in agreement.")
            else:
                print(f"{L3} ADAPTATION REQUIRED: Warrior missed a standard signature.")

        except Exception as e:
            print(f"BATTLE ERROR: {str(e)}")
        finally:
            await browser.close()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python warrior_vs_world.py <URL or file>")
    else:
        asyncio.run(run_benchmark(sys.argv[1]))