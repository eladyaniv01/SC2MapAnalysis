# Changelog

All notable changes to this project will be documented in this file. See [standard-version](https://github.com/conventional-changelog/standard-version) for commit guidelines.

### [0.0.51](https://github.com/eladyaniv01/SC2MapAnalysis/compare/v0.0.50...v0.0.51) (2020-08-14)


### Features

* Polygon/ Region now has the property 'buildable_points' ([#63](https://github.com/eladyaniv01/SC2MapAnalysis/issues/63)) ([2100501](https://github.com/eladyaniv01/SC2MapAnalysis/commit/21005016ab9669dfc276aee4a709e0c24435f2d2))


### Bug Fixes

* __bool__ compatibility with burnysc2 ([9618799](https://github.com/eladyaniv01/SC2MapAnalysis/commit/9618799a50f2fffcb78aa1f802e3903598c9a8ce))

### [0.0.50](https://github.com/eladyaniv01/SC2MapAnalysis/compare/v0.0.49...v0.0.50) (2020-08-13)


### Features

* Polygon/ Region now has the property 'buildable_points' ([25952f7](https://github.com/eladyaniv01/SC2MapAnalysis/commit/25952f75ed05a762124ae97e8425c946dd4cf058))


### Bug Fixes

* [[#61]](https://github.com/eladyaniv01/SC2MapAnalysis/issues/61) pathfind will not crash the bot when start or goal are not passed properly,  also a logging error will print out ([08466b5](https://github.com/eladyaniv01/SC2MapAnalysis/commit/08466b5e3650a694bf5b0d633b894fdb6bfbd7b8))
* fix point_to_numpy_array method ([4d56755](https://github.com/eladyaniv01/SC2MapAnalysis/commit/4d567559e3eceede00615c637458cdb8a0870d36))
* points_to_numpy_array now filters out outofbounds ([aedf9d2](https://github.com/eladyaniv01/SC2MapAnalysis/commit/aedf9d2ba45f585a279d7a014a7e990cbb9359a9))


### [0.0.49](https://github.com/eladyaniv01/SC2MapAnalysis/compare/v0.0.48...v0.0.49) (2020-08-12)


### Bug Fixes

* [#58](https://github.com/eladyaniv01/SC2MapAnalysis/issues/58) climber_grid is now aware of nonpathables (such as minerals, destructibles etc) ([98dcbec](https://github.com/eladyaniv01/SC2MapAnalysis/commit/98dcbec074e032047d4eacbb5f97e1961f06d395))
* [#59](https://github.com/eladyaniv01/SC2MapAnalysis/issues/59) clean air grid will now accept 'default_weight' argument (MapData, Pather) ([355ab7d](https://github.com/eladyaniv01/SC2MapAnalysis/commit/355ab7d8f0522a905d77007e979d3e57734bc4e7))
* climber_grid tests ([5216d0c](https://github.com/eladyaniv01/SC2MapAnalysis/commit/5216d0c8e796a3284c8e531e2ce4dcf3075582f4))
* import error on region-polygon ([b8ea912](https://github.com/eladyaniv01/SC2MapAnalysis/commit/b8ea9126a6dea792d9d62538688c6d9d15c395d8))
* mapdata test for plotting ([26a7c15](https://github.com/eladyaniv01/SC2MapAnalysis/commit/26a7c154a4a973995cea67267097aae0f9d58681))
* versionbump cli now commits setup.py before calling standard-version ([50eb667](https://github.com/eladyaniv01/SC2MapAnalysis/commit/50eb667c48949a0847742ed5aec8957f07cd8ff9))


### Documentation

* added cli reminder to commit setup.py on versionbump ([28a65a3](https://github.com/eladyaniv01/SC2MapAnalysis/commit/28a65a303a14ae08bf4b00253cb2ace13b8b5cff))

### [0.0.48](https://github.com/eladyaniv01/SC2MapAnalysis/compare/v0.0.47...v0.0.48) (2020-08-11)


### Bug Fixes

* path through destructables. destructables rocks radius factor from 0.8 to 1 ([2fd1a32](https://github.com/eladyaniv01/SC2MapAnalysis/commit/2fd1a326668f31317131a7586a549f472e986625))

### [0.0.47](https://github.com/eladyaniv01/SC2MapAnalysis/compare/v0.0.46...v0.0.47) (2020-08-11)

### Features

* feat: get_air_vs_ground_grid, get_clean_air_grid

### BugFixes

* fix: max_region_size up to 8500 to fix goldenwall
* added air_pathing deprecation warning for requesting through pyastar

### Issues Closed:
 * [#53 Feature request: get dead airspace from map analyzer](https://github.com/eladyaniv01/SC2MapAnalysis/issues/53)

### [0.0.46](https://github.com/eladyaniv01/SC2MapAnalysis/compare/v0.0.45...v0.0.46) (2020-08-10)

### Documentation

* moved changelog from readme.md to changelog.md ([0927cba](https://github.com/eladyaniv01/SC2MapAnalysis/commit/0927cbab8bbd2136de3527c314ab2cbd8f304cf5))

### [0.0.45](https://github.com/eladyaniv01/SC2MapAnalysis/compare/v0.0.44...v0.0.45) (2020-08-10)

### Features

Climber grid (#52)
* feat: get_climber_grid a pathing grid for climbing units such as colossus and reapers
    
### [0.0.43](https://github.com/eladyaniv01/SC2MapAnalysis/compare/v0.0.42...v0.0.43) (2020-08-10)

### BugFixes: 

 * Pather will no longer try to path through mineral walls ( like in goldenwall) 
 * Fix circular import bug on Debugger
 * Fixed malformed point orientation in rare cases 
 
### Tests

* Now testing both installation types (setup.py and requirements.txt)
* Every test  will now use the MapAnalyzer.util functions when it can
* Removed redundant test_map_data from TestSanity,  and put it in its right place,  test_mapdata

### Issues Closed:
 * [#46 Feature Request: possibility to enable pathing through rocks when calculating a path](https://github.com/eladyaniv01/SC2MapAnalysis/issues/46)
 * [#45 Feature Request: Add air grid](https://github.com/eladyaniv01/SC2MapAnalysis/issues/45)
 * [#44 Feature Request: add a setting for a custom default weight for the pathing grid](https://github.com/eladyaniv01/SC2MapAnalysis/issues/44)
 * [#39 Feature : add path_sensitivity for returning a sliced path (every nth point )](https://github.com/eladyaniv01/SC2MapAnalysis/issues/39)
 * [#38 pathfiner should return a list of Point2 and not numpy array](https://github.com/eladyaniv01/SC2MapAnalysis/issues/38)
 
<h2>Code Changes</h2>

### Debugger
 * Now inspects stack and will not save on tests
 * Will no longer circular call map_data for plotting
 
### Pather
* Radius for resource blockers is now 2, this passes all tests

### MapData

* Grouped methods in map_data for better readablitiy
* Moved `get_sets_with_mutual_elements` to utils
* Resource_blockers are now calculated with original coords
* Removed usage of neighbores ,  instead  adding influence with radius


### [0.0.42](https://github.com/eladyaniv01/SC2MapAnalysis/compare/v0.0.40...v0.0.42) (2020-08-07)

* feat Version bump cli (#50) ([b753d34](https://github.com/eladyaniv01/SC2MapAnalysis/commit/b753d3442421dd524d1c0043c4794f46b5a0b082)), closes [#50](https://github.com/eladyaniv01/SC2MapAnalysis/issues/50)

### Features

* **cli interface for version bump:** Bump Version + changelog generation ([20b1e70](https://github.com/eladyaniv01/SC2MapAnalysis/commit/20b1e70693a3aef37eba068fb38965c82d076716))

### [0.0.24](https://github.com/eladyaniv01/SC2MapAnalysis/compare/v0.0.23...v0.0.24) (2020-08-07)
