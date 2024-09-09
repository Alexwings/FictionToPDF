from fpdf import FPDF
from typing import Literal, List
import os
import math

A4_PAGE_HEIGHT = 297
A4_PAGE_WIDTH = 210
PAGE_VERTICAL_PADDING = 20
PAGE_HORIZONTAL_PADDING = 15
CONTENT_LINE_HEIGHT = 10
TITLE_LINE_HEIGHT = 15
TITLE_FONT_SIZE = 24
TITLE_CONTENT_PADDING = 10

class StructuredPDFFont:
    def __init__(self, font_name:str, font_size:int, font_file:str=None) -> None:
        self.font_name = font_name
        self.font_size = font_size
        if font_file == 'system':
            self.font_file = None
        else: 
            self.font_file = font_file

class StructuredPDFConfiguration:
    def __init__(self, header_font: StructuredPDFFont = None, footer_font: StructuredPDFFont = None, content_font: StructuredPDFFont = None) -> None:
        self.header_font = header_font
        self.footer_font = footer_font
        self.content_font = content_font

    def set_content_line_height(self, height:float):
        self.content_line_height = height

    def set_header_height(self, height:float):
        self.header_height = height
    def set_footer_height(self, height:float):
        self.footer_height = height

class PDFPage:
    def __init__(self, title:str, contents:List[str], page_num=0):
        self.title = title
        self.contents = contents
        self.page_num = page_num

    def get_footer(self) -> None:
        return None

class StructuredPDF(FPDF):

    def __init__(self, configuration:StructuredPDFConfiguration, orientation: Literal[''] | Literal['portrait'] | Literal['p'] | Literal['P'] | Literal['landscape'] | Literal['l'] | Literal['L'] = "portrait", unit: float | Literal['pt'] | Literal['mm'] | Literal['cm'] | Literal['in'] = "mm", format: tuple[float, float] | Literal[''] | Literal['a3'] | Literal['A3'] | Literal['a4'] | Literal['A4'] | Literal['a5'] | Literal['A5'] | Literal['letter'] | Literal['Letter'] | Literal['legal'] | Literal['Legal'] = "A4", font_cache_dir: Literal['DEPRECATED'] = "DEPRECATED") -> None:
        super().__init__(orientation, unit, format, font_cache_dir)
        self._config = configuration
        if configuration.header_font.font_file is not None:
            self.add_font(family=configuration.header_font.font_name, fname=configuration.header_font.font_file)
        if configuration.footer_font.font_file is not None:
            self.add_font(family=configuration.footer_font.font_name, fname=configuration.footer_font.font_file)
        if configuration.content_font.font_file is not None:
            self.add_font(family=configuration.content_font.font_name, fname=configuration.content_font.font_file)
        self._cur_page:PDFPage = None
    
    @property
    def default_footer(self) -> str:
        return f'{self.page_no()}/{self.pages_count}'

    def header(self) -> None:
        if self._cur_page is not None:
            self.set_font(family=self._config.header_font.font_name, size=self._config.header_font.font_size)
            y = PAGE_VERTICAL_PADDING
            x = PAGE_HORIZONTAL_PADDING
            width = A4_PAGE_WIDTH - 2 * PAGE_HORIZONTAL_PADDING
            self.set_y(y)
            self.set_x(x)
            if self._config.header_height is not None:
                self.cell(w=width, h=self._config.header_height, text=self._cur_page.title,align='L')
            else: 
                self.cell(w=width, text=self._cur_page.title,align='L')
        # else: #print warning
    
    def footer(self) -> None:
        if self._cur_page is not None:
            self.set_font(family=self._config.footer_font.font_name, size=self._config.footer_font.font_size)
            y = A4_PAGE_HEIGHT - PAGE_VERTICAL_PADDING
            x = PAGE_HORIZONTAL_PADDING
            self.set_y(y)
            self.set_x(x)
            width = A4_PAGE_WIDTH - 2 * PAGE_HORIZONTAL_PADDING
            footer = self._cur_page.get_footer()
            if footer is None:
                footer = self.default_footer
            if self._config.footer_height is not None:
                self.cell(w=width, h=self._config.footer_height, text=footer, align='R')
            else: 
                self.cell(w=width, h=self._config.footer_height, text=footer, align='R')
        # else: #print warning

    def set_current_page(self, page: PDFPage):
        self._cur_page = page
    
    def render_current(self) -> None:
        return None

class ArticalChapter:
    def __init__(self, title:str, contents:List[str]) -> None:
        self.title = title
        self.all_contents = contents

    def set_pages(self, pages: List[PDFPage]):
        self.pages = pages
                
class ArticalPDF(StructuredPDF):
    @property
    def total_page_num(self):
        return len(self.cur_chapter.pages) if self.cur_chapter is not None else 0
    
    @property
    def default_footer(self):
        return f'{self.cur_chapter.title}: {self._cur_page.page_num}/{self.total_page_num}' 

    def add_chapter(self, chapter: ArticalChapter):
        self.cur_chapter = self._parse_chapter(chapter)
        is_first = True
        for page in self.cur_chapter.pages:
            self.render_page(page, is_first)
            is_first = False
            
    def render_page(self,page:PDFPage, is_first_page:bool):
        self._cur_page = page
        self.add_page()
        self.set_x(PAGE_HORIZONTAL_PADDING)
        y = self.get_y() + (self._config.header_height if self._config.header_height is not None else self._config.header_font.size)
        self.set_y(y)
        if is_first_page:
            self.set_font(family=self._config.content_font.font_name, size=TITLE_FONT_SIZE)
            self.cell(w=0,text=page.title, align='C')
            y = self.get_y() + TITLE_CONTENT_PADDING
        self.set_font(family=self._config.content_font.font_name, size=self._config.content_font.font_size)
        for line in page.contents:
            self.set_y(y)
            self.multi_cell(w=A4_PAGE_WIDTH - 2 * PAGE_HORIZONTAL_PADDING, h=self._config.content_line_height, text=line, align='L')
            y = self.get_y()

    def _parse_chapter(self, chapter: ArticalChapter):
        pages:List[PDFPage] = []
        cur_contents: List[PDFPage] = []
        line_num = 0
        page_num = 1
        A4_page_line_num = math.floor(float(A4_PAGE_HEIGHT - 2 * PAGE_VERTICAL_PADDING - self._config.header_height - self._config.footer_height) / float(self._config.content_line_height))
        self.set_font(family=self._config.content_font.font_name, size=self._config.content_font.font_size)
        for line in chapter.all_contents:
            line_string_width = self.get_string_width(line)
            line_width = float(A4_PAGE_WIDTH - 2 * PAGE_HORIZONTAL_PADDING - 2 * self.c_margin)
            string_line_num = math.ceil(line_string_width / line_width) + 1
            if line_num + string_line_num <= A4_page_line_num:
                cur_contents.append(line)
                line_num = line_num + string_line_num
            else:
                page = PDFPage(chapter.title, contents=cur_contents, page_num=page_num)
                pages.append(page)
                page_num = page_num + 1
                cur_contents = [line]
                line_num = string_line_num
        if len(cur_contents) > 0 :
            pages.append(PDFPage(chapter.title, cur_contents))
        chapter.set_pages(pages)
        return chapter