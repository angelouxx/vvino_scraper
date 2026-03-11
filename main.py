import json
import re
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def extract_filter_values(driver, data_qa_attr: str) -> list:
    """Waits for initial load, then extracts all checkbox values via 'Show more' loops."""
    script = f"""
        const done = arguments[arguments.length - 1];
        (async () => {{
            let retries = 25;
            while (retries > 0) {{
                if (document.querySelector('[data-qa="{data_qa_attr}"] label[data-testid]')) break;
                await new Promise(r => setTimeout(r, 200));
                retries--;
            }}

            let btn;
            while ((btn = document.querySelector('[data-qa="{data_qa_attr}"] [data-testid="show-more-button"]'))) {{
                const key = Object.keys(btn).find(k => k.startsWith('__reactProps'));
                btn[key].onClick({{ target: btn, currentTarget: btn, preventDefault: () => {{}}, stopPropagation: () => {{}} }});
                await new Promise(r => setTimeout(r, 800));
            }}

            done([...document.querySelectorAll('[data-qa="{data_qa_attr}"] label[data-testid]')].map(l => ({{
                id: l.getAttribute('data-testid'),
                value: l.querySelector('input').value,
                text: l.querySelector('span[class*="labelWithIcon"]').textContent.trim()
            }})));
        }})();
    """
    return driver.execute_async_script(script)

def process_category(data_list: list) -> list:
    """Deduplicates and cleans item names using a set for O(1) lookups."""
    result, seen = [], set()
    for item in data_list:
        if item['id'] not in seen:
            seen.add(item['id'])
            clean_name = re.sub(r"\s*\(\d+\)", "", item['text'])
            result.append({'id': item['id'], 'value': item['value'], 'name': clean_name})
    return result

if __name__ == '__main__':
    driver = webdriver.Chrome()
    wait = WebDriverWait(driver, 15)
    driver.set_script_timeout(120)

    try:
        driver.get('https://www.vivino.com/en/explore')
        driver.maximize_window()

        # 1. Click "Ship to" using React bypass
        ship_elemnt = driver.execute_script("""
            return Array.from(document.querySelectorAll('[class*="simpleLabel-module__label"]'))
                .find(e => e.textContent.includes("Ship to"));
        """)
        driver.execute_script("arguments[0].click();", ship_elemnt)

        # 2. Wait for and click UK, then wait for page reload
        uk = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '[data-value="gb"]')))
        driver.execute_script("arguments[0].click();", uk)
        time.sleep(2)

        # 3. Define the filters we want to extract (maps JSON keys to exact HTML attributes)
        target_filters = {
            "grapes": "filterByGrape",
            "regions": "filterByRegion",
            "countries": "filterByCountry",
            "styles": "filterByStyle"
        }

        # 4. Open all filter toggles at once in the browser
        js_filters_array = json.dumps(list(target_filters.values()))
        driver.execute_script(f"""
            // SINGLE BRACES HERE: Inject the Python variable
            const filters = {js_filters_array};
            
            // DOUBLE BRACES BELOW: Escape JavaScript syntax
            filters.forEach(f => {{
                const t = document.querySelector(`[data-qa="${{f}}"] [data-testid="filter-toggle-button"]`);
                if (t && t.getAttribute('aria-expanded') === 'false') {{
                    const k = Object.keys(t).find(key => key.startsWith('__reactProps'));
                    t[k].onClick({{ target: t, currentTarget: t, preventDefault: ()=>{{}}, stopPropagation: ()=>{{}} }});
                }}
            }});
        """)

        # 5. Extract and process each category dynamically
        final_results = {}
        for json_key, html_attr in target_filters.items():
            print(f"\nScraping {json_key.capitalize()}...")
            raw_data = extract_filter_values(driver, html_attr)
            final_results[json_key] = process_category(raw_data)
            print(f"Saved {len(final_results[json_key])} unique {json_key}.")

        # 6. Save results
        with open("vivino_filters.json", "w", encoding="utf-8") as f:
            json.dump(final_results, f, ensure_ascii=False, indent=2)
        print("\nData successfully saved to vivino_filters.json!")

    finally:
        input('PRESS TO EXIT')
        driver.quit()