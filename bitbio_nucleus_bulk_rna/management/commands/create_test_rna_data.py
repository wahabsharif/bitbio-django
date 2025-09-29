from django.core.management.base import BaseCommand
from bitbio_nucleus_bulk_rna.models import (
    AnalysisOutput,
    Gene,
    GeneCollection,
    Tier,
    UserTier,
)
from app_users.models import User
import pandas as pd
import numpy as np
import os
from django.conf import settings


class Command(BaseCommand):
    help = "Create test RNA analysis data for testing purposes"

    def add_arguments(self, parser):
        parser.add_argument(
            "--genes",
            type=int,
            default=100,
            help="Number of genes to generate in test data",
        )
        parser.add_argument(
            "--samples",
            type=int,
            default=12,
            help="Number of samples to generate in test data",
        )

    def handle(self, *args, **options):
        num_genes = options["genes"]
        num_samples = options["samples"]

        # Create test TSV file
        self.create_test_tsv_file(num_genes, num_samples)

        # Create AnalysisOutput record
        analysis = self.create_analysis_output()

        # Create gene records
        self.create_gene_records(num_genes)

        # Create user tiers and gene collections
        self.create_user_tiers_and_collections(analysis)

        self.stdout.write(
            self.style.SUCCESS(
                f"Successfully created test RNA data with {num_genes} genes and {num_samples} samples"
            )
        )
        self.stdout.write(f"Analysis ID: {analysis.id}")
        self.stdout.write(f"Test file: {analysis.file_path}")
        self.stdout.write(
            "You can now test the RNA analysis at: /bulk-rna/explore/{}/".format(
                analysis.id
            )
        )

    def create_test_tsv_file(self, num_genes, num_samples):
        """Create a test TSV file with synthetic gene expression data"""

        # Generate gene names
        gene_names = [f"GENE_{i:04d}" for i in range(1, num_genes + 1)]

        # Generate sample names with different conditions
        conditions = ["control", "treated"]
        timepoints = ["day1", "day3", "day7"]
        replicates = ["R1", "R2"]

        sample_names = []
        for condition in conditions:
            for timepoint in timepoints:
                for replicate in replicates:
                    sample_names.append(f"{condition}_{timepoint}_{replicate}")

        # Take only the number of samples requested
        sample_names = sample_names[:num_samples]

        # Generate synthetic expression data
        np.random.seed(42)  # For reproducible results

        # Create base expression levels
        data = {}
        for i, gene in enumerate(gene_names):
            # Different genes have different base expression levels
            base_expression = np.random.lognormal(mean=5, sigma=1)

            # Add condition-specific effects
            gene_data = []
            for sample in sample_names:
                condition, timepoint, replicate = sample.split("_")

                # Base expression
                expr = base_expression

                # Treatment effect
                if condition == "treated":
                    expr *= np.random.uniform(
                        1.2, 3.0
                    )  # Treatment increases expression

                # Time effect
                if timepoint == "day3":
                    expr *= np.random.uniform(0.8, 1.2)
                elif timepoint == "day7":
                    expr *= np.random.uniform(0.5, 1.0)

                # Add noise
                expr *= np.random.uniform(0.7, 1.3)

                gene_data.append(max(0.1, expr))  # Ensure positive values

            data[gene] = gene_data

        # Create DataFrame
        df = pd.DataFrame(data, index=sample_names)
        df = df.T  # Transpose so genes are rows and samples are columns

        # Save to file
        test_data_dir = os.path.join(settings.BASE_DIR, "test_data")
        os.makedirs(test_data_dir, exist_ok=True)

        file_path = os.path.join(test_data_dir, "test_rna_data.tsv")
        df.to_csv(file_path, sep="\t")

        self.stdout.write(f"Created test TSV file: {file_path}")
        return file_path

    def create_analysis_output(self):
        """Create an AnalysisOutput record for the test data"""

        file_path = os.path.join(settings.BASE_DIR, "test_data", "test_rna_data.tsv")

        analysis = AnalysisOutput.objects.create(
            analysis_type="bulk_rna",
            project="Test Project",
            product="Test Cell Type",
            description="Synthetic RNA-seq data for testing purposes",
            conditions="control_day1,control_day3,control_day7,treated_day1,treated_day3,treated_day7",
            added_by="test_user",
            origin="synthetic",
            linked_benchling_entry="TEST001",
            is_visible_in_commercial_app=True,
            metadata={
                "sample_count": 12,
                "gene_count": 100,
                "platform": "synthetic",
                "normalization": "TPM",
            },
            file_path=file_path,
        )

        return analysis

    def create_gene_records(self, num_genes):
        """Create Gene records for the test genes"""

        for i in range(1, num_genes + 1):
            gene_name = f"GENE_{i:04d}"
            ensembl_id = f"ENSG{i:011d}.1"

            # Check if gene already exists
            if not Gene.objects.filter(gene_name=gene_name).exists():
                Gene.objects.create(
                    gene_name=gene_name,
                    ensembl_id=ensembl_id,
                    long_name=f"Test Gene {i:04d}",
                )

    def create_user_tiers_and_collections(self, analysis):
        """Create user tiers and gene collections for testing"""

        # Create tiers if they don't exist
        free_tier, _ = Tier.objects.get_or_create(
            name="Free",
            defaults={
                "description": "Free tier with limited gene access",
                "max_genes": 10,
            },
        )

        premium_tier, _ = Tier.objects.get_or_create(
            name="Premium",
            defaults={
                "description": "Premium tier with extended gene access",
                "max_genes": 50,
            },
        )

        researcher_tier, _ = Tier.objects.get_or_create(
            name="Researcher",
            defaults={
                "description": "Researcher tier with full gene access",
                "max_genes": 1000,
            },
        )

        # Create gene collections
        free_collection, _ = GeneCollection.objects.get_or_create(
            collection_name="Free access",
            defaults={
                "description": "Genes available in free tier",
                "private_collection": False,
                "customer_visible": True,
            },
        )

        premium_collection, _ = GeneCollection.objects.get_or_create(
            collection_name="Premium access",
            defaults={
                "description": "Genes available in premium tier",
                "private_collection": False,
                "customer_visible": True,
            },
        )

        # Link collections to analysis
        free_collection.linked_analyses.add(analysis)
        premium_collection.linked_analyses.add(analysis)

        # Add some genes to collections
        free_genes = Gene.objects.filter(gene_name__startswith="GENE_")[:20]
        premium_genes = Gene.objects.filter(gene_name__startswith="GENE_")[:50]

        free_collection.included_genes.set(free_genes)
        premium_collection.included_genes.set(premium_genes)

        self.stdout.write("Created user tiers and gene collections")
