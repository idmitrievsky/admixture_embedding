import json
from os.path import join
import sys

import altair as alt
import pandas as pd
from sklearn.manifold import TSNE
from sklearn.decomposition import PCA


def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


def embed_ancestry_fractions_into_plane(ancestry_fractions, embedder,
                                        axes_labels):
    embedded_ndarray = embedder(
        n_components=2,
        random_state=47).fit_transform(ancestry_fractions.values)
    embedded_ancestry_fractions = pd.DataFrame(
        embedded_ndarray, columns=axes_labels)

    return embedded_ancestry_fractions


def plot_embedded_ancestry_fractions(embedded_ancestry_fractions):
    x, y = embedded_ancestry_fractions.columns[:2]

    v = alt.Chart(pd.DataFrame()).mark_circle(
        size=50, color='grey', opacity=0.2).encode(
            x='{}:Q'.format(x), y='{}:Q'.format(y),
            tooltip='tooltip_label:N').interactive()

    w = alt.Chart(embedded_ancestry_fractions).mark_circle(size=50).encode(
        x=x,
        y=y,
        color=alt.Color(
            'ancestry_label',
            scale=alt.Scale(range=[
                '#a6cee3', '#1f78b4', '#b2df8a', '#33a02c', '#fb9a99',
                '#e31a1c', '#fdbf6f', '#ff7f00', '#cab2d6', '#6a3d9a',
                '#ffff99', '#b15928'
            ])),
        tooltip='tooltip_label:N').interactive()

    return v + w


def main(embedder, fam_path, fractions_path_path, axes_labels):
    ancestry_fractions = pd.read_csv(
        fractions_path_path, delimiter=' ', header=None)
    sample_info = pd.read_csv(fam_path, delimiter=' ', header=None)

    ancestry_labels = sample_info[0]
    sample_ids = sample_info[1]
    del sample_info

    if embedder is None:
        embedded_ancestry_fractions = ancestry_fractions
        column_names = list(embedded_ancestry_fractions.columns)
        column_names[0:2] = ['x', 'y']
        embedded_ancestry_fractions.columns = column_names
    else:
        embedded_ancestry_fractions = embed_ancestry_fractions_into_plane(
            ancestry_fractions, embedder, axes_labels)

    embedded_ancestry_fractions['sample_id'] = sample_ids
    embedded_ancestry_fractions['ancestry_label'] = ancestry_labels
    tooltip_labels = pd.Series(' - '.join(x) for x in zip(ancestry_labels, sample_ids))
    embedded_ancestry_fractions['tooltip_label'] = tooltip_labels

    chart = plot_embedded_ancestry_fractions(embedded_ancestry_fractions)

    with open('embedded_ancestry_template.html') as f:
        vega_lite_spec = json.dumps(chart.to_dict())

        html_file = f.read()
        html_file = html_file.replace('SPEC_VALUE', vega_lite_spec)

        print(html_file)


if __name__ == '__main__':
    _, *args = sys.argv

    if len(args) != 3:
        eprint("This script takes exactly 3 arguments as its input.")
        exit(1)

    fam_path, fractions_path_path, embedder_name = args

    if embedder_name not in ('PCA', 'TSNE', 'NONE'):
        eprint('Embedder has to be "PCA", "TSNE", or "NONE".')
        exit(2)

    if embedder_name == 'TSNE':
        embedder = TSNE
    elif embedder_name == 'PCA':
        embedder = PCA
    else:
        embedder = None

    axes_labels = ['PCA1', 'PCA2'] if embedder_name == 'PCA' else ['x', 'y']

    main(embedder, fam_path, fractions_path_path, axes_labels)
