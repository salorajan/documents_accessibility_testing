import re
import mistune
from bs4 import BeautifulSoup

class ACBProtocolAuditor:
    def __init__(self):
        self.md_parser = mistune.create_markdown()

    def run_audit(self, content, is_markdown=False):
        try:
            if is_markdown:
                # DEBUG: Ensure the transformation is happening
                html_input = self.md_parser(content)
            else:
                html_input = content

            soup = BeautifulSoup(html_input, 'html.parser')
        except Exception as e:
            return [f"CRITICAL: Parse Failure ({str(e)})"]
            
        report = []
        
        # Protocol 1: Headings
        # We use a more aggressive search for headings
        headings = soup.find_all(re.compile('^h[1-6]$'))
        prev_level = 0
        for h in headings:
            curr_level = int(h.name[1])
            if curr_level > prev_level + 1:
                report.append(f"[FAIL] Heading Jump: H{prev_level} -> {h.name.upper()}")
            prev_level = curr_level

        # Protocol 2: Alt-Text
        for img in soup.find_all('img'):
            # Check if alt exists AND is not empty (ACB standard usually requires descriptive alt)
            if not img.has_attr('alt') or not img['alt'].strip():
                report.append(f"[FAIL] Missing Alt-text: {img.get('src', 'Unknown')}")

        # Protocol 3: Large Print (HTML Only)
        if not is_markdown:
            style_tags = soup.find_all('style')
            combined_styles = " ".join([s.get_text() for s in style_tags])
            fs_matches = re.findall(r'font-size:\s*(\d+)(pt|px)', combined_styles.lower())
            for val, unit in fs_matches:
                v = int(val)
                if (unit == 'pt' and v < 18) or (unit == 'px' and v < 24):
                    report.append(f"[FAIL] ACB Violation: Font size {val}{unit} too small")

        return report