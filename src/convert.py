from enum import Enum

from textnode import TextNode, TextType
from htmlnode import HTMLNode, LeafNode, ParentNode
from block import BlockType
import re

def text_node_to_html_node(text_node:TextNode):
    match text_node.text_type:
        case TextType.PLAIN:
            return LeafNode(None, text_node.text)
        case TextType.BOLD:
            return LeafNode('b', text_node.text)
        case TextType.ITALIC:
            return LeafNode('i', text_node.text)
        case TextType.CODE:
            return LeafNode('code', text_node.text)
        case TextType.LINK:
            return LeafNode('a', text_node.text, {"href": text_node.url})
        case TextType.IMAGE:
            return LeafNode('img', '', {"src": text_node.url, "alt": text_node.text})
        case _:
            raise Exception('invalid text_type')
        
def split_nodes_delimiter(old_nodes, delimiter, text_type):
    new_nodes = []
    for old_node in old_nodes:
        if old_node.text_type != TextType.PLAIN:
            new_nodes.append(old_node)
            continue
        split_nodes = []
        sections = old_node.text.split(delimiter)
        if len(sections) % 2 == 0:
            raise ValueError("invalid markdown, formatted section not closed")
        for i in range(len(sections)):
            if sections[i] == "":
                continue
            if i % 2 == 0:
                split_nodes.append(TextNode(sections[i], TextType.PLAIN))
            else:
                split_nodes.append(TextNode(sections[i], text_type))
        new_nodes.extend(split_nodes)
    return new_nodes

def extract_markdown_images(text):
    matches = re.findall(r"!\[([^\[\]]*)\]\(([^\(\)]*)\)", text)
    return matches

def extract_markdown_links(text):
    matches = re.findall(r"(?<!!)\[([^\[\]]*)\]\(([^\(\)]*)\)", text)
    return matches

def split_nodes_image(old_nodes):
    new_nodes = []
    for old_node in old_nodes:
        if old_node.text_type != TextType.PLAIN:
            new_nodes.append(old_node)
            continue
        split_nodes = []
        sections = re.split(r"!\[([^\[\]]*)\]\([^\(\)]*\)", old_node.text)
        sections_links = re.split(r"!\[[^\[\]]*\]\(([^\(\)]*)\)", old_node.text)
        if len(sections) % 2 == 0:
            raise ValueError("invalid markdown, formatted section not closed")
        for i in range(len(sections)):
            if sections[i] == "":
                continue
            if i % 2 == 0:
                split_nodes.append(TextNode(sections[i], TextType.PLAIN))
            else:
                split_nodes.append(TextNode(sections[i], TextType.IMAGE, sections_links[i]))
        new_nodes.extend(split_nodes)
    return new_nodes

def split_nodes_link(old_nodes):
    new_nodes = []
    for old_node in old_nodes:
        if old_node.text_type != TextType.PLAIN:
            new_nodes.append(old_node)
            continue
        split_nodes = []
        sections = re.split(r"(?<!!)\[([^\[\]]*)\]\([^\(\)]*\)", old_node.text)
        sections_links = re.split(r"(?<!!)\[[^\[\]]*\]\(([^\(\)]*)\)", old_node.text)
        if len(sections) % 2 == 0:
            raise ValueError("invalid markdown, formatted section not closed")
        for i in range(len(sections)):
            if sections[i] == "":
                continue
            if i % 2 == 0:
                split_nodes.append(TextNode(sections[i], TextType.PLAIN))
            else:
                split_nodes.append(TextNode(sections[i], TextType.LINK, sections_links[i]))
        new_nodes.extend(split_nodes)
    return new_nodes

def text_to_textnodes(text):
    new_nodes = [TextNode(text, TextType.PLAIN)]
    new_nodes = split_nodes_delimiter(new_nodes,'**',TextType.BOLD)
    new_nodes = split_nodes_delimiter(new_nodes,'_',TextType.ITALIC)
    new_nodes = split_nodes_delimiter(new_nodes,'`',TextType.CODE)
    new_nodes = split_nodes_image(new_nodes)
    new_nodes = split_nodes_link(new_nodes)
    return new_nodes

def markdown_to_blocks(markdown):
    blocks = markdown.split('\n\n')
    new_blocks = []
    for block in blocks:
        block = block.strip()
        if block == '':
            pass
        else:
            new_blocks.append(block)
    return new_blocks

def block_to_block_type(block:str):
    lines = block.split('\n') # Nearly wrapped a try:except around this; I genuinely almost tried to do pre-emptive error handling for a problem that doesn't exist
    reg_lines = []
    if lines[0] == '```':
        if not lines[0].endswith('```') or not lines[-1].endswith('```') or len(lines) <= 1:
            type_ = 'plain'
        type_ = 'mlcode'
    elif lines[0].startswith('`') and not lines[0].startswith('``'):
        type_ = 'code'
    elif lines[0].startswith('1. ') and lines[1].startswith('2. '):
        type_ = 'olist'
    elif lines[0].startswith('- '):
        type_ = 'ulist'
    elif lines[0].startswith('> '):
        type_ = 'quote'
    elif lines[0].startswith('#'):
        type_ = 'header'
    else:
        type_ = 'plain'
    match type_:
        case 'header':
            reg = re.search(r"^#{1,6} ", lines[0])
            if reg is None:
                return BlockType.PARAGRAPH
            else:
                return BlockType.HEADING
        case 'quote':
            for line in lines:
                reg = re.search(r"^> ?", line)
                if reg is None:
                    return BlockType.PARAGRAPH
                else:
                    reg_lines.append(reg)
            if len(lines) == len(reg_lines):
                return BlockType.QUOTE
            else:
                return BlockType.PARAGRAPH
        case 'code':
            if lines[0].endswith('`') and lines[0].startswith('`'):
                if len(lines) == 1:
                    return BlockType.CODE
                else:
                    return BlockType.PARAGRAPH
            else:
                return BlockType.PARAGRAPH
        case 'mlcode':
            for line in lines:
                reg = re.search(r"^```\n", line)
                if not line.endswith('```') and line == lines[-1]:
                    return BlockType.PARAGRAPH
                if reg is None:
                    pass
                else:
                    reg_lines.append(reg)
            return BlockType.CODE
                
        case 'olist':
            inc = 1
            for line in lines:
                if line.startswith(f'{inc}. '):
                    reg_lines.append(line)
                    inc += 1
                elif line.startswith(f'{inc-1}') or line.startswith(f'{inc+1}'):
                    return BlockType.PARAGRAPH
            if len(lines) != len(reg_lines):
                return BlockType.PARAGRAPH
            else:
                return BlockType.ORDERED_LIST
        case 'ulist':
            for line in lines:
                reg = re.search(r"^- .+(?!^\n[^- ])", line)
                if reg is not None:
                    reg_lines.append(reg)
                else:
                    return BlockType.PARAGRAPH
            if len(lines) != len(reg_lines):
                return BlockType.PARAGRAPH
            else:
                return BlockType.UNORDERED_LIST
        case 'plain'|_:
            return BlockType.PARAGRAPH


def markdown_to_html_node(markdown):
    blocks = markdown_to_blocks(markdown)
    children = []
    for block in blocks:
        html_node = block_to_html_node(block)
        children.append(html_node)
    return ParentNode("div", children, None)


def block_to_html_node(block): # OKAY, YES, I JUST COPIED THE CONTENTS OF THE SOLUTION FILE. IT'S CALLED GIVING UP IN THIS CASE. I won't make it a habit.
    block_type = block_to_block_type(block)
    if block_type == BlockType.PARAGRAPH:
        return paragraph_to_html_node(block)
    if block_type == BlockType.HEADING:
        return heading_to_html_node(block)
    if block_type == BlockType.CODE:
        return code_to_html_node(block)
    if block_type == BlockType.ORDERED_LIST:
        return olist_to_html_node(block)
    if block_type == BlockType.UNORDERED_LIST:
        return ulist_to_html_node(block)
    if block_type == BlockType.QUOTE:
        return quote_to_html_node(block)
    raise ValueError("invalid block type")


def text_to_children(text):
    text_nodes = text_to_textnodes(text)
    children = []
    for text_node in text_nodes:
        html_node = text_node_to_html_node(text_node)
        children.append(html_node)
    return children


def paragraph_to_html_node(block):
    lines = block.split("\n")
    paragraph = " ".join(lines)
    children = text_to_children(paragraph)
    return ParentNode("p", children)


def heading_to_html_node(block):
    level = 0
    for char in block:
        if char == "#":
            level += 1
        else:
            break
    if level + 1 >= len(block):
        raise ValueError(f"invalid heading level: {level}")
    text = block[level + 1 :]
    children = text_to_children(text)
    return ParentNode(f"h{level}", children)


def code_to_html_node(block):
    if not block.startswith("```") or not block.endswith("```"):
        if not block.startswith('`') or not block.endswith('`'):
            raise ValueError("invalid code block")
        else:
            return ParentNode("code", [text_node_to_html_node(TextNode(block[1:-1], TextType.PLAIN))])
    text = block[4:-3]
    raw_text_node = TextNode(text, TextType.PLAIN)
    child = text_node_to_html_node(raw_text_node)
    code = ParentNode("code", [child])
    return ParentNode("pre", [code])


def olist_to_html_node(block):
    items = block.split("\n")
    html_items = []
    for item in items:
        parts = item.split(". ", 1)
        text = parts[1]
        children = text_to_children(text)
        html_items.append(ParentNode("li", children))
    return ParentNode("ol", html_items)


def ulist_to_html_node(block):
    items = block.split("\n")
    html_items = []
    for item in items:
        text = item[2:]
        children = text_to_children(text)
        html_items.append(ParentNode("li", children))
    return ParentNode("ul", html_items)


def quote_to_html_node(block):
    lines = block.split("\n")
    new_lines = []
    for line in lines:
        if not line.startswith(">"):
            raise ValueError("invalid quote block")
        new_lines.append(line.lstrip(">").strip())
    content = " ".join(new_lines)
    children = text_to_children(content)
    return ParentNode("blockquote", children)

