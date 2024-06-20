import wikipediaapi
from unidecode import unidecode
import re
import time
import requests
import random
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor
import threading


# Font colours
GREEN = '\033[92m'
YELLOW = '\033[93m'
RED = '\033[91m'
BLUE = '\033[94m'
WHITE = '\033[97m'
END = '\033[0m'


# The main categories of Wikipedia
main_categories = [
    'Academic_disciplines',
    'Business',
    'Communication',
    'Concepts',
    'Culture',
    'Economy',
    'Education',
    'Energy',
    'Engineering',
    'Entertainment',
    'Entities',
    'Ethics',
    'Food_and_drink',
    'Geography',
    'Government',
    'Health',
    'History',
    'Human_behavior',
    'Humanities',
    'Information',
    'Internet',
    'Knowledge',
    'Law',
    'Mass_media',
    'Mathematics',
    'Military',
    'Nature',
    'People',
    'Philosophy',
    'Politics',
    'Religion',
    'Science',
    'Society',
    'Sports',
    'Technology',
    'Time',
    'Universe',
]

# Avoid pages with these words in the title
avoid_words = [
    'Outline',
    'List',
    '?',
    '/',
    'Index',
    '.',
]

# Create a Wikipedia object
wiki_wiki = wikipediaapi.Wikipedia(
    'Transformer_trainer (luke.robertson@networkdirection.net)',
    'en',
    extract_format=wikipediaapi.ExtractFormat.WIKI
)


def get_article(article):
    # For multithreading
    # Skip articles with avoid words in the title
    if any(
        word in unidecode(article.title)
        for word
        in avoid_words
    ):
        return

    # Skip any articles that have already been done
    if unidecode(article.title) in done_list:
        print(
            f'Skipping {unidecode(article.title)} \
            (already done)'
        )
        return

    # Skip any articles that are too small
    if unidecode(article.title) in small_pages_list:
        return

    # Save the article to a text file
    save_page(article)


# Go through categories and pages recursively
def get_categories(category, depth=0, max_depth=10, randomize=True):
    # Progress bar colour
    bar_colour = 'WHITE'

    if {str(category).split(" (")[0]} in category_list:
        print(f'Skipping {category} (already done)')
        return

    try:
        # Check if the category has subcategories
        cat_list = list(category.categorymembers.keys())
        if any('Category' in entry for entry in cat_list):
            print(
                YELLOW +
                f'{str(category).split(" (")[0]} has subcategories' +
                END
            )
            bar_colour = 'YELLOW'
        else:
            print(
                BLUE +
                f'{str(category).split(" (")[0]} is a leaf category' +
                END
            )
            bar_colour = 'BLUE'

        pages = list(category.categorymembers.values())

        # Optionally shuffle the lists before starting
        if randomize:
            random.shuffle(pages)

        # Create lists of pages and categories within this category
        articles = []
        cats = []
        for page in pages:
            if page.ns == wikipediaapi.Namespace.MAIN:
                articles.append(page)
            elif page.ns == wikipediaapi.Namespace.CATEGORY:
                cats.append(page)

        # Download articles
        with ThreadPoolExecutor(max_workers=16) as executor:
            list(
                tqdm(
                    executor.map(
                        save_page,
                        articles
                    ),
                    total=len(articles),
                    colour=bar_colour,
                    desc='Getting Articles',
                    leave=False
                )
            )

        # Recursively go through subcategories
        for cat in cats:
            try:
                # Recursive call of this function
                get_categories(cat, depth + 1, max_depth)

                # If we get to this point, all subcategories are done
                #   Write this in the list of completed categories
                print(f"{GREEN}Subcategories of {cat.title} done{END}")
                with open('category_list.txt', 'a') as f:
                    f.write(f'{unidecode(cat.title)}\n')

            except requests.exceptions.ConnectionError as e:
                print(f"Connection error: {e}. Retrying...")
                time.sleep(5)  # Wait for 5 seconds before moving on

    except Exception as e:
        print(f"Error: {e}")
        print("pausing for 5 seconds...")
        time.sleep(5)  # Wait for 5 seconds before moving on


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
            print(f" Error: {e} (special characters in title)")

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

    # Load the list of categories
    done_list = []
    try:
        with open('category_list.txt', 'r') as f:
            category_list = f.read().splitlines()
    except FileNotFoundError:
        pass

    # Start the process
    random.shuffle(main_categories)

    for category in main_categories:
        get_categories(
            wiki_wiki.page(f"Category:{category}"),
            max_depth=10,
            randomize=True
        )
