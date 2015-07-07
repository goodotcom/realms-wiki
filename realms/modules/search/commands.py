import click
from realms import create_app, search
from realms.modules.wiki.models import Wiki
from realms.lib.util import filename_to_cname


@click.group(short_help="Search Module")
def cli():
    pass


@cli.command()
def rebuild_index():
    """ Rebuild search index
    """
    app = create_app()

    if app.config.get('SEARCH_TYPE') == 'simple':
        click.echo("Search type is simple, try using elasticsearch.")
        return

    with app.app_context():
        # Wiki
        search.delete_index('wiki')
        wiki = Wiki(app.config['WIKI_PATH'])
        for entry in wiki.get_index():
            assert 'name' in entry
            page = wiki.get_page(entry['name'])
            if not page:
                print "WARNING: skipping '%s'" % entry['name']
                continue
            name = filename_to_cname(page['path'])
            print "indexing page '%s'" % (name)
            # TODO add email?
            body = dict(name=name,
                        content=page['data'],
                        message=page['info']['message'],
                        username=page['info']['author'],
                        updated_on=entry['mtime'],
                        created_on=entry['ctime'])
            search.index_wiki(name, body)
