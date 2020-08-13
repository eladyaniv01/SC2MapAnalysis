# Changelog

All notable changes to this project will be documented in this file. See [standard-version](https://github.com/conventional-changelog/standard-version) for commit guidelines.

### [0.0.50](https://github.com/eladyaniv01/SC2MapAnalysis/compare/v0.0.49...v0.0.50) (2020-08-13)


### Features

* Polygon/ Region now has the property 'buildable_points' ([25952f7](https://github.com/eladyaniv01/SC2MapAnalysis/commit/25952f75ed05a762124ae97e8425c946dd4cf058))
* Polygon/ Region now has the property 'buildable_points' ([7e0291d](https://github.com/eladyaniv01/SC2MapAnalysis/commit/7e0291dccf87e9a93877e82d02ef07b2d8e83a19))
* Polygon/ Region now has the property 'buildable_points' with some usage ideas ([54e84f0](https://github.com/eladyaniv01/SC2MapAnalysis/commit/54e84f0f4e96f8962540f27d86cfae3cc30a0378))
* Polygon/ Region now has the property 'buildable_points' with some usage ideas ([41282a1](https://github.com/eladyaniv01/SC2MapAnalysis/commit/41282a150595bace594d16f2d2f51d24b9372dc9))
* Polygon/ Region now has the property 'buildable_points' with some usage ideas ([9a3408a](https://github.com/eladyaniv01/SC2MapAnalysis/commit/9a3408a6df4f6d5ce326488db24f95df1aedc3d2))
* Polygon/ Region now has the property 'buildable_points' with some usage ideas ([9d9477a](https://github.com/eladyaniv01/SC2MapAnalysis/commit/9d9477aba9068098c5f39284ee962385216cf7d1))
* Polygon/ Region now has the property 'buildable_points' with some usage ideas ([09a8728](https://github.com/eladyaniv01/SC2MapAnalysis/commit/09a872864bbec95f1a5e04890afc675627c782b6))


### Bug Fixes

* [[#61](https://github.com/eladyaniv01/SC2MapAnalysis/issues/61)](https://github.com/eladyaniv01/SC2MapAnalysis/issues/61) pathfind will not crash the bot when start or goal are not passed properly,  also a logging error will print out ([08466b5](https://github.com/eladyaniv01/SC2MapAnalysis/commit/08466b5e3650a694bf5b0d633b894fdb6bfbd7b8))
* fix point_to_numpy_array method ([4d56755](https://github.com/eladyaniv01/SC2MapAnalysis/commit/4d567559e3eceede00615c637458cdb8a0870d36))
* fix point_to_numpy_array method ([24af6b8](https://github.com/eladyaniv01/SC2MapAnalysis/commit/24af6b8c0d9d326235bc4c748887fcb6bf884b45))
* fix point_to_numpy_array method ([18c4642](https://github.com/eladyaniv01/SC2MapAnalysis/commit/18c464274dee7549bea10352736225f9917bd3c5))
* mapdata test for plotting ([0ce534b](https://github.com/eladyaniv01/SC2MapAnalysis/commit/0ce534b46839f1b983d5512ebcbbad9644cc37cf))
* mapdata test for plotting ([3d359b1](https://github.com/eladyaniv01/SC2MapAnalysis/commit/3d359b183806fcb15b67ed64ad816e617278ec19))
* points_to_numpy_array now filters out outofbounds ([aedf9d2](https://github.com/eladyaniv01/SC2MapAnalysis/commit/aedf9d2ba45f585a279d7a014a7e990cbb9359a9))
* points_to_numpy_array now filters out outofbounds ([f15a360](https://github.com/eladyaniv01/SC2MapAnalysis/commit/f15a360e7a861dc911a3cc08649be1c9b9e4da13))
* update according to last fix ([486f0f9](https://github.com/eladyaniv01/SC2MapAnalysis/commit/486f0f9346cec936228492aba77e5e7ced22a259))
* update according to last fix ([dae199b](https://github.com/eladyaniv01/SC2MapAnalysis/commit/dae199bfed3ce509cc4148864508e3a687718455))

### [0.0.49](https://github.com/eladyaniv01/SC2MapAnalysis/compare/v0.0.48...v0.0.49) (2020-08-12)


### Bug Fixes

* [[#58](https://github.com/eladyaniv01/SC2MapAnalysis/issues/58)](https://github.com/eladyaniv01/SC2MapAnalysis/issues/58) climber_grid is now aware of nonpathables (such as minerals, destructibles etc) ([98dcbec](https://github.com/eladyaniv01/SC2MapAnalysis/commit/98dcbec074e032047d4eacbb5f97e1961f06d395))
* [[#59](https://github.com/eladyaniv01/SC2MapAnalysis/issues/59)](https://github.com/eladyaniv01/SC2MapAnalysis/issues/59) clean air grid will now accept 'default_weight' argument (MapData, Pather) ([355ab7d](https://github.com/eladyaniv01/SC2MapAnalysis/commit/355ab7d8f0522a905d77007e979d3e57734bc4e7))
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
