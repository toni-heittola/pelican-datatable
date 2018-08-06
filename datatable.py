# -*- coding: utf-8 -*-
"""
Datatable plugin for Pelican
============================
Author: Toni Heittola (toni.heittola@gmail.com)

Dynamic HTML tables with visualization from given yaml-file.

"""

from past.builtins import long
import os.path
import shutil
import logging
from pelican import signals, contents
from docutils.parsers.rst import directives
import yaml
import re
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)
__version__ = '0.1.6'

# Default parameter values
datatable_defaults = {
    'source': None,
    'show-chart': 'no',
    'filter-control': 'no',
    'site-url': ''
}


def datatable_md(content):
    """
    Inject datatable into markdown document.
    """
    if isinstance(content, contents.Static):
        return

    soup = BeautifulSoup(content._content, 'html.parser')
    tables = soup.find_all('table', class_='datatable')
    if tables:
        for table in tables:
            html_elements = get_datatable_html(table)

            if html_elements:
                table_html = BeautifulSoup(html_elements['table'], "html.parser")

                if html_elements['js_include']:
                    if u'scripts' not in content.metadata:
                        content.metadata[u'scripts'] = []
                    for element in html_elements['js_include']:
                        if element not in content.metadata[u'scripts']:
                            content.metadata[u'scripts'].append(element)

                if html_elements['css_include']:
                    if u'styles' not in content.metadata:
                        content.metadata[u'styles'] = []
                    for element in html_elements['css_include']:
                        if element not in content.metadata[u'styles']:
                            content.metadata[u'styles'].append(element)

                table.replaceWith(table_html)

    content._content = soup.decode()


def get_datatable_html(table):
    """
    Generate HTML for datatable
    Parameters
    ----------
    table: element
        table [beautifulsoup object]

    Output
    ------
    {
        'table': table_start + table_thead + table_tbody + table_end,
        'js_include': js_include,
        'css_include': css_include
    }

    """

    options = {
        'source': get_attribute(table.attrs, 'yaml', datatable_defaults['source']),
        'css': table['class'],
        'filter-control': boolean(get_attribute(table.attrs, 'filter-control', datatable_defaults['filter-control'])),
        'show-chart': boolean(get_attribute(table.attrs, 'show-chart', datatable_defaults['show-chart']))
    }

    if options['source'] and os.path.isfile(options['source']):
        try:
            with open(options['source'], 'r') as field:
                data = yaml.load(field)

            if 'data' in data:
                data = data['data']

        except ValueError:
            logger.warn('`pelican-datatable` failed to load file [' + str(options['source']) + ']')
            return None
    else:
        logger.warn('`pelican-datatable` failed to load file [' + str(options['source']) + ']')
        return None

    # Table / start
    table_start = "\n"+'<table class="{}" '.format(" ".join(options['css']))

    for attr in table.attrs:
        # mirror data-attributes
        if attr.startswith('data-') and attr != 'data-yaml':
            if attr == 'data-comparison-sets-json':
                table_start += str(attr) + "='" + table.attrs[attr] + "' "
            else:
                table_start += str(attr)+'="' + table.attrs[attr] +'" '

    # Filtering
    if 'filter-control' in options and options['filter-control']:
        table_start += 'data-filter-control="' + boolean_string(options['filter-control']) + '" '
        table_start += 'data-filter-show-clear="true" '

    table_start += ">\n"
    table_end = "</table>\n"

    # Table / thead
    fields_ = []
    fields = {}
    table_thead = "<thead>\n"
    if table.thead:
        for header_row in table.thead.find_all('tr'):
            table_thead += "<tr>\n"
            column_id = -1
            for header in header_row.find_all('th'):
                item = {
                    'field': get_attribute(header.attrs, 'field', None),
                    'rank': boolean(get_attribute(header.attrs, 'rank', 'false')),
                    'value-type': get_attribute(header.attrs, 'value-type', None),
                    'title': header.text,
                }

                if 'colspan' in header.attrs:
                    column_id += int(header.attrs['colspan'])

                elif item['field'] or item['rank']:
                    column_id += 1

                if column_id in fields:
                    while column_id in fields:
                        column_id += 1

                table_thead += str(header)+"\n"  # Echo through

                if item['field'] or item['rank']:
                    fields_.append(item)

                    fields[column_id] = item

            table_thead += "</tr>\n"
    table_thead += "</thead>\n"

    # Table / tbody
    table_tbody = "<tbody>\n"
    for row in data:
        if row:
            table_tbody += '<tr'
            if 'data-row-highlighting' in table.attrs and boolean(table.attrs['data-row-highlighting']):
                if 'row_css' in row and row['row_css']:
                    table_tbody += ' class="'+row['row_css']+'"'

            if 'hline' in row and row['hline']:
                table_tbody += ' data-hline="true"'

            table_tbody += ">\n"
            for f in fields:
                item = fields[f]

                if 'rank' in item and item['rank']:
                    table_tbody += "<td></td>\n"

                elif item['field'] in row:
                    table_tbody += "  <td>"

                    field_value = row[item['field']]
                    if 'value-type' in item and item['value-type']:
                        if item['value-type'].startswith('int'):
                            if field_value is not None:
                                field_value = str(field_value)
                            else:
                                field_value = ''

                        elif item['value-type'].startswith('float1-percentage-interval'):
                            if field_value is None:
                                field_value = ''

                            elif is_interval_format(field_value):
                                numbers = re.findall(r'[+-]?\d+(?:\.\d+)', field_value)
                                if len(numbers) == 3:
                                    field_value = '{value:.1f} ({interval_low:.1f} - {interval_high:.1f})'.format(
                                        value=float(numbers[0]),
                                        interval_low=float(numbers[1]),
                                        interval_high=float(numbers[2]),
                                    )

                                else:
                                    field_value = ""

                        elif item['value-type'].startswith('float2-percentage-interval'):
                            if field_value is None:
                                field_value = ''

                            elif is_interval_format(field_value):
                                numbers = re.findall(r'[+-]?\d+(?:\.\d+)', field_value)
                                if len(numbers) == 3:
                                    field_value = '{value:.2f} ({interval_low:.2f} - {interval_high:.2f})'.format(
                                        value=float(numbers[0]),
                                        interval_low=float(numbers[1]),
                                        interval_high=float(numbers[2]),
                                    )
                                else:
                                    field_value = ""

                        elif item['value-type'].startswith('float3-percentage-interval'):
                            if field_value is None:
                                field_value = ""
                            elif is_interval_format(field_value):
                                numbers = re.findall(r'[+-]?\d+(?:\.\d+)', field_value)
                                if len(numbers) == 3:
                                    field_value = '{value:.3f} ({interval_low:.3f} - {interval_high:.3f})'.format(
                                        value=float(numbers[0]),
                                        interval_low=float(numbers[1]),
                                        interval_high=float(numbers[2]),
                                    )
                                else:
                                    field_value = ""

                        elif item['value-type'].startswith('float4-percentage-interval'):
                            if field_value is None:
                                field_value = ""
                            elif is_interval_format(field_value):
                                numbers = re.findall(r'[+-]?\d+(?:\.\d+)', field_value)
                                if len(numbers) == 3:
                                    field_value = '{value:.4f} ({interval_low:.4f} - {interval_high:.4f})'.format(
                                        value=float(numbers[0]),
                                        interval_low=float(numbers[1]),
                                        interval_high=float(numbers[2]),
                                    )
                                else:
                                    field_value = ''

                        elif item['value-type'].startswith('float1'):
                            if field_value is None:
                                field_value = ''

                            elif isinstance(field_value, (int, long, float, complex)):
                                field_value = '{:.1f}'.format(float(field_value))
                            else:
                                field_value = ''

                        elif item['value-type'].startswith('float2'):
                            if field_value is None:
                                field_value = ''

                            elif isinstance(field_value, (int, long, float, complex)):
                                field_value = '{:.2f}'.format(float(field_value))

                            else:
                                field_value = ''

                        elif item['value-type'].startswith('float3'):
                            if field_value is None:
                                field_value = ''

                            elif isinstance(field_value, (int, long, float, complex)):
                                field_value = '{:.3f}'.format(float(field_value))

                            else:
                                field_value = ''

                        elif item['value-type'].startswith('float4'):
                            if field_value is None:
                                field_value = ''

                            elif isinstance(field_value, (int, long, float, complex)):
                                field_value = '{:.4f}'.format(float(field_value))

                            else:
                                field_value = ''

                        elif item['value-type'] == 'str':
                            if field_value:
                                field_value = field_value

                            else:
                                field_value = '-'

                    try:
                        table_tbody += field_value

                    except:
                        pass

                    table_tbody += "</td>\n"

                else:
                    table_tbody += "<td></td>\n"

            table_tbody += "</tr>\n"

    table_tbody += "</tbody>\n"

    # Javascript
    js_include = [
        '<script type="text/javascript" src="' + datatable_defaults['site-url'] + '/theme/js/bootstrap-table.min.js"></script>'
    ]

    if 'filter-control' in options and options['filter-control']:
        js_include.append('<script type="text/javascript" src="' + datatable_defaults['site-url'] + '/theme/js/bootstrap-table-filter-control.min.js"></script>')

    js_include.append('<script type="text/javascript" src="' + datatable_defaults['site-url'] + '/theme/js/Chart.bundle.min.js"></script>')
    js_include.append('<script type="text/javascript" src="' + datatable_defaults['site-url'] + '/theme/js/moment.min.js"></script>')
    js_include.append('<script type="text/javascript" src="' + datatable_defaults['site-url'] + '/theme/js/datatable.min.js"></script>')

    # CSS
    css_include = [
        '<link rel="stylesheet" href="' + datatable_defaults['site-url'] + '/theme/css/bootstrap-table.min.css">'
    ]

    if 'filter-control' in options and options['filter-control']:
        css_include.append('<link rel="stylesheet" href="' + datatable_defaults['site-url'] + '/theme/css/bootstrap-table-filter-control.min.css">')

    css_include.append('<link rel="stylesheet" href="' + datatable_defaults['site-url'] + '/theme/css/datatable.min.css">')

    return {
        'table': table_start + table_thead + table_tbody + table_end,
        'js_include': js_include,
        'css_include': css_include
    }


def is_interval_format(value):
    if isinstance(value, str):
        regex = r"[+-]?\d+(?:\.\d+)\s+\([+-]?\d+(?:\.\d+)\s+-\s+[+-]?\d+(?:\.\d+)\)"
        return bool(re.search(regex, value))
    else:
        return False


def boolean(argument):
    """Conversion function for yes/no True/False."""
    value = directives.choice(argument, ('yes', 'True', 'true', '1', 'no', 'False', 'false', '0'))
    return value in ('yes', 'True', 'true', '1', True)


def boolean_string(value):
    if value:
        return "true"
    else:
        return "false"


def get_attribute(attrs, name, default=None):
    if 'data-'+name in attrs:
        return attrs['data-'+name]
    else:
        return default


def add_head(generator, metadata):
    if u'styles' not in metadata:
        metadata[u'styles'] = []
    if u'scripts' not in metadata:
        metadata[u'scripts'] = []


def copy_resources(src, dest, file_list):
    """
    Copy files from content folder to output folder

    Parameters
    ----------
    src: string
        Content folder path
    dest: string,
        Output folder path
    file_list: list
        List of files to be transferred
    Output
    ------
    Copies files from content to output
    """

    if not os.path.exists(dest):
        os.makedirs(dest)
    for file_ in file_list:
        file_src = os.path.join(src, file_)
        shutil.copy2(file_src, dest)


def move_resources(gen):
    """
    Move files from js/css folders to output folder, use minified files.

    """

    css_target = os.path.join(gen.output_path, 'theme', 'css')
    if not os.path.exists(os.path.join(gen.output_path, 'theme', 'css')):
        os.makedirs(os.path.join(gen.output_path, 'theme', 'css'))

    js_target = os.path.join(gen.output_path, 'theme', 'js')
    if not os.path.exists(os.path.join(gen.output_path, 'theme', 'js')):
        os.makedirs(os.path.join(gen.output_path, 'theme', 'js'))

    plugin_paths = gen.settings['PLUGIN_PATHS']
    for path in plugin_paths:
        css_source = os.path.join(path, 'pelican-datatable', 'js-datatable', 'css.min')
        if os.path.isdir(css_source):
            copy_resources(css_source, css_target, os.listdir(css_source))
        js_source = os.path.join(path, 'pelican-datatable', 'js-datatable', 'js.min')
        if os.path.isdir(js_source):
            copy_resources(js_source, js_target, os.listdir(js_source))


def init(gen):
    datatable_defaults['site-url'] = gen.settings['SITEURL']


def register():
    signals.page_generator_init.connect(init)
    signals.article_generator_init.connect(init)

    signals.article_generator_context.connect(add_head)
    signals.page_generator_context.connect(add_head)

    signals.content_object_init.connect(datatable_md)
    signals.article_generator_finalized.connect(move_resources)
