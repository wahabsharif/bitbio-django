from django.urls import path
from . import views

app_name = "bulk_rna"

urlpatterns = [
    path("", views.bulk_rna_analysis_list, name="bulk_rna_analysis_list"),
    path("explore/<int:analysis_id>/", views.explore_analysis, name="explore_analysis"),
    path("pca/<int:analysis_id>/", views.pca_view, name="pca_view"),
    path(
        "pca/<int:analysis_id>/2d/",
        views.pca_view,
        {"plot_3d": False},
        name="pca_view_2d",
    ),
    path(
        "pca/<int:analysis_id>/3d/",
        views.pca_view,
        {"plot_3d": True},
        name="pca_view_3d",
    ),
    path("load-genes-from-gtf/", views.load_genes_from_gtf, name="load_genes_from_gtf"),
    path("gene-autocomplete/", views.gene_autocomplete, name="gene_autocomplete"),
    path(
        "gene-collections/<int:analysis_id>/",
        views.gene_collection_list,
        name="gene_collection_list",
    ),
    path("gene-collections/", views.gene_collection_list, name="gene_collection_list"),
    path(
        "gene-collections/new/<int:analysis_id>/",
        views.create_gene_collection,
        name="create_gene_collection",
    ),
    path(
        "gene-collections/view/<int:collection_id>/",
        views.view_gene_collection,
        name="view_gene_collection",
    ),
    path(
        "gene-collections/<int:collection_id>/edit/",
        views.edit_gene_collection,
        name="edit_gene_collection",
    ),
    path(
        "gene-collections/<int:collection_id>/delete/",
        views.delete_gene_collection,
        name="delete_gene_collection",
    ),
    path("download_csv/<int:analysis_id>/", views.download_csv, name="download_csv"),
    path("user_genes/", views.view_user_genes, name="view_user_genes"),
]
