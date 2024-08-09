"""Automation using nox."""

from __future__ import annotations

import pathlib
import shutil

import nox

nox.options.reuse_existing_virtualenvs = True


@nox.session(python=["3.8", "3.9", "3.10", "3.11", "3.12"])
def tests(session: nox.Session) -> None:
    """Run the unit and regular tests."""
    session.install(".[test]")
    session.run("pip", "install", "-r", "requirements_test.txt", *session.posargs)
    session.run("pytest", *session.posargs)


## Sphinx related options

# Sphinx output and source directories
BUILD_DIR = "_build"
OUTPUT_DIR = pathlib.Path(BUILD_DIR, "html")
SOURCE_DIR = pathlib.Path()

# Location of the translation templates
TRANSLATION_TEMPLATE_DIR = pathlib.Path(BUILD_DIR, "gettext")
TRANSLATION_LOCALES_DIR = pathlib.Path("locales")

# Sphinx build commands
SPHINX_BUILD = "sphinx-build"
SPHINX_AUTO_BUILD = "sphinx-autobuild"

# Sphinx parameters used to build the guide
BUILD_PARAMETERS = ["-b", "html"]

# Sphinx parameters used to test the build of the guide
TEST_PARAMETERS = ["-W", "--keep-going", "-E", "-a"]

# Sphinx parameters to generate translation templates
TRANSLATION_TEMPLATE_PARAMETERS = ["-b", "gettext"]

# Sphinx-autobuild ignore and include parameters
AUTOBUILD_IGNORE = [
    "_build",
    ".nox",
    "build_assets",
    "tmp",
]
AUTOBUILD_INCLUDE = [pathlib.Path("_static", "pyos.css")]

## Localization options (translations)

# List of languages for which locales will be generated in (/locales/<lang>)
LANGUAGES = ["ja"]

# List of languages that should be built when releasing the guide (docs or docs-test sessions)
RELEASE_LANGUAGES = []


@nox.session
def docs(session) -> None:  # noqa: ANN001
    """Build the packaging guide."""
    session.install("-e", ".")
    session.run(SPHINX_BUILD, *BUILD_PARAMETERS, SOURCE_DIR, OUTPUT_DIR, *session.posargs)
    # When building the guide, also build the translations in RELEASE_LANGUAGES
    session.notify("build-translations", ["release-build"])


@nox.session(name="docs-test")
def docs_test(session) -> None:  # noqa: ANN001
    """
    Build the packaging guide with more restricted parameters.

    Note: this is the session used in CI/CD to release the guide.
    """
    session.install("-e", ".")
    session.run(SPHINX_BUILD, *BUILD_PARAMETERS, *TEST_PARAMETERS, SOURCE_DIR, OUTPUT_DIR, *session.posargs)
    # When building the guide with additional parameters, also build the translations in RELEASE_LANGUAGES
    # with those same parameters.
    session.notify("build-translations", ["release-build", *TEST_PARAMETERS])


@nox.session(name="docs-live")
def docs_live(session) -> None:  # noqa: ANN001
    """
    Build and launch a local copy of the guide.

    This session will use sphinx-autobuild to build the guide and launch a local server so you can
    browse it locally. It will automatically rebuild the guide when changes are detected in the source.

    It can be used with the language parameter to build a specific translation, for example:

        nox -s docs-live -- -D language=es

    Note: The docs-live-lang session below is provided as a convenience session for beginner contributors
    so they don't need to remember the specific sphinx-build parameters to build a different language.
    """
    session.install("-e", ".")
    cmd = [SPHINX_AUTO_BUILD, *BUILD_PARAMETERS, SOURCE_DIR, OUTPUT_DIR, *session.posargs]
    for folder in AUTOBUILD_IGNORE:
        cmd.extend(["--ignore", f"*/{folder}/*"])
    session.run(*cmd)


@nox.session(name="docs-live-lang")
def docs_live_lang(session) -> None:  # noqa: ANN001
    """
    A convenience session for beginner contributors to use the docs-live session with
    a specific language.

    It expects the language code to be passed as the first positional argument, so it needs
    to be called with from the command line with the following syntax:

        nox -s docs-live-lang -- LANG

    where LANG is one of the available languages defined in LANGUAGES.
    For example, for Spanish: nox -s docs-live-lang -- es
    """  # noqa: D205, D401
    if not session.posargs:
        session.error("Please provide a language using:\n\n      " "nox -s docs-live-lang -- LANG\n\n     " f" where LANG is one of: {LANGUAGES}")
    lang = session.posargs[0]
    if lang in LANGUAGES:
        session.posargs.pop(0)
        session.notify("docs-live", ("-D", f"language={lang}", *session.posargs))
    else:
        session.error(
            f"[{lang}] locale is not available. Try using:\n\n      " "nox -s docs-live-lang -- LANG\n\n      " f"where LANG is one of: {LANGUAGES}"
        )


@nox.session(name="docs-clean")
def clean_dir(session) -> None:  # noqa: ANN001
    """Clean out the docs directory used in the live build."""
    session.warn(f"Cleaning out {OUTPUT_DIR}")
    dir_contents = OUTPUT_DIR.glob("*")
    for content in dir_contents:
        session.log(f"removing {content}")
        if content.is_dir():
            shutil.rmtree(content)
        else:
            pathlib.Path(content).unlink()


@nox.session(name="update-translations")
def update_translations(session) -> None:  # noqa: ANN001
    """
    Update the translation files (./locales/*/.po) for all languages translations.

    Note: this step is important because it makes sure that the translation files are
    up to date with the latest changes in the guide.
    """
    session.install("-e", ".")
    session.install("sphinx-intl")
    session.log("Updating templates (.pot)")
    session.run(SPHINX_BUILD, *TRANSLATION_TEMPLATE_PARAMETERS, SOURCE_DIR, TRANSLATION_TEMPLATE_DIR, *session.posargs)
    for lang in LANGUAGES:
        session.log(f"Updating .po files for [{lang}] translation")
        session.run("sphinx-intl", "update", "-p", TRANSLATION_TEMPLATE_DIR, "-l", lang)


@nox.session(name="build-languages")
def build_languages(session) -> None:  # noqa: ANN001
    """
    Build the translations of the guide for the specified language.

    Note: This sessions expects a list of languages to build in the first position of the session arguments.
    It does not need to be called directly, it is started by build_translations session.
    """
    if not session.posargs:
        session.error("Please provide the list of languages to build the translation for")
    languages_to_build = session.posargs.pop(0)

    session.install("-e", ".")
    for lang in languages_to_build:
        if lang not in LANGUAGES:
            session.warn(f"Language [{lang}] is not available for translation")
            continue
        session.log(f"Building [{lang}] guide")
        session.run(SPHINX_BUILD, *BUILD_PARAMETERS, "-D", f"language={lang}", ".", OUTPUT_DIR / lang, *session.posargs)


@nox.session(name="build-translations")
def build_translations(session) -> None:  # noqa: ANN001
    """
    Build translations of the guide.

    Note: this session can be called directly to build all available translations (defined in LANGUAGES).
    It is also called by the docs and docs-test sessions with 'release-build' as the first positional
    argument, to build only the translations defined in RELEASE_LANGUAGES.
    """
    release_build = False
    if session.posargs and session.posargs[0] == "release-build":
        session.posargs.pop(0)
        release_build = True
    # if running from the docs or docs-test sessions, build only release languages
    build_languages = RELEASE_LANGUAGES if release_build else LANGUAGES
    # only build languages that have a locale folder
    build_languages = [lang for lang in build_languages if (TRANSLATION_LOCALES_DIR / lang).exists()]
    session.log(f"Declared languages: {LANGUAGES}")
    session.log(f"Release languages: {RELEASE_LANGUAGES}")
    session.log(f"Building languages{' for release' if release_build else ''}: {build_languages}")
    if not build_languages:
        session.warn("No translations to build")
    else:
        session.notify("build-languages", [build_languages, *session.posargs])


@nox.session(name="build-translations-test")
def build_translations_test(session) -> None:  # noqa: ANN001
    """
    Build all translations of the guide with testing parameters.

    This is a convenience session to test the build of all translations with the testing parameters
    in the same way docs-test does for the English version.
    """
    session.notify("build-translations", [*TEST_PARAMETERS])
