# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/en/1.0.0/) and this project
adheres to [Semantic Versioning](http://semver.org/spec/v2.0.0.html).

## 0.4.3
### Added

- Added option to auto-generate the Python code for the metamodel's dependencies,
  see the `--with-dependencies` option.

## Fixed
- Missing imports to `EDataType` references that are contained in a metamodel dependency.
- Missing default value generation for `EAttribute`.
- Missing `eSubpackages` and `eSuperPackages` at module level.

## Removed
- Removed support for Python 3.3.

## 0.4.2
### Fixed

- Missing 'templates' in the sdist package. The sdist package (`.tar.gz`) is
  built using information of the `MANIFEST.in` for non-source files. The
  templates were simply missing in it.

## 0.4.1
### Fixed

- README

## 0.4.0
### Added

- Added option to auto-register generated package in global registry, see the
  `--auto-register-package` option.
- Added option to specify a user module, from where mixin classes. These mixins must then implement
  all end-user specific code like operations and derived attributes. See the `--user-module`
  command line option.

### Fixed

- EDatatype registration.
- Various derived attribute fixes.
