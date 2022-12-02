"""Parser for Obsidian notes."""
import shutil
import urllib.request
import os
import re
from random import seed,randint
from typing import TypedDict
import frontmatter
# from obsidian_parser import WikiParser




class ObsidianParser:
    """Obsidian Parser class."""

    resourceLink = TypedDict("ResourceLink", {"source": str, "link": str, "text": str})

    def __init__(self, obsidian_vault_dir: str, vault_content_dir: str, hugo_content_dir: str):
        """Initialize ObsidianParser."""
        self.obsidian_vault_dir = obsidian_vault_dir
        self.vault_content_dir = vault_content_dir
        self.hugo_content_dir = hugo_content_dir



    def process(self, erase_hugo_content: bool) -> None:
        """
        Process the obsidian vault and convert it to hugo ready content.

        Delete the hugo content directory and copy the obsidian vault to the
        hugo content directory, then process the content so that the wiki links
        are replaced with the hugo links.

        :param erase_hugo_content: Whether to erase the hugo content directory.
        :type erase_hugo_content: bool
        """
        if erase_hugo_content:
            self.clear_hugo_content_dir()
        notes = self.get_notes_to_export(None)
        for note in notes:
            self.process_note(note)
        


    def clear_hugo_content_dir(self) -> None:
        """
        Delete the all the atrifacts currently in the Hugo content folder.

        NOTE: The folder itself gets deleted and recreated.
        """
        print("Clearing hugo content folder...")
        shutil.rmtree(self.hugo_content_dir)
        os.makedirs(self.hugo_content_dir, exist_ok=True)


    def get_notes_to_export(self, hashtag: str) -> list[str]:
        """
        Check the Obsidian vault, and return a list of notes to export.

        If a hashtag is provided, only notes with that hashtag will be returned.

        :param hashtag: The hashtag to filter by.
        :type hashtag: str

        :return: A list of notes URI's to export.
        :rtype: list[str]
        """
        print("Enumerating Note to process...")
        notes_list = []
        # Get list of all notes in the vault.
        for root, dirs, files in os.walk(os.path.join(self.obsidian_vault_dir, self.vault_content_dir)):
            for file in files:
                if file.endswith(".md"):
                    if hashtag:
                        #TODO: the file needs to be read to check for the hashtag.
                        tags = self.get_note_hashtags(os.path.join(root, file))
                        if hashtag in tags:
                            notes_list.append(os.path.join(root, file))  # type: ignore
                    else:
                        notes_list.append(os.path.join(root, file))
                    
        return notes_list


    def process_note(self, note: str) -> None:
        """
        Process a single note.

        :param note: The note to process.
        :type note: str
        """
        print(f"Processing note: {note}")
        hugo_page = self.transfer_obsidian_note(note)
        self.retrieve_bundle_assets(hugo_page)
        self.reformat_article(hugo_page)



    def transfer_obsidian_note(self, note:str) -> str:
        """Transfer the Obsidian Note to Hugo Page Bundle.
        
        Copy the Obsidian Note to the Hugo Content folder, and create a page bundle for it.

        :param note: The File URI of the Obsidian note to transfer.
        :type note: str

        :return: The File URI of the Hugo page bundle.
        :rtype: str
        """
        # Create the page bundle directory.
        page_bundle_dir = os.path.join(
            self.hugo_content_dir,
            os.path.basename(note).rsplit('.', maxsplit=1)[0]
        )
        os.makedirs(page_bundle_dir, exist_ok=True)
        # Copy the markdown file.
        shutil.copy(
            os.path.join(note),
            os.path.join(page_bundle_dir, "index.md"),
        )
        print(f"  Created Hugo Bundle: `{page_bundle_dir}`")

        return os.path.join(page_bundle_dir, "index.md")



    def get_note_hashtags(self, text: str) -> list[str]:
        """Get all hashtags from the given text and return a list of them."""
        hashtag_regex = r"#(\w+)"
        hashtag_list = re.findall(hashtag_regex, text)
        return hashtag_list

        
    
    def get_note_images(self, text: str) -> list[resourceLink]:
        """Find all image links in the given text and return a list of them."""
        image_links = []
    
        # Find all image links in the text
        # Wiki link: [[image.png]] or [[image.png|text]]
        image_link_regex = r"!\[\[(.*?)\]\]"  
        for match in re.finditer(image_link_regex, text):
            out = {
                "source": match.group(),
            }
    
            if "|" in match.group(1):
                out["link"], out["text"] = match.group(1).split("|")
            else:
                out["link"] = match.group(1)
                out["text"] = match.group(1)
    
            image_links.append(out)

        # Markdown Link: ![image.png](image.png)
        image_link_regex = r"!\[(.*)\]\((.*)\)"  # HTML Image Link
        for match in re.finditer(image_link_regex, text):
            out = {
                "source": match.group(),
            }
    
            out["link"] = match.group(2)
            out["text"] = match.group(1)
    
            image_links.append(out)
    
        return image_links


    seed(1)

    def retrieve_bundle_assets(self, hugo_page: str) -> None:
        """Retrieve the assets from the Obsidian Note and copy them to the Hugo Page Bundle."""
        hugo_bundle_dir = os.path.dirname(hugo_page)
        print(f"  Retrieving vault assets for Hugo bundle")

        # Read the file.
        with open(hugo_page, "r") as note:
            note_content = note.read()
        # Get the assets from the Obsidian Note.
        
        links = self.get_note_images(note_content)

        for link in links:
            # Copy the Asset to the Hugo Page Bundle.
            if ("http" not in link["link"]):
                image_source_path = os.path.join(self.obsidian_vault_dir, link["link"])
                print(f"    Transferring image {image_source_path}")
                try:
                    shutil.copy(image_source_path, os.path.join(hugo_bundle_dir))
                    link["link"] = os.path.basename(link["link"])
                except FileNotFoundError:
                    print(f"    Error: Vault Image not found '{image_source_path}', skipped...")
                    link["link"] = "opps-missing-image.png"
            else:
                print(f"    Downloading image '{link['link']}'")
                asset_name = 'web' + str(randint(0,10000)) +'_' + link['link'].split("/")[-1]
                asset_uri = os.path.join(os.path.join(hugo_bundle_dir),asset_name)
                try:
                    with urllib.request.urlopen(link['link']) as responese:
                        with open(asset_uri,'wb') as asset:
                            shutil.copyfileobj(responese, asset)
                    link["link"] = asset_name
                except Exception as e:
                    print(f"    Error: Downloading image '{link['link']}' failed, {e} ")
                    link["link"] = "opps-missing-image.png"
                    
            # Update the link in the Hugo Page.
            hugo_link = f'![{link["text"]}]({link["link"]})' # HTML Link
            hugo_link = f'![[{link["link"]}|{link["text"]}]]' # Wiki Link
            wiki_link = link["source"]
            note_content = note_content.replace(wiki_link, hugo_link)

            # Write the Updated Page content.
            with open(os.path.join(hugo_page), "w", encoding = "utf-8") as f:
                        f.write(note_content)
            

    WikiLink = TypedDict("WikiLink", {"wiki_link": str, "link": str, "text": str})

    def get_wiki_links(self, text: str) -> list[WikiLink]:
        """
        Get all wiki links from the given text and return a list of them.
        Each list item is a dictionary with the following keys:
        - wiki_link: the exact match
        - link: the extracted link
        - text: the possible extracted text
        """
        wiki_links = []
        wiki_link_regex = r"\[\[(.*?)\]\]"
        for match in re.finditer(wiki_link_regex, text):
            out = {
                "wiki_link": match.group(),
            }


            if "|" in match.group(1):
                out["link"], out["text"] = match.group(1).split("|")
            else:
                out["link"] = match.group(1)
                out["text"] = match.group(1)

            # Check the Links resolve correctly
            if out["link"].startswith(self.vault_content_dir):
                out["link"] = out["link"][len(self.vault_content_dir) + 1 :]

            # if the link ends with `_index` remove it
            if out["link"].endswith("_index"):
                out["link"] = out["link"][:-6]

            if out["text"].startswith(self.vault_content_dir):
                out["text"] = out["text"][len(self.vault_content_dir) + 1 :]

            wiki_links.append(out)
        return wiki_links


    def wiki_link_to_hugo_link(self, wiki_link: WikiLink) -> str:
        """
        Convert the wiki link into a hugo link.
        """
        # if the links contains a link to a heading, convert the heading part to
        # lower case and replace spaces by minus

        link_seperated = wiki_link["link"].split("#", 1)
        if len(link_seperated) > 1:
            link_combined = "#".join(
                [link_seperated[0], link_seperated[1].lower().replace(" ", "-")]
            )
        else:
            link_combined = wiki_link["link"]
        #hugo_link = f'[{wiki_link["text"]}]({{{{< ref "{link_combined}" >}}}})'
        hugo_link = f'[{wiki_link["text"]}]({link_combined})'
        return hugo_link


    def replace_wiki_links(self, text: str) -> str:
        """
        Replace all wiki links in the given text with hugo links.
        """
        links = self.get_wiki_links(text)
        for link in links:
            hugo_link = self.wiki_link_to_hugo_link(link)
            text = text.replace(link["wiki_link"], hugo_link)
        return text


    def check_frontmatter(self, hugo_page: str):
        post = frontmatter.loads(hugo_page)

        post_body = post.content
        #first_heading = re.search(r"^# (.*)", post.content, re.MULTILINE)
        title_heading = re.search(r"^# (.*)", post.content, re.MULTILINE)
        if title_heading:
            title_heading = title_heading.group(1)
            print('First Match = {}'.format(title_heading))
            post_body = post_body.replace(f'# {title_heading}\n', '')
        else:
            print('Not Found')


        newpost  = f"---\n"
        
        newpost += f"title: {post['title']}\n" if 'title' in post.keys() else  f"title: {title_heading}\n"
        newpost += f"type: {post['type']}\n" if 'type' in post.keys() else  f"type: article \n"
        if 'subtitle' in post.keys(): newpost += f"subtitle: {post['subtitle']}\n"
        if 'date' in post.keys(): newpost += f"date: {post['date']}\n"
        if 'toc' in post.keys(): newpost += f"toc: {post['toc']}\n"
        if 'years' in post.keys(): newpost += f"year: {post['years']}\n"
        if 'series' in post.keys(): newpost += f"series: {post['series']}\n"
        newpost += f"categories: {post['categories']}\n" if 'categories' in post.keys() else  f"categories: ['todo'] \n"
        if 'tags' in post.keys(): 
            newpost += f"tags: {post['tags']}\n" if post['tags'] != [] else  f"tags: ['untagged'] \n"
        else:
            newpost += f"tags: ['untagged'] \n"
        newpost += f"draft: {post['draft']}\n" if 'draft' in post.keys() else  f"draft: false \n"
        if 'lastmod' in post.keys(): newpost += f"lastmod: {post['lastmod']}\n"
        if 'url' in post.keys(): newpost += f"url: {post['url']}\n"
        if 'image' in post.keys(): newpost += f"image: {post['image']}\n"
        newpost += f"toc: {post['toc']}\n" if 'toc' in post.keys() else  f"toc: false \n"
        newpost += f"comments: {post['comments']}\n" if 'comments' in post.keys() else  f"comments: false \n"
        newpost += f"---\n\n"
        newpost += post_body
        return newpost

    def reformat_article(self, hugo_page: str) -> None:
        """Reformat the Hugo Page."""
        print(f"  Reformatting Hugo page")

        # Read the file.
        with open(hugo_page, "r") as note:
            note_content = note.read()

        # Replace wiki links with Hugo links.
        #TODO: This creates a ref which includes the complete local uri and not the hugo ref
        note_content = self.replace_wiki_links(note_content)
        tags = self.get_note_hashtags(note_content)
        note_content = self.check_frontmatter(note_content)

        # Write the Updated Page content.
        with open(os.path.join(hugo_page), "w", encoding = "utf-8") as f:
            f.write(note_content)