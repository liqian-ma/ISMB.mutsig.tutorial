import pandas as pd
import click

"""
Python dependencies with conda:
conda create -n signatures-env python=3.7 pandas click
conda activate signatures-env
"""


@click.command()
@click.option('--input', type=click.Path())  # weights table in deconstructSigs format
@click.option('--signatures', type=click.Path())  # mutational signatures probabilities per channel
@click.option('--output', type=click.Path())  # output path
def run_assign(input, signatures, output):

    """
    Takes the results of deconstructSigs.r and computes the likelihood that
    a mutation in a sample-context is generated by each signature.
    """

    # parse signature file to table
    sigs = pd.read_csv(signatures, sep="\t", index_col=0, header=0)
    sigs = sigs.T

    # parse weights per signature for each sample
    weights = pd.read_csv(input, header=0, sep='\t')

    # go over each sample in weights matrix and compute the probability
    # for each mutation type in tri-nucleotide context

    frames = []
    flag = 0
    for idx, row in weights.iterrows():  # go over each sample
        sample = row['sample_id']
        sig_dic = {}
        allsigs = []

        for col in weights.columns:
            if col not in ['sample_id', 'SSE', 'mutation_count']:
                sig_dic[col] = row[col] * row['mutation_count']
                allsigs.append(col)

        a = sigs.copy()
        for sig in allsigs:
            a[sig] *= sig_dic[sig]

        a['row_sum'] = a[allsigs].sum(axis=1)
        res = a[allsigs].div(a['row_sum'], axis=0)[allsigs]
        res['Mutation_type'] = res.index
        res['Sample'] = sample
        columns = ['Sample', 'Mutation_type'] + allsigs
        res = res[columns]

        # append results for each sample
        if flag == 0:
            frames = [res]
            flag += 1
        else:
            frames.append(res)

    results = pd.concat(frames)
    results.to_csv(output, sep='\t', index=False)


if __name__ == '__main__':

    """
    Within conda environment, run this command-line:
    python attribution.py --input $INPUT/weights.tsv \
                          --signatures $INPUT/signatures_sigprofiler.tsv \
                          --output $OUTPUT/attribution.tsv
    """

    run_assign()
