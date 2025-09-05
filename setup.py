import subprocess
import sys
from setuptools import setup, find_packages
from setuptools.command.install import install
from setuptools.command.develop import develop


class PostInstallCommand(install):
    """Custom post-installation for install mode."""

    def run(self):
        install.run(self)
        self._install_playwright()


class PostDevelopCommand(develop):
    """Custom post-installation for develop mode."""

    def run(self):
        develop.run(self)
        self._install_playwright()


def _install_playwright():
    """Install Playwright browser and dependencies."""

    try:
        # Install Playwright browser
        subprocess.check_call(
            [sys.executable, "-m", "playwright", "install", "chromium"]
        )

        # Install system dependencies
        subprocess.check_call([sys.executable, "-m", "playwright", "install-deps"])

    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing Playwright: {e}")
        print("⚠️  You may need to run these commands manually:")
        print("   python -m playwright install chromium")
        print("   python -m playwright install-deps")


# Monkey patch the install methods to include Playwright installation
PostInstallCommand._install_playwright = staticmethod(_install_playwright)
PostDevelopCommand._install_playwright = staticmethod(_install_playwright)

setup(
    name="bitbio-django",
    version="1.0.0",
    description="Django project with Playwright PDF generation",
    packages=find_packages(),
    install_requires=[
        "asgiref==3.7.2",
        "Django==4.2.16",
        "mysqlclient==2.2.7",
        "sqlparse==0.5.3",
        "tzdata==2025.2",
        "openpyxl==3.1.5",
        "playwright==1.48.0",
        "Pillow>=10.2.0",
    ],
    cmdclass={
        "install": PostInstallCommand,
        "develop": PostDevelopCommand,
    },
    python_requires=">=3.8",
)
