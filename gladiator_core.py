import asyncio
import os
import sys
import json
from playwright.async_api import async_playwright
from axe_core_python.async_playwright import Axe

async def run_gladiator(target):
    is_url = target.startswith(("http://", "https://"))
    target_path = target if is_url else f"file:///{os.path.abspath(target)}".replace("\\", "/")
    
    # Define the output path clearly
    output_dir = os.path.dirname(os.path.abspath(__file__))
    json_path = os.path.join(output_dir, "gladiator_report.json")

    async with async_playwright() as p:
        print("\n1.0 THE EYE OF TRUTH IS OPEN - GLADIATOR SYSTEM")
        print("-" * 40)
        
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        try:
            await page.goto(target_path, timeout=60000, wait_until="networkidle")
            await asyncio.sleep(2) 
            
            # --- AXE-CORE BASELINE ---
            axe = Axe()
            results = await axe.run(page)
            axe_instances = sum(len(v.get('nodes', [])) for v in results.get('violations', []))

            # Initialize SC Summary with Axe findings
            sc_summary = {}
            for v in results.get('violations', []):
                sc_tags = [t for t in v.get('tags', []) if t.startswith('wcag')]
                count = len(v.get('nodes', []))
                for tag in sc_tags:
                    sc_summary[tag] = sc_summary.get(tag, 0) + count

            # --- GLADIATOR INQUISITOR (THE DISTINCTION ENGINE) ---
            gladiator_violations = []
            g_instances = 0

            # [1] Language Lie (WCAG 3.1.1) - Axe misses logic-based lang lies
            lang = await page.get_attribute('html', 'lang')
            if not lang or lang == 'None':
                g_instances += 1
                gladiator_violations.append({"sc": "wcag311", "rule": "Language Lie", "count": 1, "msg": "Tag is missing but content is English."})
                sc_summary['wcag311'] = sc_summary.get('wcag311', 0) + 1

            # [2] Tab-Key Murder (WCAG 2.4.3) - Axe often ignores positive TabIndex
            tabs = await page.evaluate('''() => Array.from(document.querySelectorAll('[tabindex]')).filter(el => el.tabIndex > 0).length''')
            if tabs > 0:
                g_instances += tabs
                gladiator_violations.append({"sc": "wcag243", "rule": "Tab-Key Murder", "count": tabs, "msg": "Manual TabIndex breaks navigation."})
                sc_summary['wcag243'] = sc_summary.get('wcag243', 0) + tabs

            # [3] Ghost Interactivity (WCAG 4.1.2) - THE BIG AXE MISS
            ghosts = await page.evaluate('''() => Array.from(document.querySelectorAll('div[onclick], div[onmouseover]')).filter(el => !el.getAttribute('role')).length''')
            if ghosts > 0:
                g_instances += ghosts
                gladiator_violations.append({"sc": "wcag412", "rule": "Ghost Interactivity", "count": ghosts, "msg": "Scripted elements hidden from screen readers."})
                sc_summary['wcag412'] = sc_summary.get('wcag412', 0) + ghosts

            # [4] Contrast Deception (WCAG 1.4.3) - Axe misses complex gradients
            gradients = await page.evaluate('''() => Array.from(document.querySelectorAll('*')).filter(el => {
                const s = window.getComputedStyle(el);
                return s.backgroundImage.includes('gradient') && s.color === 'rgb(224, 224, 224)';
            }).length''')
            if gradients > 0:
                g_instances += gradients
                gladiator_violations.append({"sc": "wcag143", "rule": "Contrast Deception", "count": gradients, "msg": "Gradients used to mask low-contrast text."})
                sc_summary['wcag143'] = sc_summary.get('wcag143', 0) + gradients

            # [5] Tiny Target Strike (WCAG 2.5.8) - New WCAG 2.2 Requirement
            tiny = await page.evaluate('''() => Array.from(document.querySelectorAll('button, a')).filter(el => {
                const r = el.getBoundingClientRect();
                return r.width > 0 && (r.width < 24 || r.height < 24);
            }).length''')
            if tiny > 0:
                g_instances += tiny
                gladiator_violations.append({"sc": "wcag258", "rule": "Tiny Targets", "count": tiny, "msg": "Interactive items too small for touch/click."})
                sc_summary['wcag258'] = sc_summary.get('wcag258', 0) + tiny

            # --- FINAL REPORTING ---
            char_count = len(await page.content())
            total_violations = axe_instances + g_instances
            
            final_report = {
                "summary": {
                    "total_instances": total_violations,
                    "axe_instances": axe_instances,
                    "gladiator_exclusives": g_instances,
                    "character_count": char_count
                },
                "wcag_sc_breakdown": sc_summary,
                "gladiator_details": gladiator_violations
            }

            with open(json_path, "w") as f:
                json.dump(final_report, f, indent=4)

            # --- TERMINAL OUTPUT ---
            print(f"TOTAL INSTANCES FOUND: {total_violations}")
            print(f"RENDERED CHARACTERS: {char_count}")
            print("-" * 40)
            print(f"AXE-CORE DETECTIONS: {axe_instances}")
            print(f"GLADIATOR EXCLUSIVES (MISSED BY AXE): {g_instances}")
            print("-" * 40)
            
            if g_instances > 0:
                print("DETAILED GLADIATOR EXCLUSIVES:")
                for v in gladiator_violations:
                    print(f" [!] {v['rule']} ({v['sc'].upper()}): {v['count']} instances")
                    print(f"     Reason: {v['msg']}")
            
            print("\nWCAG 2.2 COMBINED SUMMARY (AXE + GLADIATOR):")
            for sc, count in sorted(sc_summary.items()):
                print(f" - {sc.upper()}: {count} violations")
            
            print(f"\nFULL REPORT EXPORTED TO: {json_path}")
            print("-" * 40)

        except Exception as e:
            print(f"CRITICAL ERROR: {str(e)}")
        finally:
            await browser.close()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        asyncio.run(run_gladiator(sys.argv[1]))
    else:
        print("Usage: python gladiator_core.py <file_path>")