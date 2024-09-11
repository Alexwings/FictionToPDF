from ebooklib import epub
from typing import List
BOOK_TITLE='剑来'
AUTHOR='烽火戏诸侯'


def html_body_wrapper(content):
    html_format = f'<html><body lang="zh">{content}</body></html>'
    return html_format
def html_chapter_header_wrapper(title):
    header = f'<h2>{title}</h2>'
    return header
def read_chapter(file_name) -> List[(str, List[str])]:
    print('Reading content...')
    BOOK_TITLE = file_name
    title = ''
    chapters = []
    with open(f'output/{file_name}.md') as file:
        line = file.readline()
        contents = []
        while line:
            if line == '\n':
                line = file.readline()
                continue
            if line.endswith("\n"):
                line = line.replace("\n", "")
            if line.startswith('### '):
                title = line.removeprefix('### ')
            elif line.startswith('---'):
                chapters.append((title, list(contents)))
                contents = []
            else:
                contents.append(line)
            line = file.readline()
    return chapters

def create_epubs(chapters: List[(str, List[str])]) -> None:
    links = []
    chapter_items = []
    book = epub.EpubBook()

    book.set_identifier(f'epub-practice-convertor-{BOOK_TITLE}')
    book.set_title(BOOK_TITLE)
    book.set_language('zh')
    book.add_author(AUTHOR)
    print('Constructing ebook objects...')
    for index, (title, content) in enumerate(chapters):
        file_name = f'text/chapter_{index + 1}.xhtml'
        body_content = html_chapter_header_wrapper(title)
        print(f'Generating chapter {title}')
        num = 1
        for p in content:
            print('\r', end='')
            print(f'Appending content: {num}', end='')
            body_content += f'<p>{p}</p>'
            num += 1
        body = html_body_wrapper(body_content)
        print(f"\nCreating chapter html.")
        chapter = epub.EpubHtml(title=title, file_name=file_name, content=body, lang='zh')
        book.add_item(chapter)
        chapter_items.append(chapter)
        links.append(epub.Link(href=file_name,title=title,uid=f'chaper_{index + 1}'))
    book.toc = links
    book.spine = ['nav'] + chapter_items
    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())

    # 定义 CSS 样式
    style = b'body {"color": "wheat"; "text-align": "center"}'
    nav_css = epub.EpubItem(uid="style_nav", file_name="style/nav.css", media_type="text/css", content=style)
    book.add_item(nav_css)
    print('Writing to disk...')
    epub.write_epub(f'output/{BOOK_TITLE}.epub', book)
