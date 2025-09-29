from django import template
from bitbio_nucleus_bulk_rna.models import Gene

register = template.Library()

@register.filter
def extract_df_strings(gene_objects):
    """
    Extract df_string property from a list of gene objects.
    """
    if not gene_objects:
        return []
    
    return [gene.df_string for gene in gene_objects if hasattr(gene, 'df_string')]
