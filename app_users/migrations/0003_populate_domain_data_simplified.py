# Generated manually to populate domain data

from django.db import migrations


def populate_domain_data(apps, schema_editor):
    """
    Populate the Domain model with whitelisted and blocklisted domains
    """
    Domain = apps.get_model("app_users", "Domain")

    # Whitelisted institutional domains
    whitelisted_domains = [
        # Research institutions
        "stanford.edu",
        "harvard.edu",
        "mit.edu",
        "caltech.edu",
        "yale.edu",
        "princeton.edu",
        "columbia.edu",
        "uchicago.edu",
        "upenn.edu",
        "northwestern.edu",
        "duke.edu",
        "jhu.edu",
        "cornell.edu",
        "brown.edu",
        "dartmouth.edu",
        "vanderbilt.edu",
        "rice.edu",
        "emory.edu",
        "georgetown.edu",
        "tufts.edu",
        "boston.edu",
        "bu.edu",
        "northeastern.edu",
        # UC system
        "berkeley.edu",
        "ucla.edu",
        "ucsd.edu",
        "ucsf.edu",
        "uci.edu",
        "ucdavis.edu",
        "ucsb.edu",
        "ucsc.edu",
        "ucr.edu",
        "ucmerced.edu",
        # International institutions
        "ox.ac.uk",
        "cam.ac.uk",
        "imperial.ac.uk",
        "ed.ac.uk",
        "manchester.ac.uk",
        "kcl.ac.uk",
        "utoronto.ca",
        "mcgill.ca",
        "ubc.ca",
        "ethz.ch",
        "epfl.ch",
        "mpg.de",
        "u-tokyo.ac.jp",
        "kyoto-u.ac.jp",
        "nus.edu.sg",
        "ntu.edu.sg",
        "melbourne.edu.au",
        "sydney.edu.au",
        # Government and research organizations
        "nih.gov",
        "cdc.gov",
        "fda.gov",
        "usda.gov",
        "doe.gov",
        "nasa.gov",
        "nsf.gov",
        "noaa.gov",
        # Major research institutes
        "scripps.edu",
        "cshl.edu",
        "broadinstitute.org",
        "whitehead.mit.edu",
        "rockefeller.edu",
        "mskcc.org",
        "stjude.org",
        "mayoclinic.org",
        "clevelandclinic.org",
        "mdanderson.org",
        # Pharmaceutical and biotech companies
        "pfizer.com",
        "novartis.com",
        "roche.com",
        "gsk.com",
        "merck.com",
        "abbvie.com",
        "bms.com",
        "jnj.com",
        "lilly.com",
        "biogen.com",
        "gilead.com",
        "regeneron.com",
        "amgen.com",
        "genentech.com",
        "celgene.com",
        "illumina.com",
        "thermofisher.com",
        "bd.com",
        "danaher.com",
        "agilent.com",
        "perkinelmer.com",
        "waters.com",
        "zeiss.com",
        # Contract research organizations
        "crl.com",
        "covance.com",
        "pra-intl.com",
        "iqvia.com",
        "parexel.com",
        "ppdi.com",
        "quintiles.com",
        "wuxi.com",
        "evotec.com",
        "eurofins.com",
        # Hospitals and medical centers
        "mayo.edu",
        "partners.org",
        "nyp.org",
        "upmc.com",
        "ucsf.edu",
        "chop.edu",
        "childrens.harvard.edu",
        "seattlechildrens.org",
        "sickkids.ca",
    ]

    # Blocklisted personal email domains
    blocklisted_domains = [
        # Major email providers
        "gmail.com",
        "yahoo.com",
        "hotmail.com",
        "outlook.com",
        "live.com",
        "msn.com",
        "aol.com",
        "icloud.com",
        "me.com",
        "mac.com",
        # International email providers
        "yandex.com",
        "yandex.ru",
        "mail.ru",
        "qq.com",
        "163.com",
        "126.com",
        "sina.com",
        "sohu.com",
        "naver.com",
        "daum.net",
        "hanmail.net",
        "protonmail.com",
        "tutanota.com",
        "gmx.com",
        "gmx.de",
        "web.de",
        "t-online.de",
        "freenet.de",
        "libero.it",
        "virgilio.it",
        "alice.it",
        "tin.it",
        "orange.fr",
        "free.fr",
        "wanadoo.fr",
        "laposte.net",
        "terra.com.br",
        "uol.com.br",
        "bol.com.br",
        "ig.com.br",
        "globo.com",
        "yahoo.com.br",
        "rediffmail.com",
        "sify.com",
        "vsnl.net",
        "indiatimes.com",
        # Temporary/disposable email services
        "10minutemail.com",
        "tempmail.org",
        "guerrillamail.com",
        "mailinator.com",
        "throwaway.email",
        "temp-mail.org",
        "getnada.com",
        "maildrop.cc",
        "sharklasers.com",
        "guerrillamailblock.com",
        "pokemail.net",
        "spam4.me",
        "tempail.com",
        "tempinbox.com",
        "yopmail.com",
        "mytemp.email",
    ]

    # Create the domain management record
    Domain.objects.create(
        whitelisted_domains=whitelisted_domains,
        blocklisted_domains=blocklisted_domains,
    )


def reverse_populate_domain_data(apps, schema_editor):
    """
    Reverse the population of domain data
    """
    Domain = apps.get_model("app_users", "Domain")
    Domain.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ("app_users", "0002_create_domain_table"),
    ]

    operations = [
        migrations.RunPython(populate_domain_data, reverse_populate_domain_data),
    ]
