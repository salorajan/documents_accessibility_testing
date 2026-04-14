import sys
import os
import re
import mistune
from bs4 import BeautifulSoup

class ACBProtocolAuditor:
    def __init__(self):
        self.md_parser = mistune.create_markdown(escape=False)

    def run_audit(self, content, is_markdown=False):
        # PRE-PROCESSOR: Force a space after every '#' to fix the common typo
        if is_markdown:
            content = re.sub(r'^(#+)(?!\s)', r'\1 ', content, flags=re.MULTILINE)
            html_input = self.md_parser(content)
        else:
            html_input = content

        soup = BeautifulSoup(html_input, 'html.parser')
        report = []
        
        # --- THE WARRIOR'S SENSORS ---
        # Search for real tags OR text that looks like Markdown headers/images
        all_headers = soup.find_all(re.compile('^h[1-6]$'))
        all_imgs = soup.find_all('img')

        # FALLBACK: If mistune failed (as seen in your debug), we hunt the text inside <p>
        if is_markdown and not all_headers:
            for p in soup.find_all('p'):
                text = p.get_text().strip()
                # Detect manual headers like "# Level 1" inside <p>
                if text.startswith('#'):
                    level = len(text.split()[0]) # Count the #
                    report.append(f"[FAIL] Improper Markdown: Header '{text}' was not parsed. Ensure a space exists after #.")
                # Detect manual images like "![]()" inside <p>
                if text.startswith('!['):
                    report.append(f"[FAIL] Improper Markdown: Image '{text}' was not parsed.")

        # --- Standard Audit Logic ---
        prev_level = 0
        for h in all_headers:
            curr_level = int(h.name[1])
            if curr_level > prev_level + 1:
                report.append(f"[FAIL] Heading Jump: H{prev_level} -> {h.name.upper()}")
            prev_level = curr_level

        for img in all_imgs:
            if not img.has_attr('alt') or not img.get('alt', '').strip():
                report.append(f"[FAIL] Missing Alt-text: {img.get('src', 'Unknown Source')}")

        if not report and not all_headers and not all_imgs:
            return ["[WARNING] No structural elements found. Verify file syntax."]

        return report

def main():
    if len(sys.argv) < 2:
        print("\nUsage: python warrior_test.py <file>")
        return

    target = sys.argv[1]
    is_md = target.lower().endswith('.md')

    with open(target, 'r', encoding='utf-8') as f:
        data = f.read()

    auditor = ACBProtocolAuditor()
    results = auditor.run_audit(data, is_markdown=is_md)

    print("\n" + "="*60)
    print(f" ACB AUDIT: {os.path.basename(target)}")
    print("="*60)
    
    if not results:
        print(" STATUS: 100% COMPLIANT")
    else:
        print(f" STATUS: {len(results)} VIOLATIONS FOUND")
        for err in results:
            print(f" >> {err}")
    print("="*60 + "\n")

if __name__ == "__main__":
    main()