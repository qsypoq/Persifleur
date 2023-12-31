#!/usr/bin/python

import markdown
import os
import errno
from pathlib import Path
from jinja2 import Environment, FileSystemLoader
from distutils.dir_util import copy_tree
from bs4 import BeautifulSoup
import readtime

### Clean old renders
os.system(f"rm -rf html/*")

def check_exist(path):
    if not os.path.exists(path):
        try:
            os.makedirs(path, exist_ok=True)
        except OSError as exc: # Guard against race condition
            if exc.errno != errno.EEXIST:
                raise

def render_medias(folder, target_path):
    fromDirectory = f"sources/{folder}medias"
    toDirectory = f"html/{target_path}medias"
    check_exist(toDirectory)
    copy_tree(fromDirectory, toDirectory)

def render_assets():
    fromDirectory = f"assets"
    toDirectory = f"html/assets"
    check_exist(toDirectory)
    copy_tree(fromDirectory, toDirectory)

def add_redirect(old_url, new_url):
    with open('html/.htaccess', 'a+') as htfile:
        htfile.write(f"\nRedirect 301 {old_url} {new_url}")

render_assets()

template_env = Environment(loader=FileSystemLoader(searchpath='./assets'))
template_home = template_env.get_template('home.html')
template_post = template_env.get_template('layout.html')
template_page = template_env.get_template('page.html')
template_htaccess = template_env.get_template('htaccess')

md = markdown.Markdown(extensions=['fenced_code', 'meta', 'pymdownx.tilde'])

### Render htaccess
with open('html/.htaccess', 'w+') as file:
    file.write(template_htaccess.render())

### Render Posts
POSTS = {}
for path in Path('sources/articles').rglob('*.md'):
    page = str(path)
    with open(page, 'r') as current_page:
        text = current_page.read()
        article = md.convert(text)

    if md.Meta:
        if md.Meta['draft'][0] == 'False':

            source = page.split("/", 1)
            target_path = page.split("/", 3)[3][:-8]
            folder = f"{source[1][:-8]}"
            target = f"html/{target_path}/index.html"
            
            render_medias(folder, target_path)

            ### Insert extra meta
            intro = str(BeautifulSoup(article[0:250], features="html.parser").text).split("\n", 1)
            md.Meta['summary'] = intro[0]
            md.Meta['slug'] = target_path
            md.Meta['timeread'] = readtime.of_text(article).text
            POSTS[page] = md.Meta

            with open(f"{target}", 'w+') as x:
                x.write(template_post.render(
                    title=md.Meta['title'][0],
                    cover=md.Meta['cover'][0],
                    date=md.Meta['date'][0],
                    article=article
                ))

            ### Render 301 if needed
            if 'oldurl' in md.Meta:
                add_redirect(f"{md.Meta['oldurl'][0]}", f"/{md.Meta['slug']}")

### Render Home
POSTS = {
    post: POSTS[post] for post in sorted(POSTS, key=lambda post: POSTS[post]['date'], reverse=True)
}
posts_metadata = [POSTS[post] for post in POSTS]

with open('html/index.html', 'w+') as file:
    file.write(template_home.render(posts=posts_metadata))

### Render Pages
for path in Path('sources/pages').rglob('*.md'):
    page = str(path)
    with open(page, 'r') as current_page:
        text = current_page.read()
        article = md.convert(text)

    if md.Meta:
        if md.Meta['draft'][0] == 'False':
            source = page.split("/", 1)
            target_path = page.split("/", 2)[2][:-8]
            folder = f"{source[1][:-8]}"
            target = f"html/{target_path}/index.html"

            render_medias(folder, target_path)

            with open(f"{target}", 'w') as x:
                x.write(template_page.render(
                    title=md.Meta['title'][0],
                    cover=md.Meta['cover'][0],
                    article=article
                ))
