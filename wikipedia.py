import wikipediaapi

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

# Create a Wikipedia object
wiki_wiki = wikipediaapi.Wikipedia(
    'Transformer_trainer (luke.robertson@networkdirection.net)',
    'en',
    extract_format=wikipediaapi.ExtractFormat.WIKI
)


# Get subcategories of a given category
def get_categories(category, page_set=None, depth=0):
    if page_set is None:
        page_set = set()
    for c in category.values():
        # Regular pages, add to the list
        if c.ns == wikipediaapi.Namespace.MAIN:
            page_set.add(c.title)

        # Subcategories, dig deeper
        elif c.ns == wikipediaapi.Namespace.CATEGORY:
            print("\033[33m" + "  " * depth + c.title + " - \033[34m" + str(len(page_set)) + "\033[0m")
            get_categories(c.categorymembers, page_set, depth + 1)

    return page_set


def get_pages_list(category):
    cat = wiki_wiki.page(f"Category:{category}")
    all_pages = get_categories(cat.categorymembers)

    # Get some stats
    print(f"List size: {len(all_pages)}")

    # Save the list of pages to a file
    with open(f'{category}_pages.txt', 'w') as f:
        for page in all_pages:
            f.write(page + '\n')


def get_page_details(category):
    page_list = []
    with open(f'{category}_pages.txt', 'r') as f:
        for line in f:
            page_list.append(line.strip())

    for page in page_list:
        page = wiki_wiki.page(page)
        print(page.title)


if __name__ == '__main__':
    for category in main_categories:
        get_pages_list(category)
        get_page_details()
