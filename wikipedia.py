import wikipediaapi
from unidecode import unidecode
import re
import time


# The main categories of Wikipedia
main_categories = [
    'Science',
    'Everyday_life',
    'Geography',
    'History',
    'Knowledge',
    'Literature',
    'People',
    'Religion',
]

# Avoid pages with these words in the title
avoid_words = [
    'Outline',
    'List',
]

# Create a Wikipedia object
wiki_wiki = wikipediaapi.Wikipedia(
    'Transformer_trainer (luke.robertson@networkdirection.net)',
    'en',
    extract_format=wikipediaapi.ExtractFormat.WIKI
)


# Go through categories and pages recursively
def get_categories(category, depth=0, max_depth=5):
    for page in category.values():
        # Regular pages, add to the list
        if page.ns == wikipediaapi.Namespace.MAIN:
            # Skip pages with avoid words in the title
            if any(word in unidecode(page.title) for word in avoid_words):
                print(f'Skipping {unidecode(page.title)} (avoid word)')
                continue
            if unidecode(page.title) in done_list:
                print(f'Skipping {unidecode(page.title)} (already done)')
                continue
            if unidecode(page.title) in small_pages_list:
                print(f'Skipping {unidecode(page.title)} (too small)')
                continue

            save_page(page)

        # Subcategories, dig deeper
        elif page.ns == wikipediaapi.Namespace.CATEGORY and depth < max_depth:
            get_categories(page.categorymembers, depth + 1, max_depth)


# Save the page to a text file
# Set clean to False to save the raw text
def save_page(page, clean=True):
    # Load the page
    try:
        page = wiki_wiki.page(page.title)
    except wikipediaapi.exceptions.PageError:
        print(f"Error: Page not found: {page.title}")
        return
    except wikipediaapi.exceptions.HTTPTimeoutError:
        print(f"Error: HTTP Timeout: {page.title}")
        time.sleep(5)
        return

    # If the page is very small, don't bother saving it
    if len(page.text) < 2000:
        with open('small_pages.txt', 'a') as f:
            f.write(f'{unidecode(page.title)}\n')

    # If it's larger, save it, and store the name in a list
    elif unidecode(page.title) not in done_list:
        # Title and content
        if clean:
            text = cleanup(unidecode(page.text))

            # Check if its too small now
            if len(text) < 2000:
                with open('small_pages.txt', 'a') as f:
                    f.write(f'{unidecode(page.title)}\n')
                return

        # Save the page to a text file
        try:
            with open(f'./data/{unidecode(page.title)}.txt', 'w') as f:
                f.write(f'{unidecode(page.title)}\n')
                f.write(text)

        # Special characters in the title throw an error
        except OSError as e:
            print(f"Error: {e}")

        # Add to the list of completed pages
        with open('page_list.txt', 'a') as f:
            f.write(f'{unidecode(page.title)}\n')


# Cleanup for dataset use
def cleanup(text):
    # Use regex to match certain patterns and remove them
    text = re.sub(r'== References ==.*$', '', text, flags=re.DOTALL)
    text = re.sub(r'== External links ==.*$', '', text, flags=re.DOTALL)
    text = re.sub(r'=== Journals ===.*$', '', text, flags=re.DOTALL)
    text = re.sub(r'See also.*$', '', text, flags=re.DOTALL)
    text = re.sub(r'Notes.*$', '', text, flags=re.DOTALL)
    text = re.sub(r'References.*$', '', text, flags=re.DOTALL)
    text = re.sub(r'Further reading.*$', '', text, flags=re.DOTALL)
    text = re.sub(r'External links.*$', '', text, flags=re.DOTALL)
    text = re.sub(r'Publications.*$', '', text, flags=re.DOTALL)
    text = re.sub(r'Bibliography.*$', '', text, flags=re.DOTALL)
    text = re.sub(r'Notable scholars.*$', '', text, flags=re.DOTALL)
    text = re.sub(r'Works cited.*$', '', text, flags=re.DOTALL)

    # Replace multiple empty lines with a single empty line
    text = re.sub(r'\n\s*\n', '\n\n', text)

    # Remove lines that contain 'wikimedia'
    text = re.sub(r'.*Wikimedia.*\n', '', text)

    # Remove lines that end in a colon
    text = re.sub(r'.*:\n', '', text)

    # Remove consecutive lines that contain only a single word
    text = re.sub(r'\b\w+\b\s*\n\s*\b\w+\b\s*\n', '', text)

    # Replace multiple empty lines with a single empty line
    text = re.sub(r'\n\s*\n', '\n\n', text)

    return text


if __name__ == '__main__':
    # Load the list of small pages
    small_pages_list = []
    try:
        with open('small_pages.txt', 'r') as f:
            small_pages_list = f.read().splitlines()
    except FileNotFoundError:
        pass

    # Load the list of completed pages
    done_list = []
    try:
        with open('page_list.txt', 'r') as f:
            done_list = f.read().splitlines()
    except FileNotFoundError:
        pass

    # Start the process
    for category in main_categories:
        get_categories(wiki_wiki.page(f"Category:{category}").categorymembers)
