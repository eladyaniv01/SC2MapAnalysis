# Changelog

All notable changes to this project will be documented in this file. See [standard-version](https://github.com/conventional-changelog/standard-version) for commit guidelines.

### 0.0.25 (2020-08-07)


### ⚠ BREAKING CHANGES

* **cli interface for version bump:** None

### Features

* **cli interface for version bump:** Bump Version + changelog generation ([20b1e70](https://github.com/eladyaniv01/SC2MapAnalysis/commit/20b1e70693a3aef37eba068fb38965c82d076716))
* added fly grid as a flag when calling pyastar grid ([88600fa](https://github.com/eladyaniv01/SC2MapAnalysis/commit/88600fae45ed1632d2b7faee5babd9eb7fc8cad8))
* added instructions on how to plug in and how to use pathing ([9e92741](https://github.com/eladyaniv01/SC2MapAnalysis/commit/9e9274180d5c54ee3c38211ca212b45eb7a8dbed))
* added resource_blockers property , running tests locally ([6e3be41](https://github.com/eladyaniv01/SC2MapAnalysis/commit/6e3be4131adf49080ea8e69558ea884dc10399db))
* improve test polygon to be more strict ([f626f58](https://github.com/eladyaniv01/SC2MapAnalysis/commit/f626f581ec58a198fcdf81279c93fc909bf045c6))
* map_data can now plot a path with its weighted array ([51f9cd5](https://github.com/eladyaniv01/SC2MapAnalysis/commit/51f9cd5aba9b21713e6282418a1b77610b305f62))
* mapdata can now fetch cached pathing grid via _get_base_pathing_grid() ([97138a8](https://github.com/eladyaniv01/SC2MapAnalysis/commit/97138a8f1901ee491d37e20e7a4eb03e7d832ae3))
* optimized where_all , calc_ramps from C to B ([b801c64](https://github.com/eladyaniv01/SC2MapAnalysis/commit/b801c64efdfe1240eea9d348d7ee6e79551733a6))
* users can now decide if they want to use diagonal pathfinding ([cbfba20](https://github.com/eladyaniv01/SC2MapAnalysis/commit/cbfba2050ef17b90aa6c4e1c33b9d46e3e562ff1))


### Bug Fixes

*  attempting to set plot when isn't needed in testing ([a968588](https://github.com/eladyaniv01/SC2MapAnalysis/commit/a968588a23da90f6914dbf88a77302c59d15de2e))
*  pathfinder failing when passed start/ goal as float ([6776231](https://github.com/eladyaniv01/SC2MapAnalysis/commit/6776231640471704823d522a408f4f72dcae58a7))
* infulence inverted points ([a05e84d](https://github.com/eladyaniv01/SC2MapAnalysis/commit/a05e84deb7e2e870747d2ed09b6298c8b9ea1c4d))
* infulence inverted points ([6687015](https://github.com/eladyaniv01/SC2MapAnalysis/commit/6687015b6b4097b7b452151f95a05a7bc4cad3c8))
* path returns in correct order now (path[0] is start) ([3636dbd](https://github.com/eladyaniv01/SC2MapAnalysis/commit/3636dbde37978eb72498c95b720bc590ecd29685))
* pathfinder now returns the correct order (np.flipud) ([5900dce](https://github.com/eladyaniv01/SC2MapAnalysis/commit/5900dce37d25d05c568ac5de1211af782c4a7f01))
* pathfinder now returns the correct order (np.flipud) ([dae27c1](https://github.com/eladyaniv01/SC2MapAnalysis/commit/dae27c1055e59a7fbfcacc4d27c934f37b0ee078))
* polygon, chokearea, region ([fb77468](https://github.com/eladyaniv01/SC2MapAnalysis/commit/fb77468a606e083e1a997500f32639a7728a3560))
* type check bug when passing a numpy array ([729764e](https://github.com/eladyaniv01/SC2MapAnalysis/commit/729764e2c74c54203b777ca013ce3c88fab23c9d))

## [0.1.0](https://github.com/eladyaniv01/SC2MapAnalysis/compare/v0.0.24...v0.1.0) (2020-08-07)


### ⚠ BREAKING CHANGES

* **cli interface for version bump:** None

### Features

* **cli interface for version bump:** Bump Version + changelog generation ([20b1e70](https://github.com/eladyaniv01/SC2MapAnalysis/commit/20b1e70693a3aef37eba068fb38965c82d076716))

### [0.0.25](https://github.com/eladyaniv01/SC2MapAnalysis/compare/v0.0.24...v0.0.25) (2020-08-07)

### [0.0.24](https://github.com/eladyaniv01/SC2MapAnalysis/compare/v0.0.23...v0.0.24) (2020-08-07)
