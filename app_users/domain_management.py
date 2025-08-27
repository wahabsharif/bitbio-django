"""
Domain management for user registration
Handles whitelist for auto-approval and blocklist for rejection
"""

# Whitelisted institutional domains - users from these domains get auto-approved
WHITELISTED_DOMAINS = {
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
    "jhu.edu",  # Johns Hopkins
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
    "ox.ac.uk",  # Oxford
    "cam.ac.uk",  # Cambridge
    "imperial.ac.uk",  # Imperial College London
    "ed.ac.uk",  # University of Edinburgh
    "manchester.ac.uk",
    "kcl.ac.uk",  # King's College London
    "utoronto.ca",  # University of Toronto
    "mcgill.ca",  # McGill University
    "ubc.ca",  # University of British Columbia
    "ethz.ch",  # ETH Zurich
    "epfl.ch",  # EPFL
    "mpg.de",  # Max Planck Institute
    "u-tokyo.ac.jp",  # University of Tokyo
    "kyoto-u.ac.jp",  # Kyoto University
    "nus.edu.sg",  # National University of Singapore
    "ntu.edu.sg",  # Nanyang Technological University
    "melbourne.edu.au",  # University of Melbourne
    "sydney.edu.au",  # University of Sydney
    # Government and research organizations
    "nih.gov",  # National Institutes of Health
    "cdc.gov",  # Centers for Disease Control
    "fda.gov",  # Food and Drug Administration
    "usda.gov",  # US Department of Agriculture
    "doe.gov",  # Department of Energy
    "nasa.gov",  # NASA
    "nsf.gov",  # National Science Foundation
    "noaa.gov",  # National Oceanic and Atmospheric Administration
    # Major research institutes
    "scripps.edu",  # Scripps Research
    "cshl.edu",  # Cold Spring Harbor Laboratory
    "broadinstitute.org",  # Broad Institute
    "whitehead.mit.edu",  # Whitehead Institute
    "rockefeller.edu",  # Rockefeller University
    "mskcc.org",  # Memorial Sloan Kettering
    "stjude.org",  # St. Jude Children's Research Hospital
    "mayoclinic.org",  # Mayo Clinic
    "clevelandclinic.org",  # Cleveland Clinic
    "mdanderson.org",  # MD Anderson Cancer Center
    # Pharmaceutical and biotech companies
    "pfizer.com",
    "novartis.com",
    "roche.com",
    "gsk.com",
    "merck.com",
    "abbvie.com",
    "bms.com",  # Bristol Myers Squibb
    "jnj.com",  # Johnson & Johnson
    "lilly.com",  # Eli Lilly
    "biogen.com",
    "gilead.com",
    "regeneron.com",
    "amgen.com",
    "genentech.com",
    "celgene.com",
    "illumina.com",
    "thermofisher.com",
    "bd.com",  # Becton Dickinson
    "danaher.com",
    "agilent.com",
    "perkinelmer.com",
    "waters.com",
    "zeiss.com",
    # Contract research organizations
    "crl.com",  # Charles River Laboratories
    "covance.com",
    "pra-intl.com",  # PRA Health Sciences
    "iqvia.com",
    "parexel.com",
    "ppdi.com",
    "quintiles.com",
    "wuxi.com",  # WuXi AppTec
    "evotec.com",
    "eurofins.com",
    # Hospitals and medical centers
    "mayo.edu",
    "partners.org",  # Partners HealthCare
    "nyp.org",  # NewYork-Presbyterian
    "upmc.com",  # University of Pittsburgh Medical Center
    "ucsf.edu",
    "chop.edu",  # Children's Hospital of Philadelphia
    "childrens.harvard.edu",  # Boston Children's Hospital
    "seattlechildrens.org",
    "sickkids.ca",  # The Hospital for Sick Children
}

# Blocklisted personal email domains - registrations from these domains are rejected
BLOCKLISTED_DOMAINS = {
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
}


def get_email_domain(email):
    """
    Extract domain from email address

    Args:
        email (str): Email address

    Returns:
        str: Domain part of the email in lowercase
    """
    if not email or "@" not in email:
        return ""

    return email.split("@")[1].lower().strip()


def is_whitelisted_domain(email):
    """
    Check if email domain is in the whitelist for auto-approval

    Args:
        email (str): Email address to check

    Returns:
        bool: True if domain is whitelisted, False otherwise
    """
    domain = get_email_domain(email)
    return domain in WHITELISTED_DOMAINS


def is_blocklisted_domain(email):
    """
    Check if email domain is in the blocklist and should be rejected

    Args:
        email (str): Email address to check

    Returns:
        bool: True if domain is blocklisted, False otherwise
    """
    domain = get_email_domain(email)
    return domain in BLOCKLISTED_DOMAINS


def get_domain_status(email):
    """
    Get the status of an email domain

    Args:
        email (str): Email address to check

    Returns:
        str: 'whitelisted', 'blocklisted', or 'neutral'
    """
    if is_blocklisted_domain(email):
        return "blocklisted"
    elif is_whitelisted_domain(email):
        return "whitelisted"
    else:
        return "neutral"


def should_auto_approve(email):
    """
    Determine if a user with this email should be auto-approved

    Args:
        email (str): Email address to check

    Returns:
        bool: True if user should be auto-approved, False otherwise
    """
    return is_whitelisted_domain(email)


def should_block_registration(email):
    """
    Determine if registration should be blocked for this email

    Args:
        email (str): Email address to check

    Returns:
        bool: True if registration should be blocked, False otherwise
    """
    return is_blocklisted_domain(email)
