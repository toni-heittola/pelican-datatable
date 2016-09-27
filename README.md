Pelican-datatable - Automatic dynamic table generation for Pelican
==================================================================

pelican-datatable is an open source Pelican plugin to produce dynamic HTML tables with visualizations. The plugin provides an automatic HTML table generation from a data structure. Currently plugin only works for Markdown formatted content. 

This pelican plugin is based on [js-datatable JQuery plugin](https://github.com/toni-heittola/js-datatable). 

**Author**

Toni Heittola (toni.heittola@gmail.com), [GitHub](https://github.com/toni-heittola), [Home page](http://www.cs.tut.fi/~heittolt/)

Installation instructions
=========================

## Requirements

**pyyaml** and **bs4** are required. To ensure that all external modules are installed, run:

    pip install -r requirements.txt

Or install one by one: 

**pyyaml**, for yaml reading 

    pip install pyyaml

**bs4** (BeautifulSoup) for parsing HTML content

    pip install beautifulsoup4


## Pelican installation

Make sure plugin installation root directory in set in `pelicanconf.py`:

    PLUGIN_PATHS = ['plugins/pelican-datatable',]

Enable pelican-datatable:

    PLUGINS = ['pelican-datatable']

To allow plugin in include css and js files, one needs to add following to the `base.html` template, in the head (to include css files):

    {% if article %}
        {% if article.styles %}
            {% for style in article.styles %}
    {{ style }}
            {% endfor %}
        {% endif %}
    {% endif %}
    {% if page %}
        {% if page.styles %}
            {% for style in page.styles %}
    {{ style }}
            {% endfor %}
        {% endif %}
    {% endif %}

At the bottom of the page before `</body>` tag (to include js files):

    {% if article %}
        {% if article.scripts %}
            {% for script in article.scripts %}
    {{ script }}
            {% endfor %}
        {% endif %}
    {% endif %}

    {% if page %}
        {% if page.scripts %}
            {% for script in page.scripts %}
    {{ script }}
            {% endfor %}
        {% endif %}
    {% endif %}

Usage
=====

## Table

Datatable is injected to `<table>` tags with class `datatable`.

Example:

    <table class="datatable table"
           data-yaml="content/data/test.yaml"
           data-show-chart="true"
           data-chart-modes="bar,scatter,comparison"
           data-chart-default-mode="scatter"
           data-id-field="code"
           data-sort-name="value1"
           data-sort-order="desc" 
           data-rank-mode="grouped_muted" 
           data-row-highlighting="false" 
           data-pagination="false" 
           data-show-pagination-switch="false"                    
           data-scatter-x="value1"
           data-scatter-y="value2"    
           data-comparison-row-id-field="code"
           data-comparison-sets-json='[{"title": "All values","data_axis_title": "Value axis", "fields": ["value1", "value2", "value3", "value4"], "field_titles": ["custom title 1","custom title 2","custom title 3","custom title 4"]},{"title": "Sub comparison 1","data_axis_title": "Value", "fields": ["value1", "value2"]},{"title": "Sub comparison 2", "data_axis_title": "Accuracy", "fields": ["value3", "value4"]}]'
           data-comparison-active-set="All values"
           data-comparison-a-row="Red"
           data-comparison-b-row="Blue"
           data-filter-control="true"
           data-filter-show-clear="true"       
           >
        <thead>
            <tr>
                <th data-rank="true">Rank</th>
                <th data-field="code" 
                    data-sortable="true">
                    Name
                </th>
                <th data-field="value1" 
                    data-sortable="true" 
                    data-value-type="float4" 
                    data-chartable="true">
                    Value 1
                </th>
                <th data-field="value2" 
                    data-sortable="true" 
                    data-value-type="float4" 
                    data-chartable="true">
                    Value 2
                </th>
                <th class="sep-left-cell"
                    data-align="center"
                    data-field="feature1"
                    data-sortable="true"
                    data-tag="true"
                    data-filter-control="select">
                    Feature 1
                </th>
                <th 
                    data-align="center"
                    data-field="feature2"
                    data-sortable="true"
                    data-tag="true"
                    data-filter-control="select">
                    Feature 2
                </th>            
            </tr>
        </thead>
    </table>


## Data structure file

Place data structure file inside pelican project folder.
Example structure:
    
    data:
      - code: Red
        value1: 12
        value2: 22
        value3: 62
        value4: 52
        feature1: square
        feature2: triangle
        row_css: danger
    
      - code: Blue
        value1: 62
        value2: 42
        value3: 62
        value4: 52
        feature1: circle
        feature2: triangle
        row_css: warning
    
      - code: Black
        value1: 18
        value2: 42
        value3: 62
        value4: 52
        feature1: square
        feature2: circle
        row_css: success
    
      - code: White
        value1: 18
        value2: 37
        value3: 62
        value4: 52
        feature1: triangle
        feature2: square
        row_css: info
    
      - code: Purple
        value1: 12
        value2: 22
        value3: 62
        value4: 52
        feature1: square
        feature2: circle
    
      - code: Brown
        value1: 42
        value2: 26
        value3: 62
        value4: 52
        feature1: block
        feature2: pyramid
    
      - code: Baseline
        value1: 62
        value2: 32
        value3: 62
        value4: 52
        feature1: triangle
        feature2: circle
        baseline: true
        row_css: active

