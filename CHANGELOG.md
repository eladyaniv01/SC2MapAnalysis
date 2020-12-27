# Changelog

All notable changes to this project will be documented in this file. See [standard-version](https://github.com/conventional-changelog/standard-version) for commit guidelines.

### [1.19.4](https://github.com/eladyaniv01/SC2MapAnalysis/compare/v0.0.76...v1.19.4) (2020-12-27)


### Features

* Debugger now plots choke side a and side b with text indicators (sA, sB) ([595a964](https://github.com/eladyaniv01/SC2MapAnalysis/commit/595a96441c2ed1ae6fc528e88efb64423ae8fcac))
* fix pyastar ref in requirements ([c0d98f0](https://github.com/eladyaniv01/SC2MapAnalysis/commit/c0d98f007467b80bac319262ef1d660dd9b85979))
* Polygon now has top,bottom,right,left properties ([a43a283](https://github.com/eladyaniv01/SC2MapAnalysis/commit/a43a283a5a50cb43bbd125098efdfb253671d76a))
* use custom implementation ofr pyastar ([2b1e9ef](https://github.com/eladyaniv01/SC2MapAnalysis/commit/2b1e9ef152f34fd74485be224d6433ae733ada11))


### Bug Fixes

* int cast bug ([b055bf4](https://github.com/eladyaniv01/SC2MapAnalysis/commit/b055bf4fb5fcd82e6d8e45025451f6ced8edc2b3))
* scout now walks the path ([2f04b03](https://github.com/eladyaniv01/SC2MapAnalysis/commit/2f04b035baae8eacceaa7d5d127fe7acf7315d11))
* temp fix for climber grid test ([1f8f611](https://github.com/eladyaniv01/SC2MapAnalysis/commit/1f8f611ccb843ec903a8cf777a6b0879659d3b0d))
* temp fix for climber grid test ([e46ed3a](https://github.com/eladyaniv01/SC2MapAnalysis/commit/e46ed3ad8d38545f8311af2b338af28c40b0dede))


### Refactoring

* left right of choke are now side_a and side_b,   sides are computed accuratly now ([10e8dca](https://github.com/eladyaniv01/SC2MapAnalysis/commit/10e8dcae335ff6d700def798538747c8d9b8300f))


### Tests

* testing the choke sides are included in choke points ([308cf29](https://github.com/eladyaniv01/SC2MapAnalysis/commit/308cf29a36115c29fc5fa7b96d86b9a77cfaf337))


### Documentation

* **release:** pretty up changelog ([c8a697f](https://github.com/eladyaniv01/SC2MapAnalysis/commit/c8a697fc8c341212c4e5242568c308bc998fc65c))
* **release:** pretty up changelog ([731bd04](https://github.com/eladyaniv01/SC2MapAnalysis/commit/731bd042c1912a9bf357f37b2df9fe315dea1343))

### [0.0.77](https://github.com/eladyaniv01/SC2MapAnalysis/compare/v0.0.76...v0.0.77) (2020-12-13)


### Features

* Debugger now plots choke side a and side b with text indicators (sA, sB) ([9dd8c07](https://github.com/eladyaniv01/SC2MapAnalysis/commit/9dd8c072ebab8a66b99c42f792d7cde4c87a1fce))
* Polygon now has top,bottom,right,left properties ([8f5b0c9](https://github.com/eladyaniv01/SC2MapAnalysis/commit/8f5b0c9cd48a2f23dd1666f14becd41aae815df7))
* Round position in add_cost to reduce inaccuracy ([#100](https://github.com/eladyaniv01/SC2MapAnalysis/pull/100))

### Refactoring

* left right of choke are now side_a and side_b, sides are computed accuratly
  now ([125f881](https://github.com/eladyaniv01/SC2MapAnalysis/commit/125f8812266c0bc80931c8d80f822276be5753ef))

### Tests

* testing the choke sides are included in choke
  points ([e3b0b26](https://github.com/eladyaniv01/SC2MapAnalysis/commit/e3b0b26d556d4cde3c7724715e6a33c76a9e5c5e))

### Issues Closed:

* [#94 Bug: choke.left and choke.right don't take account the orientation of the choke](https://github.com/eladyaniv01/SC2MapAnalysis/issues/94)

### [0.0.76](https://github.com/eladyaniv01/SC2MapAnalysis/compare/v0.0.75...v0.0.76) (2020-11-24)

### Features

* add `include_destructables`  to  `get_climber_grid` in
  mapdata ([0e8aaf9](https://github.com/eladyaniv01/SC2MapAnalysis/commit/0e8aaf926013eb04c40c1a2c12324ad929a4496d))

### [0.0.75](https://github.com/eladyaniv01/SC2MapAnalysis/compare/v0.0.74...v0.0.75) (2020-11-07)

### Features

* ChokeArea now has left/right properties ([be13d59](https://github.com/eladyaniv01/SC2MapAnalysis/commit/be13d598a7fc8ab1d2ab5e7932d36698b9635cb6))
* MDRamp offset attribute for walloff, corner_walloff, middle_walloff_depot properties ([5fb232c](https://github.com/eladyaniv01/SC2MapAnalysis/commit/5fb232c9f21e4971a0508ad887561824780c50c8))
* plot_map now also draws the Left/Right bounds of each choke ([da66c0e](https://github.com/eladyaniv01/SC2MapAnalysis/commit/da66c0e7c0dfe90214463e374b1b23fbc513c02e))
* WIP  wall off points for each and every choke ([e99bb63](https://github.com/eladyaniv01/SC2MapAnalysis/commit/e99bb63acba3ca57e9a51b16cb22b6c0bab7f395))


### Bug Fixes

* fix install order in setup ([cdbf0f7](https://github.com/eladyaniv01/SC2MapAnalysis/commit/cdbf0f7de2d0d736ac07153467ff65a29dfe898d))
* overlapping chokes from sc2pathlib are merged (still WIP) ([38cdaa5](https://github.com/eladyaniv01/SC2MapAnalysis/commit/38cdaa506af8b4360ae57dcb713e79c7e3f07e70))
* typo,  import logger from loguru ([64d0960](https://github.com/eladyaniv01/SC2MapAnalysis/commit/64d096048ad447dad77f3227f53a3cfbc5b7ccb9))


### Refactoring

* add_cost is now a static method ([8217749](https://github.com/eladyaniv01/SC2MapAnalysis/commit/8217749cff9e3f5abd8465227590a2c91ff338f5))
* overall static methods to be static ([66b4b0e](https://github.com/eladyaniv01/SC2MapAnalysis/commit/66b4b0e010f08ce04b18c441eeab3d0b56197af4))
* remove log method from MapData ([0d98393](https://github.com/eladyaniv01/SC2MapAnalysis/commit/0d9839343974126eef35e85cf2cb493b2a463edf))

### [0.0.74](https://github.com/eladyaniv01/SC2MapAnalysis/compare/v0.0.73...v0.0.74) (2020-10-17)


### Features

* added example bot ref to README.MD ([7ceedf2](https://github.com/eladyaniv01/SC2MapAnalysis/commit/7ceedf2d16f86b34ecb7ad2b32e594987c2947f1))
* dummybot.py is an example bot with a few handy use cases showing ([35f1cc9](https://github.com/eladyaniv01/SC2MapAnalysis/commit/35f1cc9295e1afac3d59ee68bb8f767f0d350c91))

### Issues Closed:

 * [#74 create basic example bot usage ](https://github.com/eladyaniv01/SC2MapAnalysis/issues/74)


### [0.0.73](https://github.com/eladyaniv01/SC2MapAnalysis/compare/v0.0.72...v0.0.73) (2020-10-01)


### Bug Fixes

* fix clean_air_grid being wrongly constructed of integers instead of np.float32 ([278241c](https://github.com/eladyaniv01/SC2MapAnalysis/commit/278241c7378709ead938b6ddb84eda4f6d6c0e10))


### Documentation

* Added instruction on how to query cost in a specific point on the grid ([e0c8e19](https://github.com/eladyaniv01/SC2MapAnalysis/commit/e0c8e19f0602576eadc4b19d84035405ad61f761))


### Tests

* now testing clean_air_grid  for dtype bugfix by checking path lengths ([b47bae4](https://github.com/eladyaniv01/SC2MapAnalysis/commit/b47bae4f412cdd1e6785a0bb68c4eed8789f62f2))

### [0.0.72](https://github.com/eladyaniv01/SC2MapAnalysis/compare/v0.0.71...v0.0.72) (2020-09-29)


### Bug Fixes

* fix double transpose bug that happens when requesting low cost points more than once per frame ([ffd6b84](https://github.com/eladyaniv01/SC2MapAnalysis/commit/ffd6b843520a1b9eb3180d1a8429485495b61461))


### Tests

* find low cost points now also tests that the distance between the point and the origin makes sense( the array is not transposed) ([76a0e19](https://github.com/eladyaniv01/SC2MapAnalysis/commit/76a0e191fcd838c95a627df2b5ec531bd5b325d0))

### [0.0.71](https://github.com/eladyaniv01/SC2MapAnalysis/compare/v0.0.70...v0.0.71) (2020-09-28)


### Bug Fixes

* fixed transposed grid bug when searching for low cost points ,  added support for grids constructed from outside sources ([c127901](https://github.com/eladyaniv01/SC2MapAnalysis/commit/c1279014e36adbdeb578b7d5717a1833eb5bdefc))
* log compatability with bots ([8960716](https://github.com/eladyaniv01/SC2MapAnalysis/commit/896071677394c08993c10b4ea61025cb75620ad9))


### Tests

* find low cost points is now tested on all grid types ([6ec010d](https://github.com/eladyaniv01/SC2MapAnalysis/commit/6ec010d172d609a7d867a6c51b29320cf310b062))

### [0.0.70](https://github.com/eladyaniv01/SC2MapAnalysis/compare/v0.0.69...v0.0.70) (2020-09-22)

### Bug Fixes

* MapData now accepts a `corner_distance` variable that will determine the corner distance calculation ([294df181](https://github.com/eladyaniv01/SC2MapAnalysis/commit/294df181c272b218eef0c167f24d1db7650a7202))


### Build System

* add wheel to requirements and setup.py ([eb663a9](https://github.com/eladyaniv01/SC2MapAnalysis/commit/eb663a95c23c1e180ea385a783af306f47178c6e))

### Issues Closed:

 * [#88 BUG: all possible corners are not found ](https://github.com/eladyaniv01/SC2MapAnalysis/issues/88)

### [0.0.69](https://github.com/eladyaniv01/SC2MapAnalysis/compare/v0.0.68...v0.0.69) (2020-09-19)


### Bug Fixes

* fix pathing grid set up incorrectly when there are no vision blockers ([d49a084](https://github.com/eladyaniv01/SC2MapAnalysis/commit/d49a084543a90efc5d515b8af43072a1c1e39adb))

### [0.0.68](https://github.com/eladyaniv01/SC2MapAnalysis/compare/v0.0.67...v0.0.68) (2020-09-19)


### Features

* Buildable points now respect  flying buildings ([b90123f](https://github.com/eladyaniv01/SC2MapAnalysis/commit/b90123f84651488af8a3eea794b95cf94df0b094))
* pathfind method will now return the path without the start point in it ([06481d8](https://github.com/eladyaniv01/SC2MapAnalysis/commit/06481d8dfec5856bc966c4ec67f5d76c73dc460b))

### Bug Fixes

* Excluded lowered supply depots from non pathables #85 ([#85](https://github.com/eladyaniv01/SC2MapAnalysis/pull/85))

### Issues Closed:

 * [#84 Bug: Lowered supply depots added to non-pathable ground grid](https://github.com/eladyaniv01/SC2MapAnalysis/issues/84)

### [0.0.67](https://github.com/eladyaniv01/SC2MapAnalysis/compare/v0.0.66...v0.0.67) (2020-09-17)


### Features

* add cost now accepts `initial_default_weights` argument   (  known use case is for air_vs_ground grid ) ([7fe542f](https://github.com/eladyaniv01/SC2MapAnalysis/commit/7fe542f0a15daf90b0136453c0c6aa8f68242dd4))

### Issues Closed:

 * [#81 Air vs ground grid cost values in non ground pathable areas](https://github.com/eladyaniv01/SC2MapAnalysis/issues/81)
 
### [0.0.66](https://github.com/eladyaniv01/SC2MapAnalysis/compare/v0.0.64...v0.0.66) (2020-09-10)

### Features

* map_data.find_lowest_cost_points within a radius ([ab5073c](https://github.com/eladyaniv01/SC2MapAnalysis/pull/80/commits/ab5073cb57d0f5411d0f35a81c5c5b7a8609f602))
* map_data.draw_influence_in_game ([23d0004](https://github.com/eladyaniv01/SC2MapAnalysis/pull/79/commits/23d00040fe9c35c106152cd8d09a83c90a4e8795))


### Issues Closed:

 * [#78 Feature request: find lowest influence / cost within a radius](https://github.com/eladyaniv01/SC2MapAnalysis/issues/78)
 
### [0.0.64](https://github.com/eladyaniv01/SC2MapAnalysis/compare/v0.0.63...v0.0.64) (2020-09-06)

### Bug Fixes

* (81, 29) on EverDreamLE  is considered in map bounds even though it is not ([63b91f5](https://github.com/eladyaniv01/SC2MapAnalysis/commit/63b91f5d80688697617175a0155c68f3bd2b2668))
* air_vs_ground grid now accounts ramp points as pathable ([99ad04d](https://github.com/eladyaniv01/SC2MapAnalysis/commit/99ad04da4b57b360bf82ebcb930b1a9213f21d3d))


### Performance Improvements

* removed duplicate calculations from polygon _set_points ([948edeb](https://github.com/eladyaniv01/SC2MapAnalysis/commit/948edeb362bc1f4c15abe38a9864f17db70d6039))


### Tests

* air_vs_ground grid now tests that ramps are computed correctly ([6a37be1](https://github.com/eladyaniv01/SC2MapAnalysis/commit/6a37be15769774a2f25c43d8b08a523378d7875a))

### Issues Closed:

 * [#77 ramp points which are pathable, are not computed correctly in the air vs ground grid](https://github.com/eladyaniv01/SC2MapAnalysis/issues/77)
 * [#76 Bug (81, 29) is not in map bounds even though it passes the in_bounds check on EverDreamLE](https://github.com/eladyaniv01/SC2MapAnalysis/issues/76)


### [0.0.63](https://github.com/eladyaniv01/SC2MapAnalysis/compare/v0.0.62...v0.0.63) (2020-09-02)


### Bug Fixes

* debugger will now not try to inherit sc2 logger when in arcade mode ([03fefd7](https://github.com/eladyaniv01/SC2MapAnalysis/commit/03fefd71869d56fff31a32b24743f34d80538c2e))
* mapdata will now compile the map  in arcade mode, with limited information available ([92d9a5f](https://github.com/eladyaniv01/SC2MapAnalysis/commit/92d9a5fb8c438e3bfea0a879ae812b4113c82ec3))

### [0.0.62](https://github.com/eladyaniv01/SC2MapAnalysis/compare/v0.0.61...v0.0.62) (2020-09-02)


### Features

* Buildable points are now mapped to Point2,   logger now inherits sc2.main.logger ([7d8dc88](https://github.com/eladyaniv01/SC2MapAnalysis/commit/7d8dc8801eaafd435a53be2b914d07326675634f))
* MapData now accepts arcade boolean argument on init ([d380f2e](https://github.com/eladyaniv01/SC2MapAnalysis/commit/d380f2e22f96e897f2a6cf1c323f2f412433f2d1))


### Performance Improvements

* Pather changed the unpacking method of vision blockers into the grid ([7f4b9c3](https://github.com/eladyaniv01/SC2MapAnalysis/commit/7f4b9c3293b888305c1259f295ce15abfc363277))

### [0.0.61](https://github.com/eladyaniv01/SC2MapAnalysis/compare/v0.0.60...v0.0.61) (2020-08-30)


### Performance Improvements

* no need to convert path(numpy) to list anymore [https://github.com/BurnySc2/python-sc2/commit/cac70d738a24fcac749d371e8e0bed5e83b26b9e]

### Features

* added check that returns only points that are in bounds ([86891c9](https://github.com/eladyaniv01/SC2MapAnalysis/commit/86891c9fb8560ffa8006bc8e9ff6e88d1952f668))

* pather now includes geysers as non pathable ([94d592c](https://github.com/eladyaniv01/SC2MapAnalysis/commit/94d592c5e76b2cca79786ce963269521ceacd9a8))

### Issues Closed:

 * [#70 pather ignores geysers](https://github.com/eladyaniv01/SC2MapAnalysis/issues/70)
 * [#73 clean_air_grid size is bigger than playable area size, so pather with try to path to areas where units can't go](https://github.com/eladyaniv01/SC2MapAnalysis/issues/73)


### [0.0.60](https://github.com/eladyaniv01/SC2MapAnalysis/compare/v0.0.59...v0.0.60) (2020-08-30)


### Features

* visionblockers are now counted as pathable in the path grid ([8120fe9](https://github.com/eladyaniv01/SC2MapAnalysis/commit/8120fe954faab20ef88f3efd7522c1d521cab530))

### Issues Closed:

 * [#72 VisionBlockerArea is considered unpathable by the pathing grid ](https://github.com/eladyaniv01/SC2MapAnalysis/issues/72)

### [0.0.59](https://github.com/eladyaniv01/SC2MapAnalysis/compare/v0.0.58...v0.0.59) (2020-08-27)


### Refactoring

* removed in_region_i ([f8c7103](https://github.com/eladyaniv01/SC2MapAnalysis/commit/f8c710323456bb9755fd093783ea5ee9b2a7c058))


### Tests

* region tests now deault to using `where_all` instead of `where` ([1ec9fc1](https://github.com/eladyaniv01/SC2MapAnalysis/commit/1ec9fc1a7c0c675544c25bf5ad948c0d3f46ea62))
* removed `is_inside_indices` ([429dd52](https://github.com/eladyaniv01/SC2MapAnalysis/commit/429dd5251312c035482b5ef861dc6bb63894c66e))

### [0.0.58](https://github.com/eladyaniv01/SC2MapAnalysis/compare/v0.0.57...v0.0.58) (2020-08-26)


### Bug Fixes

* geysers are now accounted for iin the path grid,  lowered mineral radius,  changed the radius constants to more descriptive name (radius_factor) ([94d592c](https://github.com/eladyaniv01/SC2MapAnalysis/commit/94d592c5e76b2cca79786ce963269521ceacd9a8))

### [0.0.57](https://github.com/eladyaniv01/SC2MapAnalysis/compare/v0.0.56...v0.0.57) (2020-08-26)


### ⚠ BREAKING CHANGES

* Polygon.buildable_points  -> Polygon.buildables

### Features

* debugger now has .scatter method, moved readme examples to docs ([91be892](https://github.com/eladyaniv01/SC2MapAnalysis/commit/91be8925bcb22815c0b2edb806191a138467c6fd))


### Documentation

* slight  style changes ([dbc321c](https://github.com/eladyaniv01/SC2MapAnalysis/commit/dbc321c6eb6e8c8d35e3bca8cfd8eb973dd0581a))


### Refactoring

* BuildablePoints to Buildables ([ce3b7ac](https://github.com/eladyaniv01/SC2MapAnalysis/commit/ce3b7acb2d3cacdf7b744d76c2f9e02aabe71413))
* Pather add_influence to add_cost ([8cc6c47](https://github.com/eladyaniv01/SC2MapAnalysis/commit/8cc6c4747f1d0aa0228037cffa3d2989ee9ece83))

### [0.0.56](https://github.com/eladyaniv01/SC2MapAnalysis/compare/v0.0.55...v0.0.56) (2020-08-22)


### Bug Fixes

* fixed the calling order in polygon._set_points() ([2e60287](https://github.com/eladyaniv01/SC2MapAnalysis/commit/2e6028708efd7756925f0748f5aa8a4b14c80d14))


### Documentation

* pretty up with autoapi ([4835350](https://github.com/eladyaniv01/SC2MapAnalysis/commit/48353502ced12f937d36500702a9b4bc07e4c9e5))


### Refactoring

* version attribute is now in MapAnalyzer.__init__.py ,  updated versionbump methods  in vb,  and adjusted setup ([4409c7d](https://github.com/eladyaniv01/SC2MapAnalysis/commit/4409c7d2aea65b7ec5599916e0d466d3d82a4062))

### [0.0.55](https://github.com/eladyaniv01/SC2MapAnalysis/compare/v0.0.54...v0.0.55) (2020-08-20)


### Bug Fixes

* all point properties are now converted to int instead of np.int + tests for tuple vs Point2 ([120b27f](https://github.com/eladyaniv01/SC2MapAnalysis/commit/120b27fae6835dd7f4d3b00b0252d9b93068ac6c))


### Refactoring

* Polygon now calls ._set_points() instead of doing it in __init__ ([02229e2](https://github.com/eladyaniv01/SC2MapAnalysis/commit/02229e29b98570aafd28fa76e3edb0a293b45a26))


### Documentation

* build changlog for new version ([b5b357b](https://github.com/eladyaniv01/SC2MapAnalysis/commit/b5b357bf3549b7ff8b4d6752b1bf154a724f5fd3))
* clean up + fix vb makedocs ([3e68375](https://github.com/eladyaniv01/SC2MapAnalysis/commit/3e6837557536b9258cbd4a766c4bfafbb308fbe6))
* clean up readme a bit ([d7250fa](https://github.com/eladyaniv01/SC2MapAnalysis/commit/d7250fa312bf3d10b19db6c596cedd90e56586d7))
* documented polygon, region, constructs ([131bbd3](https://github.com/eladyaniv01/SC2MapAnalysis/commit/131bbd3793d2c981f25740cc98b8f540a6479859))

### [0.0.54](https://github.com/eladyaniv01/SC2MapAnalysis/compare/v0.0.48...v0.0.54) (2020-08-19)


### ⚠ BREAKING CHANGES

### Refactoring

* *add_influence* to *add_cost*, r to radius, p to position, arr to grid ([4bfbfee](https://github.com/eladyaniv01/SC2MapAnalysis/commit/4bfbfee6edbddaa1f45a0d1bc06b5edc61bcb643))
* compile_map is now a private method (_compile_map) ([8b27883](https://github.com/eladyaniv01/SC2MapAnalysis/commit/8b2788367c92f4eb5a4201ae96c165c75687f830))

### Bug Fixes

* all points returned from mapdata object will now be of type Point2,  and populated with standard integers

### Documentation

* documentation is in draft stage and can be found at https://eladyaniv01.github.io/SC2MapAnalysis


### [0.0.53](https://github.com/eladyaniv01/SC2MapAnalysis/compare/v0.0.48...v0.0.53) (2020-08-16)

### Features

* MapData.region_connectivity_all_paths will now return all options for pathing from Region to Region, while respecting a not_through list of regions to be excluded. ([9758950](https://github.com/eladyaniv01/SC2MapAnalysis/commit/975895046b8bda12af90e2c413a106ce013443fe))

* Base (#65) -> dev -> master (#66) ([60e2d2d](https://github.com/eladyaniv01/SC2MapAnalysis/commit/60e2d2de8cb89d6649a09e8e66e379483d0a7a0f)), closes [#65](https://github.com/eladyaniv01/SC2MapAnalysis/issues/65) [#66](https://github.com/eladyaniv01/SC2MapAnalysis/issues/66) [#64](https://github.com/eladyaniv01/SC2MapAnalysis/issues/64)

### Issues Closed:
 * [#51 Feature request: Pathfinding through regions](https://github.com/eladyaniv01/SC2MapAnalysis/issues/51)

### [0.0.52](https://github.com/eladyaniv01/SC2MapAnalysis/compare/v0.0.51...v0.0.52) (2020-08-15)

### ⚠ BREAKING CHANGES

* Region is now a Child of Polygon (Refactor)

### Bug Fixes

* regions and ramps now set each other correctly

* mapdata test for plotting ([b987fb6](https://github.com/eladyaniv01/SC2MapAnalysis/commit/b987fb6c29863cf57b30abfa5dad3b152456bcab))

* Base (#65) ([209d6d1](https://github.com/eladyaniv01/SC2MapAnalysis/commit/209d6d1c065893f98ce6bbfaeb34ab38b74e41a9)), closes [#65](https://github.com/eladyaniv01/SC2MapAnalysis/issues/65) [#64](https://github.com/eladyaniv01/SC2MapAnalysis/issues/64)


### [0.0.51](https://github.com/eladyaniv01/SC2MapAnalysis/compare/v0.0.50...v0.0.51) (2020-08-14)

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
