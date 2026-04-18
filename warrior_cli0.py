import sys
import os
import re
from bs4 import BeautifulSoup
from datetime import datetime

def run_battle_audit(file_path, quiet=False):
    """
    STABILIZED V1.5: Full-Strength Unified Auditor.
    Includes 10 Provisions, Deep Attribute Scanning, and Persistent Logging.
    """
    violations_count = 0
    if not os.path.exists(file_path):
        if not quiet: print(f"ERROR: File {file_path} not found.")
        return -1

    with open(file_path, 'r', encoding='utf-8') as f:
        # Using 'lxml' for strict structural reconnaissance
        soup = BeautifulSoup(f, 'lxml')

    report_log = []
    report_log.append("=" * 60)
    report_log.append(f" BATTLE REPORT: {file_path}")
    report_log.append(f" TIMESTAMP: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report_log.append(f" STATUS: RESEARCHER AUDIT ACTIVE")
    report_log.append("=" * 60)

    # 1. Heading Hierarchy (SC 1.3.1)
    headings = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
    last_level = 0
    for h in headings:
        level = int(h.name[1])
        if level > last_level + 1 and last_level != 0:
            violations_count += 1
            report_log.append(f" >> [FAIL] SC 1.3.1: Heading Skip (<h{level}> follows <h{last_level}>).")
        if not h.get_text().strip():
            violations_count += 1
            report_log.append(f" >> [FAIL] SC 1.3.1: Empty Heading (<{h.name}>).")
        last_level = level

    # 2. Image Alternative Text (SC 1.1.1)
    for img in soup.find_all('img'):
        alt = img.get('alt')
        src = img.get('src', 'unknown_source')
        if alt is None:
            violations_count += 1
            report_log.append(f" >> [FAIL] SC 1.1.1: Image '{src}' missing 'alt' attribute.")
        else:
            # Junk/Suspicious Alt Text Detection
            junk_patterns = [r'^image$', r'^picture$', r'^\d+$', r'\.jpg$', r'\.png$', r'^$']
            if any(re.search(p, alt.lower().strip()) for p in junk_patterns):
                violations_count += 1
                report_log.append(f" >> [WARN] SC 1.1.1: Suspicious Alt text '{alt}' on '{src}'.")

    # 3. Table Structure (SC 1.3.1)
    for table in soup.find_all('table'):
        if not table.find('th'):
            violations_count += 1
            report_log.append(" >> [FAIL] SC 1.3.1: Data table missing <th> headers.")

    # 4. Link Integrity (SC 2.4.4)
    for link in soup.find_all('a'):
        if not link.get_text().strip() and not link.find('img'):
            violations_count += 1
            report_log.append(f" >> [FAIL] SC 2.4.4: Empty link (href='{link.get('href', '#')}').")

    # 5. Form Control Labels (SC 3.3.2)
    for ctrl in soup.find_all(['input', 'select', 'textarea']):
        if ctrl.get('type') in ['hidden', 'submit', 'button', 'reset']: continue
        ctrl_id = ctrl.get('id')
        has_label = False
        if ctrl_id and soup.find('label', attrs={'for': ctrl_id}): has_label = True
        elif ctrl.has_attr('aria-label') or ctrl.has_attr('aria-labelledby'): has_label = True
        elif ctrl.find_parent('label'): has_label = True
        
        if not has_label:
            violations_count += 1
            report_log.append(f" >> [FAIL] SC 3.3.2: Form control '{ctrl.name}' missing label.")

    # 6. Global Document Language (SC 3.1.1)
    html_tag = soup.find('html')
    if html_tag and not html_tag.has_attr('lang'):
        violations_count += 1
        report_log.append(" >> [FAIL] SC 3.1.1: Document <html> missing 'lang' attribute.")

    # 7. Language Overrides (SC 3.1.2)
    for tag in soup.find_all(attrs={"lang": True}):
        if tag.name == 'html': continue
        if not tag['lang'].strip():
            violations_count += 1
            report_log.append(f" >> [FAIL] SC 3.1.2: Empty 'lang' override on <{tag.name}>.")

    # 8. Duplicate ID Detection (SC 4.1.1)
    ids = [tag['id'] for tag in soup.find_all(id=True)]
    seen_ids = set()
    duplicates = set()
    for x in ids:
        if x in seen_ids: duplicates.add(x)
        seen_ids.add(x)
    if duplicates:
        violations_count += len(duplicates)
        report_log.append(f" >> [FAIL] SC 4.1.1: Duplicate IDs detected: {duplicates}")

    # 9. Keyboard Accessibility (SC 2.1.1)
    for item in soup.find_all(tabindex="-1"):
        violations_count += 1
        report_log.append(f" >> [FAIL] SC 2.1.1: Element <{item.name}> removed from tab order (tabindex='-1').")

    # 10. Contrast Skepticism (SC 1.4.3) - REINFORCED
    for elem in soup.find_all(attrs={"style": True}):
        style_content = str(elem.get('style', '')).lower()
        if 'color' in style_content:
            violations_count += 1
            report_log.append(f" >> [WARN] SC 1.4.3: Inline color style on <{elem.name}> requires manual contrast audit.")

    report_log.append("-" * 60)
    report_log.append(f" STATISTICAL TOTAL: {violations_count} Violations/Warnings Found.")
    report_log.append("-" * 60)

    # Persistent Intelligence Logging
    with open("audit_results.txt", "w", encoding="utf-8") as log_file:
        log_file.write("\n".join(report_log))

    if not quiet:
        print("\n".join(report_log))

    return violations_count

def mass_verify():
    print("--- MASS CALIBRATION: PROVING GROUNDS V1.5 ---")
    benchmark_file = os.path.join("proving_grounds", "benchmarks.txt")
    if not os.path.exists(benchmark_file):
        print("CRITICAL ERROR: Benchmarks map missing.")
        return

    success_count = 0
    total_tests = 0
    with open(benchmark_file, 'r') as f:
        for line in f:
            if not line.strip(): continue
            filename, expected = line.strip().split(':')
            actual = run_battle_audit(os.path.join("proving_grounds", filename), quiet=True)
            total_tests += 1
            if actual == int(expected):
                print(f"[PASS] {filename}: Found {actual}")
                success_count += 1
            else:
                print(f"[FAIL] {filename}: Expected {expected}, Found {actual}")

    print("-" * 40)
    print(f"CALIBRATION SCORE: {success_count}/{total_tests}")
    if success_count == total_tests:
        print(">> CONSENSUS ACHIEVED. WEAPON IS BATTLE READY.")
    print("-" * 40)

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--mass-verify":
        mass_verify()
    elif len(sys.argv) == 2:
        run_battle_audit(sys.argv[1])
    else:
        print("Usage: python warrior_cli0.py <file.html> OR --mass-verify")