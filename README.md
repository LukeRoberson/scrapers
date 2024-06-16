# Wikipedia Scraper

## Purpose
A python script that uses the wikipedia API to collect Wikipedia pages as text files.

The purpose behind this is to collect text documents that can be used to train a Transformer model. However, this could be used for other purposes too.

## Categories
Wikipedia contains eight main categories, and many many subcategories. The main categories are:
* Science
* Everyday_life
* Geography
* History
* Knowledge
* Literature
* People
* Religion

This script starts at the root of each of these categories, and gets pages within. It then recursively finds the subcategories, and gets pages within those. This continues until the **max_depth** has been reached. This is the maximum level of recursion, and is set to 5 by default.

Setting the **max_depth** value too high will eventually cause python to hit its internal limit, causing the script to crash.

Many pages are in multiple categories, so it's generally not needed to go to the extremities of the wikipedia sub-categories to get a large sample of wikipedia pages.

## File Names
The script reads an article, and saves it as a text file in the /data/ folder. The filename matches the title of the article.

There are some exceptions to this:
* Unicode characters in the filename are converted to simple ASCII characters
* Articles with special characters (such as a '?' that cannot be saved in a file name) are skipped

## Article Size
Any article that is less than 2000 bytes (that is, 2000 characters) is ignored.

This is so we only get articles of a size that are useful to transformers to train on.

## Cleaning
Article cleanup is on by default, but can be disabled. This cleans the contents of the article to make it more suitable for training transformers.

It may be desirable to disable this if the articles are used for some other purpose.

The cleaning process:
* Concerts unicode characters to regular ASCII characters
* Is case-based (it does not convert to lower case, which some transformer models may prefer)
* It removes additional sources, external links, further reading, and so on that may be listed at the end of the article
* It removes cases of sequential one-word lines, which indicate a list of some sort
* Removes lines containing 'wikimedia' which usually refer to an image or another file (not present in text form)

There is a list called **avoid_words**. Any article with one of these words in the title is skipped. This can be used to skip articles with 'outline' and similar words in the title, which are usually just lists.

## Page lists

Two text files are maintained:
* page_list.txt - Contains a list of pages that are already downloaded, so they can be skipped
* small_pages.txt - Contails a list of pages known to be too small, so they can be skipped


# Usage
Just run the script as it is to start downloading pages.

Optionally, set **clean=False** when calling save_page() to prevent cleaning the contents of the file

Add or remove words to/from the **avoid_words** list to skip certain articles.

Change the article size (default is 2000) to define the size of an article that is too small to bother with.

Alternatively, you could use the pre-existing page_list.txt to just download a list of known good pages. This would require some small editing of the script

Call the function with 'randomize=True' to randomise the contents of categories when they are processed. This might help when resuming, so it's not always in the same order.
