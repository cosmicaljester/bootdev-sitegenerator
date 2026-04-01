from convert import markdown_to_html_node
import shutil
import os
import sys

try:
    basepath = sys.argv[1]
except KeyError, IndexError:
    basepath = '/'

def extract_title(markdown):
    blocks = markdown.split('\n')
    for line in blocks:
        if not line.startswith('# '):
            pass
        else:
            return line[2:].strip()
    raise Exception('no header in markdown')

def generate_page(from_path, template_path, dest_path):
    print('Generating page from {} to {} using {}'.format(from_path, dest_path, template_path))
    with open(from_path, mode='r', encoding='utf-8') as hellfile:
        markdown = hellfile.read()
    with open(template_path, mode='r', encoding='utf-8') as templatefile:
        template = templatefile.read()
    node = markdown_to_html_node(markdown).to_html()
    title = extract_title(markdown)
    template = template.replace('{{ Title }}', title)
    template = template.replace('{{ Content }}', node)
    template = template.replace('href="/', f'href="{basepath}')
    template = template.replace('src="/', f'src="{basepath}')
    path = dest_path.split('/')
    if not os.path.exists('/'.join(path[:-1])):
        os.makedirs('/'.join(path[:-1]), exist_ok=True)
    with open(dest_path, mode='w', encoding='utf-8') as destfile:
        destfile.write(template)

def generate_pages_recursive(dir_path_content, template_path, dest_dir_path):
    static = os.listdir(dir_path_content)
    if len(static) == 0:
        return True
    for item in static:
        if '.md' in item:
            generate_page(os.path.join(dir_path_content, item), template_path, os.path.join(dest_dir_path, f'{item[:-2]}html'))
        else:
            newpath = os.path.join(dir_path_content, item)
            newtarget = os.path.join(dest_dir_path, item)
            os.makedirs(newtarget, exist_ok=True)
            generate_pages_recursive(newpath, template_path, newtarget)


def copy_static(path=os.getcwd(), target=os.getcwd()):
    if path == os.getcwd():
        if 'src' in os.getcwd():
            os.chdir('..')
        if os.path.exists('./docs'):
            shutil.rmtree('./docs')
        os.mkdir('./docs')
        newpath = os.path.join(path, 'static')
        newtarget = os.path.join(target, 'docs')
        if copy_static(newpath, newtarget):
            return True
    else:
        static = os.listdir(path)
        if len(static) == 0:
            return True
        for item in static:
            if '.' in item:
                shutil.copy(os.path.join(path, item), os.path.join(target, item))
            else:
                newpath = os.path.join(path, item)
                newtarget = os.path.join(target, item)
                os.makedirs(newtarget, exist_ok=True)
                copy_static(newpath, newtarget)

    

def main():
    copy_static()
    generate_pages_recursive('content', 'template.html', 'docs')

main()