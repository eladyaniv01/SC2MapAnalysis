# Changelog

All notable changes to this project will be documented in this file. See [standard-version](https://github.com/conventional-changelog/standard-version) for commit guidelines.

### [0.0.47](https://github.com/eladyaniv01/SC2MapAnalysis/compare/v0.0.46...v0.0.47) (2020-08-11)


### Documentation

* fix requirements.txt and requirements.dev.txt ([36e7368](https://github.com/eladyaniv01/SC2MapAnalysis/commit/36e73681691f87798dd4ee59fe9570b0ac612734))
* fix requirements.txt and requirements.dev.txt ([e88637c](https://github.com/eladyaniv01/SC2MapAnalysis/commit/e88637cfc5fbfc75c05dcd29899b894f42242c1f))
* fix requirements.txt and requirements.dev.txt ([96886d5](https://github.com/eladyaniv01/SC2MapAnalysis/commit/96886d52f27706ba427bcbe3ff2c2b3fba962a0e))
* fix requirements.txt and requirements.dev.txt ([da935c7](https://github.com/eladyaniv01/SC2MapAnalysis/commit/da935c74ed5065e612b52341f21f0964c4a45be1))
* fix requirements.txt and requirements.dev.txt ([ae8dfb1](https://github.com/eladyaniv01/SC2MapAnalysis/commit/ae8dfb193471b84974788d6e5abca414bf96c9b8))

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
