import io
import os

from setuptools import find_packages, setup

# ─── Package metadata ─────────────────────────────────────────────────────────

NAME = "MahmudCore"
DESCRIPTION = "MahmudCore - a Python web framework built from scratch for learning core web framework concepts"
URL = "https://github.com/dear-mahmud-bd/python-framework-from-scratch"   
EMAIL = "dearmahmud.bd@gmail.com"
AUTHOR = "Md. Mahmudul Hasan"
REQUIRES_PYTHON = ">=3.8.0"    # 3.6 and 3.7 are end-of-life, no point supporting them
VERSION = "0.0.1"

# ─── Runtime dependencies ─────────────────────────────────────────────────────
# These get installed automatically when someone does: pip install mahmudcore

REQUIRED = [
    "webob==1.8.9",
    "parse==1.21.1",
    "requests==2.33.1",
    "requests-wsgi-adapter==0.4.1",
    "Jinja2==3.1.6",
    "whitenoise==6.12.0",
]

# ─── Optional / development dependencies ──────────────────────────────────────
# Install with: pip install mahmudcore[dev]

EXTRAS = {
    "dev": [
        "pytest",
        "pytest-cov",
        "gunicorn",
        "waitress",
    ]
}

# ─── Read long description from README ────────────────────────────────────────

here = os.path.abspath(os.path.dirname(__file__))

try:
    with io.open(os.path.join(here, "README.md"), encoding="utf-8") as f:
        long_description = "\n" + f.read()
except FileNotFoundError:
    long_description = DESCRIPTION

# ─── Version resolution ───────────────────────────────────────────────────────

about = {}
if not VERSION:
    # read version from mahmudcore/__version__.py if VERSION not set above
    project_slug = NAME.lower().replace("-", "_").replace(" ", "_")
    with open(os.path.join(here, project_slug, "__version__.py")) as f:
        exec(f.read(), about)
else:
    about["__version__"] = VERSION

# ─── Setup ────────────────────────────────────────────────────────────────────

setup(
    name=NAME,
    version=about["__version__"],
    description=DESCRIPTION,
    long_description=long_description,
    long_description_content_type="text/markdown",
    author=AUTHOR,
    author_email=EMAIL,
    url=URL,                          # ← added
    python_requires=REQUIRES_PYTHON,
    packages=find_packages(exclude=["test_*", "tests*"]),
    install_requires=REQUIRED,
    extras_require=EXTRAS,            # ← added dev dependencies
    include_package_data=True,
    license="MIT",
    classifiers=[
        # project maturity
        "Development Status :: 3 - Alpha",

        # who it's for
        "Intended Audience :: Developers",
        "Intended Audience :: Education",     # ← added, since this is a learning framework

        # license
        "License :: OSI Approved :: MIT License",

        # python versions supported
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",

        # what it does
        "Topic :: Internet :: WWW/HTTP :: WSGI",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
        "Topic :: Software Development :: Libraries :: Application Frameworks",  # ← added
    ],
    setup_requires=["wheel"],
    keywords="wsgi web framework python learning",   # ← added, helps PyPI search
)