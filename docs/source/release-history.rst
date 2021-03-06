===============
Release History
===============

Version 0.1 Initial release (2020-MM-DD)
----------------------------------------
* support for constructing MODFLOW-NWT or MODFLOW-6 models from scratch
* supported source dataset formats include GeoTiff, Arc-Ascii grids, shapefiles, NetCDF, and CSV files
* model input can also be supplied from parent model package input or MODFLOW binary output
* supported MODFLOW-NWT packages: DIS, BAS6, OC, UPW, RCH, GHB, SFR2, LAK, WEL, MNW2, HYD, GAGE, NWT
* supported MODFLOW-6 packages: DIS, IC, OC, NPF, RCHA, SFR, LAK, WEL, OBS, IMS, TDIS
* Telescopic mesh refinement (TMR) insets from MODFLOW-NWT models with specified head boundaries from parent head solution
* Local grid refinement (LGR) insets supported for MODFLOW-6 models.
* see .yml configuation files in mfsetup/tests/data folder for examples of valid input to modflow-setup
