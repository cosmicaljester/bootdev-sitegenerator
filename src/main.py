from convert import markdown_to_html_node
import shutil
import os

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
    temp = template.split('\n')
    for line in temp:
        if not line.startswith('    <title>') and not line.startswith('    <article>'):
            pass
        elif line.startswith('    <title>'):
            work = line.split(line[11:22])
            work.insert(1,title)
            temp[temp.index(line)] = ''.join(work)
        elif line.startswith('    <article>'):
            work = line.split(line[13:26])
            work.insert(1, node)
            temp[temp.index(line)] = ''.join(work)
    path = dest_path.split('/')
    if not os.path.exists('/'.join(path[:-1])):
        os.makedirs('/'.join(path[:-1]), exist_ok=True)
    with open(dest_path, mode='w', encoding='utf-8') as destfile:
        destfile.write('\n'.join(temp))

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
        if os.path.exists('./public'):
            shutil.rmtree('./public')
        os.mkdir('./public')
        newpath = os.path.join(path, 'static')
        newtarget = os.path.join(target, 'public')
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
    generate_pages_recursive('content', 'template.html', 'public')

main()